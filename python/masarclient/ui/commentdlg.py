import os

from PySide6.QtWidgets import (QApplication, QDialog, QDialogButtonBox)

from . import ui_commentdiag

class CommentDlg(QDialog,
        ui_commentdiag.Ui_commentdlg):

    def __init__(self, parent=None):
        super().__init__(parent)
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

    def on_commentLineEdit_textChanged(self):
        self.updateUi()

    def updateUi(self):
        enable =  bool(self.commentLineEdit.text().strip())
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(enable)

    def result(self):
        if not self.isAccepted:
            return None
        else:
             return (self.userID, self.commentLineEdit.text())

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = CommentDlg()
    form.show()
    app.exec()
    if form.isAccepted:
        print((form.result()))
    else:
        print('Do nothing')
