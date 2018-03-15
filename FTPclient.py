import socket


def passiveConnect(client_socket):

    client_socket.send('PASV\r\n'.encode())
    response = client_socket.recv(8192).decode()
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
    # print("Data Host: %s" % data_host)
    # print('Data Port: %d' % data_port)
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.connect((data_host, data_port))
    return data_socket

def main():

    host = 'ELEN4017.ug.eie.wits.ac.za'
    command_port = 21

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, command_port))
    print(client_socket.recv(8192).decode())

    client_socket.send('USER group18\r\n'.encode())
    print(client_socket.recv(8192).decode())

    client_socket.send('PASS Tee3ho3d\r\n'.encode())
    print(client_socket.recv(8192).decode())

    # Attempt to setup up passive FTP mode and connect data TCP connection
    data_socket = passiveConnect(client_socket)

    client_socket.send('LIST\r\n'.encode())
    print(client_socket.recv(8192).decode())
    print(client_socket.recv(8192).decode())
    print(data_socket.recv(8192).decode())
    # data_socket.close()

    client_socket.send('TYPE I\r\n'.encode())
    print("Results of Type B: " + client_socket.recv(8192).decode())
    data_socket = passiveConnect(client_socket)

    client_socket.send('RETR /files/ELEN1998.pdf\r\n'.encode())
    print("Results of RETR command: " + client_socket.recv(8192).decode())

    file_data = data_socket.recv(8192)
    f = open("ELEN1998.pdf", 'wb')

    while file_data:
        f.write(file_data)
        file_data = data_socket.recv(8192)

    print("Results of RETR command again: " + client_socket.recv(8192).decode())

    client_socket.close()
    data_socket.close()

if __name__ == '__main__':
    main()
