import json
from random import shuffle

import numpy as np
from keras import Input, Model, Sequential
from keras.layers import Embedding, Conv1D, MaxPooling1D, Dense, Conv2D, \
    Reshape, MaxPool2D, Concatenate, Flatten, Dropout, Activation

config = json.loads(open('config.json', encoding='utf-8', errors='ignore').read())

MAX_SEQUENCE_LENGTH = config['MAX_SEQUENCE_LENGTH']
EMBEDDING_DIMENSION = config['glove_dimension']
BATCH_SIZE = config['BATCH_SIZE']

filter_sizes = [3, 4, 5]
num_filters = 512
drop = 0.5


class CNN:
    def __init__(self):
        self.model = None

    def init(self, num_words, embedding_matrix):
        print("Creating model")
        input_ = Input(shape=(MAX_SEQUENCE_LENGTH,), dtype='int32')
        embedding = Embedding(
            input_dim=num_words,
            output_dim=EMBEDDING_DIMENSION,
            input_length=MAX_SEQUENCE_LENGTH,
            weights=[embedding_matrix],
            trainable=False)(input_)

        reshape = Reshape((MAX_SEQUENCE_LENGTH, EMBEDDING_DIMENSION, 1))(embedding)

        conv_0 = Conv2D(num_filters, kernel_size=(3, EMBEDDING_DIMENSION), padding='valid',
                        kernel_initializer='normal',
                        activation='relu')(reshape)
        conv_1 = Conv2D(num_filters, kernel_size=(3, EMBEDDING_DIMENSION), padding='valid',
                        kernel_initializer='normal',
                        activation='relu')(reshape)

        maxpool_0 = MaxPool2D(pool_size=(MAX_SEQUENCE_LENGTH - 3 + 1, 1), padding='valid')(conv_0)
        maxpool_1 = MaxPool2D(pool_size=(MAX_SEQUENCE_LENGTH - 3 + 1, 1), padding='valid')(conv_1)

        concatenated_tensor = Concatenate(axis=1)([maxpool_0, maxpool_1])
        flatten = Flatten()(concatenated_tensor)
        dropout = Dropout(drop)(flatten)
        output = Dense(units=1, activation='sigmoid')(dropout)

        model = Model(input_, output)
        model.compile(
            loss='binary_crossentropy',
            optimizer='rmsprop',
            metrics=['accuracy']
        )

        self.model = model

    def fit(self, data, targets):
        tmp = list(zip(data, targets))
        shuffle(tmp)
        data, targets = zip(*tmp)

        data = np.array(data)
        targets = np.array(targets)

        print('Training model')
        r = self.model.fit(
            data,
            targets,
            batch_size=config['BATCH_SIZE'],
            epochs=config['EPOCH'],
            validation_split=config['VALIDATION_SPLIT']
        )
        return r

    def predict(self, input):
        return self.model.predict(input, batch_size=BATCH_SIZE)


class CNNKim:
    def __init__(self):
        self.model = None

    def init(self, num_words, embedding_matrix):
        print("Creating Model...")
        filter_sizes = (2, 4, 5, 8)
        dropout_prob = [0.4, 0.5]
        graph_in = Input(shape=(MAX_SEQUENCE_LENGTH, EMBEDDING_DIMENSION))
        convs = []
        for fsz in filter_sizes:
            conv = Conv1D(32,
                          fsz,
                          padding='valid',
                          activation='relu',
                          strides=1)(graph_in)
            pool = MaxPooling1D(pool_size=MAX_SEQUENCE_LENGTH - fsz + 1)(conv)
            flattenMax = Flatten()(pool)
            convs.append(flattenMax)
        if len(filter_sizes) > 1:
            out = Concatenate(axis=1)(convs)
        else:
            out = convs[0]
        graph = Model(inputs=graph_in, outputs=out, name="graphModel")
        model = Sequential()
        model.add(Embedding(input_dim=num_words,  # size of vocabulary
                            output_dim=EMBEDDING_DIMENSION,
                            input_length=MAX_SEQUENCE_LENGTH,
                            trainable=False))
        model.add(Dropout(dropout_prob[0]))
        model.add(graph)
        model.add(Dense(128))
        model.add(Dropout(dropout_prob[1]))
        model.add(Activation('relu'))
        model.add(Dense(1))
        model.add(Activation('sigmoid'))
        # adam = Adam(clipnorm=.1)
        model.compile(loss='binary_crossentropy',
                      optimizer='adam',
                      metrics=['acc'])

        self.model = model

    def fit(self, data, targets):
        tmp = list(zip(data, targets))
        shuffle(tmp)
        data, targets = zip(*tmp)

        data = np.array(data)
        targets = np.array(targets)

        print('Training model')
        r = self.model.fit(
            data,
            targets,
            batch_size=config['BATCH_SIZE'],
            epochs=config['EPOCH'],
            validation_split=config['VALIDATION_SPLIT']
        )
        return r

    def predict(self, input):
        return self.model.predict(input, batch_size=BATCH_SIZE)
