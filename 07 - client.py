import sys
import socket
"""
2 points.

Create an application with CMD parameters `server` and `port`.
1) Connect to the TCP server                                                    yup
2) Read lines from the input (terminal).                                        yup
    - when the user enters "end", close the socket and exit the program         yup
    - otherwise send the user's input to the server and print the response prepended by "Result: "
3) If the server disconnects, print "Server disconnected" and exit the program  yup

Example:
    $ python3 client.py 127.0.0.1 5555
    5+5
    Result: 10
    2 * 13
    Result: 26
    asd
    Result: Invalid input
"""
if __name__ == "__main__":
    BUFFER_SIZE = 512
    TCP_IP = '127.0.0.1'  # '0.tcp.ngrok.io'
    TCP_PORT = 5555  # 17273
    server_address = (TCP_IP, TCP_PORT)

    if len(sys.argv) < 3:
        print('Usage: python3 client.py <{}> <{}>'.format(server_address[0], server_address[1]))
        exit(1)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((TCP_IP, TCP_PORT))
    print('Connected to server: {}:{}'.format(server_address[0], server_address[1]))
    msg = ''

    while True:
        msg = input()
        if msg == 'end':
            break
        msg += '\n'
        client.sendall(msg.encode())
        data = client.recv(BUFFER_SIZE).decode()

        if len(data) == 0:
            print('Server disconnected')
            client.close()
            exit(1)
        data = data.strip('\n')
        print('Result: {}'.format(data))

    client.close()
    exit(0)
