from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import requests
import json
import nltk


class SentimentAnalyzer:

    def __init__(self, data):
        self.data = data
        self.url = 'http://cryptoserver.northeurope.cloudapp.azure.com'
        nltk.download('vader_lexicon')

    def analyze_posts(self, text):
        sia = SIA()

        score = sia.polarity_scores(text)

        return score['compound']

    def send_data(self, result):
        # Sender result til databasen
        print(f'Now sending {result}')
        requests.post(self.url + "/coins", result)

    def main_logic(self):
        # Opens the json object
        data = json.loads(self.data)

        # Extracts the headline and post text.
        headline = data['title']
        post_text = data['selftext']
        full_text = headline + post_text

        # Analyzes a post, and saves the result in a result variable
        score = self.analyze_posts(full_text)

        result = {
            'timestamp': data['created_utc'],
            'coin': data['source'],
            'sentiment': score,
            'interaction': int(data['score']) + int(data['num_comments']),
            'url': data['permalink']
        }

        self.send_data(result)
