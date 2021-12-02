import pandas as pd
from tqdm import tqdm
import spacy
from spacy.tokens import DocBin
import pickle
nlp = spacy.blank("en") # load a new spacy model
db = DocBin() # create a DocBin object

TRAIN_DATA = []
VALID_DATA = []

json_file_path = "D:\\Uni-ting\\7 semester\\Projekt\\server-backend\\src\\EntityExtraction\\SpacyNER\\annotated_data.pickle"

with open(json_file_path, 'rb') as j:
        TRAIN_DATA = pickle.loads(j.read())
        VALID_DATA = TRAIN_DATA

for text, annot in tqdm(TRAIN_DATA): # data in previous format
    doc = nlp.make_doc(text) # create doc object from text
    ents = []
    for start, end, label in annot["entities"]: # add character indexes
        span = doc.char_span(start, end, label=label, alignment_mode="contract")
        if span is None:
            print("Skipping entity")
        else:
            ents.append(span)
    doc.ents = ents # label the text with the ents
    db.add(doc)

db.to_disk("D:\\Uni-ting\\7 semester\\Projekt\\server-backend\\src\\EntityExtraction\\SpacyNER\\train.spacy") # save the docbin object

db = DocBin()
for text, annot in tqdm(VALID_DATA): # data in previous format
    doc = nlp.make_doc(text) # create doc object from text
    ents = []
    for start, end, label in annot["entities"]: # add character indexes
        span = doc.char_span(start, end, label=label, alignment_mode="contract")
        if span is None:
            print("Skipping entity")
        else:
            ents.append(span)
    doc.ents = ents # label the text with the ents
    db.add(doc)

db.to_disk("D:\\Uni-ting\\7 semester\\Projekt\\server-backend\\src\\EntityExtraction\\SpacyNER\\valid.spacy") # save the docbin object