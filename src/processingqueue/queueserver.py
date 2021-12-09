import multiprocessing
from SentimentAnalyzer import SentimentAnalyzer
import kafka
import logging
logger = logging.getLogger("backend")


class QueueServer:
    def __init__(self):
        self.host = "104.41.213.247"
        self.port = "9092"
        self.server = self.host + ":" + self.port
        self.api_version = (2, 4, 0)
        self.topic = "PostsToProcess"
        self.queue = multiprocessing.Queue(100)

    def run(self):
        adm = kafka.KafkaAdminClient(bootstrap_servers=self.server, api_version=self.api_version)
        consumer = kafka.KafkaConsumer(self.topic, bootstrap_servers=self.server, api_version=self.api_version,
                                       group_id="readposts", enable_auto_commit=True, auto_commit_interval_ms=1000)
        if self.topic not in adm.list_topics():
            logger.error(f"Topic {self.topic} not present at kafka server")
            exit(1)

        logger.info(f"Start listening to {self.topic}")
        for p in consumer:
            try:
                logger.info("Received data")
                data = p.value
                self.queue.put(data.decode('utf-8'), block=True, timeout=None)
            except Exception as e:
                logger.error(e)

    def dequeue(self):
        # Takes item from queue and hands it to sentiments analyzer, called by processes from main
        data = self.queue.get()
        logger.debug(f'Now processing {data}')
        analyzer = SentimentAnalyzer(data)
        analyzer.main_logic()
