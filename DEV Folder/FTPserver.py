import socket
import os
import random



def commandEstablish(host, port):
    command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    command_socket.bind((host, port))
    return command_socket

def dataEstablish(host, port):
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.bind((host, port))
    data_socket.listen(1)
    return data_socket


def main():


    print(socket.gethostname())
    host = socket.gethostbyname(socket.gethostname())
    port = 5004

    command_socket = commandEstablish(host, port)
    print("Command:", command_socket.getsockname())
    command_socket.listen(1)

    command_connection, command_address = command_socket.accept()
    print("Command Address:", command_address)
    reply = '220 Welcome to the FTP server\r\n'.encode()
    command_connection.send(reply)
    print(reply)

    while True:
        commmandsAvailable = ['USER', 'PASS', 'PASV', 'LIST', 'PWD', 'CWD', 'TYPE', 'SYST']

        try:
            data = command_connection.recv(1024).decode()

        except socket.error as err:
            print(err)

        try:
            print("From connected client: " + data)
            command = data[:4].strip()
            message = data[4:].strip()
            print('Command received: ' + command)
            print('Message received: ' + message)

            if command in commmandsAvailable:
                if command == "USER":
                    if message == "group18":
                        print("Hello", message)
                        command_connection.send("331 Please Specify Password\r\n".encode())

                if command == "PASS":
                    if message == "dan":
                        print("Password accepted\r\n", message)
                        command_connection.send("230 Login successful\r\n".encode())
                    else:
                        command_connection.send("530 Login incorrect\r\n".encode())

                if command == "PASV":
                    print('PASV code')
                    # port_number1 = random.randint(47, 234)
                    # port_number2 = random.randint(0, 255)
                    #
                    # data_port = (port_number1*256) + port_number2
                    #
                    # data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    # result = sock.connect_ex((host, data_port))
                    # if result == 0:
                    #     print
                    #     "Port is open"
                    # else:
                    #     print
                    #     "Port is not open"
                    # data_socket.bind((host, port))
                    # data_socket.listen(1)
                    #
                    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    #

                    server_address = socket.gethostbyname(socket.gethostname())
                    server_address = server_address.split(".")
                    server_address = ','.join(server_address)
                    server_address = "(" + server_address + ",30,60)"
                    data_port = (30 * 256) + 60
                    data_socket = dataEstablish(host, data_port)
                    command_connection.send(("227 Entering passive mode" + str(server_address) + '\r\n').encode())
                    # data_socket.close()

                if command == "LIST":
                    print('List code')
                    command_connection.send("150 List is here\r\n".encode())
                    data_sock, data_address = data_socket.accept()
                    directoryList = os.listdir(os.getcwd())
                    for i in directoryList:
                        print('sending: ' + str(i))
                        data_sock.sendall((str(i) + '\r\n').encode())

                    print('Here')
                    command_connection.send('226 List is done transferring\r\n'.encode())
                    data_sock.close()

                if command == 'PWD':
                    print('pwd code')
                    pwd = os.getcwd()
                    command_connection.send(('257' + ' "' + pwd + '" ' + 'is the working directory\r\n').encode())
                    print(os.getenv('HOME'))

                if command == 'CWD':
                    path =  message
                    print("New path")
                    if os.path.exists(path):
                        os.chdir(path)
                        command_connection.send('250 Path successfully changed\r\n'.encode())
                    else:
                        command_connection.send('550 Invalid File path\r\n'.encode())

                if command == 'TYPE':
                    print('TYPE code')
                    if message == 'A':
                        command_connection.send('200 ascii mode enabled\r\n'.encode())
                    elif message == 'I':
                        command_connection.send('200 binary mode has been set\r\n'.encode())

                if command == 'SYST':
                    print('SYS code')
                    command_connection.send("215 MAC \r\n".encode())

            elif command not in commmandsAvailable:
                # print('Here')
                command_connection.send("502 Command not implemented \r\n".encode())

        except AttributeError as err:
            print(err)

    command_connection.close()

if __name__ == '__main__':
    main()
