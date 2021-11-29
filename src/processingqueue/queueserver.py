import socket
import sys
import pickle
import time
import multiprocessing
from SentimentAnalyzer import SentimentAnalyzer
import logging
logger = logging.getLogger("backend")


class QueueServer:
    def __init__(self, host='0.0.0.0', port=65432):
        self.host = host
        self.port = port
        self.queue = multiprocessing.Queue()

    def _recv_timeout(self, the_socket, timeout=2):
        # make socket non blocking
        the_socket.setblocking(0)

        # total data partwise in an array
        total_data = []
        data = ''

        # beginning time
        begin = time.time()
        while 1:
            # if you got some data, then break after timeout
            if total_data and time.time() - begin > timeout:
                break

            # if you got no data at all, wait a little longer, twice the timeout
            elif time.time() - begin > timeout * 2:
                break

            # recv something
            try:
                data = the_socket.recv(1024 * 8)
                if data:
                    total_data.append(data)
                    # change the beginning time for measurement
                    begin = time.time()
                else:
                    # sleep for sometime to indicate a gap
                    time.sleep(0.1)
            except socket.error:
                # Catch non-blocking socket exception as part of timeout functionality
                pass

        # join all parts to make final bytestring
        return b''.join(total_data)

    def run(self):
        logger.info(f'QueueServer now listening on {self.host}:{self.port}')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))

            while True:
                s.listen()
                conn, addr = s.accept()
                with conn:
                    logger.debug(f'Connected by {addr}')
                    data = self._recv_timeout(conn)
                    logger.debug(f"Received {len(data)}")
                    if not data:
                        conn.sendall(pickle.dumps('Error receiving data'))
                        logger.error("Error receiving data")
                        break
                    if pickle.loads(bytes(data)) == 'terminate':
                        conn.sendall(pickle.dumps('Terminating server'))
                        logger.debug("Terminating server")
                        sys.exit()
                    self.queue.put(pickle.loads(data))
                    conn.sendall(pickle.dumps('Data put into queue'))

    def dequeue(self):
        # Takes item from queue and hands it to sentiments analyzer, called by processes from main
        data = self.queue.get()
        logger.debug(f'Now processing {data}')
        analyzer = SentimentAnalyzer(data)
        analyzer.main_logic()
