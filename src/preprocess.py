import re
import json
import matplotlib.pyplot as plt
import numpy as np
import modules.util as util
from keras import Input, Model
from keras.layers import Embedding, Conv1D, MaxPooling1D, Dense, GlobalMaxPooling1D, GlobalAveragePooling1D, Conv2D, \
    GlobalMaxPooling2D, MaxPooling2D, Reshape, MaxPool2D, Concatenate, Flatten, Dropout
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

filter_sizes = [3, 4, 5]
num_filters = 512
drop = 0.5

print("Creating Model...")
input_ = Input(shape=(MAX_SEQUENCE_LENGTH,), dtype='int32')
embedding = Embedding(
    input_dim=num_words,
    output_dim=EMBEDDING_DIMENSION,
    input_length=MAX_SEQUENCE_LENGTH,
    weights=[embedding_matrix],
    trainable=False)(input_)

reshape = Reshape((MAX_SEQUENCE_LENGTH, EMBEDDING_DIMENSION, 1))(embedding)

conv_0 = Conv2D(num_filters, kernel_size=(filter_sizes[0], EMBEDDING_DIMENSION), padding='valid',
                kernel_initializer='normal',
                activation='relu')(reshape)
conv_1 = Conv2D(num_filters, kernel_size=(filter_sizes[1], EMBEDDING_DIMENSION), padding='valid',
                kernel_initializer='normal',
                activation='relu')(reshape)
conv_2 = Conv2D(num_filters, kernel_size=(filter_sizes[2], EMBEDDING_DIMENSION), padding='valid',
                kernel_initializer='normal',
                activation='relu')(reshape)

maxpool_0 = MaxPool2D(pool_size=(MAX_SEQUENCE_LENGTH - filter_sizes[0] + 1, 1), strides=(1, 1), padding='valid')(conv_0)
maxpool_1 = MaxPool2D(pool_size=(MAX_SEQUENCE_LENGTH - filter_sizes[1] + 1, 1), strides=(1, 1), padding='valid')(conv_1)
maxpool_2 = MaxPool2D(pool_size=(MAX_SEQUENCE_LENGTH - filter_sizes[2] + 1, 1), strides=(1, 1), padding='valid')(conv_2)

concatenated_tensor = Concatenate(axis=1)([maxpool_0, maxpool_1, maxpool_2])
flatten = Flatten()(concatenated_tensor)
dropout = Dropout(drop)(flatten)
output = Dense(units=1, activation='sigmoid')(dropout)

model = Model(input_, output)
model.compile(
    loss='binary_crossentropy',
    optimizer='rmsprop',
    metrics=['accuracy']
)

print('Training model')
r = model.fit(
    data,
    targets,
    batch_size=BATCH_SIZE,
    epochs=EPOCH,
    validation_split=VALIDATION_SPLIT
)

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
