# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_masar.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox,
    QDateTimeEdit, QFrame, QGridLayout, QHeaderView,
    QLabel, QLineEdit, QMainWindow, QMenuBar,
    QPlainTextEdit, QPushButton, QSizePolicy, QSplitter,
    QStatusBar, QTabWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget)
from . import masarRC_rc

class Ui_masar(object):
    def setupUi(self, masar):
        if not masar.objectName():
            masar.setObjectName(u"masar")
        masar.setWindowModality(Qt.WindowModal)
        masar.resize(1532, 1168)
        palette = QPalette()
        brush = QBrush(QColor(255, 255, 255, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush)
        brush1 = QBrush(QColor(237, 236, 235, 255))
        brush1.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush1)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush1)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush1)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush1)
        masar.setPalette(palette)
        masar.setFocusPolicy(Qt.ClickFocus)
        masar.setAcceptDrops(False)
        icon = QIcon()
        icon.addFile(u":/icons/nsls2-logo.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        masar.setWindowIcon(icon)
        masar.setWindowOpacity(1.000000000000000)
        masar.setAutoFillBackground(False)
        masar.setDocumentMode(True)
        masar.setTabShape(QTabWidget.Rounded)
        masar.setDockNestingEnabled(True)
        masar.setDockOptions(QMainWindow.AllowNestedDocks|QMainWindow.AllowTabbedDocks|QMainWindow.AnimatedDocks|QMainWindow.ForceTabbedDocks|QMainWindow.VerticalTabs)
        masar.setUnifiedTitleAndToolBarOnMac(True)
        self.mainwidget = QWidget(masar)
        self.mainwidget.setObjectName(u"mainwidget")
        self.verticalLayout_2 = QVBoxLayout(self.mainwidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.splitter = QSplitter(self.mainwidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.configEventSplitter = QSplitter(self.splitter)
        self.configEventSplitter.setObjectName(u"configEventSplitter")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.configEventSplitter.sizePolicy().hasHeightForWidth())
        self.configEventSplitter.setSizePolicy(sizePolicy)
        self.configEventSplitter.setMinimumSize(QSize(600, 0))
        self.configEventSplitter.setOrientation(Qt.Vertical)
        self.configLayoutWidget = QWidget(self.configEventSplitter)
        self.configLayoutWidget.setObjectName(u"configLayoutWidget")
        self.configVerticalLayout = QVBoxLayout(self.configLayoutWidget)
        self.configVerticalLayout.setObjectName(u"configVerticalLayout")
        self.configVerticalLayout.setContentsMargins(0, 0, 0, 0)
        self.configGridLayout = QGridLayout()
        self.configGridLayout.setObjectName(u"configGridLayout")
        self.systemCombox = QComboBox(self.configLayoutWidget)
        self.systemCombox.setObjectName(u"systemCombox")
        self.systemCombox.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.systemCombox.setMouseTracking(True)

        self.configGridLayout.addWidget(self.systemCombox, 0, 1, 1, 1)

        self.systemLabel = QLabel(self.configLayoutWidget)
        self.systemLabel.setObjectName(u"systemLabel")

        self.configGridLayout.addWidget(self.systemLabel, 0, 0, 1, 1)

        self.configFilterLabel = QLabel(self.configLayoutWidget)
        self.configFilterLabel.setObjectName(u"configFilterLabel")

        self.configGridLayout.addWidget(self.configFilterLabel, 1, 0, 1, 1)

        self.fetchConfigButton = QPushButton(self.configLayoutWidget)
        self.fetchConfigButton.setObjectName(u"fetchConfigButton")

        self.configGridLayout.addWidget(self.fetchConfigButton, 2, 0, 1, 1)

        self.configTableWidget = QTableWidget(self.configLayoutWidget)
        self.configTableWidget.setObjectName(u"configTableWidget")
        self.configTableWidget.setFocusPolicy(Qt.WheelFocus)
        self.configTableWidget.setFrameShape(QFrame.WinPanel)
        self.configTableWidget.setFrameShadow(QFrame.Sunken)
        self.configTableWidget.setLineWidth(1)
        self.configTableWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.configTableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.configTableWidget.setSortingEnabled(True)

        self.configGridLayout.addWidget(self.configTableWidget, 3, 0, 1, 2)

        self.configFilterLineEdit = QLineEdit(self.configLayoutWidget)
        self.configFilterLineEdit.setObjectName(u"configFilterLineEdit")
        self.configFilterLineEdit.setDragEnabled(True)

        self.configGridLayout.addWidget(self.configFilterLineEdit, 1, 1, 1, 1)


        self.configVerticalLayout.addLayout(self.configGridLayout)

        self.configEventSplitter.addWidget(self.configLayoutWidget)
        self.eventLayoutWidget = QWidget(self.configEventSplitter)
        self.eventLayoutWidget.setObjectName(u"eventLayoutWidget")
        self.eventVerticalLayout = QVBoxLayout(self.eventLayoutWidget)
        self.eventVerticalLayout.setObjectName(u"eventVerticalLayout")
        self.eventVerticalLayout.setContentsMargins(0, 0, 0, 0)
        self.eventGridLayout = QGridLayout()
        self.eventGridLayout.setObjectName(u"eventGridLayout")
        self.fetchEventButton = QPushButton(self.eventLayoutWidget)
        self.fetchEventButton.setObjectName(u"fetchEventButton")

        self.eventGridLayout.addWidget(self.fetchEventButton, 5, 0, 1, 2)

        self.ByWho = QLabel(self.eventLayoutWidget)
        self.ByWho.setObjectName(u"ByWho")

        self.eventGridLayout.addWidget(self.ByWho, 1, 0, 1, 1)

        self.eventEndDateTime = QDateTimeEdit(self.eventLayoutWidget)
        self.eventEndDateTime.setObjectName(u"eventEndDateTime")
        self.eventEndDateTime.setEnabled(False)
        self.eventEndDateTime.setAlignment(Qt.AlignCenter)
        self.eventEndDateTime.setReadOnly(False)
        self.eventEndDateTime.setDateTime(QDateTime(QDate(2000, 3, 1), QTime(0, 0, 0)))
        self.eventEndDateTime.setCalendarPopup(True)

        self.eventGridLayout.addWidget(self.eventEndDateTime, 4, 1, 1, 2)

        self.eventStartDateTime = QDateTimeEdit(self.eventLayoutWidget)
        self.eventStartDateTime.setObjectName(u"eventStartDateTime")
        self.eventStartDateTime.setEnabled(False)
        self.eventStartDateTime.setAlignment(Qt.AlignCenter)
        self.eventStartDateTime.setReadOnly(False)
        self.eventStartDateTime.setCalendarPopup(True)

        self.eventGridLayout.addWidget(self.eventStartDateTime, 3, 1, 1, 2)

        self.eventFilterLabel = QLabel(self.eventLayoutWidget)
        self.eventFilterLabel.setObjectName(u"eventFilterLabel")

        self.eventGridLayout.addWidget(self.eventFilterLabel, 0, 0, 1, 1)

        self.eventEndLabel = QLabel(self.eventLayoutWidget)
        self.eventEndLabel.setObjectName(u"eventEndLabel")

        self.eventGridLayout.addWidget(self.eventEndLabel, 4, 0, 1, 1)

        self.authorTextEdit = QLineEdit(self.eventLayoutWidget)
        self.authorTextEdit.setObjectName(u"authorTextEdit")

        self.eventGridLayout.addWidget(self.authorTextEdit, 1, 2, 1, 1)

        self.timeRangeCheckBox = QCheckBox(self.eventLayoutWidget)
        self.timeRangeCheckBox.setObjectName(u"timeRangeCheckBox")

        self.eventGridLayout.addWidget(self.timeRangeCheckBox, 2, 0, 1, 2)

        self.eventFilterLineEdit = QLineEdit(self.eventLayoutWidget)
        self.eventFilterLineEdit.setObjectName(u"eventFilterLineEdit")

        self.eventGridLayout.addWidget(self.eventFilterLineEdit, 0, 2, 1, 1)

        self.eventStartLabel = QLabel(self.eventLayoutWidget)
        self.eventStartLabel.setObjectName(u"eventStartLabel")

        self.eventGridLayout.addWidget(self.eventStartLabel, 3, 0, 1, 1)


        self.eventVerticalLayout.addLayout(self.eventGridLayout)

        self.eventTableWidget = QTableWidget(self.eventLayoutWidget)
        self.eventTableWidget.setObjectName(u"eventTableWidget")
        self.eventTableWidget.setMinimumSize(QSize(350, 0))
        self.eventTableWidget.setMouseTracking(True)
        self.eventTableWidget.setFocusPolicy(Qt.StrongFocus)
        self.eventTableWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.eventTableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.eventTableWidget.setSortingEnabled(True)

        self.eventVerticalLayout.addWidget(self.eventTableWidget)

        self.snapshotGridLayout = QGridLayout()
        self.snapshotGridLayout.setObjectName(u"snapshotGridLayout")
        self.getGoldenButton = QPushButton(self.eventLayoutWidget)
        self.getGoldenButton.setObjectName(u"getGoldenButton")

        self.snapshotGridLayout.addWidget(self.getGoldenButton, 2, 1, 1, 1)

        self.fetchSnapshotButton = QPushButton(self.eventLayoutWidget)
        self.fetchSnapshotButton.setObjectName(u"fetchSnapshotButton")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.fetchSnapshotButton.sizePolicy().hasHeightForWidth())
        self.fetchSnapshotButton.setSizePolicy(sizePolicy1)

        self.snapshotGridLayout.addWidget(self.fetchSnapshotButton, 5, 0, 1, 2)

        self.searchSnapshotButton = QPushButton(self.eventLayoutWidget)
        self.searchSnapshotButton.setObjectName(u"searchSnapshotButton")

        self.snapshotGridLayout.addWidget(self.searchSnapshotButton, 3, 1, 1, 1)

        self.snapshotIdLineEdit = QLineEdit(self.eventLayoutWidget)
        self.snapshotIdLineEdit.setObjectName(u"snapshotIdLineEdit")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.snapshotIdLineEdit.sizePolicy().hasHeightForWidth())
        self.snapshotIdLineEdit.setSizePolicy(sizePolicy2)

        self.snapshotGridLayout.addWidget(self.snapshotIdLineEdit, 3, 0, 1, 1)

        self.setGoldenButton = QPushButton(self.eventLayoutWidget)
        self.setGoldenButton.setObjectName(u"setGoldenButton")

        self.snapshotGridLayout.addWidget(self.setGoldenButton, 2, 0, 1, 1)


        self.eventVerticalLayout.addLayout(self.snapshotGridLayout)

        self.configEventSplitter.addWidget(self.eventLayoutWidget)
        self.splitter.addWidget(self.configEventSplitter)
        self.snapshotLayoutWidget = QWidget(self.splitter)
        self.snapshotLayoutWidget.setObjectName(u"snapshotLayoutWidget")
        self.verticalLayout = QVBoxLayout(self.snapshotLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.snapshotTabWidget = QTabWidget(self.snapshotLayoutWidget)
        self.snapshotTabWidget.setObjectName(u"snapshotTabWidget")
        sizePolicy.setHeightForWidth(self.snapshotTabWidget.sizePolicy().hasHeightForWidth())
        self.snapshotTabWidget.setSizePolicy(sizePolicy)
        self.snapshotTabWidget.setMinimumSize(QSize(500, 0))
        self.snapshotTabWidget.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.snapshotTabWidget.setAcceptDrops(False)
        self.snapshotTabWidget.setDocumentMode(False)
        self.snapshotTabWidget.setTabsClosable(True)
        self.snapshotTabWidget.setMovable(True)
        self.commentTab = QWidget()
        self.commentTab.setObjectName(u"commentTab")
        self.commentTabWindowLayout = QVBoxLayout(self.commentTab)
        self.commentTabWindowLayout.setObjectName(u"commentTabWindowLayout")
        self.currentCommentText = QPlainTextEdit(self.commentTab)
        self.currentCommentText.setObjectName(u"currentCommentText")
        self.currentCommentText.setMinimumSize(QSize(500, 0))
        palette1 = QPalette()
        brush2 = QBrush(QColor(231, 231, 231, 255))
        brush2.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush2)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush1)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush2)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush1)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush1)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush1)
        self.currentCommentText.setPalette(palette1)
        self.currentCommentText.setAutoFillBackground(True)
        self.currentCommentText.setReadOnly(True)
        self.currentCommentText.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)
        self.currentCommentText.setBackgroundVisible(False)

        self.commentTabWindowLayout.addWidget(self.currentCommentText)

        self.snapshotTabWidget.addTab(self.commentTab, "")

        self.verticalLayout.addWidget(self.snapshotTabWidget)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.compareSnapshotsButton = QPushButton(self.snapshotLayoutWidget)
        self.compareSnapshotsButton.setObjectName(u"compareSnapshotsButton")

        self.gridLayout.addWidget(self.compareSnapshotsButton, 0, 3, 2, 1)

        self.pvFilterLineEdit = QLineEdit(self.snapshotLayoutWidget)
        self.pvFilterLineEdit.setObjectName(u"pvFilterLineEdit")
        sizePolicy1.setHeightForWidth(self.pvFilterLineEdit.sizePolicy().hasHeightForWidth())
        self.pvFilterLineEdit.setSizePolicy(sizePolicy1)
        self.pvFilterLineEdit.setLayoutDirection(Qt.RightToLeft)

        self.gridLayout.addWidget(self.pvFilterLineEdit, 2, 3, 1, 1, Qt.AlignLeft)

        self.getLiveMachineButton = QPushButton(self.snapshotLayoutWidget)
        self.getLiveMachineButton.setObjectName(u"getLiveMachineButton")

        self.gridLayout.addWidget(self.getLiveMachineButton, 0, 1, 2, 1)

        self.saveMachineSnapshotButton = QPushButton(self.snapshotLayoutWidget)
        self.saveMachineSnapshotButton.setObjectName(u"saveMachineSnapshotButton")

        self.gridLayout.addWidget(self.saveMachineSnapshotButton, 0, 2, 2, 1)

        self.restoreMachineButton = QPushButton(self.snapshotLayoutWidget)
        self.restoreMachineButton.setObjectName(u"restoreMachineButton")

        self.gridLayout.addWidget(self.restoreMachineButton, 0, 0, 2, 1)

        self.saveDataFileButton = QPushButton(self.snapshotLayoutWidget)
        self.saveDataFileButton.setObjectName(u"saveDataFileButton")

        self.gridLayout.addWidget(self.saveDataFileButton, 0, 4, 2, 1)

        self.pvSearchButton = QPushButton(self.snapshotLayoutWidget)
        self.pvSearchButton.setObjectName(u"pvSearchButton")
        sizePolicy2.setHeightForWidth(self.pvSearchButton.sizePolicy().hasHeightForWidth())
        self.pvSearchButton.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.pvSearchButton, 2, 4, 1, 1, Qt.AlignLeft)

        self.rampingMachineButton = QPushButton(self.snapshotLayoutWidget)
        self.rampingMachineButton.setObjectName(u"rampingMachineButton")

        self.gridLayout.addWidget(self.rampingMachineButton, 2, 0, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.splitter.addWidget(self.snapshotLayoutWidget)

        self.verticalLayout_2.addWidget(self.splitter)

        masar.setCentralWidget(self.mainwidget)
        self.menubar = QMenuBar(masar)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1532, 19))
        masar.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(masar)
        self.statusbar.setObjectName(u"statusbar")
        masar.setStatusBar(self.statusbar)
        QWidget.setTabOrder(self.systemCombox, self.configFilterLineEdit)
        QWidget.setTabOrder(self.configFilterLineEdit, self.fetchConfigButton)
        QWidget.setTabOrder(self.fetchConfigButton, self.configTableWidget)
        QWidget.setTabOrder(self.configTableWidget, self.eventFilterLineEdit)
        QWidget.setTabOrder(self.eventFilterLineEdit, self.authorTextEdit)
        QWidget.setTabOrder(self.authorTextEdit, self.timeRangeCheckBox)
        QWidget.setTabOrder(self.timeRangeCheckBox, self.eventStartDateTime)
        QWidget.setTabOrder(self.eventStartDateTime, self.eventEndDateTime)
        QWidget.setTabOrder(self.eventEndDateTime, self.fetchEventButton)
        QWidget.setTabOrder(self.fetchEventButton, self.eventTableWidget)
        QWidget.setTabOrder(self.eventTableWidget, self.snapshotTabWidget)
        QWidget.setTabOrder(self.snapshotTabWidget, self.currentCommentText)

        self.retranslateUi(masar)
        self.eventFilterLineEdit.textChanged.connect(masar.eventFilterChanged)
        self.authorTextEdit.textChanged.connect(masar.authorTextChanged)
        self.timeRangeCheckBox.stateChanged.connect(masar.useTimeRange)
        self.fetchEventButton.clicked["void"].connect(masar.fetchEventAction)
        self.fetchSnapshotButton.clicked["void"].connect(masar.retrieveSnapshot)
        self.restoreMachineButton.clicked["void"].connect(masar.restoreSnapshotAction)
        self.getLiveMachineButton.clicked.connect(masar.getLiveMachineAction)
        self.saveDataFileButton.clicked.connect(masar.saveDataFileAction)
        self.systemCombox.currentIndexChanged.connect(masar.systemComboxChanged)
        self.configFilterLineEdit.textChanged.connect(masar.configFilterChanged)
        self.fetchConfigButton.clicked.connect(masar.fetchConfigAction)
        self.snapshotTabWidget.tabCloseRequested.connect(masar.closeTab)
        self.snapshotTabWidget.currentChanged.connect(masar.configTab)
        self.compareSnapshotsButton.clicked.connect(masar.openMsgBox)
        self.saveMachineSnapshotButton.clicked.connect(masar.saveMachineSnapshot)
        self.pvFilterLineEdit.textChanged.connect(masar.pvFilterChanged)
        self.pvSearchButton.clicked.connect(masar.searchPV)
        self.rampingMachineButton.clicked.connect(masar.rampingMachine)
        self.snapshotIdLineEdit.textChanged.connect(masar.snapshotIdChanged)
        self.searchSnapshotButton.clicked.connect(masar.retrieveSnapshotById)
        self.setGoldenButton.clicked.connect(masar.setGoldenSnapshot)
        self.getGoldenButton.clicked.connect(masar.fetchGoldenSnapshotAction)

        self.systemCombox.setCurrentIndex(-1)
        self.snapshotTabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(masar)
    # setupUi

    def retranslateUi(self, masar):
        masar.setWindowTitle(QCoreApplication.translate("masar", u"MASAR Viewer", None))
