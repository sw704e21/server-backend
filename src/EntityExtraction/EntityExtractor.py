import json
import os
import spacy
import random
from spacy.language import Language
from spacy.training import Example
from spacy.util import minibatch
import pickle
import warnings
warnings.filterwarnings("error")


class EntityExtractor:

    def __init__(self):
        # Load an existing model if it exists
        self.file_path = os.path.dirname(os.path.realpath(__file__))
        if os.path.isdir(self.file_path + "\\Model"):
            self.nlp = Language().from_disk("D:\\Uni-ting\\7 semester\\Projekt\\server-backend\\src\\EntityExtraction\\SpacyNER\\ner_demo\\training\\model-best")
        with open(self.file_path + "\\annotated_data.pickle", 'rb') as j:
            self.data = pickle.load(j)
        self.ner = spacy.load("D:\\Uni-ting\\7 semester\\Projekt\\server-backend\\src\\EntityExtraction\\SpacyNER\\ner_demo\\training\\model-best")

    def train(self, iterations, training_data):
        nlp = spacy.blank("en")
        ner = nlp.add_pipe("ner")
        ner.add_label("crypto")
        nlp.add_pipe("ner", name="crypto_ner")
        print("Added pipes")

        nlp.initialize()
        print("Begun training")
        k = 0
        for itn in range(iterations):
            print("starting outer iteration: " + str(k))
            k = k + 1
            random.shuffle(training_data)
            examples = []
            for text, annots in training_data:
                examples.append(Example.from_dict(nlp.make_doc(text), annots))
                with open(("D:/Uni-ting/7 semester/Projekt/" +
                           "server-backend/src/EntityExtraction" +
                           "/test.json"), 'w') as j:
                    json.dumps(text)
                    json.dumps(annots)
            nlp.initialize(lambda: examples)
            for i in range(5):
                print("Iteration: " + str(i))
                random.shuffle(examples)
                j = 0
                for batch in minibatch(examples, size=32):
                    j += 1
                    print("batch iteration: " + str(j))
                    nlp.update(batch)
        nlp.to_disk(self.file_path + "\\model")
        return nlp

    def predict(self, text):
        if self.nlp is None:
            if os.path.isdir(self.file_path + "\\Model"):
                self.nlp = spacy.load(self.file_path + "\\Model")
            else:
                print("No model folder present")
        doc = self.nlp(text)
        return doc.ents


ent = EntityExtractor()
# ent.train(10, ent.data)
json_file_path = ent.file_path + "\\stemmed_data.json"

matches = 0
doc = ent.ner("I like ethereum and bitcoin however i think algorand has" +
              "a better identifier")
print("Cryptos in: " + doc.text)
for ent in doc.ents:
    print(ent.text)
