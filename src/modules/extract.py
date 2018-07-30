import json
import numpy as np

import modules.util as util
import modules.entities as ent

from models.task import Task

from dateparser.search import search_dates

""" Gets called when a user receives an email -> extracts the task """
def mail_callback(nn, sentences, content):
    """

    :param nn:
    :param sentences: list of strings
    :param content:
    :return:
    """
    sequences = util.preprocess_new_sentences(sentences)
    predictions = nn.predict(sequences)
    threshold = 0.4 # test by changing this parameter
    predictions = [p >= threshold for p in predictions]

    tasks = []

    for i, is_task in enumerate(predictions):
        if is_task:
            print("Got a task")
            entities = ent.get_entities(sentences[i])

            location_list = []
            person_list = []
            datetime_list = []
            saved = ""
            for key, value in entities.items():
                print("{0} - {1}".format(key, value))
                if key == 'name':
                    saved = value
                elif key == 'type':
                    if value == 'LOCATION':
                        location_list.append(saved)
                    elif value == 'PERSON':
                        person_list.append(saved)

            datetimes = search_dates(sentences[i], languages=['en'])
            if datetimes is not None:
                for datetime in datetimes:
                    dt = datetime[1]
                    datetime_parsed = '{0}-{1:02d}-{2:02d}'.format(dt.year, dt.month, dt.day)
                    datetime_list.append(datetime_parsed)
                    print("Found date: " + datetime_parsed)

            task = Task(
                id = None,
                title = sentences[i],
                description = content,
                location_list = location_list,
                person_list = person_list,
                datetime_list = datetime_list
            )
            tasks.append(task)
            
    return tasks