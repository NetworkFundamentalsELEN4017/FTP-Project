import sys
import os
from PyQt5.QtWidgets import QFileSystemModel, QDirModel
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import QDir
from PyQt5.uic import loadUi

class Login(QDialog):
    def __init__(self):
        super().__init__()
        loadUi('Login.ui', self)
        self.setWindowTitle('FTP Client')
        self.btnLogin.clicked.connect(self.onLoginButtonClicked)
        self.treeView.hide()
        self.btnUpload.hide()
        self.treeView.clicked.connect(self.onClicked)

    def onLoginButtonClicked(self):
        self.lblOutput.setText("Welcome " + self.edtUser.text() + "!")
        self.frmLogin.hide()
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.currentPath())


        self.treeView.setModel(self.model)
        self.treeView.setRootIndex(self.model.index(QDir.currentPath()))

        self.treeView.header().resizeSection(0, 200)
        self.treeView.setWindowTitle("Dir View")
        self.treeView.show()
        self.btnUpload.show()


    def onClicked(self, index):
        path = self.sender().model().filePath(index)
        print(path)









app = QApplication(sys.argv)
widget = Login()
widget.show()
sys.exit(app.exec_())