#!/usr/bin/env python
# masarServer_p4p.py
#
# Pure-Python MASAR RPC server built on p4p (PVXS / QSRV2).
# Wire-compatible replacement for the legacy C++ pvAccessCPP RPCServer
# (cpp/src/masarServiceRun).  It speaks the same protocol as the existing
# C++ masarclient:
#
#   request  : NTNameValue  { string[] name, string[] value, string function }
#   response : epics:nt/NTTable:1.0 { string[] labels, structure value,
#                                     alarm_t alarm, time_t timeStamp }
#
# Backend is pymasarsqlite (pure Python) talking to the SQLite database
# pointed to by $MASAR_SQLITE_DB.  Live machine access (getLiveMachine and
# the live-gather part of saveSnapshot) uses Channel Access through
# cothread.catools, replacing the old C++ GatherV3Data.
#
# Copyright - See the COPYRIGHT that is included with this distribution.

from __future__ import print_function

import os
import sys
import time
import signal

from p4p import Type, Value
from p4p.server import Server, StaticProvider
from p4p.server.thread import SharedPV

import pymasarsqlite as pymasar


# ---------------------------------------------------------------------------
# EPICS DBR/DBF type groups (see db_access.h)
#   DBF_STRING 0  DBF_INT/SHORT 1  DBF_FLOAT 2  DBF_ENUM 3
#   DBF_CHAR 4    DBF_LONG 5       DBF_DOUBLE 6  DBF_NO_ACCESS 7
# ---------------------------------------------------------------------------
EPICS_INT = (1, 4, 5)
EPICS_STRING = (0, 3)
EPICS_DOUBLE = (2, 6)
EPICS_NOACCESS = (7,)

# alarm severities / status used by the legacy server
NO_ALARM = 0
MAJOR_ALARM = 2
CLIENT_STATUS = 7  # epics::pvData alarmStatus "clientStatus"

# standard 14-column labels for snapshot / live tables
SNAPSHOT_LABELS = (
    'pv name', 'string value', 'double value', 'long value', 'dbr type',
    'isConnected', 'secondsPastEpoch', 'nanoSeconds', 'timeStampTag',
    'alarmSeverity', 'alarmStatus', 'alarmMessage', 'is_array', 'array_value',
)


# ---------------------------------------------------------------------------
# Type helpers
# ---------------------------------------------------------------------------
_ALARM_T = ('S', 'alarm_t', [
    ('severity', 'i'), ('status', 'i'), ('message', 's')])
_TIME_T = ('S', 'time_t', [
    ('secondsPastEpoch', 'l'), ('nanoseconds', 'i'), ('userTag', 'i')])


def _norm(name):
    """Normalise a label into a valid structure field name (mirrors the
    normalizeFieldName() helper in the C++ dslPY.cpp)."""
    if not name:
        return 'col'
    out = []
    for c in str(name):
        if c.isalnum() or c == '_':
            out.append(c)
        else:
            out.append('_')
    if out[0].isdigit():
        out.insert(0, '_')
    return ''.join(out)


def _now_time_value(usertag=0):
    now = time.time()
    sec = int(now)
    nano = int(round((now - sec) * 1e9))
    return sec, nano, int(usertag)


def _set_alarm_time(val, severity, status, message, usertag=0):
    val['alarm.severity'] = severity
    val['alarm.status'] = status
    val['alarm.message'] = message
    sec, nano, tag = _now_time_value(usertag)
    val['timeStamp.secondsPastEpoch'] = sec
    val['timeStamp.nanoseconds'] = nano
    val['timeStamp.userTag'] = tag


# ---------------------------------------------------------------------------
# Result table builders
# ---------------------------------------------------------------------------
def build_status_table(ok, message):
    """Single boolean 'status' column table used for errors and for
    updateSnapshotEvent results (mirrors noDataEnetry / updateSnapshotEvent
    in dslPY.cpp)."""
    t = Type([
        ('labels', 'as'),
        ('value', ('S', None, [('status', 'a?')])),
        ('alarm', _ALARM_T),
        ('timeStamp', _TIME_T),
    ], 'epics:nt/NTTable:1.0')
    v = Value(t)
    v['labels'] = ['status']
    v['value.status'] = [bool(ok)]
    _set_alarm_time(v, MAJOR_ALARM, CLIENT_STATUS, message)
    return v


