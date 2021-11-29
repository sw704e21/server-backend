from processingqueue.queueclient import QueueClient
import sys


if __name__ == '__main__':
    if len(sys.argv) > 0:
        m = sys.argv[1]
        client = QueueClient()
        client.send(m)
    else:
        print('Missing message')
