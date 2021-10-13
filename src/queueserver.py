import socket
import queue
import sys

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
queue = queue.Queue()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    while True:
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    conn.sendall(b'Error recieving da')
                    break
                if data.decode('utf_8') == 'terminate':
                    sys.exit()
                queue.put(data)
                conn.sendall(b'code 100')