def build_events_table(labels, rows, numeric):
    """Build an NTTable where the first `numeric` columns are long[] and the
    remaining columns are string[].  Mirrors retrieveServiceConfigEvents() in
    dslPY.cpp.  `labels` is the label tuple, `rows` the list of data tuples."""
    tuple_size = len(labels)
    if tuple_size < numeric:
        numeric = tuple_size
    names = [_norm(labels[i]) for i in range(tuple_size)]

    cols = []
    for i in range(tuple_size):
        cols.append((names[i], 'al' if i < numeric else 'as'))
    t = Type([
        ('labels', 'as'),
        ('value', ('S', None, cols)),
        ('alarm', _ALARM_T),
        ('timeStamp', _TIME_T),
    ], 'epics:nt/NTTable:1.0')

    v = Value(t)
    v['labels'] = names

    for i in range(tuple_size):
        column = []
        for row in rows:
            cell = row[i]
            if i < numeric:
                column.append(int(cell) if cell is not None else 0)
            else:
                column.append('' if cell is None else str(cell))
        v['value.' + names[i]] = column

    _set_alarm_time(v, NO_ALARM, 0, '')
    return v


def _snapshot_type(names):
    arr_sub = [('stringVal', 'as'), ('doubleVal', 'ad'), ('intVal', 'ai')]
    cols = []
    for i, nm in enumerate(names):
        if i in (0, 1, 11):          # pv name, string value, alarm message
            cols.append((nm, 'as'))
        elif i == 2:                 # double value
            cols.append((nm, 'ad'))
        elif i == 13:                # array_value -> structure[]
            cols.append((nm, ('aS', 'structure', arr_sub)))
        else:                        # everything else stored as long[]
            cols.append((nm, 'al'))
    return Type([
        ('labels', 'as'),
        ('value', ('S', None, cols)),
        ('alarm', _ALARM_T),
        ('timeStamp', _TIME_T),
    ], 'epics:nt/NTTable:1.0')


def build_snapshot_table(labels, rows, usertag=0,
                         severity=NO_ALARM, status=0, message=''):
    """Build the 14-column snapshot/live NTTable (mirrors retrieveSnapshot()
    in dslPY.cpp).  `rows` is a list of per-channel 14-tuples:
      (pv name, string value, double value, long value, dbr type, isConnected,
       secondsPastEpoch, nanoSeconds, timeStampTag, alarmSeverity, alarmStatus,
       alarmMessage, is_array, array_value)
    """
    names = [_norm(labels[i]) for i in range(len(labels))]
    v = Value(_snapshot_type(names))
    v['labels'] = names

    n = len(rows)

    def _col(idx, cast, default):
        out = []
        for r in rows:
            c = r[idx]
            out.append(default if c is None else cast(c))
        return out

    # string columns
    v['value.' + names[0]] = _col(0, str, '')
    v['value.' + names[1]] = _col(1, str, '')
    v['value.' + names[11]] = _col(11, str, '')
    # double column
    v['value.' + names[2]] = _col(2, float, 0.0)
    # long columns
    for idx in (3, 4, 5, 6, 7, 8, 9, 10, 12):
        v['value.' + names[idx]] = _col(idx, int, 0)

    # array_value structure[]
    arr = []
    for r in rows:
        is_array = r[12]
        dbr = r[4] if r[4] is not None else 0
        av = r[13]
        entry = {}
        if is_array and av:
            if dbr in EPICS_INT:
                entry['intVal'] = [int(x) for x in av]
            elif dbr in EPICS_DOUBLE:
                entry['doubleVal'] = [float(x) for x in av]
            else:  # string / enum / no-access
                entry['stringVal'] = [str(x) for x in av]
        arr.append(entry)
    v['value.' + names[13]] = arr

    _set_alarm_time(v, severity, status, message, usertag)
    return v


