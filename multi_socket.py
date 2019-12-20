import socket
PORT = 7000
HOST = '172.17.170.11'

while(True):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    s.bind((HOST,PORT))
    s.listen()
    sock_conn,addr = s.accept()

    sock_conn.sendall(bytes('helloclient','utf-8'))

    s.close()
