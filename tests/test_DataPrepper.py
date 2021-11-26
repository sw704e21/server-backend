import src.EntityExtraction.DataPrepper as data

string = "Why bitcoin Gambling Is The Future Of Online Casinos"
string2 = "bitcoin is better than ethereum, and also bitcoin"


def test_annotate_string():
    annotated_string = (string, {"entities": [(4, 11, 'crypto')]})
    annotated_string2 = (string2, {"entities": [(0, 7, 'crypto'),
                         (42, 49, 'crypto'), (23, 31, 'crypto')]})
    result = data.annotate_text(string, ["bitcoin"], "crypto")
    result2 = data.annotate_text(string2, ["bitcoin", "ethereum"], "crypto")
    assert result == annotated_string
    assert result2 == annotated_string2
