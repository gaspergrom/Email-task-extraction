import json

from models.cnn import CNN, CNNKim
from models.rnn import RNN
from modules.util import visualize_data, preprocess_data, precision_recall_plot

config = json.loads(open('config.json', encoding='utf-8', errors='ignore').read())
sentences_training = open(r'datasets/sentences_training.txt', encoding='utf-8', errors='ignore').read().split('\n')
sentences_test = open(r'datasets/sentences_test.txt', encoding='utf-8', errors='ignore').read().split('\n')

num_words, embedding_matrix, data, targets = preprocess_data(sentences_training)
_, _, x_test, y_test = preprocess_data(sentences_test, test_data=True)

# CNN
cnn = CNNKim()
cnn.init(num_words, embedding_matrix)
r_cnn = cnn.fit(data, targets)
visualize_data(r_cnn)

y_pred = cnn.predict(x_test)

## RNN
# rnn = RNN()
# rnn.init(num_words, embedding_matrix)
# r_rnn = rnn.fit(data, targets)
# visualize_data(r_rnn)
#
# y_pred = rnn.predict(x_test)

precision_recall_plot(y_test, y_pred)

# predictions = rnn.predict(np.array(test_data))

# print(len(predictions))
# print(predictions)
