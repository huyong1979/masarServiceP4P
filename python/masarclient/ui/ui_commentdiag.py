# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_commentdiag.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QSizePolicy, QWidget)

class Ui_commentdlg(object):
    def setupUi(self, commentdlg):
        if not commentdlg.objectName():
            commentdlg.setObjectName(u"commentdlg")
        commentdlg.resize(426, 135)
        self.gridLayout = QGridLayout(commentdlg)
        self.gridLayout.setObjectName(u"gridLayout")
        self.commentLineEdit = QLineEdit(commentdlg)
        self.commentLineEdit.setObjectName(u"commentLineEdit")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.commentLineEdit.sizePolicy().hasHeightForWidth())
        self.commentLineEdit.setSizePolicy(sizePolicy)
        self.commentLineEdit.setMinimumSize(QSize(408, 0))
        self.commentLineEdit.setMaxLength(80)
        self.commentLineEdit.setDragEnabled(True)

        self.gridLayout.addWidget(self.commentLineEdit, 2, 0, 1, 2)

        self.label_2 = QLabel(commentdlg)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.authorInfo = QLabel(commentdlg)
        self.authorInfo.setObjectName(u"authorInfo")

        self.horizontalLayout.addWidget(self.authorInfo)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(commentdlg)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttonBox, 3, 1, 1, 1)


        self.retranslateUi(commentdlg)
        self.buttonBox.rejected.connect(commentdlg.reject)
        self.buttonBox.accepted.connect(commentdlg.accept)
        self.commentLineEdit.textChanged.connect(commentdlg.on_commentLineEdit_textChanged)

        QMetaObject.connectSlotsByName(commentdlg)
    # setupUi

    def retranslateUi(self, commentdlg):
        commentdlg.setWindowTitle(QCoreApplication.translate("commentdlg", u"Comment", None))
        self.commentLineEdit.setText("")
        self.label_2.setText(QCoreApplication.translate("commentdlg", u"Concise Description (<80 characters):", None))
        self.authorInfo.setText(QCoreApplication.translate("commentdlg", u"Author:", None))
    # retranslateUi

