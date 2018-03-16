import socket

def commandEstablish(host, port):
    command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    command_socket.bind((host, port))
    return command_socket

def dataEstablish(host, port):
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.bind((host, port))
    return data_socket

def Main():
    print(socket.gethostname())
    host = socket.gethostbyname(socket.gethostname())
    port = 5000

    command_socket = commandEstablish(host, port)
    print("Server is running on port", port)
    command_socket.listen(1)

    c, address = command_socket.accept()
    print("Connection from: " + str(address))
    while True:
        data = c.recv(1024).decode()
        print("From connected client: " + data)
        command = data[:4]
        message = data[5:].strip()

        if command == "USER":
            if message == "group18":
                print("Hello", message)
                c.send("200 OK".encode())

        if not data:
            break
    c.close()

if __name__ == '__main__':
    Main()