# ---------------------------------------------------------------------------
# Live machine gather via Channel Access (cothread.catools)
# ---------------------------------------------------------------------------
def gather_live(channel_names):
    """Gather current values of the given V3 channels and return a list of
    per-channel 14-tuples in the format expected by both the snapshot table
    builder and pymasar.masardata.saveSnapshot.  Replaces the C++ GatherV3Data.
    """
    from cothread import catools

    n = len(channel_names)
    timeout = n * 1.0e-3
    if timeout < 1.0:
        timeout = 1.0
    if timeout > 10.0:
        timeout = 10.0

    results = catools.caget(list(channel_names), format=catools.FORMAT_TIME,
                            timeout=timeout, throw=False)

    # DBF_ENUM (dbr type 3) channels come back as a numeric index from a plain
    # caget.  The legacy C++ GatherV3Data stored the enum *label* string (e.g.
    # 'Enabled'), so do a second pass over just the enum channels requesting
    # DBR_ENUM_STR to resolve their string choices.  Keeps wire compatibility
    # with snapshots saved by the old MASAR server.
    enum_labels = {}
    enum_names = [name for name, r in zip(channel_names, results)
                  if getattr(r, 'ok', False) and int(getattr(r, 'datatype', 0)) == 3]
    if enum_names:
        enum_results = catools.caget(enum_names, datatype=catools.DBR_ENUM_STR,
                                     format=catools.FORMAT_TIME,
                                     timeout=timeout, throw=False)
        for en, er in zip(enum_names, enum_results):
            if getattr(er, 'ok', False):
                enum_labels[en] = er

    rows = []
    for name, r in zip(channel_names, results):
        connected = bool(getattr(r, 'ok', False))
        string_value = ''
        double_value = 0.0
        long_value = 0
        dbr = 0
        is_array = 0
        array_value = []
        sev = NO_ALARM
        sts = 0
        sec = 0
        nano = 0

        if connected:
            dbr = int(getattr(r, 'datatype', 0))
            sev = int(getattr(r, 'severity', 0) or 0)
            sts = int(getattr(r, 'status', 0) or 0)
            ts = float(getattr(r, 'timestamp', 0.0) or 0.0)
            sec = int(ts)
            nano = int(round((ts - sec) * 1e9))

            # determine array vs scalar.  A DBF_STRING scalar comes back from
            # catools as a Python str (ca_str), which supports len() and would
            # otherwise be mistaken for an N-character array -- treat str/bytes
            # as a single scalar value.
            if isinstance(r, (str, bytes)):
                count = 1
                scalar = True
            else:
                try:
                    count = len(r)
                    scalar = False
                except TypeError:
                    count = 1
                    scalar = True
            # a 1-element waveform is still a scalar to CA semantics here
            is_array = 0 if (scalar or count == 1) else 1

            if is_array:
                if dbr in EPICS_INT:
                    array_value = [int(x) for x in r]
                elif dbr in EPICS_DOUBLE:
                    array_value = [float(x) for x in r]
                elif dbr == 3 and name in enum_labels:  # enum array -> labels
                    array_value = [str(x) for x in enum_labels[name]]
                else:
                    array_value = [str(x) for x in r]
            else:
                scalar_val = r if scalar else r[0]
                if dbr in EPICS_DOUBLE:
                    double_value = float(scalar_val)
                    string_value = '%e' % double_value
                    long_value = int(double_value)
                elif dbr in EPICS_INT:
                    long_value = int(scalar_val)
                    double_value = float(long_value)
                    string_value = '%d' % long_value
                elif dbr == 3 and name in enum_labels:  # enum -> label string
                    el = enum_labels[name]
                    string_value = str(el if scalar else el[0])
                else:  # string / enum (label unavailable)
                    string_value = str(scalar_val)

        rows.append((
            str(name),       # 0  pv name
            string_value,    # 1  string value
            double_value,    # 2  double value
            long_value,      # 3  long value
            dbr,             # 4  dbr type
            1 if connected else 0,  # 5 isConnected
            sec,             # 6  secondsPastEpoch
            nano,            # 7  nanoSeconds
            0,               # 8  timeStampTag
            sev,             # 9  alarmSeverity
            sts,             # 10 alarmStatus
            '',              # 11 alarmMessage
            is_array,        # 12 is_array
            array_value,     # 13 array_value
        ))
    return rows


