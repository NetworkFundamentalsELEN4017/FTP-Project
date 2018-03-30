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
        self.btnDirectory.clicked.connect(self.directory_change)
        self.treeViewUp.hide()
        self.pteDownload.hide()
        self.btnUpload.hide()
        self.btnDirectory.hide()
        self.btnDownload.hide()
        self.edtDirectory.hide()
        self.edtUpload.hide()
        self.lblServer.hide()
        self.lblClient.hide()
        self.edtDownload.hide()
        self.lblDownload.hide()
        self.lblUpload.hide()
        self.btnRefresh.hide()
        self.treeViewUp.clicked.connect(self.onClicked)
        self.btnUpload.clicked.connect(self.upload_file)
        self.btnDownload.clicked.connect(self.download_file)
        self.btnRefresh.clicked.connect(self.refresh_directory)

    def onLoginButtonClicked(self):
        self.frmLogin.hide()
        self.model = QFileSystemModel()

        host = self.edtHost.text()
        name = self.edtUser.text()
        password = self.edtPass.text()
        command_port = self.edtPort.text()

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, int(command_port)))
        connection_owner = self.client_socket.recv(8192).decode()
        self.pteConsole.appendPlainText("Connected to: " + connection_owner)

        cmd_user = 'USER ' + name + '\r\n'
        self.send_cmd(self.client_socket, cmd_user)

        cmd_pass = 'PASS ' + password + '\r\n'
        self.send_cmd(self.client_socket, cmd_pass)

        cmd_pasv = 'PASV\r\n'
        response = self.send_cmd(self.client_socket, cmd_pasv)
        data_socket = self.setup_data(response)

        cmd_list = 'LIST\r\n'
        self.send_cmd(self.client_socket, cmd_list)
        response = data_socket.recv(8192).decode()
        self.pteDownload.appendPlainText(response)

        data_socket.close()

        directory = os.getcwd()
        print(directory)
        self.model.setRootPath(str(directory))

        self.treeViewUp.setModel(self.model)
        self.treeViewUp.setRootIndex(self.model.index(str(directory)))

        self.treeViewUp.header().resizeSection(0, 200)
        self.treeViewUp.setWindowTitle("Dir View")
        self.treeViewUp.show()
        self.btnUpload.show()
        self.btnDownload.show()
        self.pteDownload.show()
        self.btnDirectory.show()
        self.edtDirectory.show()
        self.lblServer.show()
        self.lblClient.show()
        self.edtUpload.show()
        self.edtDownload.show()
        self.lblDownload.show()
        self.lblUpload.show()
        self.btnRefresh.show()

    def directory_change(self):
        cmd_cwd = 'CWD ' + self.edtDirectory.text() + '\r\n'
        self.send_cmd(self.client_socket, cmd_cwd)

    def upload_file(self):
        user_file_name = self.edtUpload.text()
        print(user_file_name)
        if user_file_name:
            filetype = user_file_name.split('.')[-1]
            print(filetype)
            if filetype == 'txt':
                cmd_type = 'TYPE A\r\n'
            else:
                cmd_type = 'TYPE I\r\n'
            self.send_cmd(self.client_socket, cmd_type)

        cmd_pasv = 'PASV\r\n'
        response = self.send_cmd(self.client_socket, cmd_pasv)
        data_socket = self.setup_data(response)

        cmd_stor = 'STOR ' + user_file_name + '\r\n'
        #cmd_stor = 'STOR ' + 'Sloth1.jpg' + '\r\n'
        self.send_cmd(self.client_socket, cmd_stor)

        pic = open(user_file_name, 'rb')
        reading = pic.read(8192)

        while reading:
            print('reading file')
            data_socket.send(reading)
            reading = pic.read(8192)
        data_socket.close()
        self.pteConsole.appendPlainText("Return message: " + self.client_socket.recv(8192).decode())

    def download_file(self):
        down_folder_name = "Server_Downloads"
        if not os.path.exists(down_folder_name):
            os.makedirs(down_folder_name)

        user_file_name = self.edtDownload.text()
        if user_file_name:
            filetype = user_file_name.split('.')[-1]
            if filetype == 'txt':
                cmd_type = 'TYPE A\r\n'
            else:
                cmd_type = 'TYPE I\r\n'
            self.send_cmd(self.client_socket, cmd_type)

            cmd_pasv = 'PASV\r\n'
            response = self.send_cmd(self.client_socket, cmd_pasv)
            data_socket = self.setup_data(response)

            cmd_stor = 'RETR ' + user_file_name + '\r\n'
            #cmd_stor = 'RETR ' + 'Sloth1.jpg' + '\r\n'
            self.send_cmd(self.client_socket, cmd_stor)

            file_data = data_socket.recv(8192)
            f = open(down_folder_name + "/Sloth1.jpg", 'wb')

            while file_data:
                f.write(file_data)
                file_data = data_socket.recv(8192)

            self.pteConsole.appendPlainText(self.client_socket.recv(8192).decode())
        else:
            self.pteConsole.appendPlainText("Please select a file to download.")

    def refresh_directory(self):

        cmd_pasv = 'PASV\r\n'
        response = self.send_cmd(self.client_socket, cmd_pasv)
        data_socket = self.setup_data(response)
        cmd_list = 'LIST\r\n'
        self.send_cmd(self.client_socket, cmd_list)
        response = data_socket.recv(8192).decode()
        self.pteDownload.setPlainText(response)
        data_socket.close()


    def onClicked(self, index):
        path = self.sender().model().filePath(index)
        filename = path.split('/')[-1]
        self.edtUpload.setText(filename)
        #self.pteConsole.appendPlainText("Selected File Path: " + path)
        #cmd_cwd = self.edtDirectory + '\r\n'
        #self.send_cmd(self.client_socket,cmd_cwd)



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