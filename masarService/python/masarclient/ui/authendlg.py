'''
Created on Sept 06, 2013

@author: yhu
'''





from PySide6.QtWidgets import (QDialog, QVBoxLayout, QGridLayout, QLabel,
                         QDialogButtonBox, QLineEdit)
from PySide6.QtCore import Qt
    
class AuthenDlg(QDialog):
    def __init__(self, password, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Authentication')
        self.password = password
        layout = QGridLayout(self)

        desc = QLabel()
        if self.password != "":#authentication is required only once Once it is correct
            desc.setText("Caution! your action will be recorded on the logbook\n \
Click OK if you want to continue, otherwise click Cancel")
        else: 
            desc.setText("Your action will be recorded on the logbook\n \
Please enter your password if you want to continue\n \
Otherwise Click Cancel \n")       
            self.passWdLineEdit = QLineEdit()
            self.passWdLineEdit.setEchoMode(QLineEdit.EchoMode.Password)
            vbox = QVBoxLayout()
            vbox.addWidget(self.passWdLineEdit)
            vbox.addStretch(1)    
            self.passWdLineEdit.textChanged.connect(self.getPassWd)
            layout.addWidget(self.passWdLineEdit,1,0,1,1)
        
        buttonBox = QDialogButtonBox()
        buttonBox.setOrientation(Qt.Orientation.Horizontal)
        buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        
        layout.addWidget(desc,0,0,1,1)
        layout.addWidget(buttonBox,2,0,1,1)
        self.setLayout(layout)
            
    def getPassWd(self):
        self.password = str(self.passWdLineEdit.text())
         
    def accept(self, *args, **kwargs):
        self.isAccepted = True
        return QDialog.accept(self, *args, **kwargs)
    
    def reject(self, *args, **kwargs):
        self.isAccepted = False
        return QDialog.reject(self, *args, **kwargs)    
    
    def result(self):
        if not self.isAccepted:
            return None
        else:
            return (self.password)
        