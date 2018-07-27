import numpy as np
import keras as K
from models.cnn import CNN
from models.rnn import RNN
import modules.util as util
import modules.preprocess as pp

import matplotlib.pyplot as plt

sentences_training = open(r'datasets/sentences_training.txt', encoding='utf-8', errors='ignore').read().split('\n')
sentences_test = open(r'datasets/sentences_test.txt', encoding='utf-8', errors='ignore').read().split('\n')

num_words, embedding_matrix, data, targets = pp.preprocess_data(sentences_training)
_, _, test_data, test_targets = pp.preprocess_data(sentences_test)

## CNN
# cnn = CNN()
# cnn.init(num_words, embedding_matrix)
# r_cnn = cnn.fit(data, targets)
# util.visualize_data(r_cnn)

## RNN
rnn = RNN()
rnn.init(num_words, embedding_matrix)
r_rnn = rnn.fit(data, targets)
#util.visualize_data(r_rnn)

#tokens = myTokenizer.texts_to_matrix(test_data)
#predictions = rnn.predict(np.array(tokens))

error_sum = 0
predictions = rnn.predict(np.array(test_data))

for i in np.arange(0, 1, 0.05):
    util.apply_threshold(predictions.copy(), test_targets, i)

# print(len(predictions))
# print(predictions)