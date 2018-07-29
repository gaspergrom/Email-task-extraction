import json
import numpy as np

import modules.util as util
import modules.entities as ent

from models.task import Task

from dateparser.search import search_dates

""" Gets called when a user receives an email -> extracts the task """
def mail_callback(nn, sentences, content):
    _, _, inputs, _ = util.preprocess_data(sentences)
    #predictions = nn.predict(inputs)
    predictions = []
    for input in inputs:
        predictions.append(1)
    tasks = []

    for i, prediction in enumerate(predictions):
        # if prediction == 1:
            print("Got a task") # TODO: CHECK IF TASK!!
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