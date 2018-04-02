import socket
import threading
import os
import random
import platform


class FTPServer (threading.Thread):
    def __init__(self, connection_socket, address_ip):
        threading.Thread.__init__(self)
        self.command_connection = connection_socket
        self.data_connection = None
        self.address_ip = address_ip
        self.data_connection = None
        self.type = None
        self.isConnectionTerminated = False
        self.isActiveMode = None
        self.cwd = os.getcwd()
        self.user = ' '

    def run(self):
        print("Connection from: ", str(self.address_ip))
        self.command_connection.send('220 Welcome to the FTP server\r\n'.encode())

        while True:
            commands_available = ['USER', 'PASS', 'PASV', 'LIST', 'PWD', 'CWD', 'TYPE', 'SYST', 'RETR', 'STOR', 'NOOP',
                                  'QUIT', 'PORT', 'DELE', 'MKD', 'RMD', 'CDUP']

            if self.isConnectionTerminated:
                break

            client_message = self.command_connection.recv(1024).decode()
            print("From connected client " + self.user + ": " + client_message)
            command = client_message[:4].strip()
            argument = client_message[4:].strip()

            if command in commands_available:

                ftp_command = getattr(self, command)

                if argument == '':
                    ftp_command()
                else:
                    ftp_command(argument)

            elif command not in commands_available:
                self.command_connection.send("502 Command not implemented \r\n".encode())

    def USER(self, argument):
        if argument == "group18" or argument == "group19":
            self.user = argument
            reply = "331 Please Specify Password\r\n"
            print('Response sent to connected client ' + self.user + ': ' + reply)
            self.command_connection.send(reply.encode())
        else:
            reply = "530 Login incorrect\r\n"
            print('Response sent to connected client ' + self.user + ': ' + reply)
            self.command_connection.send(reply.encode())
            self.command_connection.close()

    def PASS(self, argument):
        if (self.user == "group18" and argument == "dan") or (self.user == "group19" and argument == "mat"):
            reply = "230 Login successful\r\n"
            print('Response sent to connected client ' + self.user + ': ' + reply)
            self.command_connection.send(reply.encode())
        else:
            reply = "530 Login incorrect\r\n"
            print('Response sent to connected client ' + self.user + ': ' + reply)
            self.command_connection.send(reply.encode())
            self.command_connection.close()

    def PASV(self):
        self.isActiveMode = False
        port_number1 = random.randint(47, 234)
        port_number2 = random.randint(0, 255)
        # port_number1 = 60
        # port_number2 = 30
        server_address = socket.gethostbyname(socket.gethostname())
        server_address = server_address.split(".")
        server_address = ','.join(server_address)
        server_address = "(" + server_address + "," + str(port_number1) + "," + str(port_number2) + ")"
        data_port = (port_number1 * 256) + port_number2
        host = socket.gethostbyname(socket.gethostname())
        try:
            self.data_connection = self.data_establish(host, data_port)
            reply = "227 Entering passive mode" + str(server_address) + '\r\n'
            print('Response sent to connected client ' + self.user + ': ' + reply)
            self.command_connection.send(reply.encode())
        except socket.error:
            reply = "425 Cannot open Data connection \r\n"
            print('Response sent to connected client ' + self.user + ': ' + reply)
            self.command_connection.send(reply.encode())

    def PORT(self, argument):
        # print('PORT function has been called')
        self.isActiveMode = True
        argument = argument.split(',')
        data_host = '.'.join(argument[0:4])
        port_number = argument[-2:]
        data_port = (int(port_number[0]) * 256) + int(port_number[1])
        data_port = int(data_port)
        # print("Data Host: %s" % data_host)
        # print('Data Port: %d' % data_port)
        self.data_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.data_connection.connect((data_host, data_port))
            reply = "225 Entering Active mode \r\n"
            print('Response sent to connected client ' + self.user + ': ' + reply)
            self.command_connection.send(reply.encode())
        except socket.error:
            reply = "425 Cannot open Data connection \r\n"
            print('Response sent to connected client ' + self.user + ': ' + reply)
            self.command_connection.send(reply.encode())

    def LIST(self):
        reply = "150 File status okay; about to open data connection.\r\n"
        print('Response sent to connected client ' + self.user + ': ' + reply)
        self.command_connection.send(reply.encode())

        if not self.isActiveMode:
            data_sock, data_address = self.data_connection.accept()

        directory_list = os.listdir(self.cwd)
        for item in directory_list:
            # Uncomment to see what list contents are being sent
            # print('sending: ' + str(item))
            if not self.isActiveMode:
                data_sock.sendall((str(item) + '\r\n').encode())
            else:
                self.data_connection.sendall((str(item) + '\r\n').encode())

        reply = '226 Closing data connection. Requested transfer action successful\r\n'
        print('Response sent to connected client ' + self.user + ': ' + reply)
        self.command_connection.send(reply.encode())

        if not self.isActiveMode:
            data_sock.close()
        self.data_connection.close()

    def PWD(self):
        reply = '257' + ' "' + self.cwd + '" ' + 'is the working directory\r\n'
        print('Response sent to connected client ' + self.user + ': ' + reply)
        self.command_connection.send(reply.encode())

    def CWD(self, argument):
        path = argument
        if os.path.exists(path):
            self.cwd = path
            reply = '250 Requested file action okay, completed.\r\n'
            print('Response sent to connected client ' + self.user + ': ' + reply)
            self.command_connection.send(reply.encode())
        else:
            reply = '550 Requested action not taken. File/Directory unavailable\r\n'
            print('Response sent to connected client ' + self.user + ': ' + reply)
            self.command_connection.send(reply.encode())

    def TYPE(self, argument):
            if argument == 'A':
                reply = '200 ASCII mode enabled\r\n'
                print('Response sent to connected client ' + self.user + ': ' + reply)
                self.command_connection.send(reply.encode())
                self.type = 'A'
            elif argument == 'I':
                reply = '200 binary mode enabled\r\n'
                print('Response sent to connected client ' + self.user + ': ' + reply)
                self.command_connection.send(reply.encode())
                self.type = 'I'
            else:
                reply = '501 Syntax error in parameters or arguments\r\n'
                print('Response sent to connected client ' + self.user + ': ' + reply)
                self.command_connection.send(reply.encode())

    def SYST(self):
        reply = "215 " + platform.system() + "\r\n"
        print('Response sent to connected client ' + self.user + ': ' + reply)
        self.command_connection.send(reply.encode())

    def RETR(self, argument):
        reply = '150 File status okay; about to open data connection.\r\n'
        print('Response sent to connected client ' + self.user + ': ' + reply)
        self.command_connection.send(reply.encode())
        if not self.isActiveMode:
            data_sock, data_address = self.data_connection.accept()
        filename = argument
        if self.type == 'A':
            file = open(filename, 'r')
            reading = file.read(8192)

            while reading:
                print('reading file')
                if not self.isActiveMode:
                    data_sock.send((reading + '\r\n').encode())
                else:
                    self.data_connection.send((reading + '\r\n').encode())
                reading = file.read(8192)

            file.close()
            if not self.isActiveMode:
                data_sock.close()
            self.data_connection.close()
            reply = '226 Closing data connection. Requested transfer action successful \r\n'
            print('Response sent to connected client ' + self.user + ': ' + reply)
            self.command_connection.send(reply.encode())
            # should I close the data_connection

        elif self.type == 'I':
            file = open(filename, 'rb')
            reading = file.read(8192)

            while reading:
                print('reading file')
                if not self.isActiveMode:
                    data_sock.send(reading)
                else:
                    self.data_connection.send(reading)

                reading = file.read(8192)

            file.close()
            if not self.isActiveMode:
                data_sock.close()
            self.data_connection.close()
            reply = '226 Closing data connection. Requested transfer action successful \r\n'
            print('Response sent to connected client ' + self.user + ': ' + reply)
            self.command_connection.send(reply.encode())
            # should I close the data_connection

    def STOR(self, argument):
        reply = '150 File status okay; about to open data connection.\r\n'
        print('Response sent to connected client ' + self.user + ': ' + reply)
        self.command_connection.send(reply.encode())

        if not self.isActiveMode:
            data_sock, data_address = self.data_connection.accept()
        filename = argument
        if self.type == 'A':
            file = open(filename, 'w')
            if not self.isActiveMode:
                file_data = data_sock.recv(8192).decode()
            else:
                file_data = self.data_connection.recv(8192).decode()

            while file_data:
                print('writing file')
                file.write(file_data)
                if not self.isActiveMode:
                    file_data = data_sock.recv(8192).decode()
                else:
                    file_data = self.data_connection.recv(8192).decode()

            file.close()
            if not self.isActiveMode:
                data_sock.close()
            self.data_connection.close()
            reply = '226 Closing data connection. Requested transfer action successful \r\n'
            print('Response sent to connected client ' + self.user + ': ' + reply)
            self.command_connection.send(reply.encode())
            # should I close the data_connection

        elif self.type == 'I':
            file = open(filename, 'wb')
            if not self.isActiveMode:
                file_data = data_sock.recv(8192)
            else:
                file_data = self.data_connection.recv(8192)

            while file_data:
                print('writing file')
                file.write(file_data)
                if not self.isActiveMode:
                    file_data = data_sock.recv(8192)
                else:
                    file_data = self.data_connection.recv(8192)

            file.close()
            if not self.isActiveMode:
                data_sock.close()
            self.data_connection.close()
            reply = '226 Closing data connection. Requested transfer action successful \r\n'
            print('Response sent to connected client ' + self.user + ': ' + reply)
            self.command_connection.send(reply.encode())
            file.close()

    def NOOP(self):
        reply = '200 NOOP OK \r\n'
        print('Response sent to connected client ' + self.user + ': ' + reply)
        self.command_connection.send(reply.encode())

    def DELE(self, argument):
        file_name = argument
        file_path = self.cwd + '/' + str(file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            reply = '250 Requested file action okay, completed.\r\n'
            print('Response sent to connected client ' + self.user + ': ' + reply)
            self.command_connection.send(reply.encode())
        else:
            reply = '550 Could not execute delete, file not found\r\n'
            print('Response sent to connected client ' + self.user + ': ' + reply)
            self.command_connection.send(reply.encode())


    def MKD(self, argument):
        directory_name = argument
        directory_path = self.cwd + '/' + str(directory_name)
        if os.path.exists(directory_path):
            reply = '550 Requested action not taken. File/Directory unavailable\r\n'
            print('Response sent to connected client ' + self.user + ': ' + reply)
            self.command_connection.send(reply.encode())
        else:
            os.makedirs(directory_path)
            reply = '257 Folder has been successfully created\r\n'
            print('Response sent to connected client ' + self.user + ': ' + reply)
            self.command_connection.send(reply.encode())

    def RMD(self, argument):
        directory_name = argument
        directory_path = self.cwd + '/' + str(directory_name)
        if os.path.exists(directory_name):
            os.rmdir(directory_path)
            reply = '250 Requested file action okay, completed. \r\n'
            print('Response sent to connected client ' + self.user + ': ' + reply)
            print(section)
            self.command_connection.send(reply.encode())
        else:
            reply = '550 Requested action not taken. File/Directory unavailable\r\n'
            print('Response sent to connected client ' + self.user + ': ' + reply)
            print(section)
            self.command_connection.send(reply.encode())

    def CDUP(self):
        parent_directory = self.cwd.split('/')
        parent_directory = parent_directory[:-1]
        parent_directory = '/'.join(parent_directory)

        if os.path.exists(parent_directory):
            self.cwd = parent_directory
            reply = '200 Changed directory successfully \r\n'
            print('Response sent to connected client ' + self.user + ': ' + reply)
            self.command_connection.send(reply.encode())
        else:
            reply = '550 Requested action not taken. File/Directory unavailable\r\n'
            print('Response sent to connected client ' + self.user + ': ' + reply)
            self.command_connection.send(reply.encode())

    def QUIT(self):
            reply = '221 Goodbye\r\n'
            print('Response sent to connected client ' + self.user + ': ' + reply)
            self.command_connection.send(reply.encode())
            self.command_connection.close()
            self.isConnectionTerminated = True

    def data_establish(self, host, port):
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_socket.bind((host, port))
        data_socket.listen(5)
        return data_socket


def main():
    # Local Machine IP
    host = socket.gethostbyname(socket.gethostname())
    port = 5001

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    print('FTP Server initialized at ' + host)
    print("Awaiting a connection from a client")

    while True:
        server_socket.listen(1)
        connection_socket, address_ip = server_socket.accept()
        thread = FTPServer(connection_socket, address_ip)
        thread.start()

if __name__ == '__main__':
    main()