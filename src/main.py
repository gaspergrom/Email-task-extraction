from models.cnn import CNN
from models.rnn import RNN
import modules.util as util
import modules.preprocess as pp

sentences_training = open(r'datasets/sentences_training.txt', encoding='utf-8', errors='ignore').read().split('\n')
sentences_test = open(r'datasets/sentences_test.txt', encoding='utf-8', errors='ignore').read().split('\n')

num_words, embedding_matrix, data, targets = pp.preprocess_data(sentences_training)
_, _, data_test, targets_test = pp.preprocess_data(sentences_test)

## CNN
# cnn = CNN()
# cnn.init(num_words, embedding_matrix)
# r_cnn = cnn.fit(data, targets)
# util.visualize_data(r_cnn)

## RNN
# rnn = RNN()
# rnn.init(num_words, embedding_matrix)
# r_rnn = rnn.fit(data, targets)
# util.visualize_data(r_rnn)