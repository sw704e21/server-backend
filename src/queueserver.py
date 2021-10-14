import socket
import queue
import sys
import pickle

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
                    conn.sendall(pickle.dumps('Error receiving data'))
                    break
                if pickle.loads(data) == 'terminate':
                    conn.sendall(pickle.dumps('Terminating server'))
                    sys.exit()
                queue.put(pickle.dumps(data))
                conn.sendall(pickle.dumps('Data put into queue'))
