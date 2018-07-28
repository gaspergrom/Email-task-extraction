import json
import numpy as np
import os.path as path

from flask import Flask, request

from models.cnn import CNN
from models.rnn import RNN
from models.task import Task

import modules.util as util
import modules.connect as conn
import modules.entities as ent
import modules.preprocess as pp
import modules.extract as ex

import keras as K
from keras.models import load_model
from keras.preprocessing.text import Tokenizer

config = json.loads(open('config.json', encoding='utf-8', errors='ignore').read())
sentences_training = open(r'datasets/sentences_training.txt', encoding='utf-8', errors='ignore').read().split('\n')
sentences_test = open(r'datasets/sentences_test.txt', encoding='utf-8', errors='ignore').read().split('\n')

fname = '{0}glove.6B.{1}d.txt'.format(config['glove_path'], config['glove_dimension'])
if path.isfile(fname):
    num_words, embedding_matrix, data, targets = pp.preprocess_data(sentences_training)
    _, _, test_data, test_targets = pp.preprocess_data(sentences_test)

    ## initializing the RNN
    fname = "{0}{1}".format(config['weights_path'], config['weights_file'])
    rnn = RNN()

    if path.isfile(fname):
        rnn = load_model(fname)
    else:
        rnn.init(num_words, embedding_matrix)
        r_rnn = rnn.fit(data, targets)
        rnn.save(fname)
        util.visualize_data(r_rnn)

    ## modules/connect.py
    conn.start_serve(rnn, ex.mail_callback)

## flask server
# run with:
# $env:FLASK_APP = "main.py"
# python -m flask run
app = Flask(__name__)

@app.route('/')
def hello_world():
    print('Hello there!')
    return 'Hello, World! We here'

@app.route('/tasks', methods=['POST'])
def submitted_form():
    print(request)
    # TODO: something with this
    return 'Post request, thank you!'