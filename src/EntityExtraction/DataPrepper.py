import re
import praw
import json
from praw.reddit import Subreddit
import tweepy

TWITTER_APP_KEY = "VVHRzSdTp6T35a04AJuqlr3SR"
TWITTER_APP_SECRET = "83MFy2JuE3sbyLhqWtpKV7KoBLQ7EDQgFCWEXVQgNqf44cJaxD"
TWITTER_KEY = "611585498-MgduwddC5tSVylz6CzUTMJKULy8qM6PJsdASvTtX"
TWITTER_SECRET = "S7gX7cTaqfnfkenpG0C3PD0Fu0YGAMKEijgGsWmsE1OZV"

test_coins = (["Bitcoin", "BTC", "ETH", "DOGE" "Ethereum",
              "dogecoin", "Binance coin", "BNB", "Tether", "USDT", "Solana",
               "SOL", "Cardano", "ADA", "XRP", "XRP", "Polkadot", "DOT",
               "USD Coin", "USDC", "Avalanche", "AVAX"])


def annotate_text(text, list_of_words, annotation):
    entity_list = []
    for word in list_of_words:
        for entry in re.finditer(word, text):
            tuple = (entry.start(), entry.end(), annotation)
            entity_list.append(tuple)
    dict = {"entities": entity_list} 
    if entity_list:
        return (text, dict)

def reddit_download_all():
    post_list = []
    reddit = praw.Reddit(
        client_id="Dc1e8D7Wl-kLwJ8BTNbXsw",
        client_secret="JBNSGeUIVtkP2s_FacZdptpNaxPo3g",
        user_agent="Savings-Stop3619",
    )
    for coin in test_coins:
        for submission in reddit.subreddit("all").search(coin, limit = 1000):
            if any(ext in submission.selftext for ext in test_coins) or any(ext in submission.title for ext in test_coins):
                post_list.append(submission.title + submission.selftext)
    return post_list


def download_subreddit_posts(subreddit, lim):
    post_list = []
    reddit = praw.Reddit(
        client_id="Dc1e8D7Wl-kLwJ8BTNbXsw",
        client_secret="JBNSGeUIVtkP2s_FacZdptpNaxPo3g",
        user_agent="Savings-Stop3619",
    )
    for submission in reddit.subreddit(subreddit).hot(limit=lim):
        post_list.append(submission.selftext.lower())
    return post_list

def download_twitter_posts(hashtag_list, lim):
    tweet_list = []
    auth = tweepy.OAuthHandler(TWITTER_APP_KEY, TWITTER_APP_SECRET)
    auth.set_access_token(TWITTER_KEY, TWITTER_KEY)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    for crypto in hashtag_list:
        for tweet in tweepy.Cursor(api.search_tweets, q=("#" + crypto), count=lim,
                                   lang="en",
                                   since="2017-04-03").items():
                                   tweet_list.append(tweet.text.lower())


def scrape_and_list():
    datapath = ("D:/Uni-ting/7 semester/Projekt/" +
                "server-backend/src/EntityExtraction/data.json")
    dataset = []
    annotated_dataset = []
    for entry in download_subreddit_posts("cryptocurrency", 1000):
        if any(ext in entry for ext in test_coins):
            dataset.append(entry)
    for entry in download_subreddit_posts("bitcoin", 1000):
        if any(ext in entry for ext in test_coins):
            dataset.append(entry)
    for entry in download_subreddit_posts("ethereum", 1000):
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
    for entry in list(dict.fromkeys(dataset)):
        annotated_dataset.append(annotate_text(entry, test_coins, "crypto"))
    print(len(annotated_dataset))
    with open(datapath, 'w') as f:
        json.dump(annotated_dataset, f)

scrape_and_list()