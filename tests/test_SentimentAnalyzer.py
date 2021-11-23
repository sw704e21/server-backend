import json
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import requests
from src.SentimentAnalyzer import SentimentAnalyzer


server_url = 'http://cryptoserver.northeurope.cloudapp.azure.com'

def test_analyze_get_coin_names():
    sa = SentimentAnalyzer([])
    coin_list = sa.get_all_coins()
    assert ('dogecoin', 'DOGE') in coin_list
    assert ('bitcoin', 'BTC') in coin_list
    assert len(json.loads(requests.get(server_url + '/coins/all').content)) == len(coin_list)

def test_analyze_multiple_coins():
    nltk.download('vader_lexicon')
    sa = SentimentAnalyzer([])

    headline = "EtHEreum efpwokefopewk q¨d sHIb"
    post_text = "BTC, ælewr,rf eå¨q rfkweopdogecoinlæewkf"
    full_text = headline + post_text
    result = sa.identify_coins(full_text)
    assert len(result) == 4
    assert set(result) == set(['bitcoin', 'ethereum', 'dogecoin', 'shibainucoin'])

def testAnalyzePost():
    nltk.download('vader_lexicon')
    sia = SIA()
    sa = SentimentAnalyzer([])

    headline = "The next bitcoin halving will be in approximately 909 days." \
               " Keep on stacking my friends while bitcoin is cheap."
    post_text = "Quick question. I have money on my cash app with Bitcoin. " \
                "Can I go to a Bitcoin atm and withdraw cash with my cash" \
                " app btc wallet address?', 'What you think about binance"
    full_text = headline + post_text

    result = sa.analyze_posts(full_text)

    headline_score = sia.polarity_scores(headline)
    headline_score['headline'] = headline

    post_text_score = sia.polarity_scores(post_text)
    post_text_score['post text'] = post_text

    assert type(result) == float
    assert -1 <= result <= 1
