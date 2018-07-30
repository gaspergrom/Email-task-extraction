import json
import os.path as path

from keras.models import load_model

import modules.connect as conn
import modules.extract as ex
from modules.util import preprocess_data, preprocess_new_sentences, visualize_data
from models.cnn import CNNKim

## Loading config & datasets
config = json.loads(open('config.json', encoding='utf-8', errors='ignore').read())
sentences_training = open(r'datasets/sentences_training.txt', encoding='utf-8', errors='ignore').read().split('\n')
sentences_test = open(r'datasets/sentences_test.txt', encoding='utf-8', errors='ignore').read().split('\n')

## Preprocessing data
num_words, embedding_matrix, data, targets = preprocess_data(sentences_training)
_, _, test_data, test_targets = preprocess_data(sentences_test)

## Initializing the NN
fname = "{0}{1}".format(config['weights_path'], config['weights_file'])
nn = CNNKim()

# Load the model weights if they already exist (pre-trained models)
if path.isfile(fname):
    nn = load_model(fname)
else:
    nn.init(num_words, embedding_matrix)
    r_nn = nn.fit(data, targets)
    nn.model.save(fname)
    visualize_data(r_nn)

## Listening to new emails
conn.start_serve(nn, ex.mail_callback)