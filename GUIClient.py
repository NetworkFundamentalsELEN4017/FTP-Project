import sys
import os
import random
import socket
from PyQt5.QtWidgets import QFileSystemModel
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.uic import loadUi
from PyQt5.QtCore import QCoreApplication


class Login(QDialog):
    def __init__(self):
        super().__init__()
        loadUi('Login.ui', self)
        self.setWindowTitle('FTP Client')
        self.components_hide();
        self.btnLogin.clicked.connect(self.login_event)
        self.btnDirectory.clicked.connect(self.directory_change)

        self.treeViewUp.clicked.connect(self.highlighted)
        self.btnUpload.clicked.connect(self.upload_file)
        self.btnDownload.clicked.connect(self.download_file)
        self.btnRefresh.clicked.connect(self.refresh_directory)
        self.btnCheck.clicked.connect(self.check_connection)
        self.btnQuit.clicked.connect(self.quit_client)
        self.btnReturn.clicked.connect(self.directory_return)

    def components_hide(self):
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
        self.btnQuit.hide()
        self.btnCheck.hide()
        self.btnReturn.hide()

    def components_show(self):
        self.frmLogin.hide()
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
        self.btnQuit.show()
        self.btnCheck.show()
        self.btnReturn.show()

    def login_event(self):
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
        self.model.setRootPath(str(directory))

        self.treeViewUp.setModel(self.model)
        self.treeViewUp.setRootIndex(self.model.index(str(directory)))

        self.treeViewUp.header().resizeSection(0, 200)
        self.treeViewUp.setWindowTitle("Dir View")
        self.components_show()

    def directory_change(self):
        cmd_cwd = 'CWD ' + self.edtDirectory.text() + '\r\n'
        self.send_cmd(self.client_socket, cmd_cwd)

    def directory_return(self):
        cmd_cdup = 'CDUP\r\n'
        self.send_cmd(self.client_socket, cmd_cdup)

    def PORT(self):
        print('PORT code')
        port_number1 = random.randint(47, 234)
        port_number2 = random.randint(0, 255)
        client_address = socket.gethostbyname(socket.gethostname())
        client_address = client_address.split(".")
        client_address = ','.join(client_address)
        client_address = "(" + client_address + "," + str(port_number1) + "," + str(port_number2) + ")"
        data_port = (port_number1 * 256) + port_number2
        print(client_address)
        print(data_port)
        host = socket.gethostbyname(socket.gethostname())
        data_connection = self.data_establish(host, data_port)
        #command_connection.send(("227 Entering passive mode" + str(client_address) + '\r\n').encode())

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
            self.send_cmd(self.client_socket, cmd_stor)

            file_data = data_socket.recv(8192)
            f = open(down_folder_name + "/" + user_file_name, 'wb')

            while file_data:
                f.write(file_data)
                file_data = data_socket.recv(8192)

            self.pteConsole.appendPlainText(self.client_socket.recv(8192).decode())
        else:
            self.pteConsole.appendPlainText("Please select a file to download.")
        data_socket.close()

    def refresh_directory(self):

        #cmd_pasv = 'PASV\r\n'
        #response = self.send_cmd(self.client_socket, cmd_pasv)
        #data_socket = self.setup_data(response)

        print('PORT code')
        port_number1 = random.randint(47, 234)
        port_number2 = random.randint(0, 255)
        client_address = socket.gethostbyname(socket.gethostname())
        client_address = client_address.split(".")
        client_address = ','.join(client_address)
        client_address = client_address + "," + str(port_number1) + "," + str(port_number2)
        data_port = (port_number1 * 256) + port_number2
        print(client_address)
        print(data_port)



        host = socket.gethostbyname(socket.gethostname())
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_socket.bind((host, data_port))
        data_socket.listen(5)

        cmd_port = 'PORT ' + client_address + '\r\n'
        response = self.send_cmd(self.client_socket, cmd_port)
        print(response)

        connection_socket, address_ip = data_socket.accept()


        #command_connection.send(("227 Entering passive mode" + str(client_address) + '\r\n').encode())

        cmd_list = 'LIST\r\n'
        self.send_cmd(self.client_socket, cmd_list)
        #response = data_socket.recv(8192).decode()
        response = connection_socket.recv(8192).decode()
        self.pteDownload.setPlainText(response)
        #self.pteDownload.setPlainText(response)
        #data_socket.close()
        connection_socket.close()
    def highlighted(self, index):
        path = self.sender().model().filePath(index)
        filename = path.split('/')[-1]
        self.edtUpload.setText(filename)

    def check_connection(self):
        cmd_noop = 'NOOP\r\n'
        self.send_cmd(self.client_socket, cmd_noop)

    def quit_client(self):
        cmd_quit = 'QUIT\r\n'
        self.send_cmd(self.client_socket, cmd_quit)
        self.components_hide()
        self.frmLogin.show()

    def send_cmd(self, client_socket, command):
        client_socket.send(command.encode())
        return_message = client_socket.recv(8192).decode()
        self.pteConsole.appendPlainText("Sent command: " + command)
        self.pteConsole.appendPlainText("Return message: " + return_message)
        if command == 'LIST\r\n':
            return_message = client_socket.recv(8192).decode()
            self.pteConsole.appendPlainText("Return message: " + return_message)
        QCoreApplication.processEvents()
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