#!/usr/bin/env python
'''
Created on Dec 1, 2011

@Original author: shengb
@co-author: Yong Hu (yhu@bnl.gov)
'''

from __future__ import division
from __future__ import print_function

import os, sys, time, datetime, re, fnmatch, importlib.util, traceback, platform

from PySide6.QtWidgets import (QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QTableWidget,
                        QFileDialog)
from PySide6.QtGui import (QColor, QBrush, QShortcut, QKeySequence)
from PySide6.QtCore import (QDateTime, Qt, QEventLoop)

if sys.version_info[:2]>=(2,7):
    from collections import OrderedDict as odict
else:
    sys.exit("Python version 2.7 or higher is needed.")

try:
    from . import ui_masar
    from . import commentdlg
    from .showarrayvaluedlg import ShowArrayValueDlg
    from .selectrefsnapshotdlg import ShowSelectRefDlg
    from .finddlg import FindDlg
    from .verifysetpoint import VerifySetpoint
    from .gradualput import GradualPut
    from . import getmasarconfig
except ImportError:
    import ui_masar
    import commentdlg
    from showarrayvaluedlg import ShowArrayValueDlg
    from selectrefsnapshotdlg import ShowSelectRefDlg
    from finddlg import FindDlg
    from verifysetpoint import VerifySetpoint
    from gradualput import GradualPut
    import getmasarconfig

masarConfigDict = getmasarconfig.getmasarconfig()

try:
    if importlib.util.find_spec('pyOlog') is not None and str(masarConfigDict["Olog"]["use"]) == 'True':
        pyOlogExisting = True
    else:
        pyOlogExisting = False
except ImportError:
    pyOlogExisting = False


import masarclient.masarClient as masarClient
from masarclient.channelRPC import epicsExit

__version__ = "1.0.1"

def usage():
    print("""usage: masar.py [option]

command option:
-h  --help       help

masar.py v {0}. Copyright (c) 2011 Brookhaven National Laboratory. All rights reserved.
""".format(__version__))
    sys.exit()

# import this last to avoid import error on some platform and with different versions.
os.environ["EPICS_CA_MAX_ARRAY_BYTES"] = '40000000'
import cothread
import cothread.catools as cav3


class masarUI(QMainWindow, ui_masar.Ui_masar):
    severityDict= {0: 'NO_ALARM',
                   1: 'MINOR_ALARM',
                   2: 'MAJOR_ALARM',
                   3: 'INVALID_ALARM',
                   4: 'ALARM_NSEV'
    }

    alarmDict = { 0: 'NO_ALARM',
                 1: 'READ_ALARM',
                 2: 'WRITE_ALARM',
                 3: 'HIHI_ALARM',
                 4: 'HIGH_ALARM',
                 5: 'LOLO_ALARM',
                 6: 'LOW_ALARM',
                 7: 'STATE_ALARM',
                 8: 'COS_ALARM',
                 9: 'COMM_ALARM',
                 10: 'TIMEOUT_ALARM',
                 11: 'HW_LIMIT_ALARM',
                 12: 'CALC_ALARM',
                 13: 'SCAN_ALARM',
                 14: 'LINK_ALARM',
                 15: 'SOFT_ALARM',
                 16: 'BAD_SUB_ALARM',
                 17: 'UDF_ALARM',
                 18: 'DISABLE_ALARM',
                 19: 'SIMM_ALARM',
                 20: 'READ_ACCESS_ALARM',
                 21: 'WRITE_ACCESS_ALARM',
                 22: 'ALARM_NSTATUS'
    }


    def __init__(self, channelname='masarService', parent=None):
        super(masarUI, self).__init__(parent)
        self.setupUi(self)
        self.eventStartDateTime.setDateTime(QDateTime.currentDateTime())
        self.eventEndDateTime.setDateTime(QDateTime.currentDateTime())
        #the following 3 lines have to be before self.__initSystemCombox()
        self.__service = 'masar'
        self.mc = masarClient.client(channelname)
        self.currentConfigFilter = str(self.configFilterLineEdit.text())
        self.currentPvFilter = str(self.pvFilterLineEdit.text())
        self.pvFilterLineEdit.returnPressed.connect(self.searchPV)
        self.snapshotIdLineEdit.returnPressed.connect(self.retrieveSnapshotById)

        self.__initSystemCombox()
        time.sleep(1.0)

        self.eventConfigFilter = str(self.eventFilterLineEdit.text())
        self.authorText = str(self.authorTextEdit.text())
        self.UTC_OFFSET_TIMEDELTA = datetime.datetime.utcnow() - datetime.datetime.now()
        self.time_format = "%Y-%m-%d %H:%M:%S"
        self.tabWindowDict = {'comment': self.commentTab}# comment, preview, compare, filter
        self.e2cDict = {} # event to config dict; see retrieveEventData()
        self.pv4cDict = {} # pv name list for each selected configuration / eid
        self.data4eid = {} # snapshot data for eventId: 'filter' is an eventID
        self.arrayData = {} # store all array data
        self.previewId = None
        self.previewConfName = None
        self.isPreviewSaved = False
        # True only when the current preview already created a record in the MASAR database
        # (i.e. the saveSnapshot fallback was used). For the normal read-only getLiveMachine
        # preview this stays False, so clicking 'Ignore' leaves nothing in the database.
        self._previewInDb = False
        self.compareLiveWithMultiSnapshots = False
        self.compareSnapshotsTableKeys = []
        self.eventIds = []
        self.origID = ""
        self.tempPW = ''       # password cached after a successful authentication
        self._candidatePW = '' # not-yet-validated password from the Authentication dialog
        self.timeAtRetrieveSnapshot = 0
        self.timeAtSetSnapshotTabWindow = 0
        self.dlgFlag = [0]
        self.verifyWindowDict = {}#

        # set bad pv row to grey: they were disconnected when the snapshot was taken
        self.brushbadpv = QBrush(QColor(128, 128, 128))
        self.brushbadpv.setStyle(Qt.SolidPattern)
        # set currently disconnected pv row to pink
        self.brushdisconnectedpv = QBrush(QColor(255, 0, 255))
        self.brushdisconnectedpv.setStyle(Qt.SolidPattern)
        # DBR_TYPE definition
        #define DBF_STRING  0
        #define DBF_INT     1
        #define DBF_SHORT   1
        #define DBF_FLOAT   2
        #define DBF_ENUM    3
        #define DBF_CHAR    4
        #define DBF_LONG    5
        #define DBF_DOUBLE  6
        self.epicsLong   = [1, 4, 5]
        self.epicsString = [0, 3]
        self.epicsDouble = [2, 6]
        self.epicsNoAccess = [7]
        self.userID = os.popen('whoami').read()[:-1]
        dirPath = os.path.dirname(os.path.abspath(__file__))
        self.goldenDataFilePath = dirPath + '/goldenSnapshotData/'
        #automatically fetch all configs at startup. This action should be quick
        self.fetchConfigAction()
        time.sleep(1.0)


#********* Start of Config Table ******************************************************************
    def __initSystemCombox(self):
        # Block signals while populating: the combo's currentTextChanged is
        # already connected (in setupUi) to systemComboxChanged -> fetchConfigAction
        # -> retrieveConfigData, which would fire here before attributes such as
        # self.system / self.time_format / self.UTC_OFFSET_TIMEDELTA are set.
        self.systemCombox.blockSignals(True)
        self.systemCombox.addItem("")
        self.systemCombox.setItemText(0, "all")
        results = self.getSystemList()
        if results:
            for i in range(len(results)):
                self.systemCombox.addItem("")
                self.systemCombox.setItemText(i+1, results[i])
        self.system = str(self.systemCombox.currentText())
        self.systemCombox.blockSignals(False)


    def getSystemList(self):
        try:
            return self.mc.retrieveSystemList()
        except:
            QMessageBox.warning(self,
            "Warning",
            "Cannot connect to MASAR server to getSystemList.\nPlease check the serviceName, etc.")

            return


    def systemComboxChanged(self, qstring):
        """
        see ui_masar.py(.ui)
        QObject.connect(self.systemCombox,
                QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")), masar.systemComboxChanged)
        """
        self.system = str(qstring)
        self.fetchConfigAction()


    def configFilterChanged(self):
        """
        see ui_masar.py(.ui)
        QtCore.QObject.connect(self.configFilterLineEdit,
                QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), masar.configFilterChanged)
        """
        self.currentConfigFilter = str(self.configFilterLineEdit.text())
        self.fetchConfigAction()


    def fetchConfigAction(self):
        """
        see ui_masar.py(.ui)
        QtCore.QObject.connect(self.fetchConfigButton,
                QtCore.SIGNAL(_fromUtf8("clicked()")), masar.fetchConfigAction)
        """
        self.setConfigTable()
        self.configTableWidget.resizeColumnsToContents()


    def setConfigTable(self):
        """
        automatically get a list of snapshots if any config is selected by mouse or keyboard
        interesting: fetchEventAction() is called twice whenever config(s) is selected
        """
        reorderedData = odict([('Config Name', []), ('CID', []), ('Description', []),
                               ('Date', []), ('Status', []), ('Version', [])])
        data = self.retrieveConfigData()
        if not data:
            QMessageBox.warning(self, "Waring", "Can't get Configuration list")
            return
        if len(data['CID']) == 0:
            return

        confOrder = []
        try:
            confOrderStr = str(masarConfigDict["Order"]["conf_order"])
            confOrder = [int(conf) for conf in confOrderStr.split() if conf.isdigit()]
        except:
            pass

        confOrderSet = set(confOrder)
        if confOrderSet and confOrderSet.issubset(set(data['CID'])):
            for cf in confOrder:
                idx = list(data['CID']).index(cf)
                reorderedData['Config Name'].append(data['Config Name'][idx])
                reorderedData['CID'].append(cf)
                reorderedData['Description'].append(data['Description'][idx])
                reorderedData['Date'].append(data['Date'][idx])
                reorderedData['Status'].append(data['Status'][idx])
                reorderedData['Version'].append(data['Version'][idx])

            confL = list(set(data['CID']).difference(confOrderSet))
            confL.sort(reverse=True)

            for cf in confL:
                idx = list(data['CID']).index(cf)
                reorderedData['Config Name'].append(data['Config Name'][idx])
                reorderedData['CID'].append(cf)
                reorderedData['Description'].append(data['Description'][idx])
                reorderedData['Date'].append(data['Date'][idx])
                reorderedData['Status'].append(data['Status'][idx])
                reorderedData['Version'].append(data['Version'][idx])

            data = reorderedData
            self.configTableWidget.setSortingEnabled(False)
            self.setTable(data, self.configTableWidget)
            self.configTableWidget.sortByColumn(4, Qt.AscendingOrder)
            self.configTableWidget.setSortingEnabled(True)
        else:
            self.configTableWidget.setSortingEnabled(False)
            self.setTable(data, self.configTableWidget)
            self.configTableWidget.sortByColumn(3, Qt.DescendingOrder)
            self.configTableWidget.sortByColumn(4, Qt.AscendingOrder)
            self.configTableWidget.setSortingEnabled(True)

        self.configTableWidget.itemSelectionChanged.connect(self.fetchEventAction)

        self.configTableWidget.itemSelectionChanged.connect(lambda: self.resizeSplitter(0))


    def retrieveConfigData(self):
        data = odict()

        params = {"system": self.system,
                  "servicename": self.__service,
                  "configname": self.currentConfigFilter}
        try:
            rpcResult = self.mc.retrieveServiceConfigs(params)
            utctimes = rpcResult[3]
            config_ts = []
            for ut in utctimes:
                ts = str(datetime.datetime.fromtimestamp(
                         time.mktime(time.strptime(ut, self.time_format)))
                         - self.UTC_OFFSET_TIMEDELTA)
                config_ts.append(ts)

        except:
            print("%s: Fatal error happened during retrieving Configs"%datetime.datetime.now())
            QMessageBox.warning(self,
                                "Warning",
                                "Fatal error happened during retrieving configurations!")
            import atexit
            atexit._run_exitfuncs()
            epicsExit()
            sys.exit()#should we quit right away?

        if not rpcResult:
            return False

        data['Config Name'] = rpcResult[1]
        data['CID'] = rpcResult[0]
        data['Description'] = rpcResult[2]
        data['Date'] = config_ts
        data['Status'] = rpcResult[5]
        data['Version'] = rpcResult[4]
        return data


    def setTable(self, data, table):
        """
        Set data view.
        The data has to be an ordered dictionary, and table is a QtGui.QTableWidget
        Here is an example to construct an ordered dictionary.
        """
        if data:
            length = len(list(data.values())[0])
        else:
            print ('data is empty, exit.')
            return
        for i in range(1, len(data)):
            if length != len(list(data.values())[i]):
                QMessageBox.warning(self,
                                    "Warning",
                                    "Data length are not consistent.")

                return

        if isinstance(data, odict) and isinstance(table, QTableWidget):
            table.clear()
            nrows = len(list(data.values())[0])
            ncols = len(data)
            table.setRowCount(nrows)
            table.setColumnCount(ncols)
            table.setHorizontalHeaderLabels(list(data.keys()))

            n = 0
            for key in data:
                m = 0
                for item in data[key]:
                    if not isinstance(item, str):
                        item = str(item)
                    if item:
                        newitem = QTableWidgetItem(item)
                        newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
                        table.setItem(m, n, newitem)
                    m += 1
                n += 1
        else:
            raise RuntimeError("error occurred in setTable(self, data, table)")


    def resizeSplitter(self, tableID):
        if tableID == 1:
            self.splitter.setSizes([600,900])
        if tableID == 0:
            self.splitter.setSizes([600,900])
