from processingqueue.queueserver import QueueServer
from multiprocessing import Process
import time


# A process which starts dequeue processes periodically if queue is non-empty
def manage_processes(server, process_delay):
    p = Process(target=start_dequeue_process, args=(server,))
    while True:
        # If something is in queue, start a new process
        if server.queue.qsize() > 0:
            print('Starting new thread')
            p.start()
        time.sleep(process_delay)


# While something is in queue, keep processing items in queue
def start_dequeue_process(server):
    while server.queue.qsize() > 0:
        server.dequeue()


if __name__ == '__main__':
    server = QueueServer()
    server_process = Process(target=server.run)
    thread_process = Process(target=manage_processes, args=(server, 10))
    server_process.start()
    thread_process.start()
