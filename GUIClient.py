import sys
import os
from PyQt5.QtWidgets import QFileSystemModel
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.uic import loadUi
import socket


class Login(QDialog):
    def __init__(self):
        super().__init__()
        loadUi('Login.ui', self)
        self.setWindowTitle('FTP Client')
        self.btnLogin.clicked.connect(self.onLoginButtonClicked)
        self.treeViewUp.hide()
        self.treeViewDown.hide()
        self.btnUpload.hide()
        self.btnDownload.hide()
        self.treeViewUp.clicked.connect(self.onClicked)
        self.treeViewDown.clicked.connect(self.onClicked)

    def onLoginButtonClicked(self):
        self.frmLogin.hide()
        self.model = QFileSystemModel()

        host = self.edtHost.text()
        name = self.edtUser.text()
        password = self.edtPass.text()
        command_port = self.edtPort.text()

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, int(command_port)))
        connection_owner = client_socket.recv(8192).decode()
        self.pteConsole.appendPlainText("Connected to: " + connection_owner)

        cmd_user = 'USER ' + name + '\r\n'
        self.send_cmd(client_socket, cmd_user)

        cmd_pass = 'PASS ' + password + '\r\n'
        self.send_cmd(client_socket, cmd_pass)

        cmd_pasv = 'PASV\r\n'
        response = self.send_cmd(client_socket, cmd_pasv)
        data_socket = self.setup_data(response)

        cmd_list = 'LIST\r\n'
        self.send_cmd(client_socket, cmd_list)
        response = data_socket.recv(8192).decode()
        #print(response)

        directory = os.listdir()
        #print(directory)
        directory = os.getcwd()
        #print(directory)
        self.model.setRootPath(str(directory))

        self.treeViewUp.setModel(self.model)
        self.treeViewUp.setRootIndex(self.model.index(str(directory)))

        self.treeViewUp.header().resizeSection(0, 200)
        self.treeViewUp.setWindowTitle("Dir View")
        self.treeViewUp.show()
        self.btnUpload.show()
        self.btnDownload.show()
        self.treeViewDown.show()


    def onClicked(self, index):
        path = self.sender().model().filePath(index)
        self.lblOutput.setText(path)
        print(path)

    def send_cmd(self, client_socket, command):
        client_socket.send(command.encode())
        return_message = client_socket.recv(8192).decode()
        self.pteConsole.appendPlainText("Sent command: " + command)
        self.pteConsole.appendPlainText("Return message: " + return_message)
        if command == 'LIST\r\n':
            return_message = client_socket.recv(8192).decode()
            self.pteConsole.appendPlainText("Return message: " + return_message)
        return return_message

    def setup_data(self, response):
        index_start = response.find('(')
        index_end = response.find(')')
        response = response[index_start + 1:index_end]
        response = response.split(",")
        data_host = '.'.join(response[0:4])
        port_response = response[-2:]
        data_port = (int(port_response[0]) * 256) + int(port_response[1])
        data_port = int(data_port)
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_socket.connect((data_host, data_port))
        return data_socket

app = QApplication(sys.argv)
widget = Login()
widget.show()
sys.exit(app.exec_())