#********* End of Config Table ********************************************************************


    def createNewTableWidget(self, eventID, label):
        """
        types of tables in snapshotTab: comment(Welcome page), ordinary(double-click on event
        table), preview, compare, filter
        """
        if str(eventID) in self.tabWindowDict:
            tableWidget = self.tabWindowDict[str(eventID)]
        else:
            tableWidget = QTableWidget()
            self.tabWindowDict[str(eventID)] = tableWidget
            tableWidget.cellDoubleClicked.connect(self.__showArrayData)
            shortcut4Find = QShortcut(QKeySequence('Ctrl+F'), tableWidget)
            shortcut4Find.activated.connect(self.handleFind)

        self.snapshotTabWidget.addTab(tableWidget, label)
        self.snapshotTabWidget.setTabText(self.snapshotTabWidget.count(), label)
        self.snapshotTabWidget.setCurrentWidget(tableWidget)
        return tableWidget


    def handleFind(self):
        if self.dlgFlag[0] == 1:#only open one Find dialog
            return

        self.dlgFlag[0] = 1
        tabWidget = self.snapshotTabWidget
        findDlg = FindDlg(tabWidget, self.dlgFlag, self)
        findDlg.show()


#********* Start of Save machine snapshot *********************************************************
    def getAuthentication(self):
        if not masarConfigDict:
            return True # no authentication if no file for masar config

        if masarConfigDict['LDAP']['existing'] == 'True':
            import ldap
            try:
                from .authendlg import AuthenDlg
            except ImportError:
                from authendlg import AuthenDlg

            userID = self.userID
            dlg = AuthenDlg(self.tempPW)
            dlg.exec_()

            if dlg.isAccepted:
                self._candidatePW = dlg.result()
                ldap.protocol_version = 3
                ldap.set_option(ldap.OPT_REFERRALS, 0)
                # Trust the AD certificate chain so ldaps:// to the domain
                # controllers verifies properly WITHOUT disabling verification.
                # The python2-ldap uses a bundled OpenSSL so point it at the system trust bundle.
                # Configurable via [LDAP] cacertfile; defaults to the system bundle.
                cacert = masarConfigDict['LDAP'].get('cacertfile',
                             '/etc/pki/tls/certs/ca-bundle.crt')
                if cacert and os.path.isfile(cacert):
                    ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, cacert)
                    ldap.set_option(ldap.OPT_X_TLS_NEWCTX, 0)
                try:
                    lp = ldap.initialize(masarConfigDict['LDAP']['url'])
                    username = masarConfigDict['LDAP']['username']%userID
                    lp.simple_bind_s(username, self._candidatePW)
                    # Cache the validated password for the session.
                    self.tempPW = self._candidatePW
                    return True
                except ldap.INVALID_CREDENTIALS:
                    # The AD server was reachable and explicitly REJECTED the  password.
                    # This is a definite wrong-password, so never fall back to ignorepw.
                    self._candidatePW = ""
                    self.tempPW = ""
                    QMessageBox.warning(self, 'Warning',
                        "It seems you typed wrong password. You may try again. Your accounts "
                        "will be locked out if you fail multiple times in a few minutes.")
                    return False
                except:
                    # Any OTHER failure (every domain controller unreachable,
                    # TLS/network error, ...). We cannot validate the password,
                    # so honor ignorepw to keep MASAR usable when AD is down.
                    # Olog logging still validates the password independently.
                    if (masarConfigDict['LDAP']['ignorepw'] == 'True'
                            and 8 <= len(self._candidatePW) <= 32):
                        self.tempPW = self._candidatePW
                        return True

                    self._candidatePW = ""
                    self.tempPW = ""
                    QMessageBox.warning(self, 'Warning',
                        'Failed to get anthentication, try your password again if you like')
                    return False

            else:#if not dlg.isAccepted:
                return False

        return True #masarConfigDict['LDAP']['existing'] == 'False'


    def createLogEntry(self, logText, logbookName = None):
        """Attempt ONE Olog entry with the password obtained from getAuthentication().
        """
        if not (masarConfigDict and pyOlogExisting): return 'ok'

        # Pick the target logbook: explicit arg > config value > 'Operations'
        if not logbookName:
            try:
                logbookName = str(masarConfigDict['Olog']['logbookname']).strip()
            except:
                logbookName = 'Operations'

        try:
            # Compatibility shim: the shared pyOlog (normally run on Python 3.6)
            # uses configparser.SafeConfigParser, an alias removed in Python
            # 3.12+.  It is behaviourally identical to ConfigParser, so restore
            # the name instead of editing the read-only shared package.
            import configparser
            if not hasattr(configparser, 'SafeConfigParser'):
                configparser.SafeConfigParser = configparser.ConfigParser
            from pyOlog import SimpleOlogClient
            # ask=False stops pyOlog from falling back to an interactive
            # terminal getpass() prompt (invisible to a GUI operator).
            olog_client = SimpleOlogClient(url=str(masarConfigDict['Olog']['url']).strip(),
                                           username=self.userID,
                                           password=self._candidatePW,
                                           ask=False)

            olog_client.log(text=logText, logbooks=logbookName)
        except:
            errmsg = traceback.format_exc()
            print("%s: failed to create an Olog entry"%datetime.datetime.now())
            print(errmsg)
            try:
                dirPath = os.path.dirname(os.path.abspath(__file__))
                logFile = dirPath + '/masar.log'
                if os.path.isfile(logFile):
                    fd = open(logFile, 'a')
                    fd.write('%s: %s from %s FAILED to create an Olog entry:\n'
                             % (datetime.datetime.now(), self.userID, platform.node()))
                    fd.write(errmsg + '\n')
                    fd.close()
            except:
                print("Failed to write Olog-related entries to masar.log")

            # Make the failure visible: the operator's action itself succeeded,
            # but the logbook was NOT updated (e.g. Olog unreachable, or a wrong
            # password slipped through the ignorepw fallback).
            QMessageBox.warning(self, 'Olog Warning',
                'Your action completed, but creating the Olog logbook entry '
                'FAILED, so the logbook was NOT updated.\n'
                'Please notify the controls group (details in masar.log).')


    def saveMachineSnapshot(self):
        """
        See ui_masar.py(.ui):
        QtCore.QObject.connect(self.saveMachineSnapshotButton,
                    QtCore.SIGNAL(_fromUtf8("clicked()")), masar.saveMachineSnapshot)
        Purpose: implement one button 'Save Machine ...' to preview live data and then save.
        Challenge: get the pv list for getLiveMachineData(pvList) from the 'config' table
        Solution: get config name --> use retrieveEventData() to get at least one eventId
                    --> retrieveSnapshot() to get the pv list for that config
        """
        selectedConfig = self.configTableWidget.selectionModel().selectedRows()
        lc = len(selectedConfig)
        if lc != 1:
            QMessageBox.warning(self,
                "Warning",
                "Please select one configuration from the left-top Config Table, and one only.")
            return

        if not self.getAuthentication():
            return

        self.saveMachineSnapshotButton.setEnabled(False)
        QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
        self.previewId = None
        self.previewConfName = None
        if cav3.caget("arcapp-acc:MASAR-Cmd") == 0:
            return

        eventIds = []
        configIds = []
        configNames = []
        disConnectedPVs = []

        cname = str(self.configTableWidget.item(selectedConfig[0].row(), 0).text())
        configID = str(self.configTableWidget.item(selectedConfig[0].row(), 1).text())
        configDesc = str(self.configTableWidget.item(selectedConfig[0].row(), 2).text())
        # Build a PREVIEW of the current machine data. We prefer a pure, read-only live read
        # (getLiveMachine) so that NOTHING is written to the MASAR database until the user has
        # explicitly confirmed by clicking 'Continue...' and supplied a valid comment. This
        # requires the config's PV list, which we resolve from the config's most recent existing
        # snapshot. If the config has no previous snapshot (so its PV list cannot be resolved on
        # the client), we fall back to the legacy saveSnapshot() path, which resolves the PV list
        # server-side but creates an unapproved record immediately.
        pvlist = self._getConfigPvList(configID)
        if pvlist:
            # Pure read-only live read (NO database write). Reuse the existing
            # getLiveMachineData(), which returns a tuple; assemble it into the odict that
            # setSnapshotTable() and the rest of the snapshot machinery expect.
            liveData = self.getLiveMachineData(pvlist)
            if liveData:
                data = odict()
                data['PV Name']           = liveData[0]
                data['Status']            = liveData[9]
                data['Severity']          = liveData[10]
                data['Time stamp']        = liveData[11]
                data['Time stamp (nano)'] = liveData[12]
                data['DBR']               = liveData[4]
                data['S_value']           = liveData[1]
                data['I_value']           = liveData[3]
                data['D_value']           = liveData[2]
                data['isConnected']       = liveData[5]
                data['isArray']           = liveData[6]
                data['arrayValue']        = liveData[7]
            else:
                data = False
            eid = 'preview'
            self._previewInDb = False
        else:
            result = self._getMachinePreviewData(cname)
            if result:
                eid = result[0]
                data = result[1]
            else:
                data = False
            self._previewInDb = True

        if data:
                self.resizeSplitter(1)
                #The real event id is created at commit time (clean path) or already exists
                #(fallback path); see _saveMachinePreviewAction().
                self.previewId = eid
                self.previewConfName = cname
                self.isPreviewSaved = False
                self.pv4cDict[str(eid)] = data['PV Name']
                self.data4eid[str(eid)] = data
                self.e2cDict[str(eid)] = [configID, configDesc, cname]

                if self._previewInDb:
                    label = (cname+': Preview: '+str(eid))
                else:
                    label = (cname+': Preview (NOT saved yet)')
                tabWidget = self.createNewTableWidget('preview', label)
                self.setSnapshotTable(data, tabWidget, eid)
                #sort the table by "Connection"
                tabWidget.sortByColumn(1, Qt.DescendingOrder)

                for j in range(len(data['isConnected'])):
                    if not data['isConnected'][j]:
                        disConnectedPVs.append(data['PV Name'][j])

                if self._previewInDb:
                    savedHint = ("\n\nNOTE: this config had no previous snapshot, so a record "
                                 "was created immediately; clicking Ignore will leave an "
                                 "invisible (unapproved) snapshot.")
                else:
                    savedHint = ("\n\nThis is only a PREVIEW - nothing has been saved to the "
                                 "MASAR database yet. Clicking Ignore saves nothing.")

                if len(disConnectedPVs) > 0:
                    detailedText = ""
                    for i in range(len(disConnectedPVs)):
                        detailedText += '\n' + disConnectedPVs[i]
                    msg = QMessageBox(self, windowTitle="Warning",
                        text="%d PVs in the Config %s are disconnected, click Show Details ... "
                             "below to see the PV list.%s\n\nClick Continue... to save this "
                             "snapshot, otherwise click Ignore."
                             %(len(disConnectedPVs), cname, savedHint))
                    msg.setDetailedText(detailedText)
                else:
                    msg = QMessageBox(self, windowTitle="Good Machine Snapshot",
                        text="Great! All PVs in the Config %s have valid data so it's a good "
                             "snapshot.%s\n\nClick Continue... to save it, otherwise click "
                             "Ignore."%(cname,savedHint))

                msg.setModal(False)
                continueButton = msg.addButton("Continue...", QMessageBox.ActionRole)
                quitButton = msg.addButton(QMessageBox.Ignore)
                msg.setAttribute(Qt.WA_DeleteOnClose)
                msg.show()

                continueButton.clicked.connect(self._saveMachinePreviewAction)
                quitButton.clicked.connect(self._ignorePreviewAction)
        else: # not data
            self.saveMachineSnapshotButton.setEnabled(True)


    def _getMachinePreviewData(self, configName):
        """
        Take a snapshot via the saveSnapshot RPC, which reads the live machine AND writes an
        (unapproved) record to the MASAR database, returning (eventid, data).

        In the current design this is used (a) at commit time in the normal read-only flow -
        i.e. only after the user clicked 'Continue...' and gave a valid comment - and (b) as a
        fallback preview for configs that have no previous snapshot (where the PV list cannot be
        resolved on the client). It may generate an invisible snapshot if the user then ignores
        a fallback preview.
        """
        params = {'configname': configName,
                  'servicename': 'masar'}

        try:
            rpcResult = self.mc.saveSnapshot(params)
        except:
            QMessageBox.warning(self,
                                "Warning",
                                "Except happened during getting machine preview.")
            return False
        if not rpcResult:
            QMessageBox.warning(self,
                                "Warning",
                                "Failed to save a snapshot")
            print("failed to save a snapshot for %s"%configName)
            return False
        eventid = rpcResult[0]
        pvnames = rpcResult[1]
        s_value = rpcResult[2]
        d_value = rpcResult[3]
        i_value = rpcResult[4]
        dbrtype = rpcResult[5]
        isConnected = rpcResult[6]
        ts = rpcResult[7]
        ts_nano = list(rpcResult[8])
        severity = list(rpcResult[9])
        status = list(rpcResult[10])
        is_array = rpcResult[11]
        raw_array_value  = rpcResult[12]

        array_value = []
        for i in range(len(severity)):
            try:
                severity[i] = self.severityDict[severity[i]]
            except:
                severity[i] = 'N/A'
            try:
                status[i] = self.alarmDict[status[i]]
            except:
                status[i] = 'N/A'

            if dbrtype[i] in self.epicsLong:
                array_value.append(raw_array_value[i][2])
            elif dbrtype[i] in self.epicsDouble:
                array_value.append(raw_array_value[i][1])
            elif dbrtype[i] in self.epicsString:
                # string value
                array_value.append(raw_array_value[i][0])
            elif dbrtype[i] in self.epicsNoAccess:
                # when the value is no_access, use the double value no matter what it is
                array_value.append(raw_array_value[i][1])

        data = odict()
        data['PV Name'] = pvnames
        data['Status'] = status
        data['Severity'] = severity
        data['Time stamp'] = ts
        data['Time stamp (nano)'] = ts_nano
        data['DBR'] = dbrtype
        data['S_value'] = s_value
        data['I_value'] = i_value
        data['D_value'] = d_value
        data['isConnected'] = isConnected
        data['isArray'] = is_array
        data['arrayValue'] = array_value

        return (eventid, data)


    def _getConfigPvList(self, configID):
        """
        Resolve the PV name list for a configuration WITHOUT taking or saving a snapshot.

        The MASAR server exposes no dedicated RPC to resolve a config's PV list; its config->PV
        resolution (pgetchannames) is only invoked internally by saveSnapshot (which writes to
        the database). So we read the PV list back from the config's most recent existing
        snapshot via retrieveServiceEvents() + retrieveSnapshot().

        Returns a Python list of PV names, or None if the config has no prior snapshot (in which
        case the caller should fall back to the saveSnapshot-based preview).
        """
        try:
            rpcResult = self.mc.retrieveServiceEvents({'configid': str(configID)})
        except:
            QMessageBox.warning(self, "Warning",
                                "Exception happened while retrieving events for the config.")
            return None
        if not rpcResult:
            return None
        eids = list(rpcResult[0])
        if not eids:
            return None
        # Use the most recent event (highest auto-increment id) to reflect the latest PV set.
        try:
            latestEid = max(eids, key=lambda e: int(e))
        except Exception:
            latestEid = eids[0]
        data = self.retrieveMasarData(eventid=str(latestEid))
        if not data or not isinstance(data, odict):
            return None
        try:
            pvlist = list(data['PV Name'])
        except Exception:
            return None
        if not pvlist:
            return None
        return pvlist


    def _ignorePreviewAction(self):
        """
        The user chose 'Ignore' on the preview.

        In the normal read-only path (_previewInDb is False) the preview came from
        getLiveMachine(), a pure read, so NOTHING was written to the MASAR database - there is
        nothing to clean up and no invisible snapshot is created.

        In the fallback path (_previewInDb is True, used only for configs that had no previous
        snapshot) saveSnapshot() already created an unapproved record during the preview, so we
        preserve the historical behavior of logging it as an invisible snapshot.
        """
        self.saveMachineSnapshotButton.setEnabled(True)
        if self._previewInDb:
            logText = ("saved an invisible snapshot %s using CID# %s"
                       %(self.previewId, self.previewConfName))
            self.createLogEntry(logText)
        self.previewConfName = None


    def _saveMachinePreviewAction(self):
        self.saveMachineSnapshotButton.setEnabled(True)

        if self.previewConfName == None:
            QMessageBox.warning(self, "Warning",
                                'No preview to save. Please click '
                                '"Save Machine Snapshot ..." first')
            return

        if self.isPreviewSaved:
            QMessageBox.warning(self, "Warning",
                                "The preview for config (%s) has already been saved"
                                %(self.previewConfName))
            return

        comment = self.__getComment()

        # Only save if the user provided BOTH a user name and a description. If the comment
        # dialog is cancelled or incomplete, NOTHING is written to the database (read-only path).
        if not (comment and isinstance(comment, tuple) and comment[0] and comment[1]):
            QMessageBox.warning(self, "Not Saved",
                "No snapshot was saved to the MASAR database because the user name or comment "
                "was empty.\n\nClick 'Save Machine Snapshot ...' again to retry.")
            # In the fallback path a record already exists; keep it as an invisible snapshot.
            if self._previewInDb:
                self._ignorePreviewAction()
            return

        commentDetail = ''
        if pyOlogExisting:
            commentDetail = self.__getCommentDetail()

        confname = self.previewConfName

        if self._previewInDb:
            # Fallback path: the (unapproved) record already exists from the preview step; just
            # approve it with the user name and comment.
            eventid = self.previewId
        else:
            # Normal path: this is the FIRST time anything is written to the database. Take a
            # fresh live reading, create the (still unapproved) record and get its real id.
            result = self._getMachinePreviewData(confname)
            if not result:
                QMessageBox.warning(self, "Failures",
                                    "Failed to save a snapshot for config %s."%confname)
                return
            eventid = result[0]

        # Approve the snapshot with the user name and description.
        if self._saveMachinePreviewData(eventid, confname, comment):
            self.isPreviewSaved = True
            if commentDetail:
                logText = ("Succeed to save a snapshot #%s to MASAR database using "
                           "Config %s with description: %s.\nComment: %s"
                           %(eventid, confname, comment[1], commentDetail))
            else:
                logText = ("Succeed to save a snapshot #%s to MASAR database using "
                           "Config %s with description: %s"
                           %(eventid, confname, comment[1]))
            self.createLogEntry(logText)
        else:
            QMessageBox.warning(self, "Failures",
                                "Failed to approve snapshot #%s for config %s."
                                %(eventid, confname))


    def __getComment(self):
        cdlg = commentdlg.CommentDlg()
        cdlg.exec_()
        if cdlg.isAccepted:
            return (cdlg.result())
        else:
            return None


    def __getCommentDetail(self):
        try:
            from . import commentdetail
        except ImportError:
            import commentdetail
        cdlg = commentdetail.CommentDetail()
        cdlg.exec_()
        if cdlg.isAccepted:
            return (cdlg.result())
        else:
            return None


    def _saveMachinePreviewData(self, eventid, confname, comment):
        if not eventid:
            QMessageBox.warning(self,
                        "Warning",
                        "Unknown event.")
            return False

        params = {'eventid':    str(eventid),
                  'configname': str(confname),
                  'user':       str(comment[0]),
                  'desc':       str(comment[1])}
        try:
            result = self.mc.updateSnapshotEvent(params)
        except:
            QMessageBox.warning(self,
                                "Warning",
                                "Except happened during update snapshot event.")
            return False

        if result:
            QMessageBox.information(self, "Successful",
                "Succeed to save a snapshot %s to MASAR database using Conifg %s\n\n"
                "You may re-select the Config (click 'Select Snapshots(s)') to verify this "
                "new saved snapshot" %(eventid, confname))
            return True
        else:
            QMessageBox.information(self, "Failures", "Failed to save preview.")
            return False
