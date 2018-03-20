import socket


def passiveConnect(command_socket):

    command_socket.send('PASV\r\n'.encode())
    response = command_socket.recv(8192).decode()
    print("This is the PASV response: " + response)
    index_start = response.find('(')
    index_end = response.find(')')
    # Removes the brackets to the string from PASV
    response = response[index_start + 1:index_end]
    # Splits the numbers into an array
    response = response.split(",")
    data_host = '.'.join(response[0:4])
    port_response = response[-2:]
    data_port = (int(port_response[0]) * 256) + int(port_response[1])
    data_port = int(data_port)
    # Uncomment to print the IP address and the port that the client is trying to connect to
    print("Data Host: %s" % data_host)
    print('Data Port: %d' % data_port)
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.connect((data_host, data_port))
    return data_socket


def main():

    host = 'ELEN4017.ug.eie.wits.ac.za'
    command_port = 21
    # server_address = socket.gethostbyname(socket.gethostname())
    # command_port = 5000

    command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    command_socket.connect((host, command_port))
    print("Command socket set")

    command_socket.send('USER group18\r\n'.encode())
    print(command_socket.recv(8192).decode())

    command_socket.send('PASS Tee3ho3d\r\n'.encode())
    print(command_socket.recv(8192).decode())

    # Attempt to setup up passive FTP mode and connect data TCP connection
    data_socket = passiveConnect(command_socket)

    print("Asking for LIST now")
    command_socket.send('LIST\r\n'.encode())
    print(command_socket.recv(8192).decode())
    print(command_socket.recv(8192).decode())
    print(data_socket.recv(8192).decode())

    # Download Binary files
    command_socket.send('TYPE I\r\n'.encode())
    print("Results of Type B: " + command_socket.recv(8192).decode())
    data_socket = passiveConnect(command_socket)

    command_socket.send('RETR /files/slav.jpg\r\n'.encode())
    print("Results of RETR command: " + command_socket.recv(8192).decode())

    file_data = data_socket.recv(8192)
    f = open("slav.jpg", 'wb')

    while file_data:
        f.write(file_data)
        file_data = data_socket.recv(8192)

    print("Results of RETR command again: " + command_socket.recv(8192).decode())

    # Upload binary files
    command_socket.send('TYPE I\r\n'.encode())
    print("Results of Type B: " + command_socket.recv(8192).decode())
    data_socket = passiveConnect(command_socket)

    command_socket.send('STOR /files/Sloth.jpg\r\n'.encode())
    print("Results of RETR command: " + command_socket.recv(8192).decode())

    pic = open('Sloth.jpg', 'rb')
    reading = pic.read(8192)

    while reading:
        print('reading file')
        data_socket.send(reading)
        reading = pic.read(8192)

    print("The file has finished sending to Server")

    pic.close()
    data_socket.close()

    Reply = command_socket.recv(4096).decode("UTF-8")
    print('Control connection reply: \n' + str(Reply))

    command_socket.send('STRU F\r\n'.encode())
    print("Results of Stru F: " + command_socket.recv(8192).decode())

    command_socket.send('STRU R\r\n'.encode())
    print("Results of Stru R: " + command_socket.recv(8192).decode())

    command_socket.send('STRU P\r\n'.encode())
    print("Results of Stru P: " + command_socket.recv(8192).decode())

    command_socket.send('MODE S\r\n'.encode())
    print("Results of Mode S: " + command_socket.recv(8192).decode())

    command_socket.send('MODE B\r\n'.encode())
    print("Results of Mode B: " + command_socket.recv(8192).decode())

    command_socket.send('MODE C\r\n'.encode())
    print("Results of Mode C: " + command_socket.recv(8192).decode())

    command_socket.send('PORT 10,30,126,164,47,56\r\n'.encode())
    print("Results of PORT: " + command_socket.recv(8192).decode())

    command_socket.send('NOOP\r\n'.encode())
    print("Results of Noop: " + command_socket.recv(8192).decode())

    command_socket.send('QUIT\r\n'.encode())
    print("Results of Quit: " + command_socket.recv(8192).decode())

    command_socket.close()
    data_socket.close()

if __name__ == '__main__':
    main()
