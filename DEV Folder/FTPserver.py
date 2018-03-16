import socket


def commandEstablish(host, port):
    command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    command_socket.bind((host, port))
    return command_socket

def dataEstablish(host, port):
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.bind((host, port))
    data_socket.listen(1)
    return data_socket

def Main():
    print(socket.gethostname())
    host = socket.gethostbyname(socket.gethostname())
    port = 5000

    command_socket = commandEstablish(host, port)
    print("Command:",command_socket.getsockname())
    command_socket.listen(1)

    command_connection, command_address = command_socket.accept()
    print("Command Address:",command_address)

    while True:

        data = command_connection.recv(1024).decode()
        print("From connected client: " + data)
        command = data[:4]
        message = data[5:].strip()
        '''
        if command == "USER":
            if message == "group18":
                print("Hello", message)
                command_connection.send("331 Please Specify Password".encode())

        if command == "PASS":
            if message == "Tee3ho3d":
                print("Password accepted", message)
                command_connection.send("230 Login successful".encode())
            else:
                command_connection.send("530 Login incorrect".encode())
        '''
        if command == "PASV":
            server_address = socket.gethostbyname(socket.gethostname())
            server_address = server_address.split(".")
            server_address = ','.join(server_address)
            server_address = "("+ server_address + ",30,60)"
            command_connection.send(server_address.encode())

            data_socket = dataEstablish("127.0.1.1",7740)

        if command == "LIST":
            command_connection.send("150 Listing Directory".encode())
            command_connection.send("200 OK".encode())
            data_connection, address = data_socket.accept()
            data_connection.send("This would be the directory".encode())

        if not command:
            break
    command_connection.close()

if __name__ == '__main__':
    Main()
