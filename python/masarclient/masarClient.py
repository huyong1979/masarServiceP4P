"""
Pure-Python client library for the MASAR (Machine Snapshot, Archiving and
Retrieve) service.

This is a drop-in replacement for the historical C++-backed client.  It talks
to the MASAR RPC server over pvAccess using p4p (PVXS / QSRV2) instead of the
legacy pvAccessCPP ChannelRPC + nttablePy/ntnameValuePy wrappers.  The public
API (class ``client`` and its methods) and all return values are identical to
the previous implementation, so the GUI (masarclient.ui.masar) needs no change.

Why pure Python:
  * removes the dependency on the compiled masar C++ modules (nttablePy,
    ntnameValuePy, channelRPCPy, gatherV3DataPy) and on libpvAccessCPP;
  * avoids the modern normativeTypesCPP ``NTTable::isCompatible`` check, which
    rejects the snapshot table's ``array_value`` structureArray column (the
    reason "Display Snapshot" failed against the strict C++ wrapper).

Request  : NTNameValue  { string function, string[] name, string[] value }
Response : epics:nt/NTTable:1.0 { string[] labels, structure value,
                                  alarm_t alarm, time_t timeStamp }

@author: shengb (original), pure-Python port
"""

from p4p import Type, Value
from p4p.client.thread import Context

__all__ = ['client']

# Request structure sent to the server.  The server matches fields by name, so
# field order here is irrelevant.
_NTNV_TYPE = Type([
    ('function', 's'),
    ('name', 'as'),
    ('value', 'as'),
], 'epics:nt/NTNameValue:1.0')

# Default RPC timeouts (seconds).
_TIMEOUT_DEFAULT = 10.0
_TIMEOUT_LIVE = 25.0   # getLiveMachine / saveSnapshot perform a live CA gather


def _build_request(function, params):
    v = Value(_NTNV_TYPE)
    v['function'] = function
    names = []
    values = []
    if params:
        for key, val in params.items():
            names.append(str(key))
            values.append('' if val is None else str(val))
    v['name'] = names
    v['value'] = values
    return v


class _ResultTable(object):
    """Thin wrapper over an NTTable ``Value`` that mimics the handful of
    methods the client code used from the old C++ NTTable wrapper:
    getLabel(), getNumberValues(), getValue(index) and getUserTag()."""

    def __init__(self, value):
        self._v = value
        try:
            self._labels = [str(x) for x in value['labels']]
        except Exception:
            self._labels = []
        # Column field names, in order, under the 'value' sub-structure.
        try:
            self._colnames = list(value['value'].keys())
        except Exception:
            self._colnames = list(self._labels)

    def getLabel(self):
        return self._labels

    def getNumberValues(self):
        return len(self._colnames)

    def getUserTag(self):
        try:
            return int(self._v['timeStamp.userTag'])
        except Exception:
            return 0

    def getMessage(self):
        """Server-side status/alarm message (used to surface fault reasons)."""
        try:
            return str(self._v['alarm.message'])
        except Exception:
            return ''

    @staticmethod
    def _as_list(x):
        if x is None:
            return []
        return list(x)

    def getValue(self, index):
        if index < 0 or index >= len(self._colnames):
            return None
        col = self._v['value.' + self._colnames[index]]
        # structureArray column (array_value): return a per-channel tuple of
        # (stringVal, doubleVal, intVal) lists, matching the old nttablePy
        # getStructureArrayValue() output.
        if isinstance(col, list) and len(col) > 0 and isinstance(col[0], Value):
            out = []
            for e in col:
                out.append((self._as_list(e['stringVal']),
                            self._as_list(e['doubleVal']),
                            self._as_list(e['intVal'])))
            return tuple(out)
        # scalar array column -> plain python list
        return self._as_list(col)