#********* End of Save machine snapshot *********************************************************


#********* Start of machine snapshot retrieve *****************************************************
    def eventFilterChanged(self):
        """
        see ui_masar.py(.ui)
        QtCore.QObject.connect(self.eventFilterLineEdit,
                    QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), masar.eventFilterChanged)
        """
        self.eventConfigFilter = str(self.eventFilterLineEdit.text())
        self.fetchEventAction()


    def authorTextChanged(self):
        """
        see ui_masar.py(.ui)
        QtCore.QObject.connect(self.authorTextEdit,
                    QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), masar.authorTextChanged)
        """
        self.authorText = str(self.authorTextEdit.text())
        self.fetchEventAction()


    def useTimeRange(self, state):
        """
        see ui_masar.py(.ui)
        QtCore.QObject.connect(self.timeRangeCheckBox,
                    QtCore.SIGNAL(_fromUtf8("stateChanged(int)")), masar.useTimeRange)
        """
        if state == Qt.Checked:
            self.eventStartDateTime.setEnabled(True)
            self.eventEndDateTime.setEnabled(True)
        else:
            self.eventStartDateTime.setEnabled(False)
            self.eventEndDateTime.setEnabled(False)


    def fetchEventAction(self):
        """
        click the button 'Select Snapshot(s)' or 'Display Golden Snapshot'
        eventOrder is a list of numbers (not strings)
        see ui_masar.py(.ui)
        QtCore.QObject.connect(self.fetchEventButton,
                    QtCore.SIGNAL(_fromUtf8("clicked(void)")), masar.fetchEventAction)

         also in setConfigTable():
         QObject.connect(self.configTableWidget,
                            SIGNAL(_fromUtf8("itemSelectionChanged()")),self.fetchEventAction)
        """
        selectedConfigs = self.configTableWidget.selectionModel().selectedRows()
        if len(selectedConfigs) <= 0:
            return

        configIds=[]
        configNames = []
        for idx in selectedConfigs:
            configIds.append(str(self.configTableWidget.item(idx.row(), 1).text()))
            configNames.append(str(self.configTableWidget.item(idx.row(), 0).text()))

        data = self.retrieveEventData(configids=configIds, confignames=configNames)
        reorderedData = odict([('Config Name', []), ('SID', []), ('Description', []),
                               ('Time stamp', []), ('Author', [])])
        if not data:
            QMessageBox.warning(self, "warning","Can't retrieve event list")
            return

        eventOrder = [] # a list of numbers (not strings)
        #get golden SID first
        goldenDataFile = (self.goldenDataFilePath + "goldenSnapshotOf"
                          + str(configNames[0]) + ".data")
        if os.path.isfile(goldenDataFile):
            fd = open(goldenDataFile, 'r')
            lines = fd.readlines()
            fd.close()
            for line in lines:
                eventOrder.append(int(line.split('#')[0].strip()))
            eventOrder.reverse()

        if eventOrder != []: #add prefix G* to golden snapshot desc
            for i in range(len(eventOrder)):
                desc = " [G%i] "%(i+1)
                desc += data['Description'][list(data['SID']).index(eventOrder[i])]
                data['Description'][list(data['SID']).index(eventOrder[i])] = desc

        #get customzied SID from masar.cfg
        eventInConf = []
        eventInConfStr = ''
        try:
            for cname in configNames:
                eventInConfStr += str(masarConfigDict["Order"][str(cname).lower()]) + " "
                eventInConf = [int(evt) for evt in eventInConfStr.split() if evt.isdigit()]
        except:
            pass

        eventOrder += eventInConf
        eventOrderSet = set(eventOrder)
        if eventOrderSet and eventOrderSet.issubset(set(data['SID'])):
            for evt in eventOrder:
                idx = list(data['SID']).index(evt)
                reorderedData['Config Name'].append(data['Config Name'][idx])
                reorderedData['SID'].append(evt)
                reorderedData['Description'].append(data['Description'][idx])
                reorderedData['Time stamp'].append(data['Time stamp'][idx])
                reorderedData['Author'].append(data['Author'][idx])
            evtL = list(set(data['SID']).difference(eventOrderSet))
            evtL.sort(reverse=True)
            for evt in evtL:
                idx = list(data['SID']).index(evt)
                reorderedData['Config Name'].append(data['Config Name'][idx])
                reorderedData['SID'].append(evt)
                reorderedData['Description'].append(data['Description'][idx])
                reorderedData['Time stamp'].append(data['Time stamp'][idx])
                reorderedData['Author'].append(data['Author'][idx])
            data =  reorderedData
            self.eventTableWidget.setSortingEnabled(False)
            self.setEventTable(data)
            self.eventTableWidget.sortByColumn(0, Qt.DescendingOrder)
            self.eventTableWidget.setSortingEnabled(True)
        else:
            self.eventTableWidget.setSortingEnabled(False)
            self.setEventTable(data)
            self.eventTableWidget.setSortingEnabled(True)
            self.eventTableWidget.sortByColumn(3, Qt.DescendingOrder)
        self.eventTableWidget.resizeColumnsToContents()


    def retrieveEventData(self,configids=None,confignames=None):
        """
        only called by fetchEventAction(): EventData here doesn't inlcude epics PV data, it
        only gives event header information for given / selected Config -- how many
        events/snapshots have been taken retrieveMasarData(eventId) returns PV data.
        """
        start = None
        end = None
        if self.timeRangeCheckBox.isChecked():
            start = self.eventStartDateTime.dateTime().toPython() + self.UTC_OFFSET_TIMEDELTA
            end = self.eventEndDateTime.dateTime().toPython() + self.UTC_OFFSET_TIMEDELTA
            if start > end:
                QMessageBox.warning(self,
                            "Warning",
                            "Please select a correct time range.")
                return

        event_ids = []
        event_ts = []
        event_desc = []
        c_names = []
        event_author = []

        if configids:
            for i in range(len(configids)):
                cid = configids[i]
                params = {'configid': cid,
                          "comment": self.eventConfigFilter,
                          "user": self.authorText}
                if self.timeRangeCheckBox.isChecked():
                    params['start'] = str(start)
                    params['end'] = str(end)
                try:
                    rpcResult = self.mc.retrieveServiceEvents(params)
                except:
                    QMessageBox.warning(self,
                                "Warning",
                                "Except happened during retrieving events.")
                    return False
                if not rpcResult:
                    return False
                eids = rpcResult[0]
                usertag = rpcResult[1]
                utctimes = rpcResult[2]
                author = rpcResult[3]

                event_ids = event_ids[:] + (list(eids))[:]
                event_desc = event_desc[:] + (list(usertag))[:]
                event_author = event_author[:] + (list(author))[:]
                for j in range(len(eids)):
                    self.e2cDict[str(eids[j])] = [cid, usertag[j],confignames[i]]
                for ut in utctimes:
                    c_names.append(confignames[i])
                    ts = str(datetime.datetime.fromtimestamp(time.mktime(time.strptime(
                            ut, self.time_format))) - self.UTC_OFFSET_TIMEDELTA)
                    event_ts.append(ts)
        else:
            return False

        data = odict()
        data['Config Name'] = c_names
        data['SID'] = event_ids
        data['Description'] = event_desc
        data['Time stamp'] = event_ts
        data['Author'] = event_author
        return data


    def setEventTable(self, data):
        """
        interesting / potential problem: double click on any event will call retrieveSnapshot()
        many times, which makes retrieving snapshot slower. Clicking the fetchSnapshotButton
        only call retrieveSnapshot() once, which instantly retrieves snapshot(s)
        """
        self.setTable(data, self.eventTableWidget)
        self.eventTableWidget.doubleClicked.connect(self.retrieveSnapshot)


    def snapshotIdChanged(self):
        """
        see ui_masar.py(.ui)
        QtCore.QObject.connect(self.snapshotIdLineEdit,
                QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), masar.snapshotIdChanged)
        """
        snapshotID = self.snapshotIdLineEdit.text()


    def retrieveSnapshotById(self, eventId=" "):
        """
        see ui_masar.py(.ui)
        QtCore.QObject.connect(self.searchSnapshotButton,
                QtCore.SIGNAL(_fromUtf8("clicked()")), masar.retrieveSnapshotById)
        """
        if not isinstance(eventId, str) or eventId == " ":
            eventId = str(self.snapshotIdLineEdit.text())
        if not eventId.isdigit():
            QMessageBox.warning(self, 'Error', "You have to enter one integer number and "
                                "only one in the left box. Try again if you want")
            return

        eventIds = []
        eventIds.append(eventId)
        try:
            params = {'eventid': eventId}
            _service_configs = self.mc.retrieveServiceConfigs(params)
            (configID, configName, configDesc, date, version, status) = _service_configs
            (snapshotID, snapshotDesc, ts, author) = self.mc.retrieveServiceEvents(params)
            self.e2cDict[eventId] = [configID[0], snapshotDesc[0],configName[0]]
            eventNames = []
            eventTs = []
            for i in range(len(configName)):
                eventNames.append(configName[i])
                eventTs.append(ts[i])
        except:
            traceback.print_exc()
            QMessageBox.warning(self, "Error", "Can't get Config information related to "
                                "eventId:%s. You may have typed one invalid ID"%eventId)
            return

        self.setSnapshotTabWindow(eventNames, eventTs, eventIds)
        #highlight / select the Config and Event
        self.findConfigAndEvent(configName[0], eventId)


    def findConfigAndEvent(self, configName, eventId):
        configTable = self.configTableWidget
        for i in range(configTable.rowCount()):
            if configName == configTable.item(i, 0).text():
                configTable.setCurrentCell(i, 0)
                break

        eventTable = self.eventTableWidget
        for j in range(eventTable.rowCount()):
            if eventId == eventTable.item(j, 1).text():
                eventTable.setCurrentCell(j, 0)
                break


    def retrieveSnapshot(self):
        """
        Click the button 'Display Snapshot(s)'
        self.retrieveSnapshot() --> self.setSnapshotTabWindow() --> self.retrieveMasarData() -->
            --> self.mc.retrieveSnapshot

        see ui_masar.py(.ui)
        QtCore.QObject.connect(self.fetchSnapshotButton,
                                QtCore.SIGNAL(_fromUtf8("clicked(void)")), masar.retrieveSnapshot)

        also in setEventTable():
        self.eventTableWidget.doubleClicked.connect(self.retrieveSnapshot)
        """
        selectedItems = self.eventTableWidget.selectionModel().selectedRows()
        if len(selectedItems) <= 0:
            QMessageBox.warning(self,
                            "Warning",
                            "Please select at least one Snapshot in the Snapshot table above.")
            return

        eventTs=[]
        eventNames=[]
        eventIds = []
        for idx in selectedItems:
            eventNames.append(str(self.eventTableWidget.item(idx.row(), 0).text()))
            eventTs.append(str(self.eventTableWidget.item(idx.row(), 3).text()))
            eventIds.append(str(self.eventTableWidget.item(idx.row(), 1).text()))

        self.timeAtRetrieveSnapshot = time.time()
        loopTime = self.timeAtRetrieveSnapshot - self.timeAtSetSnapshotTabWindow
        if loopTime > 1.0: #fix the problem: double-click triggers multiple-retrieve-requests
            self.setSnapshotTabWindow(eventNames, eventTs, eventIds)


    def setSnapshotTabWindow(self, eventNames, eventTs, eventIds):
        """
        ideally, this method only sets snapshot table.
        retrieveMasarData() should be in retrieveSnapshot().
        SIGNAL(_fromUtf8("cellDoubleClicked (int,int)")),self.__showArrayData):
            __showArrayData() is called once, which is correct
        """
        tableWidget = None
        isNew = True

        for i in range(len(eventIds)):
            data = self.retrieveMasarData(eventid=eventIds[i])
            if data == None or not isinstance(data, odict):
                QMessageBox.warning(self, "Warning",
                                    "Can't get snapshot data for eventId:%s"%eventIds[i])

            ts = eventTs[i].split('.')[0]
            label = (eventNames[i]+': ' +eventIds[i]+": "+ ts)
            tableWidget = self.createNewTableWidget(eventIds[i], label)
            self.setSnapshotTable(data, tableWidget, eventIds[i])

            self.pv4cDict[str(eventIds[i])] = data['PV Name']
            self.data4eid[str(eventIds[i])] = data
            tableWidget.setStatusTip("Snapshot data of " + eventNames[i] + " saved at " + ts)
            tableWidget.setToolTip("Sort the table by column \n Ctrl + C to copy \n "
                "                                    Double click to view waveform data")
            self.resizeSplitter(1)

        self.snapshotTabWidget.setCurrentIndex(self.snapshotTabWidget.count())
        self.snapshotTabWidget.setCurrentWidget(tableWidget)
        self.timeAtSetSnapshotTabWindow = time.time()


    def __showArrayData(self, row, column):
        #if column != 5 and column != 6: # display the array value only
        curWidget = self.snapshotTabWidget.currentWidget()
        if not isinstance(curWidget, QTableWidget):
            QMessageBox.warning(self, 'Warning', 'No snapshot is selected yet.')
            return

        pvname = str(curWidget.item(row, 0).text())
        eid = self.__find_key(self.tabWindowDict, curWidget)
        eid_ = eid
        if eid == 'comment':
            QMessageBox.warning(self, 'Warning', 'It is comment panel.')
            return
        #in non-compare tab, saved value / live value  is in column 3 / 4
        if eid != "compare":
            if column != 3 and column != 4:
                return
        if eid == "compare":
            if column < 1 or column > 1 + len(self.eventIds):
                return

        if eid == 'preview':
            eid_ = self.previewId
        if eid == "compare":
            if column == 1 + len(self.eventIds):#live value column: use the Ref. snapshot
                eid_ = str(self.eventIds[0])+'_compare'
            else:
                eid_ = str(self.eventIds[column-1])+'_compare'
        try:
            arraySaved = self.arrayData[pvname+'_'+str(eid_)]
        except:
            QMessageBox.warning(self, 'Warning', 'No saved array data for the PV %s'%pvname)
            return

        if eid != 'preview':
            try:
                arrayLive = self.arrayData[pvname+"_"+str(eid)+'_live']
                arrardlg = ShowArrayValueDlg(pvname, arraySaved, arrayLive)
            except:
                arrardlg = ShowArrayValueDlg(pvname, arraySaved)
        else:
            arrardlg = ShowArrayValueDlg(pvname, arraySaved)

        arrardlg.exec_()


    def __find_key(self, dic, val):
        """return the key of dictionary dic given the value"""
        return [k for k, v in dic.items() if v == val][0]


    def retrieveMasarData(self, eventid=None):
        """
        retrieve saved snapshot data including time stamp, alarm, etc. from MASAR database
        called by setSnapshotTabWindow() and compareSnapshots()
        """
        data = odict()
        params = {'eventid': eventid}

        try:
            rpcResult = self.mc.retrieveSnapshot(params)
        except:
            return rpcResult

        if not rpcResult:
            return False

        pvnames = rpcResult[0]
        s_value = rpcResult[1]
        d_value = rpcResult[2]
        i_value = rpcResult[3]
        dbrtype = rpcResult[4]
        isConnected = rpcResult[5]
        ts = rpcResult[6]
        ts_nano = rpcResult[7]
        severity = list(rpcResult[8])
        status = list(rpcResult[9])
        is_array = rpcResult[10]
        raw_array_value  = rpcResult[11]

        array_value = []
        for i in range(len(severity)):
            try:
                severity[i] = self.severityDict[severity[i]]
            except:
                severity[i] = 'N/A'
            try:
                status[i] = self.alarmDict[status[i]]
            except:
                status[i] = 'N/A'

            if dbrtype[i] in self.epicsLong:
                array_value.append(raw_array_value[i][2])
            elif dbrtype[i] in self.epicsDouble:
                array_value.append(raw_array_value[i][1])
            elif dbrtype[i] in self.epicsString:
                # string value
                array_value.append(raw_array_value[i][0])
            elif dbrtype[i] in self.epicsNoAccess:
                # when the value is no_access, use the double value no matter what it is
                array_value.append(raw_array_value[i][1])

        data['PV Name'] = pvnames
        data['Status'] = status
        data['Severity'] = severity
        data['Time stamp'] = ts
        data['Time stamp (nano)'] = ts_nano
        data['DBR'] = dbrtype
        data['S_value'] = s_value
        data['I_value'] = i_value
        data['D_value'] = d_value
        data['isConnected'] = isConnected
        data['isArray'] = is_array
        data['arrayValue'] = array_value

        return data


    def setSnapshotTable(self, data, table, eventid):
        """
        called by setSnapshotTabWindow(), saveMachineSnapshot()(preview table), and searchPV()
        This table is different from compareSnapshotsTable, see setCompareSnapshotsTable()
        """
        if data:
            length = len(list(data.values())[0])
        else:
            print ('data is empty, exit.')
            return

        for i in range(1, len(data)):
            if length != len(list(data.values())[i]):
                QMessageBox.warning(self,
                                    "Warning",
                                    "Data length are not consistent.")
                return

        if isinstance(data, odict) and isinstance(table, QTableWidget):
            table.setSortingEnabled(False)
            table.clear()

            nrows = len(list(data.values())[0])
            keys = ['PV Name', 'Saved Connection', 'Not Restore','Saved Value','Live Value','Diff',
                    'Saved Timestamp', 'Saved Status','Saved Severity',
                    'Live Connection', 'Live Timestamp', 'Live Status', 'Live Severity']
            ncols = len(keys)
            table.setRowCount(nrows)
            table.setColumnCount(ncols)
            table.setHorizontalHeaderLabels(keys)

            pvnames = data['PV Name']
            status = data['Status']
            severity = data['Severity']
            ts = data['Time stamp']
            ts_nano = data['Time stamp (nano)']
            dbrtype = data['DBR']
            s_value = data['S_value']
            i_value = data['I_value']
            d_value = data['D_value']
            isConnected = data['isConnected']
            is_array = data['isArray']
            array_value = data['arrayValue']

            for i in range(nrows):
                item = table.item(i, 2)
                if item:
                    item.setCheckState(Qt.Unchecked)
                else:
                    item = QTableWidgetItem()
                    item.setFlags(Qt.ItemIsEnabled|Qt.ItemIsUserCheckable)
                    table.setItem(i, 2, item)
                    item.setCheckState(Qt.Unchecked)

                if pvnames[i]:
                    self.__setTableItem(table, i, 0, pvnames[i])
                if status[i]:
                    self.__setTableItem(table, i, 7, str(status[i]))
                if severity[i]:
                    self.__setTableItem(table, i, 8, str(severity[i]))
                if ts[i]:
                    dt = str(datetime.datetime.fromtimestamp(ts[i]+ts_nano[i]*1.0e-9))
                    self.__setTableItem(table, i, 6, dt)

                if is_array[i]:
                    self.__setTableItem(table, i, 3, self.__arrayTextFormat(array_value[i]))
                    self.arrayData[pvnames[i]+'_'+str(eventid)] = array_value[i]
                else:
                    if dbrtype[i] in self.epicsDouble:
                        self.__setTableItem(table, i, 3, str(d_value[i]))
                    elif dbrtype[i] in self.epicsLong:
                        self.__setTableItem(table, i, 3, str(i_value[i]))
                    elif dbrtype[i] in self.epicsString:
                        self.__setTableItem(table, i, 3, str(s_value[i]))
                    elif dbrtype[i] in self.epicsNoAccess:
                        # channel are not connected.
                        pass
                    else:
                        print('invalid dbr type (code = %s)'%(dbrtype[i]))

                if isConnected[i]:
                    self.__setTableItem(table, i, 1, "Connected")
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                else:
                    self.__setTableItem(table, i, 1, 'Disconnected')
                    item.setCheckState(Qt.Checked)
                    item.setSelected(True)
                    # disable user checkable function
                    item.setFlags(item.flags() ^ Qt.ItemIsUserCheckable)
                    for item_idx in range(9):
                        itemtmp = table.item(i, item_idx)
                        if not itemtmp:
                            itemtmp = QTableWidgetItem()
                            table.setItem(i, item_idx, itemtmp)
                        itemtmp.setBackground(self.brushbadpv)

            table.setSortingEnabled(True)
            #be careful of this sorting action
            #sort by "Connection"
            table.sortItems(1, Qt.DescendingOrder)
            table.resizeColumnsToContents()
        else:
            raise RuntimeError("Error occurred in setSnapshotTable(self, data, table, eventid)")


    def __setTableItem(self, table, row, col, text):
        item = table.item(row, col)
        if item:
            item.setText(text)
        else:
            newitem = QTableWidgetItem(text)
            newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
            table.setItem(row, col, newitem)


    def __arrayTextFormat(self, arrayvalue):
        """
        display max 8 characters in a table cell
        """
        array_text = str(arrayvalue)

        if len(str(array_text)) > 8:
            array_text = str(array_text)[:8]+' ..., ...)'

        return array_text
