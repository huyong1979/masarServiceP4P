import os

from PySide6.QtWidgets import (QApplication, QDialog, QDialogButtonBox)

from . import ui_commentdetail

class CommentDetail(QDialog,
        ui_commentdetail.Ui_commentdetail):

    def __init__(self, parent=None):
        super().__init__(parent)
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

    def on_commentTextEdit_textChanged(self):
        self.updateUi()

    def updateUi(self):
        enable = bool(self.commentTextEdit.toPlainText().strip())
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(enable)

    def result(self):
        if not self.isAccepted:
            return None
        else:
            return self.commentTextEdit.toPlainText()


