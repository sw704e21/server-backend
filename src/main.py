import queue
from processingqueue.queueserver import QueueServer
from multiprocessing import Process, Manager
import time

def manage_threads(server, thread_delay):
     p = Process(target=start_dequeue_thread, args=(0, server))
     while True:
          if server.queue.qsize() > 0:
               p = Process(target=start_dequeue_thread, args=(server,))
               p.start()
          time.sleep(thread_delay)

def start_dequeue_thread(server):
          server.dequeue()



if __name__ == '__main__':
    server = QueueServer()
    server_process = Process(target=server.run)
    thread_process = Process(target=manage_threads, args=(server, 1))
    server_process.start()
    thread_process.start()
