from scipy import stats


def normalizeOld(values, bounds):
    return [bounds['desired']['lower'] + (x - bounds['actual']['lower']) * (
            bounds['desired']['upper'] - bounds['desired']['lower']) / (
                    bounds['actual']['upper'] - bounds['actual']['lower']) for x in values]


def normalize_multi(values, actual_bounds, desired_bounds):
    if actual_bounds[0] <= values[0] <= actual_bounds[1]:
        return [desired_bounds[0] + (x - actual_bounds[0]) * (desired_bounds[1] - desired_bounds[0]) / (
                    actual_bounds[1] - actual_bounds[0]) for x in values]
    elif values[0] > actual_bounds[1]:
        return [desired_bounds[1]]
    else:
        return [desired_bounds[0]]


def normalize(x, max_bound, min_bound):
    return (x - min_bound(x)) / (max_bound(x) - min_bound(x))


class TestData:

    def __init__(self):
        self.price_list1 = [61235, 61256, 59123, 62530, 62394, 61239, 62349, 63249, 61005, 59120, 58210, 59123, 61235,
                            61256, 59123, 62530, 62394, 61239, 62349, 63249, 61005, 59120, 58210, 59123]

        self.social_list = [1167/11, 317/2, 985/5, 1307/13, 435/7, 2483/17, 1108/10, 92/2, 493/3, 519/3, 833/6, 548/9,
                            519/11, 1638/15, 19/1, 11/2, 14/4, 19/5, 22/3, 28/2, 4/1, 12/5, 15/6, 3/2]

        self.sentiment_list = [0.7, 0.6, 0.9, 0.5, 0.7, 0.7, 0.6, 0.2, -0.1, 0.5, 0.9, 0.8, 0.7, 0.6,
                                0.9, 0.5, 0.7, 0.7, 0.6, 0.2, -0.1, 0.5, 0.9, 0.8]

        self.test_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


class ScoreCalculator:
    test_data = TestData()
    def __init__(self):
        api_url = 'http://cryptoserver.northeurope.cloudapp.azure.com'

    def price_score(self):
        price_list1 = self.test_data.price_list1
        dayone_average = sum(price_list1)/len(price_list1)
        daytwo_average_normalized = normalize_multi([price_list1[0]], (dayone_average * 0.95, dayone_average * 1.05), (0, 5))
        print("price score between 0-5: ", daytwo_average_normalized[0], "\n")

    def social_score(self):
        social_list = self.test_data.social_list
        average_socialscore = sum(social_list)/len(social_list)
        print("Social score between 0-5: ", sum(normalize_multi(social_list, (0, 100), (0, 5)))/len(social_list), "\n")

    def social_score_average(self, social_list):

       return sum(social_list)/len(social_list)
    def sentiment_score(self):

        print()

    def correlation_score(self):
        price_list = self.test_data.price_list
        social_list = self.test_data.social_list
        sentiment_list = self.test_data.sentiment_list
        test_list = self.test_data.social_list
        #print(stats.spearmanr(self.test_data.price_list, self.test_data.social_list))
        #print(stats.spearmanr(self.test_data.test_list, self.test_data.test_list))

        socialandprice_normalized_rank = normalizeOld(stats.spearmanr(price_list, social_list),
                        {'actual': {'lower': -1, 'upper': 1}, 'desired': {'lower': 0, 'upper': 5}})
        sentimentandprice_normalized_rank = normalizeOld(stats.spearmanr(price_list, sentiment_list),
                        {'actual': {'lower': -1, 'upper': 1}, 'desired': {'lower': 0, 'upper': 5}})
        test_normalized_rank = normalizeOld(stats.spearmanr(test_list, test_list),
                  {'actual': {'lower': -1, 'upper': 1}, 'desired': {'lower': 0, 'upper': 5}})
        print("Social and Price correlation rank between 0 - 5: ", socialandprice_normalized_rank[0], "\n",
              "Sentiment and Price correlation rank between 0 - 5: ", sentimentandprice_normalized_rank[0], "\n")
        print("Average of correlation ranks: ", ((socialandprice_normalized_rank[0] + sentimentandprice_normalized_rank[0]) / 2))

    def final_score(self):
        print()

if __name__ == '__main__':
    score = ScoreCalculator()
    score.price_score()
    # score.social_score()
    # score.correlation_score()




