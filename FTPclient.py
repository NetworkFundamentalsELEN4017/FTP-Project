import socket


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

    client_socket.send('PASV\r\n'.encode())
    resp = client_socket.recv(8192).decode()

    print("This is the response: " + resp)
    index = resp.find('(')
    endindex = resp.find(')')
    resp = resp[index+1:endindex]
    print("This is the cut content of the index: " + resp)
    resp = resp.split(",")
    print(resp)

    data_host = ''

    for i in range(0, 4):
        data_host = data_host + (resp[i]) + '.'

    data_host = data_host[:-1]
    print('Here is the data host\n')
    print(data_host)

    endResp = resp[-2:]
    print(endResp)
    data_port = (int(endResp[0]) * 256) + int(endResp[1])
    data_port = int(data_port)

    print("Data Host: %s" % data_host)
    print('Data Port: %d' % data_port)

    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.connect((data_host, data_port))

    client_socket.send('LIST\r\n'.encode())
    print("Results of 1st LIST: " + client_socket.recv(8192).decode())
    print("Result of the data socket: \n" + data_socket.recv(8192).decode())
    print("Results of 1st LIST again: " + client_socket.recv(8192).decode())

    client_socket.send('PASV\r\n'.encode())
    resp = client_socket.recv(8192).decode()
    print("This is the response: " + resp)
    index = resp.find('(')
    endindex = resp.find(')')
    resp = resp[index + 1:endindex]
    print("This is the cut content of the index: " + resp)
    resp = resp.split(",")
    print(resp)

    data_host = ''

    for i in range(0, 4):
        data_host = data_host + (resp[i]) + '.'

    data_host = data_host[:-1]
    print('Here is the data host\n')
    print(data_host)

    endResp = resp[-2:]
    print(endResp)
    data_port = (int(endResp[0]) * 256) + int(endResp[1])
    data_port = int(data_port)

    print("Data Host: %s" % data_host)
    print('Data Port: %d' % data_port)

    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.connect((data_host, data_port))

    client_socket.send('RETR 48_hour/testZilla.txt\r\n'.encode())
    print("Results of RETR: " + client_socket.recv(8192).decode())
    file_data = data_socket.recv(8192)
    print("Results of data: \n" + file_data.decode())

    with open('testZilla.txt', 'wb') as File:
        File.write(file_data)
        print("File transfer complete")
        File.close()

    client_socket.close()
    data_socket.close()

if __name__ == '__main__':
    main()