#********* End of machine snapshot retrieve *******************************************************


#************************** Start of config snapShotTab *******************************************
    def closeTab(self, index):
        """
        snapshotTab is closable, movable
        See ui_masar.py(.ui):
        QtCore.QObject.connect(self.snapshotTabWidget,
                    QtCore.SIGNAL(_fromUtf8("tabCloseRequested(int)")), masar.closeTab)
        """
        #index = self.snapshotTabWidget.currentIndex()
        if index != 0:
            self.snapshotTabWidget.removeTab(index)
        else:
            QMessageBox.warning(self, "Waring",
                                "Please don't close this page since it has all instructions")


    def configTab(self):
        """
        Highligt the tabBar of the active/selected snapshotTab
        and highlight snapshot related Config / Event
        See ui_masar.py(.ui):
        QtCore.QObject.connect(self.snapshotTabWidget,
                    QtCore.SIGNAL(_fromUtf8("currentChanged(int)")), masar.configTab)
        """
        bar = self.snapshotTabWidget.tabBar()
        totalTabs = self.snapshotTabWidget.count()
        curIndex = self.snapshotTabWidget.currentIndex()
        for i in range(totalTabs):
            if i == curIndex:
                bar.setTabTextColor(i, Qt.blue)
            else:
                bar.setTabTextColor(i, Qt.gray)

        #automatically update Config & Event table:
        try:
            curWidget = self.snapshotTabWidget.currentWidget()
            if not isinstance(curWidget, QTableWidget):
                self.fetchConfigAction() # update / un-highlight Configtable
                self.eventTableWidget.clearContents()
                return

            eid = self.__find_key(self.tabWindowDict, curWidget)
            if eid == 'comment' or eid == 'compare':
                self.fetchConfigAction() # update / un-highlight Configtable
                self.eventTableWidget.clear()
                return
            if eid == 'preview':
                eid = self.previewId
            if eid == 'filter':
                eid = self.origID

            [cid, desc, configName] = self.e2cDict[str(eid)]
            self.findConfigAndEvent(configName, str(eid))
        except:
            traceback.print_exc()
