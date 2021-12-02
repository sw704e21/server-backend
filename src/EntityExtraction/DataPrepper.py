import os
import re
import praw
import json
import tweepy
import spacy
import string
import pickle

test_coins = (["bitcoin", "bitcoins", "btc", "eth", "doge", "ethereum",
              "dogecoin", "dogecoins", "binance coin", "bnb", "tether", "usdt",
               "sol", "cardano", "ada", "xrp", "polkadot", "dot",
               "solana", "usd coin", "usdc", "avalanche", "avax", "shiba inu",
               "shib", "dogelon mars", "dogelon", "algorand", "axie infinity",
               "axs", "terra", "luna", "uniswap", "uni", "cosmos", "atom",
               "vechain", "vet", "litecoin", "ltc", "stellar", "xlm",
               "internet computer", "icp", "polkadot", "tron", "trx",
               "avalanche", "avax"])


subreddits = (["cardano", "terraluna", "Stellar", "Tronix", "litecoin",
               "ICPTrader", "UniSwap", "cosmosnetwork", "VeChain",
               "Ripple", "Avax", "dogelon", "algorand", "AxieInfinity",
               "dogelon" "Shibainucoin", "USDC", "polkadot",
               "cryptocurrency", "bitcoin", "ethereum", "dogecoin",
               "satoshistreetbets", "altcoin", "binance", "Tether",
               "solana"])


# Prepares a sentence to work as part of the dataset for the sentiment analyzer
# The format is a touple (text, {"entities" : tags})
# where tags is a touple (word_start, word_end, word tag)
# Returns None if no entities from list_of_words can be found in text
def annotate_text(text, list_of_words, annotation):
    entity_list = []
    for word in list_of_words:
        for entry in re.finditer(" " + word + " ", text):
            tuple = ((entry.start() + 1), (entry.end() - 1), annotation)
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
        for submission in reddit.subreddit("all").search(coin, limit=2000):
            # Make sure the text or title specifically mentions the coin
            if any((ext in submission.selftext for ext in test_coins) or
                    any(ext in submission.title for ext in test_coins)):
                post_list.append(submission.title + submission.selftext)
    for submission in reddit.subreddit("all").search("crypto", limit=2000):
        if any((ext in submission.selftext for ext in test_coins) or
                any(ext in submission.title for ext in test_coins)):
            post_list.append(submission.title + submission.selftext)
    for submission in (reddit.subreddit("all").
                       search("cryptocurrency", limit=2000)):
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
    for submission in reddit.subreddit(subreddit).new(limit=lim):
        post_list.append(submission.selftext.lower())
    for submission in reddit.subreddit(subreddit).top(limit=lim):
        post_list.append(submission.selftext.lower())
    return post_list


# Does processing on a sentence to simplify it for the sentiment analyzer
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
    # Removes all symbols from string
    new_text = re.sub(r'[^\w]', ' ', new_text)
    # Put space before and after text to help annotation
    new_text = " " + new_text + " "
    # Remove double space caused by any of previous lines
    new_text = " ".join(new_text.split())
    return new_text.lower()


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
    for tweet in (tweepy.Cursor(api.search_tweets,
                                q=("#crypto"), lang='en').items(lim)):
        tweet_list.append(tweet.text.lower())
    for tweet in (tweepy.Cursor(api.search_tweets,
                                q=("#cryptocurrency"), lang='en').items(lim)):
        tweet_list.append(tweet.text.lower())
    for tweet in (tweepy.Cursor(api.search_tweets,
                                q=("#altcoin"), lang='en').items(lim)):
        tweet_list.append(tweet.text.lower())
    for tweet in (tweepy.Cursor(api.search_tweets,
                                q=("#shitcoin"), lang='en').items(lim)):
        tweet_list.append(tweet.text.lower())
    for tweet in (tweepy.Cursor(api.search_tweets,
                                q=("#memecoin"), lang='en').items(lim)):
        tweet_list.append(tweet.text.lower())
    for tweet in (tweepy.Cursor(api.search_tweets,
                                q=("#coinbase"), lang='en').items(lim)):
        tweet_list.append(tweet.text.lower())
    for tweet in (tweepy.Cursor(api.search_tweets,
                                q=("#cryptomining"), lang='en').items(lim)):
        tweet_list.append(tweet.text.lower())

    return tweet_list


# Runs download_subreddit_posts on multiple relevant subreddits
def download_multiple_supreddits(subreddit_list, lim):
    dataset = []
    for reddit in subreddit_list:
        for entry in download_subreddit_posts(reddit, lim):
            if any(ext in entry for ext in test_coins):
                dataset.append(entry)
    return dataset


# Function for finding how many texts a coin has been mentioned in
# in a list of sentences
def find_amount_mentions(text_list):
    datapath = os.path.dirname(os.path.realpath(__file__))
    frequency_dict = {}
    for coin in test_coins:
        for text in text_list:
            if coin in text:
                if coin in frequency_dict:
                    frequency_dict[coin] = frequency_dict[coin] + 1
                else:
                    frequency_dict[coin] = 1
    with open(datapath + "\\coinfrequency.json", 'w') as f:
        json.dump(frequency_dict, f)
    return frequency_dict


def scrape_and_list():
    datapath = os.path.dirname(os.path.realpath(__file__))
    dataset = []
    if not (os.path.exists(datapath + "\\dataset.json")):
        dataset = download_multiple_supreddits(subreddits, 2000)
        dataset.extend(reddit_download_all())
        dataset.extend(download_twitter_posts(test_coins, 1200))
        with open(datapath + "\\dataset.json", 'w') as f:
            json.dump(dataset, f)
    else:
        with open(datapath + "\\dataset.json", 'r') as f:
            dataset = json.loads(f.read())
    if (os.path.exists(datapath + "\\stemmed_data.json")):
        with open(datapath + "\\stemmed_data.json", 'r') as f:
            stemmed_data = json.loads(f.read())
    else:
        print('Stemming')
        stemmed_data = stem_dataset(list(dict.fromkeys(dataset)))
        with open(datapath + "\\stemmed_data.json", 'w') as f:
            json.dump(stemmed_data, f)
    print('Annotating')
    annotated_dataset = annotate_dataset(stemmed_data)
    print(len(annotated_dataset))
    with open(datapath + "\\annotated_data.pickle", 'wb') as f:
        pickle.dump(annotated_dataset, f)


# Function for calling stem_post on a list of posts
# Returns list of stemmed posts
def stem_dataset(data):
    stemmed_set = []
    i = 0
    for entry in data:
        print("Stemming: " + str(i) + " out of " + str(len(data)))
        stemmed_set.append(stem_post(entry))
        i = i + 1
    return stemmed_set


# Function for annotating a full dataset
# Takes a list of strings to be annotated
def annotate_dataset(data):
    print(len(data))
    annotated_set = []
    for entry in data:
        annotation = annotate_text(entry.lower(), test_coins, 'crypto')
        if annotation:
            annotated_set.append(annotation)
    return annotated_set


scrape_and_list()
