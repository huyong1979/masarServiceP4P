'''
Created on Sept 06, 2013

@author: yhu
'''

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QGridLayout, QLabel, QGroupBox,
                               QRadioButton, QDialogButtonBox)
from PySide6.QtCore import Qt


class ShowSelectRefDlg(QDialog):
    def __init__(self, eventIDs, parent=None):
        super(ShowSelectRefDlg, self).__init__(parent)
        self.setWindowTitle('Select reference snapshot')
        self.eventIDs=eventIDs
        self.refSnapshot = ""
        self.isAccepted = False
        #print(self.eventIDs)

        desc = QLabel()
        desc.setText("%d snapshots with IDs %s to be compared.\n\n\
Please select one as the reference snapshot\n\n"%(len(eventIDs),eventIDs))
        gBox = QGroupBox("Reference Snapshot Selection")

        self.radio = [0]*len(eventIDs)
        vbox = QVBoxLayout()
        for i in range(len(eventIDs)):
            self.radio[i] = QRadioButton("Snapshot ID: %s"%eventIDs[i])
            self.radio[i].setChecked(False)
            vbox.addWidget(self.radio[i])
            self.radio[i].clicked.connect(self.reorderEventIDs)
        vbox.addStretch(1)
        gBox.setLayout(vbox)

        buttonBox = QDialogButtonBox()
        buttonBox.setOrientation(Qt.Horizontal)
        buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.rejected.connect(self.reject)
        buttonBox.accepted.connect(self.accept)

        layout = QGridLayout(self)
        layout.addWidget(desc,0,0,1,1)
        layout.addWidget(gBox,1,0,1,1)
        layout.addWidget(buttonBox,2,0,1,1)
        self.setLayout(layout)


    def reorderEventIDs(self):
        #print("re-order Event IDs")
        for i in range(len(self.eventIDs)):
            #use .isChecked() instead of .isChecked
            if self.radio[i].isChecked():
                #print("Event %s is checked"%self.eventIDs[i])
                self.refSnapshot = self.eventIDs[i]
        eventIDs = self.eventIDs
        idx = eventIDs.index(self.refSnapshot)
        eventIDs.pop(idx)
        #print(eventIDs)
        eventIDs.insert(0,self.refSnapshot)
        #print(eventIDs)
        self.eventIDs = eventIDs

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
            #print(self.refSnapshot)
            return (self.eventIDs)
