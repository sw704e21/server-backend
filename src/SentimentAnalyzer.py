from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA


class SentimentAnalyzer():
    def __init__(self, data, queue):
        self.data = data
        self.queue = queue

    def AnalyzePosts(self, headline, posttext):
        sia = SIA()

        headline_score = sia.polarity_scores(headline)
        headline_score['headline'] = headline

        posttext_score = sia.polarity_scores(posttext)
        posttext_score['post text'] = posttext

        return headline_score, posttext_score