# ---------------------------------------------------------------------------
# Backend dispatch (mirrors masarserver/dslPYSQLite.py, but pure Python)
# ---------------------------------------------------------------------------
class MasarBackend(object):
    def __init__(self):
        self.servicename = 'masar'

    # -- helpers ----------------------------------------------------------
    @staticmethod
    def _get(params, key):
        return params.get(key)

    # -- read functions ---------------------------------------------------
    def retrieveServiceConfigProps(self, params):
        name = self._get(params, 'propname')
        service = self._get(params, 'servicename') or self.servicename
        config = self._get(params, 'configname')
        conn = pymasar.utils.connect()
        try:
            result = pymasar.service.retrieveServiceConfigProps(
                conn, propname=name, servicename=service, configname=config)
        finally:
            pymasar.utils.close(conn)
        return build_events_table(result[0], result[1:], 2)

    def retrieveServiceConfigs(self, params):
        service = self._get(params, 'servicename') or self.servicename
        config = self._get(params, 'configname')
        version = self._get(params, 'configversion')
        system = self._get(params, 'system')
        eid = self._get(params, 'eventid')
        if system == 'all':
            system = None
        conn = pymasar.utils.connect()
        try:
            result = pymasar.service.retrieveServiceConfigs(
                conn, servicename=service, configname=config,
                configversion=version, system=system, eventid=eid)
        finally:
            pymasar.utils.close(conn)
        return build_events_table(result[0], result[1:], 1)

    def retrieveServiceEvents(self, params):
        cid = self._get(params, 'configid')
        start = self._get(params, 'start')
        end = self._get(params, 'end')
        comment = self._get(params, 'comment')
        user = self._get(params, 'user')
        eid = self._get(params, 'eventid')
        conn = pymasar.utils.connect()
        try:
            result = pymasar.service.retrieveServiceEvents(
                conn, configid=cid, eventid=eid, start=start, end=end,
                comment=comment, user=user)
        finally:
            pymasar.utils.close(conn)
        return build_events_table(result[0], result[1:], 2)

    def retrieveSnapshot(self, params):
        eid = self._get(params, 'eventid')
        start = self._get(params, 'start')
        end = self._get(params, 'end')
        comment = self._get(params, 'comment')
        conn = pymasar.utils.connect()
        try:
            result = pymasar.masardata.retrieveSnapshot(
                conn, eventid=eid, start=start, end=end, comment=comment)
        finally:
            pymasar.utils.close(conn)
        if not isinstance(result, list) or len(result) != 2:
            return build_status_table(
                False, 'Wrong format for returned data when retrieving masar data.')
        head_array, data_array = result[0], result[1]
        labels = head_array[1]
        # first data row is a description, skip it
        rows = data_array[1:]
        if len(rows) < 0:
            return build_status_table(False, 'no channel found in this snapshot.')
        return build_snapshot_table(labels, rows)

    # -- write functions --------------------------------------------------
    def updateSnapshotEvent(self, params):
        eid = self._get(params, 'eventid')
        user = self._get(params, 'user')
        desc = self._get(params, 'desc')
        try:
            conn = pymasar.utils.connect()
            try:
                result = pymasar.service.serviceevent.updateServiceEvent(
                    conn, int(eid), comment=str(desc), approval=True,
                    username=str(user))
                pymasar.utils.save(conn)
            finally:
                pymasar.utils.close(conn)
        except Exception as exc:
            return build_status_table(False, 'Failed to approve snapshot: %s' % exc)
        if result:
            return build_status_table(True, 'Success to save snapshot preview.')
        return build_status_table(False, 'Failed to save snapshot preview.')

    def retrieveChannelNames(self, service, config):
        conn = pymasar.utils.connect()
        try:
            result = pymasar.service.retrieveServiceConfigPVs(
                conn, config, servicename=service)
        finally:
            pymasar.utils.close(conn)
        return list(result)

    def saveSnapshot(self, params):
        service = self._get(params, 'servicename') or self.servicename
        config = self._get(params, 'configname')
        comment = self._get(params, 'comment')

        try:
            channel_names = self.retrieveChannelNames(service, config)
        except Exception as exc:
            return build_status_table(
                False, 'Failed to retrieve channel names: %s' % exc)
        if not channel_names:
            return build_status_table(
                False, 'No channel found for configuration %r.' % config)

        try:
            rows = gather_live(channel_names)
        except Exception as exc:
            return build_status_table(False, 'Machine preview failed. %s' % exc)

        try:
            conn = pymasar.utils.connect()
            try:
                eid, _result = pymasar.masardata.saveSnapshot(
                    conn, rows, servicename=service, configname=config,
                    comment=comment)
                pymasar.utils.save(conn)
            finally:
                pymasar.utils.close(conn)
        except Exception as exc:
            return build_status_table(False, 'Machine preview failed. %s' % exc)

        return build_snapshot_table(
            SNAPSHOT_LABELS, rows, usertag=eid,
            severity=MAJOR_ALARM, status=CLIENT_STATUS,
            message='Machine preview Successed. All channels are connected.')

    def getLiveMachine(self, channel_names):
        try:
            rows = gather_live(channel_names)
        except Exception as exc:
            import traceback
            traceback.print_exc()
            return build_status_table(False, 'connect failed %s' % exc)
        return build_snapshot_table(
            SNAPSHOT_LABELS, rows,
            severity=MAJOR_ALARM, status=CLIENT_STATUS,
            message='Live machine: All channels are connected.')


