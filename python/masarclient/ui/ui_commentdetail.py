# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_commentdetail.ui'
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
    QHBoxLayout, QLabel, QSizePolicy, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_commentdetail(object):
    def setupUi(self, commentdetail):
        if not commentdetail.objectName():
            commentdetail.setObjectName(u"commentdetail")
        commentdetail.resize(416, 209)
        self.verticalLayout = QVBoxLayout(commentdetail)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.label_2 = QLabel(commentdetail)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout.addWidget(self.label_2)

        self.commentTextEdit = QTextEdit(commentdetail)
        self.commentTextEdit.setObjectName(u"commentTextEdit")

        self.verticalLayout.addWidget(self.commentTextEdit)

        self.buttonBox = QDialogButtonBox(commentdetail)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(commentdetail)
        self.buttonBox.accepted.connect(commentdetail.accept)
        self.buttonBox.rejected.connect(commentdetail.reject)
        self.commentTextEdit.textChanged.connect(commentdetail.on_commentTextEdit_textChanged)

        QMetaObject.connectSlotsByName(commentdetail)
    # setupUi

    def retranslateUi(self, commentdetail):
        commentdetail.setWindowTitle(QCoreApplication.translate("commentdetail", u"Comment", None))
        self.label_2.setText(QCoreApplication.translate("commentdetail", u"Put your detailed comment which will be shown in the Olog:", None))
    # retranslateUi

