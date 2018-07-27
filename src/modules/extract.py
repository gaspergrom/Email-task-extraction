import numpy as np

import modules.preprocess as pp

""" Gets called when a user receives an email -> extracts the task """
def mail_callback(nn, sentences):
    inputs = pp.preprocess_data(sentences)
    predictions = nn.predict(inputs) # TODO: preveri če je to vse OK
    tasks = []

    for i, prediction in enumerate(predictions):
        if prediction == 1:
            # get entities for each task and create task objects
            # entities == dictionary (key, val)
            entities = ent.get_entities(inputs[i])

            # fill arrays with entities
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
                title = "title here",
                description = inputs[i],
                location_list = location_list,
                person_list = person_list,
                date_list = date_list,
                time_list = time_list)
            
            tasks.append(task)
    
    return tasks