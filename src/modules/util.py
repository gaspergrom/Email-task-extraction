import re
import json
import numpy as np
from keras.preprocessing.text import Tokenizer

import matplotlib.pyplot as plt

config = json.loads(open('config.json', encoding='utf-8', errors='ignore').read())

MAX_VOCABULARY = config['MAX_VOCABULARY']

def get_glove_word2vec(path, dimension):
    print("Loading word vectors...")
    word2vec = dict()
    
    with open('{0}glove.6B.{1}d.txt'.format(path, dimension), 'r', encoding='utf-8') as f:
        for line in f:
            values = line.split()
            word = values[0]
            vec = np.asarray(values[1:], dtype='float32')
            word2vec[word] = vec
    return word2vec

def create_embedding_matrix(word2idx, word2vec, num_words, EMBEDDING_DIM):
    embedding_matrix = np.zeros((num_words, EMBEDDING_DIM))

    for word, i in word2idx.items():
        if i < num_words:
            embedding_vector = word2vec.get(word)

            # other vectors will be all zeros
            if embedding_vector is not None:
                embedding_matrix[i] = embedding_vector

    return embedding_matrix


def tokenize(texts, max_vocabulary):
    """
    :param texts:
    :param max_vocabulary:
    :return: sequences of integers corresponding to texts, word -> integer mapping
    """

    tokenizer = Tokenizer(num_words=max_vocabulary)
    tokenizer.fit_on_texts(texts)
    sequences = tokenizer.texts_to_sequences(texts)

    return sequences, tokenizer.word_index

def visualize_data(r):
    # visualise
    plt.plot(r.history['loss'], label='loss')
    plt.plot(r.history['val_loss'], label='val_loss')
    plt.legend()
    plt.show()

    # accuracy
    plt.plot(r.history['acc'], label='acc')
    plt.plot(r.history['val_acc'], label='val_acc')
    plt.legend()
    plt.show()

def apply_threshold(predictions, targets, threshold):
    error_sum = 0

    for i, prediction in enumerate(predictions):
        if prediction[0] > threshold:
            predictions[i] = 1
        else:
            predictions[i] = 0
        
        error_sum += abs(prediction[0] - targets[i])

    print("Error with threshold {0}: {1}".format(threshold, error_sum / len(targets)))

def clean_text(text):
    text = text.lower()
    text = re.sub(r"i'm", "i am", text)
    text = re.sub(r"he's", "he is", text)
    text = re.sub(r"it's", "it is", text)
    text = re.sub(r"she's", "she is", text)
    text = re.sub(r"that's", "that is", text)
    text = re.sub(r"what's", "what is", text)
    text = re.sub(r"where's", "where is", text)
    text = re.sub(r"how's", "how is", text)
    text = re.sub(r"there's", "there is", text)
    text = re.sub(r"'cause", "because", text)
    text = re.sub(r"\'ll", " will", text)
    text = re.sub(r"\'ve", " have", text)
    text = re.sub(r"\'re", " are", text)
    text = re.sub(r"\'d", " would", text)
    text = re.sub(r"n't", " not", text)
    text = re.sub(r"won't", "will not", text)
    text = re.sub(r"can't", "can not", text)
    text = re.sub(r"don't", "do not", text)
    text = re.sub(r"don 't", "do not", text)
    text = re.sub(r"in'", "ing", text)
    text = re.sub(r"c'mon", "come on", text)
    text = re.sub(r"who's", "who is", text)
    text = re.sub(r"someone's", "someone is", text)
    text = re.sub(r"d'you", "do you", text)
    text = re.sub(r"let's", "let us", text)
    text = re.sub(r"'em", "them", text)
    text = re.sub(r"'bout", "about", text)
    text = re.sub(r"'til", "until", text)
    text = re.sub(r"woulda'", "would have", text)
    text = re.sub(r"s'long", "it is long", text)
    text = re.sub(r"how'm", "how am", text)
    text = re.sub(r"shi'ites", "shitties", text)
    text = re.sub(r"'course", "of course", text)
    text = re.sub(r"'least", "at least", text)
    text = re.sub(r"o'clock", "on clock", text)
    text = re.sub(r"prob'ly", "probably", text)
    text = re.sub(r"whatd'ya", "what do you", text)
    text = re.sub(r"would'ya", "would you", text)
    text = re.sub(r"jus'", "just", text)
    text = re.sub(r"'cept", "except", text)
    text = re.sub(r"'fore", "therefore", text)
    text = re.sub(r"y'", "you ", text)
    text = re.sub(r"\'n", " than", text)
    text = re.sub(r"\'11", " will", text)
    text = re.sub(r"an'", "and", text)
    text = re.sub(r"y'", "you ", text)
    text = re.sub(r"som'b'y", "somebody", text)
    text = re.sub(r"what'the", "what the", text)
    text = re.sub(r"s'it", "shit", text)
    text = re.sub(r"'nough", "enough", text)
    text = re.sub(r"\'1l", " will", text)
    text = re.sub(r"ma'am", "madam", text)
    text = re.sub(r"ethic'ly", "ethically", text)
    text = re.sub(r"y'wanna", "you want to", text)
    text = re.sub(r"d'ya", "do you", text)
    text = re.sub(r"got'm", "got them", text)
    text = re.sub(r"s'", "", text)
    text = re.sub(r"n'", "", text)
    text = re.sub(r"y'", "you ", text)
    text = re.sub(r"leav't", "leave it", text)
    text = re.sub(r"s'pose", "suppose", text)
    text = re.sub(r"o'", "of", text)
    text = re.sub(r"'s", "", text)
    text = re.sub(r"some'b'y", "somebody", text)
    text = re.sub(r"\'er", " her", text)
    text = re.sub(r"\'", " ", text)
    text = re.sub(r"[-()\"#/@;:<>{}`+=~|.!?,]", "", text)
    text = re.sub('\s+', ' ', text)
    text = text.strip()
    return text