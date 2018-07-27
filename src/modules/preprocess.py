import re
import json
import numpy as np
import modules.util as util
import matplotlib.pyplot as plt
from keras_preprocessing.sequence import pad_sequences

def preprocess_data(data):
    config = json.loads(open('config.json', encoding='utf-8', errors='ignore').read())

    ## split dataset sentences into two arrays (inputs & outputs)
    requires_action = []
    sentences = []
    for sentence in data:
        split = sentence.split('\t')
        if len(split) == 2:
            p1 = split[0]
            p2 = split[1]
            requires_action.append(p1)
            sentences.append(p2)
        elif len(split) == 1:
            sentences.append(split[0])

    ## clean the sentences array (lowercase, special characters, ...)
    clean_sentences = []
    for sentence in sentences:
        clean_sentences.append(util.clean_text(sentence))

    ## count how many times a word appears in the dataset
    word2count = {}
    for sentence in clean_sentences:
        for word in sentence.split():
            if word not in word2count:
                word2count[word] = 1
            else:
                word2count[word] += 1

    ## create a words2int dictionary
    words2int = {}
    word_number = 0
    for word, count in word2count.items():
        words2int[word] = word_number
        word_number += 1

    ## create an action array (yes -> 1, no -> 0)
    action_into_int = []
    if len(requires_action) > 0:
        for action in requires_action:
            if action.lower() == 'yes':
                action_into_int.append(1)
            else:
                action_into_int.append(0)

    ## pass the dataset through the tokenizer
    sequences, word_index = util.tokenize(clean_sentences, config['MAX_VOCABULARY'])
    word2vec = util.get_glove_word2vec(config['glove_path'], config['glove_dimension'])
    num_words = min(config['MAX_VOCABULARY'], len(word_index) + 1)
    data = pad_sequences(sequences, maxlen=config['MAX_SEQUENCE_LENGTH'])
    targets = np.array(action_into_int)
    embedding_matrix = util.create_embedding_matrix(words2int, word2vec, num_words, config['glove_dimension'])

    return num_words, embedding_matrix, data, targets


if __name__ == '__main__':
    sentences_training = open(r'../../datasets/sentences_training.txt', encoding='utf-8', errors='ignore').read().split('\n')
    preprocess_data(sentences_training)