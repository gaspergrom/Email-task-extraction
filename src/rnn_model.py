import re
import json
import matplotlib.pyplot as plt
import numpy as np
import modules.util as util
from keras import Input, Model, Sequential
from keras.layers import Embedding, Conv1D, MaxPooling1D, Dense, GlobalMaxPooling1D, GlobalAveragePooling1D, Conv2D, \
    GlobalMaxPooling2D, MaxPooling2D, Reshape, MaxPool2D, Concatenate, Flatten, Dropout, LSTM
from keras_preprocessing.sequence import pad_sequences

config = json.loads(open('config.json', encoding='utf-8', errors='ignore').read())
sentences_training = open(r'../datasets/sentences_training.txt', encoding='utf-8', errors='ignore').read().split('\n')
sentences_test = open(r'../datasets/sentences_test.txt', encoding='utf-8', errors='ignore').read().split('\n')

MAX_SEQUENCE_LENGTH = 30
BATCH_SIZE = 64
EPOCH = 100
VALIDATION_SPLIT = 0.2

## split dataset sentences into two arrays (inputs & outputs)
requires_action = []
sentences = []
for sentence in sentences_training:
    split = sentence.split('\t')
    p1 = split[0]
    p2 = split[1]
    requires_action.append(p1)
    sentences.append(p2)

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
for action in requires_action:
    if action.lower() == 'yes':
        action_into_int.append(1)
    else:
        action_into_int.append(0)

targets = np.array(action_into_int)

## pass the dataset through the tokenizer
sequences, word_index = util.tokenize(clean_sentences, config['MAX_VOCABULARY'])
EMBEDDING_DIMENSION = config['glove_dimension']
word2vec = util.get_glove_word2vec(config['glove_path'], EMBEDDING_DIMENSION)

num_words = min(config['MAX_VOCABULARY'], len(word_index) + 1)

embedding_matrix = util.create_embedding_matrix(words2int, word2vec, num_words, EMBEDDING_DIMENSION)

data = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH)

## create model
model_glove = Sequential()
model_glove.add(Embedding(num_words, EMBEDDING_DIMENSION, input_length=MAX_SEQUENCE_LENGTH, weights=[embedding_matrix], trainable=False))
model_glove.add(Dropout(0.2))
model_glove.add(Conv1D(64, 5, activation='relu'))
model_glove.add(MaxPooling1D(pool_size=4))
model_glove.add(LSTM(100))
model_glove.add(Dense(1, activation='sigmoid'))
model_glove.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

print('Training model')
r = model_glove.fit(data, targets, batch_size=BATCH_SIZE,
                epochs=EPOCH,
                validation_split=VALIDATION_SPLIT)



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
