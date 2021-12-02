import src.EntityExtraction.DataPrepper as data

string = "Why bitcoin Gambling Is The Future Of Online Casinos"
string2 = " bitcoin is better than ethereum and also bitcoin "


def test_annotate_string():
    annotated_string = (string, {"entities": [(4, 11, 'crypto')]})
    annotated_string2 = (string2, {"entities": [(1, 8, 'crypto'),
                         (42, 49, 'crypto'), (24, 32, 'crypto')]})
    result = data.annotate_text(string, ["bitcoin"], "crypto")
    result2 = data.annotate_text(string2, ["bitcoin", "ethereum"], "crypto")
    assert result == annotated_string
    assert result2 == annotated_string2


def test_find_amount_mentions():
    test_texts = (["i like bitcoin and cardano but i think doge is just meme",
                   "did you know ethereum is better than ripple but not" +
                   "as good as shiba inu",
                   "vechain, cosmos, xlm, bitcoin, cardano, cardano"])
    dict = data.find_amount_mentions(test_texts)
    assert dict["bitcoin"] == 2
    assert dict["cardano"] == 2
    assert dict["doge"] == 1
    assert dict["ethereum"] == 1
    assert dict["ripple"] == 1