#if QT_CONFIG(tooltip)
        masar.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.systemCombox.setToolTip(QCoreApplication.translate("masar", u"sub-system to which configs/PV list belong", None))
#endif // QT_CONFIG(tooltip)
        self.systemLabel.setText(QCoreApplication.translate("masar", u"System", None))
        self.configFilterLabel.setText(QCoreApplication.translate("masar", u"Config Filter", None))
#if QT_CONFIG(tooltip)
        self.fetchConfigButton.setToolTip(QCoreApplication.translate("masar", u"<html><head/><body><p>get pre-defined configurations</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.fetchConfigButton.setText(QCoreApplication.translate("masar", u"Select Config(s)", None))
#if QT_CONFIG(tooltip)
        self.configTableWidget.setToolTip(QCoreApplication.translate("masar", u"<html><head/><body><p>ConfigTable: a list of pre-defined configs</p><p><span style=\" color:#00ff00;\">CLICK</span> on ONE row to fetch its list of snapshot(s)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.configFilterLineEdit.setToolTip(QCoreApplication.translate("masar", u"using expression like *LN*", None))
#endif // QT_CONFIG(tooltip)
        self.configFilterLineEdit.setText(QCoreApplication.translate("masar", u"*", None))
        self.configFilterLineEdit.setPlaceholderText("")
#if QT_CONFIG(tooltip)
        self.fetchEventButton.setToolTip(QCoreApplication.translate("masar", u"get a list of snapshot(s) or event(s)", None))
#endif // QT_CONFIG(tooltip)
        self.fetchEventButton.setText(QCoreApplication.translate("masar", u"Select Snapshot(s)", None))
        self.ByWho.setText(QCoreApplication.translate("masar", u"Author", None))
        self.eventEndDateTime.setDisplayFormat(QCoreApplication.translate("masar", u"yyyy-MM-dd hh:mm:ss", None))
        self.eventStartDateTime.setDisplayFormat(QCoreApplication.translate("masar", u"yyyy-MM-dd hh:mm:ss", None))
        self.eventFilterLabel.setText(QCoreApplication.translate("masar", u"Snapshot Desc", None))
        self.eventEndLabel.setText(QCoreApplication.translate("masar", u"To:", None))
#if QT_CONFIG(tooltip)
        self.authorTextEdit.setToolTip(QCoreApplication.translate("masar", u"using expression like *mei*", None))
#endif // QT_CONFIG(tooltip)
        self.authorTextEdit.setText(QCoreApplication.translate("masar", u"*", None))
        self.timeRangeCheckBox.setText(QCoreApplication.translate("masar", u"Use time range:", None))
#if QT_CONFIG(tooltip)
        self.eventFilterLineEdit.setToolTip(QCoreApplication.translate("masar", u"using expression like *BPM*", None))
#endif // QT_CONFIG(tooltip)
        self.eventFilterLineEdit.setText(QCoreApplication.translate("masar", u"*", None))
        self.eventStartLabel.setText(QCoreApplication.translate("masar", u"From:", None))
#if QT_CONFIG(tooltip)
        self.eventTableWidget.setToolTip(QCoreApplication.translate("masar", u"<html><head/><body><p>snapshotTable: a list of saved snapshot(s) for the selected config(s)</p><p><span style=\" color:#00ff00;\">Double CLICK</span> on one row to display <span style=\" color:#00ff00;\">ONE</span> snapshot data </p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.getGoldenButton.setToolTip(QCoreApplication.translate("masar", u"<html><head/><body><p>get the Golden snapshot for the selected Config above</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.getGoldenButton.setText(QCoreApplication.translate("masar", u"Dispaly Golden Snapshot", None))
#if QT_CONFIG(tooltip)
        self.fetchSnapshotButton.setToolTip(QCoreApplication.translate("masar", u"get PVs data", None))
#endif // QT_CONFIG(tooltip)
        self.fetchSnapshotButton.setText(QCoreApplication.translate("masar", u"Display Snapshot(s)", None))
#if QT_CONFIG(tooltip)
        self.searchSnapshotButton.setToolTip(QCoreApplication.translate("masar", u"<html><head/><body><p>please enter a snapshot ID (one integer number, and only one) in the left box, then click this button</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.searchSnapshotButton.setStatusTip("")
#endif // QT_CONFIG(statustip)
        self.searchSnapshotButton.setText(QCoreApplication.translate("masar", u"search a snapshot by its ID", None))
#if QT_CONFIG(tooltip)
        self.snapshotIdLineEdit.setToolTip(QCoreApplication.translate("masar", u"<html><head/><body><p>Please enter one integer number and only one, then press Enter key or click the right-side button</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.setGoldenButton.setToolTip(QCoreApplication.translate("masar", u"<html><head/><body><p>Set the selected snapshot above as golden snapshot</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.setGoldenButton.setText(QCoreApplication.translate("masar", u"Set it As Golden", None))
#if QT_CONFIG(tooltip)
        self.snapshotTabWidget.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.currentCommentText.setPlainText(QCoreApplication.translate("masar", u"\n"
"MASAR is an EPICS V4 service which does MAchine Snapshot, Archiving, and Retrieve [1] [2]. This software was originally developed by National Synchrotron Light Source II at Brookhaven National Laboratory.\n"
"\n"
"\n"
"Quick Start ...\n"
"\n"
"    1. To restore the machine to a particular state/snapshot: click (either single or double) on one row in the left-top Config table --> double click on one row in the left-bottom Snapshot table --> click the button \"Restore Machine\";\n"
"    \n"
"    2. To save a machine snapshot: click on one row in the left-top Config table  --> click \"Save Machine Snapshot ...\" --> put a concise description (<80 characters) such as: \"SBM EmitX and Y 69 nm. This is golden\";\n"
"\n"
"    3. To compare multiple saved snapshots: click on one row in the left-top Config table --> Ctrl + mouse click to select multiple rows in the left-bottom Snapshot table --> click \"Compare Snapshots...\";\n"
"\n"
"    4. To search / filter PVs by clicking the button \"PV search\" or using the"
                        " keyboard 'Ctrl + F': use * to match multiple characters, use ? to match single character, use [m-n] to match the range from m to n, and use [!character-set] to exclude PVs which contain any character in the 'character-set', i.e. *BPM:[1-3]* means searching any PV name which contains BPM:1, BPM:2 and BPM:3, *[!SP] means searching PV which doesn't have 'SP' at the end. The searching can be nested -- you may search the filtered snapshot again and again using different search pattern to refine your search result; \n"
"\n"
"    5. To partially restore snapshot (don't restore some PVs): click 'Not Restore' in the snapshot Tab for the PV you don't want to restore; better way: firstly filter PVs as #4 instruction, then only restore the filtered PVs by clicking \"Restore Machine\".\n"
"\n"
"\n"
"Tips ...\n"
"    \n"
"    1. Always put the mouse cursor over the things you don't know for 2 seconds, the GUI will show you what it is or how to do it;\n"
"    \n"
"    2. Always follow the instructions on the pop-up message "
                        "which shows something is not working as expected and how to fix it; \n"
"  \n"
"    3. MASAR GUI is mainly table-based. Treat the table as Microsoft Excel: resize the column, sort by the column, select multiple rows, Ctrl + c to copy one single cell ...  \n"
"   \n"
"\n"
"Terminology ...\n"
"    \n"
"    * machine: it can be accelerator, system, etc.: Linac, Booster, Storage Ring, BPM system, Magnet system ...\n"
"    \n"
"    * snapshot: a list of PVs associated with data (value, time stamp, alarm status ... ) saved at a particular time for a particular machine state.\n"
"\n"
"    * config table: pre-defined a list of configurations for different machines; it has a unique Name, Description, Date when it is created ...  \n"
"\n"
"    * snapshot table: a list of saved snapshots (without EPICS data) for a particular config; it has Config Name which is listed in the config table, Description,  Author ...  \n"
"\n"
"    * snapshot tab: the EPICS data of one snapshot is presented in the form of table in a Tab windo"
                        "w.\n"
"\n"
"\n"
"More Info ...\n"
"\n"
"    please check out the links below:\n"
"\n"
"    [1] http://epics-pvdata.sourceforge.net/\n"
"    [2] http://epics-pvdata.hg.sourceforge.net/hgweb/epics-pvdata/masarService/raw-file/tip/documentation/userManual.html", None))
        self.snapshotTabWidget.setTabText(self.snapshotTabWidget.indexOf(self.commentTab), QCoreApplication.translate("masar", u"Welcome to MASAR", None))
#if QT_CONFIG(tooltip)
        self.snapshotTabWidget.setTabToolTip(self.snapshotTabWidget.indexOf(self.commentTab), QCoreApplication.translate("masar", u"How to use MASAR", None))
#endif // QT_CONFIG(tooltip)
        self.compareSnapshotsButton.setText(QCoreApplication.translate("masar", u"Compare Snapshots...", None))
#if QT_CONFIG(tooltip)
        self.pvFilterLineEdit.setToolTip(QCoreApplication.translate("masar", u"<html><head/><body><p>*BPM:[1-3]* to search any pv containing BPM:1, BPM:2, and BPM:3; press Enter key  or click the button 'PV Search' when you are done with the search pattern</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pvFilterLineEdit.setText("")
#if QT_CONFIG(tooltip)
        self.getLiveMachineButton.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.getLiveMachineButton.setText(QCoreApplication.translate("masar", u"Compare Live Machine", None))
        self.saveMachineSnapshotButton.setText(QCoreApplication.translate("masar", u"Save Machine Snapshot ...", None))
#if QT_CONFIG(tooltip)
        self.restoreMachineButton.setToolTip(QCoreApplication.translate("masar", u"one-step simple put", None))
#endif // QT_CONFIG(tooltip)
        self.restoreMachineButton.setText(QCoreApplication.translate("masar", u"Restore Machine", None))
        self.saveDataFileButton.setText(QCoreApplication.translate("masar", u"Export Snapshot to File ...", None))
#if QT_CONFIG(tooltip)
        self.pvSearchButton.setToolTip(QCoreApplication.translate("masar", u"<html><head/><body><p>search/filter pvs in the active snapshot Tab (the one you are watching. You can use Ctrl + F to search) </p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pvSearchButton.setText(QCoreApplication.translate("masar", u"PV Search", None))
#if QT_CONFIG(tooltip)
        self.rampingMachineButton.setToolTip(QCoreApplication.translate("masar", u"multiple-step grdual put", None))
#endif // QT_CONFIG(tooltip)
        self.rampingMachineButton.setText(QCoreApplication.translate("masar", u"Ramping Machine...", None))
    # retranslateUi