#************************** End of config snapShotTab *********************************************


#************************ Start of machine restore: simple put or ramping *************************
    def ignore4RestoreMachine(self):
        self.restoreMachineButton.setEnabled(True)
        self.rampingMachineButton.setEnabled(True)

    def getRestoreInfo(self):
        curWidget = self.snapshotTabWidget.currentWidget()
        if not isinstance(curWidget, QTableWidget):
            QMessageBox.warning(self, 'Warning',
                        'No snapshot is selected yet. Please refer Welcome to MASAR for help')
            self.restoreMachineButton.setEnabled(True)
            self.rampingMachineButton.setEnabled(True)
            return

        eid = self.__find_key(self.tabWindowDict, curWidget)
        if eid == 'comment' or eid == 'preview' or eid == 'compare':
            QMessageBox.warning(self, 'Warning',
                        'No restore, %s tab is selected. Please select other Non-%s Tab'%(eid,eid))
            self.restoreMachineButton.setEnabled(True)
            self.rampingMachineButton.setEnabled(True)
            return
        if eid == 'filter':
            eid4Log = self.origID + '(filtered with pattern %s)'%self.currentPvFilter
        else:
            eid4Log = eid

        if not self.getAuthentication():
            self.restoreMachineButton.setEnabled(True)
            self.rampingMachineButton.setEnabled(True)
            return

        selectedNoRestorePv = {}
        noRestorePvStr = ''
        cname = self.e2cDict[str(eid)][2]
        try:
            noRestorePvStr = masarConfigDict["NoRestore"][str(cname).lower()]
        except:
            pass

        # get table rows
        rowCount = curWidget.rowCount()
        for row in range(rowCount):
            if str(curWidget.item(row, 0).text()) in noRestorePvStr:
                curWidget.item(row, 2).setCheckState(Qt.Checked)

            selectedNoRestorePv[str(curWidget.item(row, 0).text())] = (
                                                (curWidget.item(row, 2).checkState() == Qt.Checked))
        pvlist = list(self.pv4cDict[str(eid)])
        data = self.data4eid[str(eid)]
        s_val = data['S_value']
        d_val = data['D_value']
        i_val = data['I_value']
        dbrtype = data['DBR']
        is_array = data['isArray']
        array_value = data['arrayValue']

        r_pvlist = [] # restore all pv value in this list
        r_data = []   # value to be restored.
        r_dbrtype = []
        r_isArray = []
        no_restorepvs = []  # either 'Not Restore' is checked or the PV is disconnected
        ignoreall = False # Ignore all pv those do not have any value.
        for index in range(len(pvlist)):
            try:
                # pv is unchecked, which means restore this pv
                if not selectedNoRestorePv[pvlist[index]]:
                    r_pvlist.append(pvlist[index])
                    r_dbrtype.append(dbrtype[index])
                    r_isArray.append(is_array[index])
                    if is_array[index]:
                        r_data.append(array_value[index])
                    elif dbrtype[index] in self.epicsDouble:
                        r_data.append(d_val[index])
                    elif dbrtype[index] in self.epicsLong:
                        r_data.append(i_val[index])
                    elif dbrtype[index] in self.epicsString:
                        r_data.append(s_val[index])
                    elif dbrtype[index] in self.epicsNoAccess:
                        if not ignoreall:
                            reply = QMessageBox.warning(self, 'Warning',
'Cannot restore pv: %s\nValue is invalid.\nDo you want to ignore it and continue?'%(pvlist[index]),
                QMessageBox.Yes | QMessageBox.YesToAll | QMessageBox.Cancel, QMessageBox.Cancel)
                            if reply == QMessageBox.Yes:
                                no_restorepvs.append(pvlist[index])
                            elif reply == QMessageBox.YesToAll:
                                no_restorepvs.append(pvlist[index])
                                ignoreall = True
                            elif reply == QMessageBox.Cancel:
                                self.restoreMachineButton.setEnabled(True)
                                self.rampingMachineButton.setEnabled(True)
                                return
                        else:
                            no_restorepvs.append(pvlist[index])
                else:
                    no_restorepvs.append(pvlist[index])
            except:
                print (type(pvlist[index]), pvlist[index])
                QMessageBox.warning(self, 'Warning', 'PV name (%s) is invalid.'%(pvlist[index]))
                self.restoreMachineButton.setEnabled(True)
                self.rampingMachineButton.setEnabled(True)
                return

        if len(no_restorepvs) == rowCount:
            QMessageBox.warning(self, 'Warning', 'All pvs are checked, and not restoring.')
            self.restoreMachineButton.setEnabled(True)
            self.rampingMachineButton.setEnabled(True)
            return

        liveData = self.getLiveMachineData(r_pvlist)
        if not liveData:
            self.restoreMachineButton.setEnabled(True)
            self.rampingMachineButton.setEnabled(True)
            return

        disConnectedPVs = liveData[8]#disconnected PV belongs to no_restorepvs
        for i in range(len(disConnectedPVs)):
            if disConnectedPVs[i] not in no_restorepvs:
                no_restorepvs.append(disConnectedPVs[i])

        str_no_restore = "\n"
        if len(no_restorepvs) > 0:
            for no_restorepv in no_restorepvs:
                str_no_restore += ' - %s' %no_restorepv + '\n'
            print("No restore for the following pvs:\n"+str_no_restore+"\nlist end (no-restore)")

        if ignoreall:
            print("No restore for the following pvs:\n"+str_no_restore+"\nlist end (no-restore)")
        elif len(disConnectedPVs) > 0:#pop up this warning only when there is a disconnected PV
            msg = QMessageBox(self, windowTitle='Warning',
                text="%d PVs will not be restored. Click Show Details... to see the "
                     "disconnected / no-restore Pvs.\nIt may take a while to restore "
                     "the machine. Do you want to continue?"
                     %len(no_restorepvs))
            msg.setModal(False)
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            msg.setDetailedText(str_no_restore)
            reply = msg.exec_()
            if reply == QMessageBox.No:
                self.restoreMachineButton.setEnabled(True)
                self.rampingMachineButton.setEnabled(True)
                return

        return (eid, eid4Log, r_pvlist, r_data, r_dbrtype, r_isArray, no_restorepvs, rowCount)


    def simplePut(self, eid, eid4Log, r_pvlist, r_data, no_restorepvs, rowCount):
        bad_pvs = [] # bad pv does not mean disconnected; disconnected pv belongs to no_restorepvs
        logText = '' # bad_pvs and no_restorepvs (Not Restore + disconnected) will be logged
        try:
            final_restorepv = []
            final_restorepvval = []
            for i in range(len(r_pvlist)):
                if r_pvlist[i] not in no_restorepvs:
                    final_restorepv.append(r_pvlist[i])
                    final_restorepvval.append(r_data[i])
            if cav3.caget("arcapp-acc:MASAR-Cmd") == 0:
                return
            if len(final_restorepv) > 0:
                results = cav3.caput(final_restorepv, final_restorepvval, wait=True, throw=False)
                for i in range(len(results)):
                    res = results[i]
                    if not res.ok:
                        # try 3 times again to set value to each pv
                        for j in range(1, 2):
                            ressub = cav3.caput(final_restorepv[i], final_restorepvval[i],
                                                wait=True, throw=False, timeout=j)
                            if ressub.ok:
                                break
                        if not ressub.ok:
                            # record as a bad pv if it still fails
                            bad_pvs.append(res)
        except:
            QMessageBox.warning(self, 'Warning', 'Error during restoring machine.')
            self.restoreMachineButton.setEnabled(True)
            self.rampingMachineButton.setEnabled(True)
            return

        if len(bad_pvs) > 0:#show no_restorepvs in the pop-up message only when there are bad pvs
            output = ""
            for bad_pv in bad_pvs:
                output += "\n  "+bad_pv.name + ": "+cav3.cadef.ca_message(bad_pv.errorcode)
            for no_restorepv in no_restorepvs:
                output += "\n  "+no_restorepv + ": Disconnected or Not Restore"

            logText = ("Snapshot #%s of Config %s was restored, but failed to restore the "
                       "following pvs which is caused by:\n"
                       %(eid4Log,self.e2cDict[eid][2])+output+"\n")

            totalNotRestoredPVs = len(bad_pvs)+len(no_restorepvs)
            msg = QMessageBox(self, windowTitle='Warning',
                              text="Not Very Successful: %d PVs are not restored."
                              "Click Show Details... to see the failure details\n"
                              "\\You may take a moment to review the restored PV values "
                              "by clicking the button Compare Live Machine"
                               %totalNotRestoredPVs)
            msg.setDetailedText(output)
            msg.setModal(False)
            continueButton = msg.addButton("Ok", QMessageBox.ActionRole)
            quitButton = msg.addButton(QMessageBox.Ignore)
            msg.setAttribute(Qt.WA_DeleteOnClose)
            msg.show()
            continueButton.clicked.connect(self.ignore4RestoreMachine)
            quitButton.clicked.connect(self.ignore4RestoreMachine)
        else:#DO NOT show no_restorepvs in the pop-up message; put no_restorepvs in logbook
            self.restoreMachineButton.setEnabled(True)
            self.rampingMachineButton.setEnabled(True)
            QMessageBox.information(self, "Congratulation",
                            "Bingo! Restoring machine is done. You may take a moment to "
                            "review the restored PV values by clicking the button "
                            "Compare Live Machine")
            if len(no_restorepvs) > 0:
                str_no_restore = "\n"
                for no_restorepv in no_restorepvs:
                    str_no_restore += '    %s' %no_restorepv + '\n'
                logText = ("successfully restore machine with the snapshot #%s of Conifg %s.\n"
                           "PS: these PVs are not restored because they are 'Not Restore' "
                           "or temporarily disconnected:%s"
                           %(eid4Log, self.e2cDict[eid][2], str_no_restore))
            else:
                logText = ("successfully restore machine with the snapshot #%s of Conifg %s"
                           %(eid4Log, self.e2cDict[eid][2]))

        self.createLogEntry(logText)

        dirPath = os.path.dirname(os.path.abspath(__file__))
        #keep a local log file logging restore actions
        try:
            logFile = dirPath + '/masar.log'
            if not os.path.isfile(logFile):
                return
            userID =  self.userID
            fd = open(logFile,'a')
            fd.write(str(userID)+' from '+str(platform.node())+' did a restore at %s:\n'
                     %datetime.datetime.now())
            fd.write(logText+"\n\n")
            fd.close()
        except:
            pass

        #compare readback & setpoint after restoring machine
        configFile = dirPath + '/configure/' + self.e2cDict[eid][2] + '.cfg'
        if not os.path.isfile(configFile):
            return
        #print("config File exists, masar will monitor setpoint v.s. readback")
        if configFile not in self.verifyWindowDict:
            verifyWin = VerifySetpoint(configFile, rowCount, self.verifyWindowDict, self)
            verifyWin.show()
            self.verifyWindowDict[configFile] = verifyWin


    def restoreSnapshotAction(self):
        """
         QtCore.QObject.connect(self.restoreMachineButton,
                 QtCore.SIGNAL(_fromUtf8("clicked(void)")), masar.restoreSnapshotAction)
        """
        self.restoreMachineButton.setEnabled(False)
        QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

        restoreInfo = self.getRestoreInfo()
        if None == restoreInfo:
            return
        (eid, eid4Log, r_pvlist, r_data, r_dbrtype, r_isArray,
            no_restorepvs, rowCount) = restoreInfo

        self.simplePut(eid, eid4Log, r_pvlist, r_data, no_restorepvs, rowCount)


    def rampingMachine(self):
        """
        See ui_masar.py (.ui):
        QtCore.QObject.connect(self.rampingMachineButton,
                QtCore.SIGNAL(_fromUtf8("clicked()")), masar.rampingMachine)
        """
        self.rampingMachineButton.setEnabled(False)
        QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
        restoreInfo = self.getRestoreInfo()
        if None == restoreInfo:
            return
        (eid, eid4Log, r_pvlist, r_data, r_dbrtype, r_isArray,
            no_restorepvs, rowCount) = restoreInfo
        gradualPutDlg = GradualPut(r_pvlist, r_data, r_dbrtype, r_isArray, no_restorepvs, self)
        reply = gradualPutDlg.exec_()
        if reply == 1:#1 means clicked QDialogButtonBox.Yes
            rampingPutResult = gradualPutDlg.rampingPut()
            if None == rampingPutResult:
                self.rampingMachineButton.setEnabled(True)
                return

            self.simplePut(eid, eid4Log, r_pvlist, r_data, no_restorepvs, rowCount)
        else:
            self.rampingMachineButton.setEnabled(True)

