import json
import numpy as np

from models.cnn import CNN
from models.rnn import RNN
from models.task import Task

import modules.util as util
import modules.connect as conn
import modules.entities as ent
import modules.preprocess as pp
import modules.extract as ex

import keras as K
from keras.preprocessing.text import Tokenizer

config = json.loads(open('config.json', encoding='utf-8', errors='ignore').read())
sentences_training = open(r'datasets/sentences_training.txt', encoding='utf-8', errors='ignore').read().split('\n')
sentences_test = open(r'datasets/sentences_test.txt', encoding='utf-8', errors='ignore').read().split('\n')

num_words, embedding_matrix, data, targets = pp.preprocess_data(sentences_training)
_, _, test_data, test_targets = pp.preprocess_data(sentences_test)

# TODO: saving/loading weights
## RNN
rnn = RNN()
rnn.init(num_words, embedding_matrix)
r_rnn = rnn.fit(data, targets)
util.visualize_data(r_rnn)

## modules/connect.py
conn.start_serve(rnn, ex.mail_callback)

# predictions = rnn.predict(np.array(test_data))
# print(len(predictions))
# print(predictions)