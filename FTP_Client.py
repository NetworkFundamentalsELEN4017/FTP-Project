# FTP Client was implemented by Iordan Tchaparov (1068874)

# Imports the needed python libaries for the client program
import sys
import os
import random
import socket
from PyQt5.QtWidgets import QFileSystemModel
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.uic import loadUi
from PyQt5.QtCore import QCoreApplication


class FTP_Client(QDialog):
    # This creates the button click events and initializes the GUI
    def __init__(self):
        super().__init__()
        loadUi('GUI.ui', self)
        self.setWindowTitle('FTP Client')
        self.components_hide(); # Hides all the components that cant be accessed before logging in

        # All the button click events and the functions they call when clicked
        self.btnLogin.clicked.connect(self.login_procedure)
        self.btnDirectory.clicked.connect(self.directory_change)
        self.treeViewUp.clicked.connect(self.highlighted_file)
        self.btnUpload.clicked.connect(self.upload_file)
        self.btnDownload.clicked.connect(self.download_file)
        self.btnRefresh.clicked.connect(self.refresh_directory)
        self.btnCheck.clicked.connect(self.check_connection)
        self.btnQuit.clicked.connect(self.quit_client)
        self.btnReturn.clicked.connect(self.directory_return)
        self.btnNew.clicked.connect(self.directory_create)
        self.btnRemove.clicked.connect(self.directory_delete)
        self.btnDelete.clicked.connect(self.delete_file)

    # A function to hide all components before logging in
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
        self.rbnPort.hide()
        self.rbnPasv.hide()
        self.grpClient.hide()
        self.grpServerFile.hide()
        self.grpServerDirect.hide()

    # A function to show all components once logged in
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
        self.rbnPort.show()
        self.rbnPasv.show()
        self.grpClient.show()
        self.grpServerFile.show()
        self.grpServerDirect.show()

    # The function can controls logging in to the server
    def login_procedure(self):
        self.frmLogin.hide()                # Hides the log in form
        self.model = QFileSystemModel()     # Makes a file system model to represent the directory of the client

        # Saves the parameters from the edit boxes that the user inputs data into
        host = self.edtHost.text()
        name = self.edtUser.text()
        password = self.edtPass.text()
        command_port = self.edtPort.text()

        # Initializes the socket that will be used for the TCP control connection
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, int(command_port)))

        # Displays server the client connects to
        connection_owner = self.client_socket.recv(8192).decode()
        self.pteConsole.appendPlainText("Connected to: " + connection_owner)

        # Sends the command to identify the user of the client
        cmd_user = 'USER ' + name + '\r\n'
        self.send_cmd(self.client_socket, cmd_user)

        # Sends the command to the server for the password to the above user
        cmd_pass = 'PASS ' + password + '\r\n'
        self.send_cmd(self.client_socket, cmd_pass)

        # Creates the TCP data connection
        data_socket = self.setup_data()

        # Sends the command to the server to list the files in the server
        cmd_list = 'LIST\r\n'
        self.send_cmd(self.client_socket, cmd_list)
        response = data_socket.recv(8192).decode()
        self.pteDownload.setPlainText(response)     # Prints the files in the server

        # Closes the data socket per FTP standards
        data_socket.close()

        # This code assigns the client directory to the TreeView component
        directory = os.getcwd()
        self.model.setRootPath(str(directory))
        self.treeViewUp.setModel(self.model)
        self.treeViewUp.setRootIndex(self.model.index(str(directory)))
        self.components_show()      # Shows the user the other components they have access to once they log in

    # Function to change the directory of the server
    def directory_change(self):
        cmd_cwd = 'CWD ' + self.edtDirectory.text() + '\r\n'
        self.send_cmd(self.client_socket, cmd_cwd)

    # Function to go up a directory in the server
    def directory_return(self):
        cmd_cdup = 'CDUP\r\n'
        self.send_cmd(self.client_socket, cmd_cdup)

    # Function to create a folder on the server
    def directory_create(self):
        cmd_mkd = 'MKD ' + self.edtDirectory.text() + '\r\n'
        self.send_cmd(self.client_socket, cmd_mkd)

    # Function to delete a folder on the server
    def directory_delete(self):
        cmd_rmd = 'RMD ' + self.edtDirectory.text() + '\r\n'
        self.send_cmd(self.client_socket, cmd_rmd)

    # Function to upload a file to the server's current directory
    def upload_file(self):
        user_file_name = self.edtUpload.text()
        if user_file_name:      # Checks that edit box is filled with the name of a file
            filetype = user_file_name.split('.')[-1] # Checks the file extension

            # Depending on the extension, the appriopriate type is chosen
            if filetype == 'txt':
                cmd_type = 'TYPE A\r\n'
            else:
                cmd_type = 'TYPE I\r\n'
            self.send_cmd(self.client_socket, cmd_type)

        # Creates TCP data connection
        data_socket = self.setup_data()

        # Sends the command to store the file on the server
        cmd_stor = 'STOR ' + user_file_name + '\r\n'
        self.send_cmd(self.client_socket, cmd_stor)

        # Opens the file to be uploaded and reads it
        pic = open(user_file_name, 'rb')
        reading = pic.read(8192)

        # While it is reading, it uploads it and displays the process on the GUI. Continues until the entire file is uploaded
        while reading:
            self.pteConsole.appendPlainText('Uploading file...')
            data_socket.send(reading)
            reading = pic.read(8192)

        #  Closes the data socket
        data_socket.close()
        self.pteConsole.appendPlainText("Return message: " + self.client_socket.recv(8192).decode())

    # Function to delete a file on the server
    def delete_file(self):
        user_file_name = self.edtDownload.text()
        cmd_dele = 'DELE ' + user_file_name + '\r\n'
        self.send_cmd(self.client_socket, cmd_dele)

    # Function to download a file on the server
    def download_file(self):
        down_folder_name = "Server_Downloads"

        # Creates a folder to save the files downloaded from the server
        if not os.path.exists(down_folder_name):
            os.makedirs(down_folder_name)

        user_file_name = self.edtDownload.text()
        if user_file_name:  # If the file exists, this code runs

            # Extracts the file type and choose the appropriate command based on it
            filetype = user_file_name.split('.')[-1]
            if filetype == 'txt':
                cmd_type = 'TYPE A\r\n'
            else:
                cmd_type = 'TYPE I\r\n'
            self.send_cmd(self.client_socket, cmd_type)

            # Creates the data connection
            data_socket = self.setup_data()

            # Sends the retrieve command to the server to fetch the file
            cmd_stor = 'RETR ' + user_file_name + '\r\n'
            self.send_cmd(self.client_socket, cmd_stor)

            # Gets the name of the file and opens it in the downloads folder to save it
            file_data = data_socket.recv(8192)
            f = open(down_folder_name + "/" + user_file_name, 'wb')

            # While data is coming in through the connection, it writes it to the file and displays it on the GUI
            while file_data:
                f.write(file_data)
                self.pteConsole.appendPlainText('Downloading file...')
                file_data = data_socket.recv(8192)

            # Closes the data connection
            data_socket.close()

            self.pteConsole.appendPlainText("Return message" + self.client_socket.recv(8192).decode())
        else:
            self.pteConsole.appendPlainText("Please select a file to download.")

    # Function to call LIST and refresh the files on the server
    def refresh_directory(self):

        # Establish the data connection
        data_socket = self.setup_data()

        # Sends the LIST commands to the server
        cmd_list = 'LIST\r\n'
        self.send_cmd(self.client_socket, cmd_list)
        response = data_socket.recv(8192).decode()
        self.pteDownload.setPlainText(response)

        # Closes the data connection
        data_socket.close()

    # Function to put the name of the file into the edit box for file to upload
    def highlighted_file(self, index):
        path = self.sender().model().filePath(index)
        filename = path.split('/')[-1]
        self.edtUpload.setText(filename)

    # Function to send an FTP command to check if the connection still exists
    def check_connection(self):
        cmd_noop = 'NOOP\r\n'
        self.send_cmd(self.client_socket, cmd_noop)

    # Function to send an FTP command to terminate the TCP control connection
    def quit_client(self):
        cmd_quit = 'QUIT\r\n'
        self.send_cmd(self.client_socket, cmd_quit)
        self.components_hide()
        self.frmLogin.show()

    # Function to send the commands to the server
    def send_cmd(self, client_socket, command):
        client_socket.send(command.encode())                # Sends the commands on the socket
        return_message = client_socket.recv(8192).decode()  # Gets the reply message from the server

        # Prints the messages to the GUI
        self.pteConsole.appendPlainText("Sent command: " + command)
        self.pteConsole.appendPlainText("Return message: " + return_message)

        # The LIST command has 2 replies instead of just 1
        if command == 'LIST\r\n':
            return_message = client_socket.recv(8192).decode()
            self.pteConsole.appendPlainText("Return message: " + return_message)

        # This code updates the GUI while it is processing it so there is no waiting until the entire function is complete to print text to the GUI
        QCoreApplication.processEvents()
        return return_message

    # Function that sets up the data connection based on the users discretion of passive or active
    def setup_data(self):
        # If statement to check whether its a passive or active connection
        if self.rbnPort.isChecked():

            # Picks 2 random numbers that make up the port to use for the data connection
            port_number1 = random.randint(47, 234)
            port_number2 = random.randint(0, 255)

            # Gets the client address
            client_address = socket.gethostbyname(socket.gethostname())
            client_address = client_address.split(".")
            client_address = ','.join(client_address)

            # Creates the tuple of the address and the port number
            client_address = client_address + "," + str(port_number1) + "," + str(port_number2)
            data_port = (port_number1 * 256) + port_number2

            # Creates the data socket by listening for the connection
            host = socket.gethostbyname(socket.gethostname())
            data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            data_socket.bind((host, data_port))
            data_socket.listen(5)

            # Sends the PORT commands and tuple to the server
            cmd_port = 'PORT ' + client_address + '\r\n'
            response = self.send_cmd(self.client_socket, cmd_port)

            # Accepts the connection from the server
            data_connection, address_ip = data_socket.accept()
            return data_connection
        else:
            # Sends the PASV command to set the data connection to passive
            cmd_pasv = 'PASV\r\n'
            response = self.send_cmd(self.client_socket, cmd_pasv)

            # Splits the returned tuple into the server address and its port
            index_start = response.find('(')
            index_end = response.find(')')
            response = response[index_start + 1:index_end]
            response = response.split(",")
            data_host = '.'.join(response[0:4])
            port_response = response[-2:]
            data_port = (int(port_response[0]) * 256) + int(port_response[1])
            data_port = int(data_port)

            # Creates a TCP socket and establishes the data connection with the server
            data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            data_socket.connect((data_host, data_port))
            return data_socket


# This is the main code
app = QApplication(sys.argv)  # Creates a QApplication object based on the system settings
widget = FTP_Client()         # Creates the widget based on the class that was defined above
widget.show()                 # Displays the widget to the user
sys.exit(app.exec_())         # A condition to close the program if the exit button is pressed on the GUI