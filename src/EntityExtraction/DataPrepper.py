import re
import praw
import json
from praw.reddit import Subreddit

test_coins = ["bitcoin", "BTC", "ETH", "DOGE" "ethereum", "dogecoin", "Binance coin", "BNB", "Tether", "USDT", "Solana", "SOL", "Cardano", "ADA", "XRP", "XRP", "Polkadot", "DOT", "USD Coin", "USDC", "Avalanche", "AVAX"]

def annotate_text(text, list_of_words, annotation):
    entity_list = []
    for word in list_of_words:
        for entry in re.finditer(word, text):
            tuple = (entry.start(), entry.end(), annotation)
            entity_list.append(tuple)
    dict = {"entities": entity_list}
    if entity_list: 
        return (text, dict)

def download_posts(subreddit, lim):
    post_list = []
    reddit = praw.Reddit(
    client_id="Dc1e8D7Wl-kLwJ8BTNbXsw",
    client_secret="JBNSGeUIVtkP2s_FacZdptpNaxPo3g",
    user_agent="Savings-Stop3619",
    )
    for submission in reddit.subreddit(subreddit).hot(limit=lim):
        post_list.append(submission.selftext)
    return post_list

def scrape_and_list():
    dataset = []
    for entry in download_posts("cryptocurrency", 10):
        if annotate_text(entry, test_coins, 'crypto'):
            dataset.append(annotate_text(entry, test_coins, 'crypto'))
    for entry in download_posts("bitcoin", 10):
        if annotate_text(entry, test_coins, 'crypto'):
            dataset.append(annotate_text(entry, test_coins, 'crypto'))
    for entry in download_posts("ethereum", 10):
        if annotate_text(entry, test_coins, 'crypto'):
            dataset.append(annotate_text(entry, test_coins, 'crypto'))
    for entry in download_posts("dogecoin", 10):
        if annotate_text(entry, test_coins, 'crypto'):
            dataset.append(annotate_text(entry, test_coins, 'crypto'))
    out_file = open("data.json", "rb")
  
    json.dump(dataset, out_file, indent = 6)
  
    out_file.close()

scrape_and_list()