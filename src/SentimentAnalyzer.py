from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import requests


class SentimentAnalyzer:

    def __init__(self, data, queue, url=""):
        self.data = data
        self.queue = queue
        self.url = url

    def analyze_posts(self, headline, post_text):
        sia = SIA()

        # Extracter headline
        headline_score = sia.polarity_scores(headline)
        headline_score['headline'] = headline

        # Extracter post text
        post_text_score = sia.polarity_scores(post_text)
        post_text_score['post text'] = post_text

        return headline_score, post_text_score

    def send_data(self, result):
        # Sender result til databasen
        requests.post(self.url + "/sentiment", result)

    def main_logic(self):
        while(self.queue.empty != True):
            # Gets element from queue
            data = self.queue.dequeue()

            # Opens the json object
            data.loads()

            # Extracts the headline and post text.
            headline = data['title']
            post_text = data['selftext']

            # Analyzes a post, and saves the result in a result variable
            result = self.analyze_posts(headline, post_text)

            # Returns True / False?
            self.send_data(result)
