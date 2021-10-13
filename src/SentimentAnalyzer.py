from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA


class SentimentAnalyzer:

    def __init__(self, data, queue):
        self.data = data
        self.queue = queue

    def analyze_posts(self, headline, post_text):
        sia = SIA()

        headline_score = sia.polarity_scores(headline)
        headline_score['headline'] = headline

        post_text_score = sia.polarity_scores(post_text)
        post_text_score['post text'] = post_text

        return headline_score, post_text_score
