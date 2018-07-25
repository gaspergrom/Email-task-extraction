import re
import json
import numpy as np
import modules.util as util

config = json.loads(open('config.json', encoding='utf-8', errors='ignore').read())
sentences_training = open('datasets/sentences_training.txt', encoding='utf-8', errors='ignore').read().split('\n')
sentences_test = open('datasets/sentences_test.txt', encoding='utf-8', errors='ignore').read().split('\n')

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

## pass the dataset through the tokenizer
sequences, word_index = util.tokenize(clean_sentences, config['MAX_VOCABULARY'])
word2vec = util.get_glove_word2vec(config['glove_path'], config['glove_dimension'])
embedding_matrix = util.create_embedding_matrix(words2int, word2vec, len(word_index), config['glove_dimension'])