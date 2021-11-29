import re
import praw
import json
from pydantic import networks
import tweepy
import spacy
import string

test_coins = (["Bitcoin", "BTC", "ETH", "DOGE", "Ethereum",
              "dogecoin", "Binance coin", "BNB", "Tether", "USDT", "Solana",
               "SOL", "Cardano", "ADA", "XRP", "Polkadot", "DOT",
               "USD Coin", "USDC", "Avalanche", "AVAX"])


# Prepares a sentence to work as part of the dataset for the sentiment analyzer
# The format is a touple (text, {"entities" : tags})
# where tags is a touple (word_start, word_end, word tag)
def annotate_text(text, list_of_words, annotation):
    entity_list = []
    for word in list_of_words:
        for entry in re.finditer(word, text):
            tuple = (entry.start(), entry.end(), annotation)
            entity_list.append(tuple)
    dict = {"entities": entity_list}
    if entity_list:
        return (text, dict)


# Download from reddit/all, find posts containing any word from test_coins
def reddit_download_all():
    print('Scrape reddit: all')
    post_list = []
    reddit = praw.Reddit(
        client_id="Dc1e8D7Wl-kLwJ8BTNbXsw",
        client_secret="JBNSGeUIVtkP2s_FacZdptpNaxPo3g",
        user_agent="Savings-Stop3619",
    )
    for coin in test_coins:
        for submission in reddit.subreddit("all").search(coin, limit=1000):
            # Make sure the text or title specifically mentions the coin
            if any((ext in submission.selftext for ext in test_coins) or
               any(ext in submission.title for ext in test_coins)):
                post_list.append(submission.title + submission.selftext)
    return post_list


# Download from specific subreddit
def download_subreddit_posts(subreddit, lim):
    print("Scrape reddit: " + subreddit)
    post_list = []
    reddit = praw.Reddit(
        client_id="Dc1e8D7Wl-kLwJ8BTNbXsw",
        client_secret="JBNSGeUIVtkP2s_FacZdptpNaxPo3g",
        user_agent="Savings-Stop3619",
    )
    for submission in reddit.subreddit(subreddit).hot(limit=lim):
        post_list.append(submission.selftext.lower())
    return post_list


# Does post processing on a sentence to simplify it for the sentiment analyzer
# Should probably not be called stem
def stem_post(text):
    sp = spacy.load('en_core_web_sm')
    new_text = ""
    sentence = sp(text)
    # Lemmatize the words in the sentence, simplifying their forms
    for word in sentence:
        new_text = str(new_text) + " " + str(word.lemma_)
    # Remove punctuation from the sentence
    new_text = new_text.translate(str.maketrans('', '', string.punctuation))
    new_text = new_text.encode("ascii", "ignore")
    new_text = new_text.decode()
    new_text = re.sub(r'[^\w]', ' ', new_text)
    new_text = " ".join(new_text.split())
    return new_text


# Download twitter posts with a specific hashtag
# the function adds the hashtag itself
# Takes a list of words which should be searched for
def download_twitter_posts(hashtag_list, lim):
    print("Scrape twitter")
    tweet_list = []
    auth = (tweepy.AppAuthHandler("pBqTJwT6A7bi3fIhVQvwt0A7o",
            "S2HLZGIs5ZZGcsa6NNdGqgA8OmgzzCs46gOOIStqelZpC06p3O"))
    api = tweepy.API(auth, wait_on_rate_limit=True)
    for crypto in hashtag_list:
        for tweet in (tweepy.Cursor(api.search_tweets,
                      q=("#" + crypto), lang='en').items(lim)):
            tweet_list.append(tweet.text.lower())
    return tweet_list


def scrape_and_list():
    datapath = ("D:/Uni-ting/7 semester/Projekt/" +
                "server-backend/src/EntityExtraction/data.json")
    dataset = []
    annotated_dataset = []
    for entry in download_subreddit_posts("cryptocurrency", 1000):
        # Checks if any of the words in test_coins is used in the text
        if any(ext in entry for ext in test_coins):
            dataset.append(entry)
    for entry in download_subreddit_posts("bitcoin", 1000):
        if any(ext in entry for ext in test_coins):
            dataset.append(entry)
    for entry in download_subreddit_posts("ethereum", 100):
        if any(ext in entry for ext in test_coins):
            dataset.append(entry)
    for entry in download_subreddit_posts("dogecoin", 1000):
        if any(ext in entry for ext in test_coins):
            dataset.append(entry)
    for entry in download_subreddit_posts("satoshistreetbets", 1000):
        if any(ext in entry for ext in test_coins):
            dataset.append(entry)
    for entry in download_subreddit_posts("altcoin", 1000):
        if any(ext in entry for ext in test_coins):
            dataset.append(entry)
    dataset.extend(reddit_download_all())
    dataset.extend(download_twitter_posts(test_coins, 100))
    print('Stemming')
    i = 0
    for entry in dataset:
        print('Stemming: ' + str(i) + ' out of ' + str(len(dataset)))
        entry = stem_post(entry)
        i = i + 1
    print('Annotating')
    # Uses list(dict) to remove duplicates as scraping multiple subreddits
    # may give the same post multiple times
    for entry in list(dict.fromkeys(dataset)):
        annotated_dataset.append(annotate_text(entry, test_coins, "crypto"))
    print(len(annotated_dataset))
    with open(datapath, 'w') as f:
        json.dump(annotated_dataset, f)


datapath = ("D:/Uni-ting/7 semester/Projekt/" +
                "server-backend/src/EntityExtraction/data.json")

with open(datapath, 'r') as j:
    data = json.loads(j.read())
    i = 0
    for item in data:
        print(str(i))
        item[0] = stem_post(item[0])
        i = i+1
        if i > 20:
            break
    with open(datapath, 'w') as f:
        json.dump(data, f)
scrape_and_list()
