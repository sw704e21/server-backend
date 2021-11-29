from processingqueue.queueclient import QueueClient
import sys
import json

if __name__ == '__main__':
    if len(sys.argv) > 0:
        #m = sys.argv[1]
        m = {"title": "testtitle", "selftext": "testtext", "created_utc": 1234, "permalink": "testUrl", "source": "testcoin", "score": 1234, "num_comments": 123}
        client = QueueClient()
        client.send(json.dumps(m))
    else:
        print('Missing message')
