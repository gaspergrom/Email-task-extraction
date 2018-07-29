import json
import re

import matplotlib.pyplot as plt
import numpy as np
from keras.preprocessing.text import Tokenizer
from keras_preprocessing.sequence import pad_sequences
from sklearn.metrics import precision_recall_curve, average_precision_score
import spacy

# install English model with python as Admin -m spacy download en
nlp = spacy.load('en')

config = json.loads(open('config.json', encoding='utf-8', errors='ignore').read())

MAX_VOCABULARY = config['MAX_VOCABULARY']

def split_sentences(text):
    doc = nlp(text)
    return [s for s in doc.sents]

class Glove:
    word2vec = None
    embedding_matrix_loaded = False
    embedding_matrix = None

    @staticmethod
    def get_word2vec(path, dimension):
        if Glove.word2vec:
            return Glove.word2vec

        print("Loading word vectors...")
        word2vec = dict()
        with open('{0}glove.6B.{1}d.txt'.format(path, dimension), 'r', encoding='utf-8') as f:
            for line in f:
                values = line.split()
                word = values[0]
                vec = np.asarray(values[1:], dtype='float32')
                word2vec[word] = vec

        Glove.word2vec = word2vec
        return word2vec

    @staticmethod
    def create_embedding_matrix(word2idx, num_words, EMBEDDING_DIM, recreate=False):
        if Glove.embedding_matrix_loaded and not recreate:
            return Glove.embedding_matrix

        Glove.embedding_matrix = np.zeros((num_words, EMBEDDING_DIM))

        for word, i in word2idx.items():
            if i < num_words:
                embedding_vector = Glove.word2vec.get(word)

                # other vectors will be all zeros
                if embedding_vector is not None:
                    Glove.embedding_matrix[i] = embedding_vector

        Glove.embedding_matrix_loaded = True
        return Glove.embedding_matrix

class Tokenization:
    tokenizer = None

    @staticmethod
    def tokenize(texts, max_vocabulary, word_count, refit=True):
        """
        :param word_count: dict of word: count mappings
        :param texts:
        :param max_vocabulary:
        :return: sequences of integers corresponding to texts, word -> integer mapping
        """
        if not Tokenization.tokenizer:
            Tokenization.tokenizer = Tokenizer(num_words=max_vocabulary)
            Tokenization.tokenizer.fit_on_texts(texts)
            sequences = Tokenization.tokenizer.texts_to_sequences(texts)
            word_index = Tokenization.remove_infrequence_words(Tokenization.tokenizer.word_index, word_count)
            return sequences, word_index
        else:
            if refit:
                print("Warning: Refitting the tokenizer might change your index table")
                Tokenization.tokenizer.fit_on_texts(texts)

            sequences = Tokenization.tokenizer.texts_to_sequences(texts)
            word_index = Tokenization.remove_infrequence_words(Tokenization.tokenizer.word_index, word_count)

            return sequences, word_index

    @staticmethod
    def remove_infrequence_words(word_index, word_count, min_freq=10):
        count = len(word_index)
        trimmed_word_index = {word: index for word, index in word_index.items() if
                              word_count.get(word, min_freq) >= min_freq}

        print('INFO: Removed {} infrequent words (min_freq = {})'.format(count - len(trimmed_word_index), min_freq))

        return trimmed_word_index

def visualize_data(r):
    # visualise
    plt.plot(r.history['loss'], label='loss')
    plt.plot(r.history['val_loss'], label='val_loss')
    plt.legend()
    plt.show()

    # accuracy
    plt.plot(r.history['acc'], label='acc')
    plt.plot(r.history['val_acc'], label='val_acc')
    plt.title('Max validation accuracy = {:.2f}'.format(max(r.history['val_acc'])))
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.show()

def precision_recall_plot(targets, predictions):
    prec, recall, _ = precision_recall_curve(targets, predictions)

    average_precision = average_precision_score(targets, predictions)

    plt.step(recall, prec, alpha=0.2)
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.ylim([0.0, 1.05])
    plt.xlim([0.0, 1.0])
    plt.title('Average Precision={0:0.2f}'.format(
        average_precision))
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
    # text = re.sub(r"[-()\"#/@;:<>{}`+=~|.!?,]", "", text)
    text = re.sub('\s+', ' ', text)
    text = text.strip()
    return text

def preprocess_data(data, test_data=False):
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
        clean_sentences.append(clean_text(sentence))

    ## count how many times a word appears in the dataset
    word2count = {}
    for sentence in clean_sentences:
        for word in sentence.split():
            if word not in word2count:
                word2count[word] = 1
            else:
                word2count[word] += 1

    ## create an action array (yes -> 1, no -> 0)
    action_into_int = []
    if len(requires_action) > 0:
        for action in requires_action:
            if action.lower() == 'yes':
                action_into_int.append(1)
            else:
                action_into_int.append(0)

    ## pass the dataset through the tokenizer
    refit = not test_data
    sequences, word_index = Tokenization.tokenize(clean_sentences, config['MAX_VOCABULARY'], word2count, refit=refit)
    word2vec = Glove.get_word2vec(config['glove_path'], config['glove_dimension'])
    num_words = min(config['MAX_VOCABULARY'], len(word_index) + 1)
    embedding_matrix = Glove.create_embedding_matrix(word_index, num_words, config['glove_dimension'], recreate=refit)
    data = pad_sequences(sequences, maxlen=config['MAX_SEQUENCE_LENGTH'])
    targets = np.array(action_into_int)

    return num_words, embedding_matrix, data, targets