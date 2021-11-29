from processingqueue.queueserver import QueueServer
from multiprocessing import Process
import time
import logging
import datetime
import os
logger = logging.getLogger("backend")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(name)s:%(levelname)s - %(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

now = datetime.datetime.now()

handler = logging.FileHandler(f"{os.getcwd()}/logs/{now.day}-{now.month}-{now.year}.log", "a")
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

logger.addHandler(handler)


# A process which starts dequeue processes periodically if queue is non-empty
def manage_processes(server, process_delay):
    while True:
        p = Process(target=start_dequeue_process, args=(server,))
        # If something is in queue, start a new process
        if server.queue.qsize() > 0:
            logger.info('Starting new dequeue process')
            p.start()
        time.sleep(process_delay)


# While something is in queue, keep processing items in queue
def start_dequeue_process(server):
    while server.queue.qsize() > 0:
        server.dequeue()
    logger.info('Now closing dequeue process')


if __name__ == '__main__':
    server = QueueServer()
    server_process = Process(target=server.run)
    thread_process = Process(target=manage_processes, args=(server, 10))
    server_process.start()
    thread_process.start()
