import json
from keras import Input, Model, Sequential
from random import shuffle
import numpy as np
from keras.layers import Embedding, Conv1D, MaxPooling1D, Dense, GlobalMaxPooling1D, GlobalAveragePooling1D, Conv2D, \
    GlobalMaxPooling2D, MaxPooling2D, Reshape, MaxPool2D, Concatenate, Flatten, Dropout, LSTM

config = json.loads(open('config.json', encoding='utf-8', errors='ignore').read())

MAX_SEQUENCE_LENGTH = config['MAX_SEQUENCE_LENGTH']
EMBEDDING_DIMENSION = config['glove_dimension']
BATCH_SIZE = config['BATCH_SIZE']
EPOCH = config['EPOCH']
VALIDATION_SPLIT = config['VALIDATION_SPLIT']

class RNN:
    def __init__(self):
        self.model = None
        pass
    
    def init(self, num_words, embedding_matrix):
        print("Creating RNN model")
        model_glove = Sequential()
        model_glove.add(Embedding(num_words, EMBEDDING_DIMENSION, input_length=MAX_SEQUENCE_LENGTH, weights=[embedding_matrix], trainable=False))
        model_glove.add(Dropout(0.2))
        model_glove.add(Conv1D(64, 5, activation='relu'))
        model_glove.add(MaxPooling1D(pool_size=4))
        model_glove.add(LSTM(100))
        model_glove.add(Dense(1, activation='sigmoid'))
        model_glove.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

        self.model = model_glove
    
    def fit(self, data, targets):
        tmp = list(zip(data, targets))
        shuffle(tmp)
        data, targets = zip(*tmp)

        data = np.array(data)
        targets = np.array(targets)

        print('Training model')
        r = self.model.fit(data, targets, batch_size=BATCH_SIZE,
                        epochs=EPOCH,
                        validation_split=VALIDATION_SPLIT)
        return r
    
    def predict(self, input):
        # TODO: post-processing
        return self.model.predict(input, batch_size=BATCH_SIZE)

    def save(self, fname):
        if self.model is not None:
            print("Saving RNN model")
            self.model.save(fname)
