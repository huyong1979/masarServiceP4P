
import os

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (QApplication, QDialog, QDialogButtonBox)

try:
    from . import ui_commentdiag
except ImportError:
    import ui_commentdiag

class CommentDlg(QDialog,
        ui_commentdiag.Ui_commentdlg):

    def __init__(self, parent=None):
        super(CommentDlg, self).__init__(parent)
        self.setupUi(self)
        self.userID = os.popen('whoami').read()[:-1]#username without \n
        self.authorInfo.setText("Author: "+self.userID)
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
        enable = bool(self.commentLineEdit.text())
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(enable)

    def result(self):
        if not self.isAccepted:
            return None
        else:
            return (self.userID, str(self.commentLineEdit.text()))

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = CommentDlg()
    form.show()
    app.exec()
    if form.isAccepted:
        print(form.result())
    else:
        print('Do nothing')
