from genericpath import exists
import json
import os
import spacy
import random
from spacy.language import Language
from spacy.training import Example
from spacy.util import minibatch


class EntityExtractor:

    def __init__(self):
        self.file_path = os.path.dirname(os.path.realpath(__file__))
        if os.path.isdir(self.file_path + "\\Model"):
            self.nlp = Language().from_disk(self.file_path + "\\Model")
        with open(self.file_path + "\\data.json", 'r') as j:
            self.data = json.loads(j.read())
            self.data.append( ("Im 23 Im from Brazil and I have 30k dollars on my bank account" +
     "Im thinking about invest 20 of it about to 6k dollars on bitcoin I" +
     "hope it can reach 200k dollars or more 1kk dol in future",
     {"entities": [(120, 128, 'crypto')]}))
        self.data.append(("Why bitcoin Gambling Is The Future ethereum Of Online Casinos",
     {"entities": [(4, 11, 'crypto')]}))

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
        if os.path.isdir(self.file_path + "\\Model"):
            self.nlp = spacy.load(self.file_path + "\\Model")
            doc = self.nlp(text)
            return doc.ents
        else:
            print("No model folder present")


ent = EntityExtractor()
ent.train(5, ent.data)
doc = ent.predict("why ethereum gambling is the future of online casinos")
print(doc[0].text, doc[0].label_)
