#!/usr/bin/env python3

import socket
import sys

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

if len(sys.argv) > 1:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(sys.argv[1].encode('utf_8'))
        data = s.recv(1024)
        print(data.decode('utf_8'))