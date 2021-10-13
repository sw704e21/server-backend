import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
from src.SentimentAnalyzer import SentimentAnalyzer


def testAnalyzePost():
    sia = SIA()
    sa = SentimentAnalyzer([], [])
    nltk.download('vader_lexicon')
    headline = "The next bitcoin halving will be in approximately 909 days." \
               " Keep on stacking my friends while bitcoin is cheap."
    post_text = "Quick question. I have money on my cash app with Bitcoin. " \
                "Can I go to a Bitcoin atm and withdraw cash with my cash" \
                " app btc wallet address?', 'What you think about binance"

    sa.analyze_posts(headline, post_text)

    headline_score = sia.polarity_scores(headline)
    headline_score['headline'] = headline

    post_text_score = sia.polarity_scores(post_text)
    post_text_score['post text'] = post_text

    assert sa.analyze_posts(headline, post_text) == \
           (headline_score, post_text_score)
