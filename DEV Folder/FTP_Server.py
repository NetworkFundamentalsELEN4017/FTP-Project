import socket
import threading
import os
import random


class FTPServer (threading.Thread):
    def __init__(self, connection_socket, address_ip):
        threading.Thread.__init__(self)
        self.command_connection = connection_socket
        self.address_ip = address_ip
        self.data_connection = None
        self.type = None
        self.isConnectionTerminated = False

    def run(self):
        print("Connection from: ", str(self.address_ip))
        self.command_connection.send('220 Welcome to the FTP server\r\n'.encode())

        while True:
            commands_available = ['USER', 'PASS', 'PASV', 'LIST', 'PWD', 'CWD', 'TYPE', 'SYST', 'RETR', 'STOR', 'NOOP',
                                  'QUIT']

            if self.isConnectionTerminated:
                break

            print('Out the loop')

            client_message = self.command_connection.recv(1024).decode()
            print("From connected client: " + client_message)
            command = client_message[:4].strip()
            argument = client_message[4:].strip()

            if command in commands_available:
                if command == "USER":
                    if argument == "group18":
                        print("Hello", argument)
                        self.command_connection.send("331 Please Specify Password\r\n".encode())

                if command == "PASS":
                    if argument == "dan":
                        print("Password accepted\r\n")
                        self.command_connection.send("230 Login successful\r\n".encode())
                    else:
                        self.command_connection.send("530 Login incorrect\r\n".encode())

                if command == "PASV":
                    print('PASV code')
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
                    data_connection = self.data_establish(host, data_port)
                    self.command_connection.send(("227 Entering passive mode" + str(server_address) + '\r\n').encode())
                    # data_socket.close()

                if command == "LIST":
                    print('List code')
                    self.command_connection.send("150 List is here\r\n".encode())
                    data_sock, data_address = data_connection.accept()
                    directory_list = os.listdir(os.getcwd())
                    for item in directory_list:
                        print('sending: ' + str(item))
                        data_sock.sendall((str(item) + '\r\n').encode())

                    self.command_connection.send('226 List is done transferring\r\n'.encode())
                    data_sock.close()
                    data_connection.close()

                if command == 'PWD':
                    print('pwd code')
                    pwd = os.getcwd()
                    self.command_connection.send(('257' + ' "' + pwd + '" ' + 'is the working directory\r\n').encode())
                    print(os.getenv('HOME'))

                if command == 'CWD':
                    # issue with going down the directory, going up works out okay
                    path = argument
                    print("New path")
                    if os.path.exists(path):
                        os.chdir(path)
                        self.command_connection.send('250 Path successfully changed\r\n'.encode())
                    else:
                        self.command_connection.send('550 Invalid File path\r\n'.encode())

                if command == 'TYPE':
                    print('TYPE code')
                    if argument == 'A':
                        self.command_connection.send('200 ascii mode enabled\r\n'.encode())
                        self.type = 'A'
                    elif argument == 'I':
                        self.command_connection.send('200 binary mode has been set\r\n'.encode())
                        self.type = 'I'

                if command == 'SYST':
                    print('SYS code')
                    self.command_connection.send("215 MAC \r\n".encode())

                if command == 'RETR':
                    self.command_connection.send('150 File status okay; about to open data connection.\r\n'.encode())
                    data_sock, data_address = data_connection.accept()
                    filename = argument
                    if self.type == 'A':
                        file = open(filename, 'r')
                        reading = file.read(8192)

                        while reading:
                            print('reading file')
                            data_sock.send((reading + '\r\n').encode())
                            reading = file.read(8192)

                        file.close()
                        data_sock.close()
                        data_connection.close()
                        self.command_connection.send('226 file transfer completed \r\n'.encode())
                        # should I close the data_connection

                    elif self.type == 'I':
                        file = open(filename, 'rb')
                        reading = file.read(8192)

                        while reading:
                            print('reading file')
                            data_sock.send(reading)
                            reading = file.read(8192)

                        file.close()
                        data_sock.close()
                        data_connection.close()
                        self.command_connection.send('226 file transfer completed \r\n'.encode())
                        # should I close the data_connection

                if command == 'STOR':
                    self.command_connection.send('150 File status okay; about to open data connection.\r\n'.encode())
                    data_sock, data_address = data_connection.accept()
                    filename = argument
                    if self.type == 'A':
                        file = open(filename, 'w')
                        file_data = data_sock.recv(8192).decode()

                        while file_data:
                            print('writing file')
                            file.write(file_data)
                            file_data = data_sock.recv(8192).decode()

                        file.close()
                        data_sock.close()
                        data_connection.close()
                        self.command_connection.send('226 file transfer completed \r\n'.encode())
                        # should I close the data_connection

                    elif self.type == 'I':
                        file = open(filename, 'wb')
                        file_data = data_sock.recv(8192)

                        while file_data:
                            print('writing file')
                            file.write(file_data)
                            file_data = data_sock.recv(8192)

                        file.close()
                        data_sock.close()
                        data_connection.close()

                        self.command_connection.send('226 file transfer completed \r\n'.encode())
                        # should I close the data_connection

                        file.close()
                        data_sock.close()

                if command == 'NOOP':
                    self.command_connection.send('200 NOOP OK \r\n'.encode())

                if command == 'QUIT':
                    self.command_connection.send('221 Goodbye\r\n'.encode())
                    self.command_connection.close()
                    self.isConnectionTerminated = True

            elif command not in commands_available:
                self.command_connection.send("502 Command not implemented \r\n".encode())

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