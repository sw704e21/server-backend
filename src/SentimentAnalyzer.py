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

    # Return a list of all coin names and identifiers
    def get_all_coins(self):
        coins = json.loads(requests.get(self.url + '/coins/all').content)
        coin_names = []
        for element in coins:
            coin_names.append((element['name'], element['identifier']))
        return coin_names

    def run_analysis(self, full_text, data, coins):
        
        # Analyzes a post, and saves the result in a result variable
        score = self.analyze_posts(full_text)

        result = {
            'timestamp': data['created_utc'],
            'coin': coins,
            'sentiment': score,
            'interaction': int(data['score']) + int(data['num_comments']),
            'url': data['permalink']
        }

        #self.send_data(result)

    def identify_coins(self, text):
        associated_coins = []
        all_coins = self.get_all_coins()
        for coin in all_coins:
            if coin[0].casefold() in text.casefold() or coin[1].casefold() in text.casefold():
                    associated_coins.append(coin[0])
        return associated_coins

    def main_logic(self):
        # Opens the json object
        data = json.loads(self.data)

        # Extracts the headline and post text.
        headline = data['title']
        post_text = data['selftext']
        full_text = headline + post_text
        associated_coins = self.identify_coins(full_text)
        self.run_analysis(full_text, data, associated_coins)
        