#************************** End of machine restore *********************************************


    def getLiveMachineAction(self):
        """
        See ui_masar.py (.ui):
            QtCore.QObject.connect(self.getLiveMachineButton, ... , masar.getLiveMachineAction).
        getLiveMachineData() returns live timestamp, live alarm via cav3.caget.
        Comparing live machine with multiple snapshots is special, see setCompareSnapshotsTable()
        """
        curWidget = self.snapshotTabWidget.currentWidget()
        if isinstance(curWidget, QTableWidget):
            # get event id
            eid = self.__find_key(self.tabWindowDict, curWidget)
            # 2 special case:
            if eid == 'preview':
                eid = self.previewId # get event id for preview snapshot
            elif eid == 'comment':
                self.getLiveMachineButton.setEnabled(True)
                return # nothing should do here
            elif eid == 'compare':
                self.getLiveMachineButton.setEnabled(False)
                QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
                data_ = self.data4eid['compare']
                pvlist_ = self.pv4cDict['compare']
                eventIds_ = self.eventIds
                self.compareLiveWithMultiSnapshots = True
                self.setCompareSnapshotsTable(data_, curWidget, pvlist_, eventIds_)
                #since compareSnapshotsTable is so different from singleSnapshotTable,
                ## don't continue and just return
                self.getLiveMachineButton.setEnabled(True)
                return

            self.getLiveMachineButton.setEnabled(False)
            QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
            #catch KeyError: 'None'
            pvlist = self.pv4cDict[str(eid)]

            data = self.getLiveMachineData(pvlist)
            if data:
                channelName = data[0]
                s_value = data[1]
                d_value = data[2]
                i_value = data[3]
                dbrtype = data[4]
                is_array = data[6]
                array_value = data[7]
                disConnectedPVs = data[8]
                alarm_status = data[9]
                alarm_severity = data[10]
                ts = data[11]
                ts_nano = data[12]
                dd = {}
                noMatchedPv = []

                # put channel name and its order into a dictionary
                for i in range(len(channelName)):
                    dd[str(channelName[i])] = i

                # get table rows
                rowCount = curWidget.rowCount()
                colCount = curWidget.columnCount()
                for i in range(rowCount):
                    try:
                        index = dd[str(curWidget.item(i, 0).text())]
                        if dbrtype[index] in self.epicsNoAccess:
                            self.__setTableItem(curWidget, i, 9, "Disconnected")
                        else:
                            self.__setTableItem(curWidget, i, 9, "Connected")

                        dt=str(datetime.datetime.fromtimestamp(ts[index]+ts_nano[index]*1.0e-9))
                        self.__setTableItem(curWidget, i, 10, dt)
                        self.__setTableItem(curWidget, i, 11, str(alarm_status[index]))
                        self.__setTableItem(curWidget, i, 12, str(alarm_severity[index]))

                        if is_array[index]:
                            self.__setTableItem(curWidget, i, 4,
                                                self.__arrayTextFormat(array_value[index]))
                            self.arrayData[channelName[index]+"_"+str(eid)+'_live'] = (
                                                array_value[index])
                            try:
                                saved_array = self.arrayData[channelName[index]+"_"+str(eid)]
                                if str(saved_array) != str(array_value[index]):
                                    delta_ =[m - n for m, n in zip(array_value[index],saved_array)]
                                    delta_array = tuple(delta_)
                                    self.__setTableItem(curWidget, i, 5,
                                                        self.__arrayTextFormat(delta_array))
                                else:
                                    self.__setTableItem(curWidget, i, 5, "")
                            except:
                                self.__setTableItem(curWidget, i, 5, "N/A")
                        else:
                            if dbrtype[index] in self.epicsDouble:
                                self.__setTableItem(curWidget, i, 4, str(d_value[index]))

                                try:
                                    saved_val = float(str(curWidget.item(i, 3).text()))
                                    if str(d_value[index]) != str(saved_val):
                                        delta = d_value[index] - saved_val
                                        self.__setTableItem(curWidget, i, 5, str(delta))
                                    else:
                                        self.__setTableItem(curWidget, i, 5, "")
                                except:
                                    self.__setTableItem(curWidget, i, 5, "N/A")
                            elif dbrtype[index] in self.epicsLong:
                                self.__setTableItem(curWidget, i, 4, str(i_value[index]))

                                if dbrtype[index] in self.epicsNoAccess:
                                    pass
                                else:
                                    try:
                                        saved_val = int(float(str(curWidget.item(i, 3).text())))
                                        if str(i_value[index]) != str(saved_val):
                                            delta = i_value[index] - saved_val
                                            self.__setTableItem(curWidget, i, 5, str(delta))
                                        else:
                                            self.__setTableItem(curWidget, i, 5, "")
                                    except:
                                        self.__setTableItem(curWidget, i, 5, "N/A")
                            elif dbrtype[index] in self.epicsString:
                                self.__setTableItem(curWidget, i, 4, str(s_value[index]))
                                try:
                                    saved_val = str(curWidget.item(i, 3).text())
                                    if s_value[index] != saved_val:
                                        self.__setTableItem(curWidget, i, 5, "NotEqual")
                                    else:
                                        self.__setTableItem(curWidget, i, 5, "")
                                except:
                                    self.__setTableItem(curWidget, i, 5, "N/A")
                            else:#if dbrtype[index] in self.epicsDouble:
                                self.__setTableItem(curWidget, i, 5, "N/A")
                    except:
                        self.__setTableItem(curWidget, i, 5, "N/A")
                        noMatchedPv.append(str(curWidget.item(i, 0).text()))
                #end of for i in range(rowCount):
                if len(noMatchedPv) > 0:
                    print ("Can not find the following pvs for this snapshot: \n", noMatchedPv)
                    QMessageBox.warning(self,"Warning",
                            "Can not find the following pvs for this snapshot: %s"%noMatchedPv)

                #Mark all disconnected PVs with pink color
                for i in range(rowCount):
                    try:
                        if str(curWidget.item(i, 9).text()) == "Disconnected":
                            self.__setTableItem(curWidget, i, 5, "N/A")
                            for item_idx in range(colCount):
                                itemtmp = curWidget.item(i, item_idx)
                                if not itemtmp:
                                    itemtmp = QTableWidgetItem()
                                    curWidget.setItem(i, item_idx, itemtmp)
                                itemtmp.setBackground(self.brushdisconnectedpv)
                    except:
                        pass

                curWidget.sortItems(5, Qt.DescendingOrder)
                curWidget.resizeColumnsToContents()
                curWidget.sortItems(9, Qt.DescendingOrder)
                detailedText = ""
                for i in range(len(disConnectedPVs)):
                    detailedText += '\n' + disConnectedPVs[i]
                if len(disConnectedPVs) > 0:
                    msg = QMessageBox(self,windowTitle="Be Aware!",
                        text="There are %s PVs disconnected. Click Show Details ... "
                        "below for more info\n"
                        "Or scroll down the SnapshotTab table if you like" %len(disConnectedPVs))
                    msg.setModal(False)
                    msg.setDetailedText(detailedText)
                    msg.exec_()

        else:# end of if isinstance(curWidget, QTableWidget):
            QMessageBox.warning(self, "Warning",
                                "No snapshot is displayed. Please refer Welcome to MASAR for help")
            self.getLiveMachineButton.setEnabled(True)
            return

        self.getLiveMachineButton.setEnabled(True)
