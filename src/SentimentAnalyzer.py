from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import requests
import json


class SentimentAnalyzer:

    def __init__(self, data):
        self.data = data

    def analyze_posts(self, headline, post_text):
        sia = SIA()

        # Extracter headline
        headline_score = sia.polarity_scores(headline)
        headline_score['headline'] = headline

        # Extracter post text
        post_text_score = sia.polarity_scores(post_text)
        post_text_score['post text'] = post_text

        result = 0
        if headline_score['compound'] > 0 and post_text_score['compound'] > 0:
            result = 1
        elif headline_score['compound'] < 0 and post_text_score['compound'] < 0:
            result = -1

        return result

    def send_data(self, result):
        # Sender result til databasen
        requests.post(self.url + "/coin", result)

    def main_logic(self):
        # Opens the json object
        data = json.loads(self.data)

        # Extracts the headline and post text.
        headline = data['title']
        post_text = data['selftext']

        # Analyzes a post, and saves the result in a result variable
        result = self.analyze_posts(headline, post_text)

        # Analyzes a post, and saves the result in a result variable
        score = self.analyze_posts(headline, post_text)

        result = {
            'timestamp': data['created_utc'],
            'coin': 'bitcoin',  # WARNING: placeholder value
            'sentiment': score,
            'interaction': data['score'] + data['num_comments'],
            'url': data['url']
        }

        # Returns True / False?
        self.send_data(result)