# ---------------------------------------------------------------------------
# Request parsing + RPC handler
# ---------------------------------------------------------------------------
SUPPORTED = {
    'saveSnapshot', 'retrieveSnapshot', 'retrieveServiceConfigProps',
    'retrieveServiceConfigs', 'saveServiceConfig', 'retrieveServiceEvents',
    'saveServiceEvent', 'updateSnapshotEvent', 'getLiveMachine',
}


def _parse_request(req):
    """Return (function, names, values, params-dict) from an NTNameValue
    request Value."""
    function = ''
    try:
        function = str(req['function'])
    except Exception:
        pass
    names, values = [], []
    try:
        names = [str(x) for x in req['name']]
    except Exception:
        pass
    try:
        values = [str(x) for x in req['value']]
    except Exception:
        pass
    params = {}
    for n, v in zip(names, values):
        if n:
            params[n] = v
    return function, names, values, params


class MasarRPCHandler(object):
    def __init__(self, backend):
        self.backend = backend

    def put(self, pv, op):
        op.done(error='MASAR channel is RPC-only')

    def rpc(self, pv, op):
        try:
            req = op.value()
            function, names, values, params = _parse_request(req)

            if function not in SUPPORTED:
                op.done(self._unsupported(function))
                return

            backend = self.backend
            if function == 'getLiveMachine':
                # client passes the PV list as the request values
                result = backend.getLiveMachine(values)
            elif function == 'saveSnapshot':
                result = backend.saveSnapshot(params)
            elif function == 'retrieveSnapshot':
                result = backend.retrieveSnapshot(params)
            elif function == 'retrieveServiceConfigProps':
                result = backend.retrieveServiceConfigProps(params)
            elif function == 'retrieveServiceConfigs':
                result = backend.retrieveServiceConfigs(params)
            elif function == 'retrieveServiceEvents':
                result = backend.retrieveServiceEvents(params)
            elif function == 'updateSnapshotEvent':
                result = backend.updateSnapshotEvent(params)
            else:
                # saveServiceConfig / saveServiceEvent: accepted by the legacy
                # protocol but never implemented in the Python DSL layer.
                result = build_status_table(
                    False, 'Function %r is not implemented.' % function)
            op.done(result)
        except Exception as exc:
            import traceback
            traceback.print_exc()
            try:
                op.done(build_status_table(False, 'server error: %s' % exc))
            except Exception:
                op.done(error=str(exc))

    @staticmethod
    def _unsupported(function):
        return build_status_table(
            False, 'pvArgument has an unsupported function: %r' % function)


# ---------------------------------------------------------------------------
# Server bootstrap
# ---------------------------------------------------------------------------
def main(argv):
    channelname = argv[1] if len(argv) > 1 else os.environ.get(
        'MASAR_CHANNEL', 'masarService')

    dbfile = os.environ.get('MASAR_SQLITE_DB', '(unset)')
    print('MASAR p4p server starting')
    print('  channel : %s' % channelname)
    print('  database: %s' % dbfile)
    print('  Using SQLite as backend')

    backend = MasarBackend()
    handler = MasarRPCHandler(backend)

    # SharedPV must be open to be served; the initial value is never read by
    # clients because they always use channelRPC.
    pv = SharedPV(handler=handler, initial=build_status_table(True, 'ready'))

    provider = StaticProvider('masar')
    provider.add(channelname, pv)

    server = Server(providers=[provider])
    print('pvAccess (p4p/PVXS) server running. Channel = %r' % channelname)
    sys.stdout.flush()

    stop = {'flag': False}

    def _sig(signum, frame):
        stop['flag'] = True

    signal.signal(signal.SIGINT, _sig)
    signal.signal(signal.SIGTERM, _sig)

    try:
        while not stop['flag']:
            time.sleep(0.5)
    finally:
        server.stop()
        print('MASAR p4p server stopped')


if __name__ == '__main__':
    main(sys.argv)
