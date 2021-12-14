import time
from scipy import stats
import requests
import schedule
import logging
logger = logging.getLogger("backend")


def normalize_multi(values, actual_bounds, desired_bounds):
    if actual_bounds[0] <= values[0] <= actual_bounds[1]:
        return [desired_bounds[0] + (x - actual_bounds[0]) * (desired_bounds[1] - desired_bounds[0]) / (
                    actual_bounds[1] - actual_bounds[0]) for x in values]
    elif values[0] > actual_bounds[1]:
        return [desired_bounds[1]]
    else:
        return [desired_bounds[0]]


class ScoreCalculator:

    def __init__(self):
        self.api_url = 'http://cryptoserver.northeurope.cloudapp.azure.com/'
        self.coins_id = self.get_coin_id()

    def price_score(self, price_list):
        daily_average = sum(price_list)/len(price_list)
        if daily_average == 0:
            return 0
        else:
            price_score = normalize_multi([price_list[0]], (daily_average * 0.95, daily_average * 1.05), (0, 5))
            return float(price_score[0])

    def social_score(self, social_list, influence):
        average_socialscore = sum(social_list)/len(social_list)
        influence_score = normalize_multi([influence], (0, 20000), (0, 5))
        social_score = normalize_multi([average_socialscore], (0, 50), (0, 5))
        return float((social_score[0] + influence_score[0]) / 2)

    def sentiment_score(self, sentiment_average):

        sentiment_score = normalize_multi(
            [sentiment_average], (-0.1, 0.35), (0, 5))
        return float(sentiment_score[0])

    def correlation_score(self, price_list, social_list, sentiment_list):
        socialandprice_normalized_rank = \
            normalize_multi(stats.spearmanr(price_list, social_list), (-1, 0.8), (0, 5))
        # sentimentandprice_normalized_rank = \
        # normalize_multi(stats.spearmanr(price_list, sentiment_list), (-1, 0.8), (0, 5))
        return float(socialandprice_normalized_rank[0])

    def final_score(self, price_score, social_score, sentiment_score, correlation_score):
        score_sum = price_score + social_score + sentiment_score + correlation_score
        return round(int(score_sum * (score_sum/4)))

    def handle_scores(self):
        coins_id = self.get_coin_id()
        for i in range(len(self.coins_id)):
            price_list = self.get_scoredata("price", coins_id[i])
            mentions_list = self.get_scoredata("mentions", coins_id[i])
            interactions_list = self.get_scoredata("interactions", coins_id[i])
            social_list = self.social_calculation(mentions_list, interactions_list)
            sentiment_list = self.get_scoredata("sentiment", coins_id[i])['list']
            sentiment_average = self.get_scoredata("sentiment", coins_id[i])['24hours']
            influence = self.get_coindata(coins_id[i])['mostInfluence']

            price_score = self.price_score(price_list)
            social_score = self.social_score(social_list, influence)
            sentiment_score = self.sentiment_score(sentiment_average)
            correlation_score = self.correlation_score(price_list, social_list, sentiment_list)

            dict = {"identifier": coins_id[i],
                    "price_score": "{:.1f}".format(price_score),
                    "social_score": "{:.1f}".format(social_score),
                    "average_sentiment": "{:.1f}".format(sentiment_score),
                    "correlation_rank": "{:.1f}".format(correlation_score),
                    "final_score": self.final_score(price_score, social_score, sentiment_score, correlation_score)}
            print("Score dictionary: ", dict)
            self.post_scoredata(dict)

    def score_schedule(self):
        schedule.every().hour.at(':15').do(self.handle_scores)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def get_coin_id(self):
        r = requests.get(self.api_url + "track")
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(e)
        data = r.json()
        list = []
        for x in data:
            list.append(x['identifier'])
        return list

    def get_coindata(self, id):
        r = requests.get(self.api_url + f"coins/{id}/info")
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(e)
        return r.json()

    def get_scoredata(self, scoretype, id):
        r = requests.get(self.api_url + f"score/{scoretype}/{id}")
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(e)
        return r.json()

    def post_scoredata(self, data):
        r = requests.post(self.api_url + "score", data=data)

        # Exception handling
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(e)

    def social_calculation(self, mentions, interactions):
        social_list = []
        for i in range(len(mentions)):
            if interactions[i] != 0 or mentions[i] != 0:
                social_list.append(interactions[i]/mentions[i])
            else:
                social_list.append(0)
        return social_list


score = ScoreCalculator()
score.handle_scores()
