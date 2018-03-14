import socket


def passiveConnect(client_socket):
    client_socket.send('PASV\r\n'.encode())
    response = client_socket.recv(8192).decode()

    print("This is the PASV response: " + response)
    index_start = response.find('(')
    index_end = response.find(')')
    response = response[index_start + 1:index_end]  # Removes the brackets to the string from PASV
    response = response.split(",")                  # Splits the numbers into an array

    data_host = ''

    for i in range(0, 4):
        data_host = data_host + (response[i]) + '.'

    data_host = data_host[:-1]
    end_response = response[-2:]
    data_port = (int(end_response[0]) * 256) + int(end_response[1])
    data_port = int(data_port)

    print("Data Host: %s" % data_host)
    print('Data Port: %d' % data_port)

    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.connect((data_host, data_port))
    return(data_socket)


def main():
    host = 'ftp.uconn.edu'
    command_port = 21

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, command_port))
    print(client_socket.recv(8192).decode())

    client_socket.send('USER anonymous\r\n'.encode())
    print(client_socket.recv(8192).decode())

    client_socket.send('PASS anonymous@\r\n'.encode())
    print(client_socket.recv(8192).decode())

    data_socket = passiveConnect(client_socket)

    client_socket.send('LIST\r\n'.encode())
    print("Results of LIST command trigger: " + client_socket.recv(8192).decode())
    print("Result of the data socket: \n" + data_socket.recv(8192).decode())
    print("Results of LIST command end: " + client_socket.recv(8192).decode())

    data_socket = passiveConnect(client_socket)

    client_socket.send('RETR 48_hour/testZilla.txt\r\n'.encode())
    print("Results of RETR command: " + client_socket.recv(8192).decode())
    file_data = data_socket.recv(8192)
    print("Results of data connection: \n" + file_data.decode())

    with open('testZilla.txt', 'wb') as File:
        File.write(file_data)
        print("File transfer complete")
        File.close()

    client_socket.close()
    data_socket.close()

if __name__ == '__main__':
    main()
