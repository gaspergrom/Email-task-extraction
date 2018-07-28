import numpy as np

import modules.entities as ent
import modules.preprocess as pp

from models.task import Task

from dateutil.parser import parse

""" Gets called when a user receives an email -> extracts the task """
def mail_callback(nn, sentences, content):
    _, _, inputs, _ = pp.preprocess_data(sentences)
    predictions = nn.predict(inputs)
    tasks = []

    for i, prediction in enumerate(predictions):
        # if prediction == 1:
            print("Got a task") # TODO: CHECK IF TASK!!
            # get entities for each task and create task objects
            # entities == dictionary (key, val)
            entities = ent.get_entities(sentences[i])

            # fill arrays with entities
            # TODO: preveriti, če Google podpira te entityje
            location_list = []
            person_list = []
            datetime_list = []
            for key, value in entities.items():
                if key == 'LOCATION':
                    location_list.append(value)
                elif key == 'PERSON':
                    person_list.append(value)
            
            # TODO: parse dates/times
            datetime = parse(sentences[i])
            print(datetime)

            task = Task(
                title = sentences[i], # TODO: title iz keywordov
                description = content,
                location_list = location_list,
                person_list = person_list,
                datetime_list = datetime_list)
            
            tasks.append(task)
    
    return tasks