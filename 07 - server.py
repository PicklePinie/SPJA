import sys
import socket
import threading
def cyklus_na_radku_19(client, client_address):
    que_raw = ''
    que = ''  # otazka
    ans = ''  # odpoved
    while True:
        try:
            #que_raw = client.recv(BUFFER_SIZE)
            if '\n' in que_raw:
                que = que_raw[:que_raw.index('\n')]
                que_raw = que_raw[que_raw.index('\n') + 1:]
                # print("Usage: python3 {} <{}>".format(sys.argv[0],sys.argv[1]))
                print('Question: {} from {}:{}'.format(que, client_address[0], client_address[1]))
                try:
                    if '+' in que:
                        que = que.split('+')
                        ans = int(que[0]) + int(que[1])
                    if '-' in que:
                        que = que.split('-')
                        ans = int(que[0]) - int(que[1])
                    if '*' in que:
                        que = que.split('*')
                        ans = int(que[0]) * int(que[1])
                    if '/' in que:
                        que = que.split('/')
                        ans = int(que[0]) / int(que[1])
                    if '^' in que:
                        que = que.split('^')
                        ans = int(que[0]) ** int(que[1])
                    int(que[0])  # zabira na osetreni int vstupu o.O
                    ans = str(ans)
                    ans += '\n'
                    client.sendall(ans.encode())
                    print('Answer: {}'.format(ans))
                except ValueError:
                    ans = "Invalid input"
                    client.sendall(ans.encode())
            else:
                que_raw += client.recv(BUFFER_SIZE).decode()
                if len(que_raw) == 0:
                    print('Exited connection from: {}:{} (client is away)'.format(client_address[0],client_address[1]))
                    client.close()
                    break
        except:
            print('Exited connection from: {}:{} (something gone wrong in thread function)'.format(client_address[0], client_address[1]))#sys._getframe().f_code.co_name
            client.close()


if __name__ == "__main__":
    try:
        #if len(sys.argv) < 2:
        #    print("Usage: python3 server.py <port>")
        #    exit(1)

        TCP_IP = '127.0.0.1'  # sys.argv[0]
        TCP_PORT = 5555  # sys.argv[1]
        BUFFER_SIZE = 512
        server_address = (TCP_IP, TCP_PORT)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # vytvorim TCP/IP socket
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # o tomhle radku se nemluvi - reuse address
        print('Connecting to %s port %s' % server_address)
        sock.bind(server_address)  # assign to address
        sock.listen()  # start listening
        while True:
            client, client_address = sock.accept()  # accept client
            print('Received connection from: {}:{}'.format(client_address[0], client_address[1]))
            thr = threading.Thread(target=cyklus_na_radku_19, args=(client, client_address))
            thr.start()

    except KeyboardInterrupt:
        print("Server exiting")
        exit(0)