#************************** End of getLiveMachineAction(self) *************************************


    def getLiveMachineData(self, pvlist):
        """
        Oct-24-2013: self.mc.getLiveMachine(params) does return live timestamp, live alarm, etc.

        #self.mc.getLiveMachine(params) doesn't return live timestamp, live alarm,
        #get these data via cav3.caget
        #Called by getLiveMachineAction(), setCompareSnapshotsTable(), resoreSnapshotAction()
        """
        params = {}
        for pv in pvlist:
            params[pv] = pv
        # channelName,stringValue,doubleValue,longValue,dbrType,isConnected, is_array, array_value
        array_value = []
        disConnectedPVs = []
        try:
            rpcResult = self.mc.getLiveMachine(params)
        except:
            QMessageBox.warning(self,
                                "Warning",
                                "Except happened during getting live machine.")
            return False
        if not rpcResult:
            QMessageBox.warning(self,
                                "Warning",
            "Exception occurred when retieving live data, please check network or IOC status")
            return False
        channelName = rpcResult[0]
        stringValue = rpcResult[1]
        doubleValue = rpcResult[2]
        longValue = rpcResult[3]
        dbrtype = rpcResult[4]
        isConnected = rpcResult[5]
        ts = rpcResult[6]
        ts_nano = rpcResult[7]
        severity = list(rpcResult[8])
        status = list(rpcResult[9])
        is_array = rpcResult[10]
        raw_array_value  = rpcResult[11]

        for i in range(len(is_array)):
            try:
                severity[i] = self.severityDict[severity[i]]
            except:
                severity[i] = 'N/A'
            try:
                status[i] = self.alarmDict[status[i]]
            except:
                status[i] = 'N/A'
            if dbrtype[i] in self.epicsLong:
                array_value.append(raw_array_value[i][2])
            elif dbrtype[i] in self.epicsDouble:
                array_value.append(raw_array_value[i][1])
            elif dbrtype[i] in self.epicsString:
                # string value
                array_value.append(raw_array_value[i][0])
            elif dbrtype[i] in self.epicsNoAccess:
                # when the value is no_access, use the double value no matter what it is
                array_value.append(raw_array_value[i][1])

        # if dbrtype is NoAccess, it means that the PV is disconnected at the moment
        for i in range(len(dbrtype)):
            if dbrtype[i] in self.epicsNoAccess:
                disConnectedPVs.append(channelName[i])

        return (channelName,stringValue,doubleValue,longValue,dbrtype,isConnected,is_array,
                array_value,disConnectedPVs,status, severity, ts, ts_nano)


    def saveDataFileAction(self):
        """
        See ui_masar.py(.ui):
        QtCore.QObject.connect(self.saveDataFileButton,
                        QtCore.SIGNAL(_fromUtf8("clicked()")), masar.saveDataFileAction)
        Save data into a file.
        """
        curWidget = self.snapshotTabWidget.currentWidget()
        if not isinstance(curWidget, QTableWidget):
            QMessageBox.warning(self, 'Warning',
                                'No snapshot is selected. Please refer Welcome to MASAR for help')
            return

        eid = self.__find_key(self.tabWindowDict, curWidget)
        data = self.data4eid[str(eid)]

        pvnames = data['PV Name']
        status = data['Status']
        severity = data['Severity']
        ts = data['Time stamp']
        ts_nano = data['Time stamp (nano)']
        dbrtype = data['DBR']
        s_value = data['S_value']
        i_value = data['I_value']
        d_value = data['D_value']
        isConnected = data['isConnected']
        is_array = data['isArray']
        array_value = data['arrayValue']

        head = ('# pv name, elem location, elem type, status, severity, time stamp, '
                'epics dbr, is connected, is array, value')

        filename, _ = QFileDialog.getSaveFileName(self, 'Save File as .csv', '.')
        if not filename:
            return
        try:
            fname = open(filename, 'w')
            fname.write(head+'\n')
            for i in range(len(pvnames)):
                line = pvnames[i]
                # a quick, urgly solution for NSLS II naming conversion only
                # to be replaced by information from other service like channel finder
                if pvnames[i].startswith("SR:C"):
                    line += ','+pvnames[i][3:6]
                else:
                    line += ','

                if 'MG' in pvnames[i]:
                    loc1 = pvnames[i].find("{PS:")
                    loc2 =  pvnames[i][loc1:].find("}")
                    if loc1 != -1 and loc2 != 0 and loc1+4<loc1+loc2:
                        line += ','+pvnames[i][loc1+4:loc1+loc2]
                    else:
                        line += ','
                else:
                    line += ','

                # need to make above pretty and general
                line += ','+str(status[i])
                line += ','+str(severity[i])
                line += ','+str(datetime.datetime.fromtimestamp(ts[i]+ts_nano[i]*1.0e-9))
                line += ','+str(dbrtype[i])
                line += ','+str(bool(isConnected[i]))
                line += ','+str(bool(is_array[i]))
                if is_array[i]:
                    line += ','+str(array_value[i])
                else:
                    if dbrtype[i] in self.epicsDouble:
                        line += ','+str(d_value[i])
                    elif dbrtype[i] in self.epicsLong:
                        line += ','+str(i_value[i])
                    elif dbrtype[i] in self.epicsString:
                        line += ','+str(s_value[i])
                    else:
                        line += ''

                fname.write(line+'\n')
            fname.close()
        except:
            QMessageBox.warning(self,
                                "Warning",
                                "Cannot write to the file. Please check the writing permission.")


#************************** Start of comparing multiple snapshots *********************************
    def ignoreCompare(self):
        self.compareSnapshotsButton.setEnabled(True)

    def openMsgBox(self):
        """
        Dialog for comparing multiple snapshots
        See ui_masar.py(.ui):
        QtCore.QObject.connect(self.compareSnapshotsButton,
                    QtCore.SIGNAL(_fromUtf8("clicked()")), masar.openMsgBox)
        """
        self.compareSnapshotsButton.setEnabled(False)
        QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

        selectedEvents = self.eventTableWidget.selectionModel().selectedRows()
        ln = len(selectedEvents)
        if ln == 0:
            msg = QMessageBox(self, windowTitle="Snapshot Selection",
                          text="Don't click OK until you have done the following:\n\n"
                          "Select 2 ~ 9 snapshots (Ctrl key + mouse Click) from the "
                          "left-bottom Snapshot Table\n\n"
                          "If the Snapshot Table is empty, please double click on one row "
                          "in the Config Table \n\n"
                          "Click Ignore if you don't want to continue")
            okButton = msg.addButton("OK", QMessageBox.ActionRole)
            quitButton = msg.addButton(QMessageBox.Ignore)
            msg.setAttribute(Qt.WA_DeleteOnClose)
            msg.setModal(False)
            msg.show()
            okButton.clicked.connect(self.compareSnapshots)
            quitButton.clicked.connect(self.ignoreCompare)

        elif ln >=2 and ln <= 9:
            self.compareSnapshots()

        elif ln >0 and ln <2 or ln > 9:
            QMessageBox.warning(self,"Waring",
                                "Please select 2 ~ 9 snapshots for comparison,not %d snapshots"%ln)
            self.compareSnapshotsButton.setEnabled(True)
            return


    def compareSnapshots(self):
        selectedEvents = self.eventTableWidget.selectionModel().selectedRows()
        ln = len(selectedEvents)
        if ln == 0:
            self.compareSnapshotsButton.setEnabled(True)
            return
        elif ln < 2 or ln > 9:
            QMessageBox.warning(self,"Waring",
                                "Please select 2 ~ 9 snapshots for comparison,not %d snapshots"%ln)
            self.compareSnapshotsButton.setEnabled(True)
            return

        eventNames=[]
        eventIds = []
        data = []
        self.compareId = None
        self.compareConfName =  None
        for idx in selectedEvents:
            eventNames.append(str(self.eventTableWidget.item(idx.row(), 0).text()))
            eventIds.append(str(self.eventTableWidget.item(idx.row(), 1).text()))

        msg = QMessageBox(self, windowTitle="Select one reference snapshot",
                          text="Snapshots comparison is made between the reference snapshot "
                          "and other snapshots:\n\n"
                          "Snapshot %s is the reference since you clicked it first, "
                          "click OK to keep it as it\n\n"
                          "Otherwise click Change the ref. snapshot ..."%eventIds[0])
        msg.addButton("Change the ref. snapshot ...",QMessageBox.AcceptRole)
        msg.addButton("OK", QMessageBox.RejectRole)
        ret = msg.exec_()
        if ret == 0:
            reorderedIDs = self.selectRefSnapshot(eventIds)
            if reorderedIDs:
                eventIds = reorderedIDs

        self.eventIds = eventIds
        for i in range(len(eventIds)):
            result = self.retrieveMasarData(eventid = eventIds[i])
            if result == None or not isinstance(result, odict) :
                QMessageBox.warning(self,"Warning",
                                    "Failed to retrieve data for snapshot %s"%eventIds[i])
                self.compareSnapshotsButton.setEnabled(True)
                return
            else:
                data.append(result)
        #save data to dictionary for future retrieval (i.e. getLiveMachineAction())
        self.data4eid['compare'] = data

        if 'compare' in self.tabWindowDict:
            tableWidget = self.tabWindowDict['compare']
        else:
            tableWidget = QTableWidget()
            self.tabWindowDict['compare'] = tableWidget
            tableWidget.cellDoubleClicked.connect(self.__showArrayData)

        labelText = ""
        for eventId in eventIds:
            labelText += '_' + eventId
        label = "Compare Snapshots: IDs" + labelText
        self.snapshotTabWidget.addTab(tableWidget, label)
        self.snapshotTabWidget.setTabText(self.snapshotTabWidget.count(), label)
        self.snapshotTabWidget.setCurrentIndex(self.snapshotTabWidget.count())
        self.snapshotTabWidget.setCurrentWidget(tableWidget)
        self.resizeSplitter(1)
        keys = ['PV name']
        pvList = []
        nEvents = len(data)
        for i in range(nEvents):
            keys.append("Saved Value "+str(i+1)+"\n"+"(" + "in snapshot "+str(eventIds[i])+")")

        keys.append('Live Value 0')
        nDelta = nEvents - 1
        for i in range(nDelta):
            keys.append("Delta%s1"%str(i+2))
        keys.append('Delta01')
        for i in range(nEvents):
            keys.append("Timestamp "+str(i+1)+"\n"+"(" + "in snapshot "+str(eventIds[i])+")")
        self.compareSnapshotsTableKeys  = keys

        pvList = list(data[0]['PV Name'])
        self.pv4cDict['compare'] = pvList
        nRows = len(pvList)
        nCols = len(keys)
        tableWidget.setRowCount(nRows)
        tableWidget.setColumnCount(nCols)
        self.setCompareSnapshotsTable(data, tableWidget, pvList, eventIds)
        tableWidget.resizeColumnsToContents()
        tableWidget.setStatusTip("compare %d snapshots with snapshotIds:%s"%(nEvents,eventIds))
        tableWidget.setToolTip("delta21: value in 2nd snapshot - value in 1st snapshot\n"
                               "delta01: live value - value in 1st snapshot")
        self.compareSnapshotsButton.setEnabled(True)


    def selectRefSnapshot(self, eventIDs):
        dlg = ShowSelectRefDlg(eventIDs)
        dlg.exec_()
        if dlg.isAccepted:
            return(dlg.result())


    def setCompareSnapshotsTable(self, data, table, pvlist, eventIds):
        assert(data!=None and isinstance(table,QTableWidget) and pvlist!=None and len(eventIds)>=2)
        pvList = pvlist
        nRows = len(pvList)
        nEvents = len(data)
        #must have the following two lines, otherwise the sorting will make data messed up
        table.setSortingEnabled(False)
        table.clear()
        keys = self.compareSnapshotsTableKeys
        table.setHorizontalHeaderLabels(keys)

        for i in range(nRows):
            self.__setTableItem(table, i, 0, pvList[i])
            for j in range(nEvents):
                if pvList[i] in data[j]['PV Name']:
                    pvIndex = data[j]['PV Name'].index(pvList[i])
                    if data[j]['Time stamp'][pvIndex]:
                        dt = str(datetime.datetime.fromtimestamp(data[j]['Time stamp'][pvIndex] +
                                                    data[j]['Time stamp (nano)'][pvIndex]*1.0e-9))
                        self.__setTableItem(table, i, 2*(nEvents+1)+j, dt)
                    if data[j]['isArray'][pvIndex]:
                        self.__setTableItem(table, i, j+1,
                                        self.__arrayTextFormat(data[j]['arrayValue'][pvIndex]))
                        self.arrayData[pvList[i]+'_'+str(eventIds[j])+'_compare'] = (
                            data[j]['arrayValue'][pvIndex])
                        try:
                            ref_wf = data[0]['arrayValue'][pvIndex]
                            if j >0 and str(data[j]['arrayValue'][pvIndex])!=str(ref_wf):
                                delta = [m-n for m,n in zip(data[j]['arrayValue'][pvIndex],ref_wf)]
                                delta_array = tuple(delta)
                                self.__setTableItem(table, i,nEvents+1+j,
                                                    self.__arrayTextFormat(delta_array))
                        except:
                            self.__setTableItem(table, i,nEvents+1+j,"N/A")

                    elif data[j]['DBR'][pvIndex] in self.epicsDouble:
                        self.__setTableItem(table, i, j+1, str(data[j]['D_value'][pvIndex]))
                        try:
                            if (j > 0 and str(table.item(i, 1).text())
                                    != str(data[j]['D_value'][pvIndex])):
                                delta=data[j]['D_value'][pvIndex]-float(str(table.item(i,1).text()))
                                self.__setTableItem(table, i,nEvents+1+j,str(delta))
                        except:
                            self.__setTableItem(table, i,nEvents+1+j,"N/A")

                    elif data[j]['DBR'][pvIndex] in self.epicsLong:
                        self.__setTableItem(table, i, j+1, str(data[j]['I_value'][pvIndex]))
                        try:
                            if (j > 0 and str(table.item(i, 1).text())
                                    != str(data[j]['I_value'][pvIndex])):
                                delta=data[j]['I_value'][pvIndex] - int(str(table.item(i,1).text()))
                                self.__setTableItem(table, i,nEvents+1+j,str(delta))
                        except:
                            self.__setTableItem(table, i,nEvents+1+j,"N/A")

                    elif data[j]['DBR'][pvIndex] in self.epicsString:
                        self.__setTableItem(table, i, j+1, str(data[j]['S_value'][pvIndex]))
                        try:
                            if (j > 0 and str(table.item(i, 1).text())
                                    != str(data[j]['S_value'][pvIndex])):
                                self.__setTableItem(table, i,nEvents+1+j,str("NotEqual"))
                        except:
                            self.__setTableItem(table, i,nEvents+1+j,"N/A")
                    elif j > 0:
                        self.__setTableItem(table, i,nEvents+1+j,"N/A")
                    else:
                        self.__setTableItem(table, i,nEvents+2+j,"N/A")

                else:#if pvList[i] in data[j]['PV Name']:
                    self.__setTableItem(table, i,nEvents+1+j,"N/A")

        if self.compareLiveWithMultiSnapshots:
            self.compareLiveWithMultiSnapshots = False
            liveData = self.getLiveMachineData(pvList)
            if liveData:
                channelName = liveData[0]
                s_value = liveData[1]
                d_value = liveData[2]
                i_value = liveData[3]
                dbrtype = liveData[4]
                is_array = liveData[6]
                array_value = liveData[7]
                for i in range(nRows):
                    if pvList[i] in channelName:
                        liveIndex = channelName.index(pvList[i])
                        if is_array[liveIndex]:
                            self.__setTableItem(table, i, nEvents+1,
                                                self.__arrayTextFormat(array_value[liveIndex]))
                            self.arrayData[pvList[i]+'_compare'+'_live']=array_value[liveIndex]
                            try:
                                pvIndex = data[0]['PV Name'].index(pvList[i])
                                ref_wf = data[0]['arrayValue'][pvIndex]
                                if str(ref_wf) != str(array_value[liveIndex]):
                                    delta=[m-n for m,n in zip(ref_wf,array_value[liveIndex])]
                                    delta_array = tuple(delta)
                                    self.__setTableItem(table,i,2*nEvents+1,
                                                        self.__arrayTextFormat(delta_array))
                            except:
                                self.__setTableItem(table, i,2*nEvents+1,str("N/A"))

                        elif dbrtype[liveIndex] in self.epicsDouble:
                            self.__setTableItem(table, i, nEvents+1, str(d_value[liveIndex]))
                            try:
                                if str(table.item(i,1).text()) != str(d_value[liveIndex]):
                                    delta = d_value[liveIndex] - float(str(table.item(i,1).text()))
                                    self.__setTableItem(table, i,2*nEvents+1,str(delta))
                            except:
                                self.__setTableItem(table, i,2*nEvents+1,str("N/A"))

                        elif dbrtype[liveIndex] in self.epicsLong:
                            self.__setTableItem(table, i, nEvents+1, str(i_value[liveIndex]))
                            try:
                                if str(table.item(i,1).text()) != str(i_value[liveIndex]):
                                    delta = i_value[liveIndex] - int(str(table.item(i,1).text()))
                                    self.__setTableItem(table, i,2*nEvents+1,str(delta))
                            except:
                                self.__setTableItem(table, i,2*nEvents+1,str("N/A"))

                        elif dbrtype[liveIndex] in self.epicsString:
                            self.__setTableItem(table, i, nEvents+1, str(s_value[liveIndex]))
                            try:
                                if str(table.item(i,1).text()) != str(s_value[liveIndex]):
                                    self.__setTableItem(table, i,2*nEvents+1,str("NotEqual"))
                            except:
                                self.__setTableItem(table, i,2*nEvents+1,str("N/A"))
                        elif dbrtype[liveIndex] in self.epicsNoAccess:
                            self.__setTableItem(table, i,2*nEvents+1,str("N/A"))
                        else:
                            self.__setTableItem(table, i,2*nEvents+1,str("N/A"))

                    else:#if pvList[i] in channelName:
                        self.__setTableItem(table, i,2*nEvents+1,str("N/A"))
            table.setSortingEnabled(True)
            table.sortItems(2*nEvents+1, Qt.AscendingOrder)
        else:#if self.compareLiveWithMultiSnapshots:
            table.setSortingEnabled(True)
            table.sortItems(nEvents+2, Qt.AscendingOrder)
