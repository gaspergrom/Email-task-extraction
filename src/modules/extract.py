import numpy as np

import modules.entities as ent
import modules.preprocess as pp

from models.task import Task

""" Gets called when a user receives an email -> extracts the task """
def mail_callback(nn, sentences):
    print(sentences)
    _, _, inputs, _ = pp.preprocess_data(sentences)
    print(inputs)
    predictions = nn.predict(inputs)
    print(predictions)
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
            date_list = []
            time_list = []
            for key, value in entities.items():
                if key == 'LOCATION':
                    location_list.append(value)
                elif key == 'PERSON':
                    person_list.append(value)
                elif key == 'DATE':
                    date_list.append(value)
                elif key == 'TIME':
                    time_list.append(value)

            task = Task(
                title = "Task title", # TODO: title iz keywodov
                description = sentences[i],
                location_list = location_list,
                person_list = person_list,
                date_list = date_list,
                time_list = time_list)
            
            tasks.append(task)
    
    return tasks