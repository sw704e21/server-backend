import json
import os
import spacy
import random
from spacy.language import Language
from spacy.training import Example
from spacy.util import minibatch
import DataPrepper


class EntityExtractor:

    def __init__(self):
        # Load an existing model if it exists
        self.file_path = os.path.dirname(os.path.realpath(__file__))
        if os.path.isdir(self.file_path + "\\Model"):
            self.nlp = Language().from_disk(self.file_path + "\\Model")
        with open(self.file_path + "\\data.json", 'r') as j:
            self.data = json.loads(j.read())

    def train(self, iterations, training_data):

        nlp = spacy.blank("en")
        ner = nlp.add_pipe("ner")
        ner.add_label("crypto")
        nlp.add_pipe("ner", name="crypto_ner")
        print("Added pipes")

        nlp.begin_training()
        print("Begun training")
        k = 0
        for itn in range(iterations):
            print("starting outer iteration: " + str(k))
            k = k + 1
            random.shuffle(training_data)
            examples = []
            for text, annots in training_data:
                examples.append(Example.from_dict(nlp.make_doc(text), annots))
            nlp.initialize(lambda: examples)
            for i in range(3):
                print("Iteration: " + str(i))
                random.shuffle(examples)
                j = 0
                for batch in minibatch(examples, size=8):
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
        doc = self.nlp(DataPrepper.stem_post(text))
        return doc.ents


ent = EntityExtractor()
ent.train(5, ent.data)
doc = ent.predict("why ethereum gambling is the future of online casinos")
print(doc[0].text, doc[0].label_)