#************************** End of comparing multiple snapshots ***********************************

    def pvFilterChanged(self):
        self.currentPvFilter = str(self.pvFilterLineEdit.text())


    def getInfoFromTableWidget(self):
        curWidget = self.snapshotTabWidget.currentWidget()
        if not isinstance(curWidget, QTableWidget):
            QMessageBox.warning(self, "Warning",
                                "No snapshot is displayed. Please refer Welcome to MASAR for help")
            return None

        eid = self.__find_key(self.tabWindowDict, curWidget)
        if eid == 'comment':
            return
        if eid == 'preview':
            eid = self.previewId
        if eid == 'compare':
            QMessageBox.warning(self, "Warning",
                                "Sorry, pv searching on compareSnapshotTab is not supported yet")
            return

        data_ = self.data4eid[str(eid)]#'filter' is an eid
        pvlist_ = self.pv4cDict[str(eid)]
        eventIds_ = self.eventIds
        config_ = self.e2cDict[eid]
        return(data_, pvlist_, eid, eventIds_, config_)


    def searchPV(self):
        data = odict()
        pattern_ = self.currentPvFilter
        pattern = fnmatch.translate(pattern_)

        info = self.getInfoFromTableWidget()
        if info == None:
            return
        if str(info[2]).isdigit():
            self.origID = str(info[2])
            self.e2cDict['filter'] = info[4]
        pvList = info[1]
        regex = re.compile(pattern, re.IGNORECASE)
        filteredPVs = [pv for pv in pvList for m in [regex.search(pv)] if m]
        if 0 == len(filteredPVs):
            QMessageBox.warning(self, "Warning",
                                "No matching pv. Did you forget to use * at the beginning / "
                                "the end of your search characters?\n\n"
                                "Please refer Welcome to MASAR tab for help, "
                                "then re-enter your search pattern.")
            return

        if str(info[2]) == 'filter':
            label = "filtered snapshot(ID_" + self.origID + "_filter)"
        else:
            label = "filtered snapshot(ID_" + str(info[2]) + ")"

        tableWidget = self.createNewTableWidget("filter", label)

        status, severity, ts, ts_nano, dbr = [], [], [], [], []
        sval, ival, dval, isCon, isArr, arr = [], [], [], [], [], []
        for i in range(len(filteredPVs)):
            index = info[0]['PV Name'].index(filteredPVs[i])
            status.append(info[0]['Status'][index])
            severity.append(info[0]['Severity'][index])
            ts.append(info[0]['Time stamp'][index])
            ts_nano.append(info[0]['Time stamp (nano)'][index])
            dbr.append(info[0]['DBR'][index])
            sval.append(info[0]['S_value'][index])
            ival.append(info[0]['I_value'][index])
            dval.append(info[0]['D_value'][index])
            isCon.append(info[0]['isConnected'][index])
            isArr.append(info[0]['isArray'][index])
            arr.append(info[0]['arrayValue'][index])

        data['PV Name'] = filteredPVs
        data['Status'] = status
        data['Severity'] = severity
        data['Time stamp'] = ts
        data['Time stamp (nano)'] = ts_nano
        data['DBR'] = dbr
        data['S_value'] = sval
        data['I_value'] = ival
        data['D_value'] = dval
        data['isConnected'] = isCon
        data['isArray'] = isArr
        data['arrayValue'] = arr

        self.pv4cDict['filter'] = data['PV Name']#eventID: numbers, 'filter'
        self.data4eid['filter'] = data#'filter' is an eventID

        tableWidget.clear()
        self.setSnapshotTable(data, tableWidget, 'filter')


    def setGoldenSnapshot(self):
        if self.userID not in masarConfigDict["OperatorList"]["account"]:
            QMessageBox.warning(self, "Warning",
                        "You DO NOT have the privilege to set golden snapshot")
            return
        selectedItems = self.eventTableWidget.selectionModel().selectedRows()
        if len(selectedItems) != 1:
            QMessageBox.warning(self, "Warning",
                "Please select one and only one snapshot to be set as Golden")
            return
        if not self.getAuthentication():
            return
        eventID = str(self.eventTableWidget.item(selectedItems[0].row(), 1).text())
        configName = str(self.eventTableWidget.item(selectedItems[0].row(), 0).text())
        goldenDataFile = self.goldenDataFilePath + "goldenSnapshotOf" + configName + ".data"
        logText = (eventID + " # " + configName + " marked as Golden snapshot at " +
                   str(datetime.datetime.now()) + " by " + self.userID + "\n")
        try:
            umask_original = os.umask(0) #needed to solve permission issue
            fdesc = os.open(goldenDataFile,os.O_WRONLY|os.O_CREAT|os.O_APPEND, 0o666)
            os.umask(umask_original)
            fd = os.fdopen(fdesc,'a')
            fd.write(logText)
            fd.close()
            fd = open(goldenDataFile, 'r')
            lines = fd.readlines()
            fd.close()
            for line in lines[:-1]:
                if eventID in line:
                    lines.remove(line) #remove dumplicated entries
                    fd = open(goldenDataFile, 'w')
                    fd.writelines(lines)
                    fd.close()
            if len(lines) > 10: # keep 10 golden snapshots
                fd = open(goldenDataFile, 'w')
                fd.writelines(lines[-10:])
                fd.close()
        except:
            traceback.print_exc()
            QMessageBox.warning(self, "Warning",
                "Failed to tag the selected snapshot as golden")
            return
        QMessageBox.warning(self, "Congrats",
                            "SnapshotID %s has been successfully marked as Gold. "
                            "You may click 'Display Golden Snapshot' to confirm this"%eventID)
        self.createLogEntry(logText)

    def fetchGoldenSnapshotAction(self):
        try:
            self._fetchGoldenSnapshotAction()
        except:
            traceback.print_exc()

    def _fetchGoldenSnapshotAction(self):
        selectedConfigs = self.configTableWidget.selectionModel().selectedRows()
        if len(selectedConfigs) != 1:
            QMessageBox.warning(self, "Warning",
                "Please select one and only one Config to get a golden snapshot")
            return
        configName = str(self.configTableWidget.item(selectedConfigs[0].row(), 0).text())
        goldenDataFile = self.goldenDataFilePath + "goldenSnapshotOf" + configName + ".data"
        if not (os.path.isfile(goldenDataFile)):
            QMessageBox.warning(self, "Warning",
                                "No golden snapshot has been tagged yet. Please set one snapshot"
                                " as Golden first")
            return
        fd = open(goldenDataFile, 'r')
        lines = fd.readlines()
        fd.close()
        goldenID = lines[-1].split('#')[0].strip()
        self.fetchEventAction()
        self.retrieveSnapshotById(goldenID)

 #end of class masarUI


def main(channelname = None):
    app = QApplication(sys.argv)
    app.setOrganizationName("NSLS II")
    app.setOrganizationDomain("BNL")
    app.setApplicationName("MASAR Viewer")
    if channelname:
        form = masarUI(channelname=channelname)
    else:
        form = masarUI()
    hostname = platform.node()
    title = "MASAR Viewer (PySide6) on " + str(hostname) + " for MASAR Server " + str(channelname)
    form.setWindowTitle(title)
    form.show()
    app.exec()

    import atexit
    # clean Python local objects first, especially the cothread stuff.
    # Cothread adds a new function in catools._catools_atexit(), ca_flush_io(), since version 2.8
    # to flush all io and do a clean up. This function registered at Python exit, and will be called
    # by Python exit handler.
    # This forces the clean up has be done before calling epicsExit().
    atexit._run_exitfuncs()

    # it is safe to clean epics objects now.
    epicsExit()

    # call os.exit() instead of sys.exit()
    # os._exit(0)
    # however, os._exit() does nothing when exiting.
    # It would be better to call sys.exit
    sys.exit()


if __name__ == '__main__':
    args = sys.argv[1:]
    while args:
        arg = args.pop(0)
        if arg in ("-h", "--help", "help"):
            usage()
        else:
            print ('Unknown option.')

    main()
