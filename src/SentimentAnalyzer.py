import ast
import pickle

from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import requests
import json


class SentimentAnalyzer:

    def __init__(self, data):
        self.data = data
        self.url = 'http://cryptoserver.northeurope.cloudapp.azure.com'
        self.initialize_pickledic()

    def initialize_pickledic(self):
        dic = {}

        a_file = open("worddictionary.pkl", "wb")
        pickle.dump(dic, a_file)
        a_file.close()

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
        print(f'Noe sending {result}')
        requests.post(self.url + "/coins", result)

    def main_logic(self):
        # Opens the json object
        data = json.loads(self.data)

        # Extracts the headline and post text.
        headline = data['title']
        post_text = data['selftext']

        # Analyzes a post, and saves the result in a result variable
        score = self.analyze_posts(headline, post_text)

        # Extracts the timestamp and url.
        timestamp = data['created_utc']
        url = data['url']

        #Updates the Word Dictionary
        self.manage_dictionary(url, timestamp, post_text)

        result = {
            'timestamp': data['created_utc'],
            'coin': data['source'],
            'sentiment': score,
            'interaction': int(data['score']) + int(data['num_comments']),
            'url': data['url']
        }

        self.send_data(result)


    # { "word1": {"total": 5, "occurences": [(2,"url1", 12345678), (3, "url2", 23456789)]}, "word2": {"total": 3, "occurences": [(3, "url3". 12345678), (4, "url4", 12345679)]} }
    def manage_dictionary(self, url, timestamp, post_text):
        # Fixing sentiment:
        dic = {}
        post_text = post_text.split()
        for word in post_text:
            if word in dic:
                dic[word] = dic[word] + 1
            else:
                dic[word] = 1

        # Load dictionary


        a_file = open("worddictionary.pkl", "rb")
        dictionary = pickle.load(a_file)
        a_file.close()

        # For hvert word i sorted sentiment:
        for word in dic:
            # Check om det word eksisterer i dictionary
            if word in dictionary:
                # Hvis det gør, adder total amount, sæt url og timestamp ind.
                temp = dictionary[word]
                total = temp['total'] + dic[word]
                occurences = list(temp['occurences'])
                occurences.append([dic[word], url, timestamp])
                temp['total'] = total
                temp['occurences'] = occurences
                dictionary[word] = temp
            else:
                # Hvis ikke, lav en ny entry i dictionary, sæt total amount, url og timestamp.
                temp = {}
                temp['total'] = dic[word]
                temp['occurences'] = (dic[word], url, timestamp)
                dictionary[word] = temp

        print(dictionary)
        a_file = open("worddictionary.pkl", "wb")
        pickle.dump(dictionary, a_file)
        a_file.close()

        #Tilføj til RemoveList dictionary: url, amount of timestamp

    def test(self):
        testpost = {'title': 'Doge is speaking Tesla',
                    'full_link': 'https://www.reddit.com/r/dogecoin/comments/qv7ia3/doge_is_speaking_tesla/',
                    'score': 1, 'created_utc': 1637068420, 'selftext': '', 'num_comments': 0}
        testpost2 = {'title': 'I have 1.14 running',
                     'full_link': 'https://www.reddit.com/r/dogecoin/comments/qv7jdq/i_have_114_running/', 'score': 1,
                     'created_utc': 1637068527,
                     'selftext': 'What is the benefit to me.  It has been running for about a month with good in and out connections.',
                     'num_comments': 0}
        testpost3 = {'title': 'No change to the extended forecast, .44 next stop',
                     'full_link': 'https://www.reddit.com/r/dogecoin/comments/qv7kzb/no_change_to_the_extended_forecast_44_next_stop/',
                     'score': 1, 'created_utc': 1637068678, 'selftext': '', 'num_comments': 0}
        testpost4 = {
            'title': "When you post that you just 100Xed your crypto investment and all of a sudden every girl you've never met be like..",
            'full_link': 'https://www.reddit.com/r/dogecoin/comments/qv7n6o/when_you_post_that_you_just_100xed_your_crypto/',
            'score': 1, 'created_utc': 1637068881, 'selftext': '', 'num_comments': 0}
        testpost5 = {
            'title': 'This is how it ended up for people following a guy preaching about rockets, spaceships and going to the moon...',
            'full_link': 'https://www.reddit.com/r/dogecoin/comments/qv7paf/this_is_how_it_ended_up_for_people_following_a/',
            'score': 1, 'created_utc': 1637069080, 'selftext': '', 'num_comments': 0}
        testpost6 = {'title': 'I had a dream last night BTC was $663,000. What would that put DOGE at?',
                     'full_link': 'https://www.reddit.com/r/dogecoin/comments/qv7r30/i_had_a_dream_last_night_btc_was_663000_what/',
                     'score': 1, 'created_utc': 1637069242, 'selftext': '', 'num_comments': 0}
        testpost7 = {'title': 'If you ever wanted to get into Doge now would be the time to buy a nice bag',
                     'full_link': 'https://www.reddit.com/r/dogecoin/comments/qv7rw8/if_you_ever_wanted_to_get_into_doge_now_would_be/',
                     'score': 1, 'created_utc': 1637069310, 'selftext': '[removed]', 'num_comments': 0}
        testpost8 = {'title': 'Is Binance short on doge, they stopped withdrawals!!!',
                     'full_link': 'https://www.reddit.com/r/dogecoin/comments/qv7rx9/is_binance_short_on_doge_they_stopped_withdrawals/',
                     'score': 1, 'created_utc': 1637069314,
                     'selftext': 'It only makes sense if you are very short to lock it down like they have and blame it on a "technical issues".',
                     'num_comments': 0}
        testpost9 = {
            'title': '🎧 NFTMusic.Stream 🎧 Incredible Tech. Live Utility. The most underrated project on BSC. 💎 Load your bags before any moment it 🎗',
            'full_link': 'https://www.reddit.com/r/dogecoin/comments/qv7wrh/nftmusicstream_incredible_tech_live_utility_the/',
            'score': 1, 'created_utc': 1637069725, 'selftext': '', 'num_comments': 1}

        post_text = testpost4['title']
        timestamp = testpost4['created_utc']
        url = testpost4['full_link']
        self.manage_dictionary(url, timestamp, post_text)

        post_text = testpost5['title']
        timestamp = testpost5['created_utc']
        url = testpost5['full_link']
        self.manage_dictionary(url, timestamp, post_text)



