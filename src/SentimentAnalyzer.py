import pickle
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import requests
import json
import datetime
import os
import logging
import re

logger = logging.getLogger("backend")


class SentimentAnalyzer:
    def __init__(self, data):
        self.data = data
        self.url = 'http://cryptoserver.northeurope.cloudapp.azure.com'

    def initialize_dictionary(self, coin):
        r = requests.get(self.url + f'/data/tfdict/{coin}')
        dic = r.json()

        a_file = open("worddictionary%s.pkl" % coin, "wb")
        pickle.dump(dic, a_file)
        a_file.close()

    def initialize_delete_dictionary(self, coin):
        dic = {}

        a_file = open("deletedictionary%s.pkl" % coin, "wb")
        pickle.dump(dic, a_file)
        a_file.close()

    def analyze_posts(self, text):
        sia = SIA()

        score = sia.polarity_scores(text)

        return score['compound']

    def send_data(self, result):
        # Sender result til databasen
        try:
            logger.info(f'Now sending {result["url"]}')
            r = requests.post(self.url + "/coins", result)
            r.raise_for_status()
            logger.debug(f'Sent with status {r.status_code}')
            if r.status_code != 201:
                logger.error(r.json())
        except Exception as e:
            logger.error(e)

    def main_logic(self):
        # Opens the json object
        data = json.loads(self.data)

        # Extracts the headline and post text.
        headline = data['title']
        post_text = data['selftext']
        full_text = headline + post_text

        # Analyzes a post, and saves the result in a result variable
        score = self.analyze_posts(full_text)

        # Extracts the timestamp and url.
        timestamp = data['created_utc']
        url = data['permalink']

        # Updates the Word Dictionary
        coins = self.extract_coin(full_text)
        if len(coins) > 0:
            for coin in coins:
                self.manage_dictionary(url, timestamp, full_text, coin)

            result = {
                'timestamp': data['created_utc'],
                'identifiers': coins,
                'sentiment': score,
                'interaction': int(data['score']) + int(data['num_comments']),
                'url': data['permalink'],
                'influence': data['karma'],
                'uuid': data['uuid'],
                'source': data['source']
            }

            self.send_data(result)

    def manage_dictionary(self, url, timestamp, post_text, coin):
        # Check hvis dokumenterne eksisterer for den givne coin
        if not os.path.exists("./worddictionary%s.pkl" % coin):
            self.initialize_dictionary(coin)

        if not os.path.exists("./deletedictionary%s.pkl" % coin):
            self.initialize_delete_dictionary(coin)

        # Fixing sentiment:
        dic = {}
        # Splitting the text into tokens, splitting them at each space symbols.
        # Removing symbols
        post_text = re.sub(r'\'', '', post_text)
        post_text = re.sub(r"\d+", "", post_text)
        cleantext = re.sub(r'[^\w]', ' ', post_text)
        no_special_characters = cleantext.split()
        # dstemmer = SnowballStemmer("english")

        # Laver et dictionary, som gemmer words og mapper det til total occurence
        for word in no_special_characters:
            # Stemming each word
            # tword = dstemmer.stem(word)
            if word in dic:
                dic[word] = dic[word] + 1
            else:
                dic[word] = 1

        # Loader dictionary med alle words
        a_file = open("worddictionary%s.pkl" % coin, "rb")
        dictionary = pickle.load(a_file)
        a_file.close()

        # For hvert word i sorted sentiment:
        for word in dic:
            # Check om det word eksisterer i dictionary
            if word in dictionary:
                # Hvis det gør, adder total amount, sæt url og timestamp ind.
                temp = dictionary[word]
                total = temp['total'] + dic[word]
                occurences = temp['occurences']
                occurences[url] = (dic[word], timestamp)
                temp['total'] = total
                temp['occurences'] = occurences
                dictionary[word] = temp
            else:
                # Hvis ikke, lav en ny entry i dictionary, sæt total amount, url og timestamp.
                temp = {}
                ocur = {}
                temp['total'] = dic[word]
                ocur[url] = (dic[word], timestamp)
                temp['occurences'] = ocur
                dictionary[word] = temp

        # Adding the post to the delete-dictionary
        self.add_to_delete_dictionary(url, timestamp, coin)

        # Opdaterer worddictionary
        logger.info("Updating dictionary")
        try:
            a_file = open("worddictionary%s.pkl" % coin, "wb")
            pickle.dump(dictionary, a_file)
            a_file.close()
            s = json.dumps(dictionary)
            print(s.encode('utf-8').__sizeof__())
            r = requests.post(self.url + "/data/tfdict/" + coin, json=dictionary)
            r.raise_for_status()
            logger.debug(f"Updated dictionary with status {r.status_code}")
        except Exception as e:
            logger.error(e.args)

    def add_to_delete_dictionary(self, url, timestamp, coin):
        # Åbner deletedictionary
        a_file = open("deletedictionary%s.pkl" % coin, "rb")
        dictionary = pickle.load(a_file)
        a_file.close()

        # Opdatere deledictionary
        dictionary[url] = timestamp

        # Gemmer deletedictionary
        a_file = open("deletedictionary%s.pkl" % coin, "wb")
        pickle.dump(dictionary, a_file)
        a_file.close()

    def maintain_dictionary(self, time, coin):
        # Loader deletedictionary
        a_file = open("deletedictionary%s.pkl" % coin, "rb")
        deldictionary = pickle.load(a_file)
        a_file.close()

        # Laver et dictionary, som indehoder de posts som skal slettes
        deletedic = {}

        #
        for url in deldictionary.copy():
            posttime = deldictionary[url]
            # Checking
            if (int(datetime.datetime.utcnow().timestamp()) - posttime > 604800):
                # If the time constraint is satisfied, the post is deleted from the deletecitionary, and added to the
                # deletedic.
                deletedic[url] = posttime
                del deldictionary[url]

        a_file = open("deletedictionary%s.pkl" % coin, "wb")
        pickle.dump(deldictionary, a_file)
        a_file.close()

        # Delete posts from dictionary
        a_file = open("worddictionary%s.pkl" % coin, "rb")
        dictionary = pickle.load(a_file)
        a_file.close()

        # For hver ord i dictionary
        for word in dictionary.copy():
            # Der checkes for hvert post, om den har en occurence i word.
            for post in deletedic:
                theword = dictionary[word]
                occurences = theword['occurences']

                # Hvis den har det, så slettes den derfra, og total opdateres
                if post in occurences:
                    test = occurences[post]
                    del occurences[post]
                    theword['total'] = theword['total'] - test[0]
                    theword['occurences'] = occurences
                    dictionary[word] = theword
            # Hvis word har en total på 0, så slettes word fra dictionary.
            theword = dictionary[word]
            if theword['total'] == 0:
                del dictionary[word]

        # Gemmer dictionary, som nu er opdatereret
        a_file = open("worddictionary%s.pkl" % coin, "wb")
        pickle.dump(dictionary, a_file)
        a_file.close()

    def extract_coin(self, text: str):
        r = requests.get(self.url + "/track/tags")
        tags = {}
        for i in r.json():
            tags[i['identifier']] = i['tags']
        result = []
        for key in tags.keys():
            for tag in tags[key]:
                if tag in text:
                    result.append(key)
        return result

    def test(self):
        testpost = {'title': '&Doge is¤ speaking $Tesla, isn\'t',
                    'full_link': 'https://www.reddit.com/r/dogecoin/comments/qv7ia3/doge_is_speaking_tesla/',
                    'score': 1, 'created_utc': 1637068420, 'selftext': '', 'num_comments': 0}
        testpost2 = {'title': 'I have 1.14 running',
                     'full_link': 'https://www.reddit.com/r/dogecoin/comments/qv7jdq/i_have_114_running/', 'score': 1,
                     'created_utc': 1637068527,
                     'selftext': 'What is the benefit to me.  It has been running for about a month with good in and '
                                 'out connections.',
                     'num_comments': 0}
        testpost3 = {'title': 'No change to the extended forecast, .44 next stop',
                     'full_link': 'https://www.reddit.com/r/dogecoin/comments/qv7kzb'
                                  '/no_change_to_the_extended_forecast_44_next_stop/',
                     'score': 1, 'created_utc': 1637068678, 'selftext': '', 'num_comments': 0}
        testpost4 = {
            'title': "When you post that you just 100Xed your crypto investment and all of a sudden every girl you've "
                     "never met be like..",
            'full_link': 'https://www.reddit.com/r/dogecoin/comments/qv7n6o'
                         '/when_you_post_that_you_just_100xed_your_crypto/',
            'score': 1, 'created_utc': 1637068881, 'selftext': '', 'num_comments': 0}
        testpost5 = {
            'title': 'This is how it ended up for people following a guy preaching about rockets, spaceships and '
                     'going to the moon...',
            'full_link': 'https://www.reddit.com/r/dogecoin/comments/qv7paf'
                         '/this_is_how_it_ended_up_for_people_following_a/',
            'score': 1, 'created_utc': 1637069080, 'selftext': '', 'num_comments': 0}
        testpost6 = {'title': 'I had a dream last night BTC was $663,000. What would that put DOGE at?',
                     'full_link': 'https://www.reddit.com/r/dogecoin/comments/qv7r30'
                                  '/i_had_a_dream_last_night_btc_was_663000_what/',
                     'score': 1, 'created_utc': 1637069242, 'selftext': '', 'num_comments': 0}
        testpost7 = {'title': 'If you ever wanted to get into Doge now would be the time to buy a nice bag',
                     'full_link': 'https://www.reddit.com/r/dogecoin/comments/qv7rw8'
                                  '/if_you_ever_wanted_to_get_into_doge_now_would_be/',
                     'score': 1, 'created_utc': 1637069310, 'selftext': '[removed]', 'num_comments': 0}
        testpost8 = {'title': 'Is Binance short on doge, they stopped withdrawals!!!',
                     'full_link': 'https://www.reddit.com/r/dogecoin/comments/qv7rx9'
                                  '/is_binance_short_on_doge_they_stopped_withdrawals/',
                     'score': 1, 'created_utc': 1637069314,
                     'selftext': 'It only makes sense if you are very short to lock it down like they have and blame '
                                 'it on a "technical issues".',
                     'num_comments': 0}
        testpost9 = {
            'title': '🎧 NFTMusic.Stream 🎧 Incredible Tech. Live Utility. The most underrated project on BSC. 💎 '
                     'Load your bags before any moment it 🎗',
            'full_link': 'https://www.reddit.com/r/dogecoin/comments/qv7wrh'
                         '/nftmusicstream_incredible_tech_live_utility_the/',
            'score': 1, 'created_utc': 1637069725, 'selftext': '', 'num_comments': 1}

        post_text = testpost['title']
        timestamp = testpost['created_utc']
        url = testpost['full_link']
        self.manage_dictionary(url, timestamp, post_text, 'btc')

        post_text = testpost2['title']
        timestamp = testpost2['created_utc']
        url = testpost2['full_link']
        self.manage_dictionary(url, timestamp, post_text, 'btc')

        post_text = testpost3['title']
        timestamp = testpost3['created_utc']
        url = testpost3['full_link']
        self.manage_dictionary(url, timestamp, post_text, 'btc')

        post_text = testpost4['title']
        timestamp = testpost4['created_utc']
        url = testpost4['full_link']
        self.manage_dictionary(url, timestamp, post_text, 'btc')

        post_text = testpost5['title']
        timestamp = testpost5['created_utc']
        url = testpost5['full_link']
        self.manage_dictionary(url, timestamp, post_text, 'btc')

        post_text = testpost6['title']
        timestamp = testpost6['created_utc']
        url = testpost6['full_link']
        self.manage_dictionary(url, timestamp, post_text, 'btc')

        post_text = testpost7['title']
        timestamp = testpost7['created_utc']
        url = testpost7['full_link']
        self.manage_dictionary(url, timestamp, post_text, 'btc')

        post_text = testpost8['title']
        timestamp = testpost8['created_utc']
        url = testpost8['full_link']
        self.manage_dictionary(url, timestamp, post_text, 'btc')

        post_text = testpost9['title']
        timestamp = testpost9['created_utc']
        url = testpost9['full_link']
        self.manage_dictionary(url, timestamp, post_text, 'btc')

        self.maintain_dictionary(1637069080, 'btc')
