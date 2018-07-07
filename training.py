import numpy as np
import re
import json

config = json.loads(open('config.json', encoding='utf-8', errors='ignore').read())
lines = open('movie_lines.txt', encoding='utf-8', errors='ignore').read().split('\n')
conversations = open('movie_conversations.txt', encoding='utf-8', errors='ignore').read().split('\n')

id2line = {}
for line in lines:
    _line = line.split(' +++$+++ ')
    if len(_line) == 5:
        id2line[_line[0]] = _line[4]

conversations_ids = []
for conversation in conversations[:-1]:
    _conversation = conversation.split(' +++$+++ ')[-1][1:-1].replace("'", "").replace(" ", "")
    conversations_ids.append(_conversation.split(','))

questions = []
answers = []
for conversation in conversations_ids:
    for i in range(len(conversation) - 1):
        questions.append(id2line[conversation[i]])
        answers.append(id2line[conversation[i + 1]])


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


clean_questions = []
for question in questions:
    clean_questions.append(clean_text(question))

clean_answers = []
for answer in answers:
    clean_answers.append(clean_text(answer))

short_questions = []
short_answers = []
i = 0
for question in clean_questions:
    if 2 <= len(question.split()) <= 25:
        short_questions.append(question)
        short_answers.append(clean_answers[i])
    i += 1
clean_questions = []
clean_answers = []
i = 0
for answer in short_answers:
    if 2 <= len(answer.split()) <= 25:
        clean_answers.append(answer)
        clean_questions.append(short_questions[i])
    i += 1

word2count = {}
for question in clean_questions:
    for word in question.split():
        if word not in word2count:
            word2count[word] = 1
        else:
            word2count[word] += 1
for answer in clean_answers:
    for word in answer.split():
        if word not in word2count:
            word2count[word] = 1
        else:
            word2count[word] += 1

threshold_questions = config["threshold_questions"]
questionswords2int = {}
word_number = 0
for word, count in word2count.items():
    if count >= threshold_questions:
        questionswords2int[word] = word_number
        word_number += 1
threshold_answers = config["threshold_answers"]
answerswords2int = {}
word_number = 0
for word, count in word2count.items():
    if count >= threshold_answers:
        answerswords2int[word] = word_number
        word_number += 1

tokens = ['<PAD>', '<EOS>', '<OUT>', '<SOS>']
for token in tokens:
    questionswords2int[token] = len(questionswords2int) + 1
for token in tokens:
    answerswords2int[token] = len(answerswords2int) + 1

answersints2word = {w_i: w for w, w_i in answerswords2int.items()}

open(config["questions"], "w", encoding='utf-8', errors='ignore').write(json.dumps(questionswords2int))
open(config["answers"], "w", encoding='utf-8', errors='ignore').write(json.dumps(answersints2word))

for i in range(len(clean_answers)):
    clean_answers[i] += ' <EOS>'

questions_into_int = []
for question in clean_questions:
    ints = []
    for word in question.split():
        if word not in questionswords2int:
            ints.append(questionswords2int['<OUT>'])
        else:
            ints.append(questionswords2int[word])
    questions_into_int.append(ints)
answers_into_int = []
for answer in clean_answers:
    ints = []
    for word in answer.split():
        if word not in answerswords2int:
            ints.append(answerswords2int['<OUT>'])
        else:
            ints.append(answerswords2int[word])
    answers_into_int.append(ints)

sorted_clean_questions = []
sorted_clean_answers = []
for length in range(1, 25 + 1):
    for i in enumerate(questions_into_int):
        if len(i[1]) == length:
            sorted_clean_questions.append(questions_into_int[i[0]])
            sorted_clean_answers.append(answers_into_int[i[0]])

# TODO: machine learning training
