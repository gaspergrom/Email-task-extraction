import json
from keras import Input, Model
from keras.layers import Embedding, Conv1D, MaxPooling1D, Dense, GlobalMaxPooling1D, GlobalAveragePooling1D, Conv2D, \
    GlobalMaxPooling2D, MaxPooling2D, Reshape, MaxPool2D, Concatenate, Flatten, Dropout

config = json.loads(open('config.json', encoding='utf-8', errors='ignore').read())

MAX_SEQUENCE_LENGTH = config['MAX_SEQUENCE_LENGTH']
EMBEDDING_DIMENSION = config['glove_dimension']

filter_sizes = [3, 4, 5]
num_filters = 512
drop = 0.5

class CNN:
    def __init__(self):
        self.model = None
        pass

    def init(self, num_words, embedding_matrix):
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

        self.model = model
    
    def fit(self, data, targets):
        print('Training model')
        r = self.model.fit(
            data,
            targets,
            batch_size=config['BATCH_SIZE'],
            epochs=config['EPOCH'],
            validation_split=config['VALIDATION_SPLIT']
        )
        return r