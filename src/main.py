from processingqueue.queueserver import QueueServer
from multiprocessing import Process, Manager, Value, cpu_count
from calculate_scores import ScoreCalculator
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

manager = Manager()
dequeue_count = Value('i', 0, lock=True)

# It does not make sense to make more dequeue processes than there are cpu cores.
max_process_count = cpu_count()


# A process which starts dequeue processes periodically if queue is non-empty
def manage_processes(server, process_delay):
    while True:

        # If something is in queue, start a new process
        if server.queue.qsize() > 0 and dequeue_count.value < max_process_count:
            p = Process(target=start_dequeue_process, args=(server,))
            logger.info('Starting new dequeue process')
            p.start()
            with dequeue_count.get_lock():
                dequeue_count.value += 1
        time.sleep(process_delay)


# While something is in queue, keep processing items in queue
def start_dequeue_process(server):
    try:
        while server.queue.qsize() > 0:
            server.dequeue()
        logger.info('Now closing dequeue process')
    except Exception as e:
        logger.error(e.__str__())
    finally:
        with dequeue_count.get_lock():
            dequeue_count.value -= 1


if __name__ == '__main__':
    server = QueueServer(max_process_count * 4)
    score_calc = ScoreCalculator()
    server_process = Process(target=server.run)
    thread_process = Process(target=manage_processes, args=(server, 10))
    score_calc_process = Process(target=score_calc.score_schedule)
    server_process.start()
    thread_process.start()
    score_calc_process.start()
