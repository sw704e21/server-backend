from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA

from src.SentimentAnalyzer import SentimentAnalyzer

sa = SentimentAnalyzer([], [])
def testAnalyzePost():
    sia = SIA()

    headline = "The next bitcoin halving will be in approximately 909 days. Keep on stacking my friends while bitcoin is cheap."
    postText = "Quick question. I have money on my cash app with Bitcoin. Can I go to a Bitcoin atm and withdraw cash with my cash app btc wallet address?', 'What you think about binance"

    sa.AnalyzePosts(headline, postText)

    headline_score = sia.polarity_scores(headline)
    headline_score['headline'] = headline

    postText_score = sia.polarity_scores(postText)
    postText_score['post text'] = postText



    assert sa.AnalyzePosts(headline, postText) == (headline_score, postText_score)


