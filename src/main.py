from models.cnn import CNN
from models.rnn import RNN
import modules.util as util
import modules.preprocess as pp

num_words, embedding_matrix, data, targets = pp.preprocess_data()

## CNN
# cnn = CNN()
# cnn.init(num_words, embedding_matrix)
# r_cnn = cnn.fit(data, targets)
# util.visualize_data(r_cnn)

## RNN
rnn = RNN()
rnn.init(num_words, embedding_matrix)
r_rnn = rnn.fit(data, targets)
util.visualize_data(r_rnn)