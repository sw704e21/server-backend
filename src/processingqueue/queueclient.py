#!/usr/bin/env python3

import socket
import pickle


class QueueClient:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port

    def send(self, message):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.sendall(pickle.dumps(message))
            data = s.recv(1024)
            print(pickle.loads(data))
