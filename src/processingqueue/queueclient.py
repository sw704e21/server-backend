#!/usr/bin/env python3

import socket
import pickle


class QueueClient:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.max_retries = 10

    def send(self, message):
        i = 0
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            for i in range(self.max_retries):
                try:
                    print(f'Try {i}')
                    s.connect((self.host, self.port))
                    s.sendall(pickle.dumps(message))
                    data = s.recv(1024)
                    print(pickle.loads(data))
                    break
                except TimeoutError:
                    print("Retry")
        if i == self.max_retries - 1:
            print("Failed to send after 10 retries")
            exit(1)