class client(object):
    def __init__(self, channelname='masarService'):
        """MASAR service client.  Default channel name is masarService."""
        self.channelname = channelname
        self._ctx = Context('pva')

    def close(self):
        try:
            self._ctx.close()
        except Exception:
            pass

    # -- internal RPC helpers --------------------------------------------
    def __clientRPC(self, function, params, timeout=_TIMEOUT_DEFAULT):
        request = _build_request(function, params)
        result = self._ctx.rpc(self.channelname, request, timeout=timeout)
        if result is None:
            raise Exception('No result returned from MASAR server for %r'
                            % function)
        return _ResultTable(result)

    @staticmethod
    def __isFault(table):
        label = table.getLabel()
        if not label:
            return True
        if label[0] == 'status':
            status = table.getValue(0)
            if status is None or len(status) == 0:
                return True
            if not status[0]:
                import sys as _sys
                msg = table.getMessage()
                _sys.stderr.write('[masar] server reported fault: %s\n'
                                  % (msg or '<no message>'))
                return True
        return False

    # -- public API ------------------------------------------------------
    def retrieveSystemList(self):
        """Retrieve all systems defined for the masar service.
        Returns a sorted list of system names, or False if none found."""
        table = self.__clientRPC('retrieveServiceConfigProps', {})
        if self.__isFault(table):
            return False
        valueCounts = table.getNumberValues()
        results = table.getValue(valueCounts - 1)
        return sorted(set(results))

    def retrieveServiceConfigs(self, params):
        """Retrieve configurations.  Returns a 6-tuple of columns
        (id, name, description, created-date, version, status) or False."""
        table = self.__clientRPC('retrieveServiceConfigs', params)
        if self.__isFault(table):
            return False
        return (table.getValue(0), table.getValue(1), table.getValue(2),
                table.getValue(3), table.getValue(4), table.getValue(5))

    def retrieveServiceEvents(self, params):
        """Retrieve the event list for a configuration.
        Returns (id, user-tag/comment, time, user-name) or False."""
        table = self.__clientRPC('retrieveServiceEvents', params)
        if self.__isFault(table):
            return False
        # 0: event_id, 1: config_id, 2: comment, 3: event_time, 4: user_name
        return (table.getValue(0), table.getValue(2),
                table.getValue(3), table.getValue(4))

    def retrieveSnapshot(self, params):
        """Retrieve a stored snapshot with real data.
        Returns a 12-tuple of columns (see module/GUI docs) or False.
        The last element (array_value) is a per-channel tuple of
        (stringVal, doubleVal, intVal) lists."""
        table = self.__clientRPC('retrieveSnapshot', params)
        if self.__isFault(table):
            return False
        return (table.getValue(0), table.getValue(1), table.getValue(2),
                table.getValue(3), table.getValue(4), table.getValue(5),
                table.getValue(6), table.getValue(7), table.getValue(9),
                table.getValue(10), table.getValue(12), table.getValue(13))

    def saveSnapshot(self, params):
        """Take a live machine snapshot, store it as an unapproved preview and
        return it.  Returns (eventid, <same 12 columns as retrieveSnapshot>) or
        False."""
        table = self.__clientRPC('saveSnapshot', params, timeout=_TIMEOUT_LIVE)
        if self.__isFault(table):
            return False
        return (table.getUserTag(),
                table.getValue(0), table.getValue(1), table.getValue(2),
                table.getValue(3), table.getValue(4), table.getValue(5),
                table.getValue(6), table.getValue(7), table.getValue(9),
                table.getValue(10), table.getValue(12), table.getValue(13))

    def updateSnapshotEvent(self, params):
        """Approve a snapshot.  Returns True on success, False otherwise."""
        table = self.__clientRPC('updateSnapshotEvent', params)
        status = table.getValue(0)
        if status is None or len(status) == 0:
            return False
        return status[0]

    def getLiveMachine(self, params):
        """Get live data for the given PV list (pv name is both key and value).
        Returns the same 12-tuple layout as retrieveSnapshot, or False."""
        table = self.__clientRPC('getLiveMachine', params, timeout=_TIMEOUT_LIVE)
        if self.__isFault(table):
            return False
        return (table.getValue(0), table.getValue(1), table.getValue(2),
                table.getValue(3), table.getValue(4), table.getValue(5),
                table.getValue(6), table.getValue(7), table.getValue(9),
                table.getValue(10), table.getValue(12), table.getValue(13))
