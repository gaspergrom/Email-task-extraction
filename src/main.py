import json

from models.rnn import RNN
from modules.util import visualize_data, preprocess_data

config = json.loads(open('config.json', encoding='utf-8', errors='ignore').read())
sentences_training = open(r'datasets/sentences_training.txt', encoding='utf-8', errors='ignore').read().split('\n')
# sentences_test = open(r'datasets/sentences_test.txt', encoding='utf-8', errors='ignore').read().split('\n')

num_words, embedding_matrix, data, targets = preprocess_data(sentences_training)
# _, _, test_data, test_targets = pp.preprocess_data(sentences_test)

# CNN
# cnn = CNN()
# cnn.init(num_words, embedding_matrix)
# r_cnn = cnn.fit(data, targets)
# visualize_data(r_cnn)

## RNN
rnn = RNN()
rnn.init(num_words, embedding_matrix)
r_rnn = rnn.fit(data, targets)
visualize_data(r_rnn)

# predictions = rnn.predict(np.array(test_data))

# print(len(predictions))
# print(predictions)