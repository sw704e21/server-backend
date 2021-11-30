from scipy import stats
import requests


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
        price_score = normalize_multi([price_list[0]], (daily_average * 0.95, daily_average * 1.05), (0, 5))
        return float(price_score[0])

    def social_score(self, social_list):
        average_socialscore = sum(social_list)/len(social_list)
        social_score = normalize_multi([average_socialscore], (0, 50), (0, 5))
        return float(social_score[0])

    def sentiment_score(self, sentiment_average):
        sentiment_score = normalize_multi(
            [sentiment_average], (-1, 0.8), (0, 5))
        return float(sentiment_score[0])

    def correlation_score(self, price_list, social_list, sentiment_list):
        socialandprice_normalized_rank = \
            normalize_multi(stats.spearmanr(price_list, social_list), (-1, 0.8), (0, 5))
        sentimentandprice_normalized_rank = \
            normalize_multi(stats.spearmanr(price_list, sentiment_list), (-1, 0.8), (0, 5))
        return float((socialandprice_normalized_rank[0] + sentimentandprice_normalized_rank[0]) / 2)

    def final_score(self, price_score, social_score, sentiment_score, correlation_score):
        score_sum = round(price_score) + round(social_score) + round(sentiment_score) + round(correlation_score)
        return int(score_sum * (score_sum/4))

    def handle_scores(self):

        for i in range(len(self.coins_id)):
            price_list = self.get_scoredata("price", self.coins_id[i])
            mentions_list = self.get_scoredata("mentions", self.coins_id[i])
            interactions_list = self.get_scoredata("interactions", self.coins_id[i])
            social_list = self.social_calculation(mentions_list, interactions_list)
            sentiment_list = self.get_scoredata("sentiment", self.coins_id[i])['list']
            sentiment_average = self.get_scoredata("sentiment", self.coins_id[i])['24hours']

            price_score = self.price_score(price_list)
            social_score = self.social_score(social_list)
            sentiment_score = self.sentiment_score(sentiment_average)
            correlation_score = self.correlation_score(price_list, social_list, sentiment_list)

            dict = {"identifier": self.get_coin_id()[i],
                    "price_score": "{:.1f}".format(price_score),
                    "social_score": "{:.1f}".format(social_score),
                    "average_sentiment": "{:.1f}".format(sentiment_score),
                    "correlation_rank": "{:.1f}".format(correlation_score),
                    "final_score": self.final_score(price_score, social_score, sentiment_score, correlation_score)}
            print("Score dictionary: ", dict)
            self.post_scoredata(dict)

    def get_coin_id(self):
        r = requests.get(self.api_url + "track")
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(e)
        data = r.json()
        list = []
        for x in data:
            list.append(x['identifier'])
        return list

    def get_scoredata(self, scoretype, id):
        r = requests.get(self.api_url + f"score/{scoretype}/{id}")
        return r.json()

    def post_scoredata(self, data):
        r = requests.post(self.api_url + "score", data=data)

        # Exception handling
        try:
            r.raise_for_status()
            print(r)
        except requests.exceptions.HTTPError as e:
            print(e)

    def social_calculation(self, mentions, interactions):
        social_list = []
        for i in range(len(mentions)):
            if interactions[i] != 0:
                social_list.append(interactions[i]/mentions[i])
            else:
                social_list.append(0)
        return social_list


if __name__ == '__main__':
    score = ScoreCalculator()
    score.handle_scores()
