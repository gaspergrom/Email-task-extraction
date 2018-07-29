import json

from models.cnn import CNNKim
from modules.util import preprocess_data, visualize_data, precision_recall_plot


config = json.loads(open(r'./config.json', encoding='utf-8', errors='ignore').read())
sentences_training = open(r'./datasets/sentences_training.txt', encoding='utf-8', errors='ignore').read().split('\n')
sentences_test = open(r'./datasets/sentences_test.txt', encoding='utf-8', errors='ignore').read().split('\n')

if __name__ == '__main__':
    num_words, embedding_matrix, data, targets = preprocess_data(sentences_training)
    _, _, x_test, y_test = preprocess_data(sentences_test, test_data=True)

    # CNN
    cnn = CNNKim()
    cnn.init(num_words, embedding_matrix)
    r_cnn = cnn.fit(data, targets)
    visualize_data(r_cnn)

    y_pred = cnn.predict(x_test)

    precision_recall_plot(y_test, y_pred)
