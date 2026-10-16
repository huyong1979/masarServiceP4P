
import os

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (QApplication, QDialog, QDialogButtonBox)

try:
    from . import ui_commentdetail
except ImportError:
    import ui_commentdetail

class CommentDetail(QDialog,
        ui_commentdetail.Ui_commentdetail):

    def __init__(self, parent=None):
        super(CommentDetail, self).__init__(parent)
        self.setupUi(self)
        self.updateUi()
        #self.authorLineEdit.setFocus()
        self.isAccepted = False

    def accept(self, *args, **kwargs):
        self.isAccepted = True
        return QDialog.accept(self, *args, **kwargs)

    def reject(self, *args, **kwargs):
        self.isAccepted = False
        return QDialog.reject(self, *args, **kwargs)

    @Slot()
    def on_commentTextEdit_textChanged(self):
        self.updateUi()

    def updateUi(self):
        enable = bool(self.commentTextEdit.toPlainText())
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(enable)

    def result(self):
        if not self.isAccepted:
            return None
        else:
            return (str(self.commentTextEdit.toPlainText()))
