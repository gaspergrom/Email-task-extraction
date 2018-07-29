import re
import os
import json
import asana
import urllib
import numpy as np

from models.task import Task

from models.bot_action import BotAction

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
base = "https://clean-sprint-app.intheloop.io"
user = 'user_507'
bot_action = BotAction.IDLE

def refresh_token_func():
    data = json.dumps({"$type": "AuthIntegration",
                       "identificator": "loop.user8@gmail.com",
                       "secret": "LYiAfAXoCRFxtlCmeIc5ZGLcrIOxR6yPMAlM0ZY/fR97m9qWjsrqCThE0kfAPd3pUck="
                       }).encode("utf-8")

    r = urllib.request.Request(base + '/api/v1/auth/integration', data)
    r.add_header("Content-Type",
                 'application/json')
    res = urllib.request.urlopen(r).read()
    authorisation = json.loads(res)["token"]["accessToken"]
    refresh_token = json.loads(res)["token"]["refreshToken"]
    return authorisation, refresh_token

def send_to_google(text):
    # print('Sending to Google: ' + text)
    url_addr = "https://dialogflow.googleapis.com/v2/projects/chatbot-loop/agent/sessions/b684f4f1-3b5f-ad82-9e24-5186ce5a0c5e:detectIntent"
    auth_token = "ya29.c.EloHBoFrgpFzK-P2OqWu-XwNDEM0sWcleKsfKoKBuc9KGG_8I0gc182j5fgx-Wa6aRJMRlHthajwUN7q-cvzjGKIvgE0N2ojMOvH6VXnguIM_Kpmi9itNluAk2A"
    data = json.dumps({
        "queryInput": {
            "text": {
                "text": text,
                "languageCode": "en"
            }
        },
        "queryParams": {
            "timeZone": "Europe/Ljubljana"
        }
    }).encode("utf-8")

    # request
    req = urllib.request.Request(url_addr, data)
    req.add_header("Content-Type",
                   'application/json')
    req.add_header("Authorization", "Bearer " + auth_token)
    response = urllib.request.urlopen(req).read()
    # print(response)

    return response

def send_to_user(msg, auth, refresh):
    data = json.dumps({
        "$type": "CommentChat",
        "shareList": {
            "resources": [
                {
                    "$type": "User",
                    "_id": user,
                    "id": user,
                    "clientId": user,
                    "name": "jure",
                    "revision": "1",
                    "email": "jure55841@gmail.com"
                }
            ],
            "offset": 0,
            "size": 1,
            "totalSize": 1
        },
        "name": "<No subject>",
        "comment": msg,
        "snippet": "IMPORTANT!",
        "attachments": {
            "resources": []
        }
    }).encode("utf-8")

    req = urllib.request.Request(base + '/api/v1/comment/chat', data)
    req.add_header("Content-Type",
                   'application/json')
    req.add_header("Authorization", "Bearer " + auth)
    try:
        response = urllib.request.urlopen(req).read()
    except Exception:
        auth, refresh = refresh_token_func()
        req = urllib.request.Request(base + '/api/v1/comment/chat', data)
        req.add_header("Content-Type",
                       'application/json')
        req.add_header("Authorization", "Bearer " + auth)
        response = urllib.request.urlopen(req).read()
    return auth, refresh

def start_serve(nn, mail_callback):
    # request na vsake tok časa da preveri keri so kej novi emaili
    sinceId = 18103081825590183
    bot_action = BotAction.IDLE
    asana_code = str(input("Vnesi asana code: "))
    last_tasks = []
    base = "https://clean-sprint-app.intheloop.io"
    authorisation = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMTEyIiwiYXRfaWQiOiIxMTJfNTc2Y2IzZTMtZjNlNi1lODgwLTZhODItZGY5MjEyOTcxN2IwIiwibmJmIjoxNTMyODUwMzQ3LCJleHAiOjE1MzI4NTM5NDcsImlhdCI6MTUzMjg1MDM0N30.PtXX-MJkw3e8WeG35lv2FS2akdQOh3bGhMmZoUYeRxM'
    user = 'user_507'
    refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMTEyIiwiYXRfaWQiOiIxMTJfNTk1ZDdlMmUtZDQyYy1mNjVhLThiODEtMmY0MjE2YTY4YTQ2IiwibmJmIjoxNTMyNzY2Mzk1LCJleHAiOjE1MzI3Njk5OTUsImlhdCI6MTUzMjc2NjM5NX0.cCCwviQt2KzTDDGfVML-0Ihjk4yZyBmui8YQyuNo6kI"
    client = asana.Client.oauth(
        client_id='759566842403050',
        client_secret='6316248cc3531236f6796574ef8bcc4a',
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
    )
    client.session.fetch_token(code=asana_code)
    while True:
        data = urllib.parse.urlencode({
            'offset': 0,
            'size': 100,
            "sinceId": sinceId,
            "longPolling": True,
            "sortOrder": "ascending",
            "eventTypeList": "CommentCreated"
        })

        req = urllib.request.Request(base + '/api/v1/event/list?' + data)
        req.add_header("Authorization", "Bearer " + authorisation)
        req.add_header("X-Impersonate-User", user)
        try:
            response = urllib.request.urlopen(req).read().decode('utf8')
        except Exception:
            authorisation, refresh_token = refresh_token_func()
            req = urllib.request.Request(base + '/api/v1/event/list?' + data)
            req.add_header("Authorization", "Bearer " + authorisation)
            req.add_header("X-Impersonate-User", user)
            response = urllib.request.urlopen(req).read().decode('utf8')
        response = json.loads(response)
        sinceId = response["lastEventId"]
        print(sinceId)

        if (len(response["resources"]) > 0):
            type = response["resources"][0]["comment"]["$type"]

            if (type == "CommentMail"):
                content = response["resources"][0]["comment"]["body"]["content"]
                content = re.sub(r'\[(.*?)\]', '', content)
                sentences = re.split('(!|\.|\?)', content)[:-1:2]
                email = response["resources"][0]["comment"]["author"]["email"]
                author = response["resources"][0]["comment"]["author"]["name"]
                subject = response["resources"][0]["comment"]["name"]
                last_tasks = mail_callback(nn, sentences, content)
                print("Got an email")
                if (len(last_tasks) > 0):
                    comment_text = "[" + author + " (" + email + ") - " + subject + "]\n"
                    if len(last_tasks) > 1:
                        comment_text += "Found " + str(len(last_tasks)) + " tasks in this email:\n"
                    else:
                        comment_text += "Found 1 task in this email:\n"
                    
                    comment_text += format_tasks_list(last_tasks)
                    comment_text += '\nDo you want me to add these tasks to Asana?'
                    authorisation, refresh_token = send_to_user(comment_text, authorisation, refresh_token)
                    bot_action = BotAction.WAIT_QUESTION
                    print(comment_text)
            elif (type == "CommentChat"):
                user_response = response["resources"][0]["comment"]["snippet"].strip()
                user_id = response["resources"][0]["comment"]["author"]["id"]
                print('User id: ' + user_id)

                #if len(user_response) < 100:
                # check if the new text is not by the bot (to prevent the bot from talking with itself)
                if user_id != 'user_112':
                    action = None
                    # the user answered a question
                    if bot_action == BotAction.WAIT_QUESTION:
                        action = handle_processed_response(send_to_google(user_response), last_tasks, client, authorisation, refresh_token)

                    # the user sent a prompt to the bot
                    if bot_action == BotAction.IDLE:
                        handle_processed_prompt(client, send_to_google(user_response), authorisation, refresh_token)

                    # set bot action
                    if action is not None:
                        bot_action = action

def handle_processed_response(bytes, last_tasks, asana_client, authorisation, refresh_token):
    decoded = bytes.decode('utf8')
    deserialized = json.loads(decoded)

    msg = ''
    query_result = 'queryResult'
    action = 'action'
    number = 'number'
    fulfillmentText = 'fulfillmentText'
    parameters = 'parameters'
    yes = 'smalltalk.confirmation.yes'
    no = 'smalltalk.confirmation.no'
    add_task_selective = 'task.addSelective'
    b_action = None

    if query_result in deserialized and action in deserialized[query_result]:
        if deserialized[query_result][action] == yes:
            print('User answered positive')
            if len(last_tasks) > 0:
                add_to_asana(asana_client, last_tasks, authorisation, refresh_token)
                msg = 'I have added the tasks to Asana for you.'
                b_action = BotAction.IDLE
        elif deserialized[query_result][action] == no:
            print('User answered negative')
            b_action = BotAction.IDLE
            msg = 'Okay, I have discarded the tasks.'
        elif deserialized[query_result][action] == add_task_selective:
            print('Selective task')
            if parameters in deserialized[query_result] and number in deserialized[query_result][parameters]:
                selected_tasks = []
                tasks_str = ""
                number_array = deserialized[query_result][parameters][number]
                
                print('Got number of tasks: ' + str(len(number_array)) + ' tasks.')

                for num in number_array:
                    i = num - 1
                    if i < len(last_tasks):
                        selected_tasks.append(last_tasks[i])
                        tasks_str += str(num) + ', '
                
                print('Added tasks: ' + tasks_str)
                add_to_asana(asana_client, selected_tasks, authorisation, refresh_token)
                msg = 'I have added task(s) nr. {0} to Asana for you.'.format(tasks_str[0:-2])
                b_action = BotAction.IDLE
        else:
            print('Unknown user response')
            msg = deserialized[query_result][fulfillmentText]
            b_action = BotAction.WAIT_QUESTION

        print('Sent \'{0}\' to user'.format(msg))
        send_to_user(msg, authorisation, refresh_token)
        return b_action
    return None

def handle_processed_prompt(client, bytes, authorisation, refresh_token):
    decoded = bytes.decode('utf8')
    deserialized = json.loads(decoded)

    msg = ''
    query_result = 'queryResult'
    query_text = 'queryText'
    action = 'action'
    parameters = 'parameters'
    number = 'number'
    fulfillmentText = 'fulfillmentText'
    show_tasks = 'task.type'

    if query_result in deserialized and query_text in deserialized[query_result]:
        print('Handling processed prompt: ' + deserialized[query_result][query_text])

    if query_result in deserialized and action in deserialized[query_result]:
        if deserialized[query_result][action] == show_tasks:
            # the user specified the number of tasks
            num = 99999
            if parameters in deserialized[query_result] and number in deserialized[query_result][parameters]:
                num = deserialized[query_result][parameters][number]

                if num != '':
                    msg = 'Here are your last {0} tasks:\n'.format(num)
                else:
                    msg = 'Here are your latest tasks:\n'
            # the user did not specify the number of tasks -> show all
            else:
                msg = 'Here are your latest tasks:\n'

            asana_tasks = get_asana_tasks(client, num)
            msg += format_tasks_list(asana_tasks)
        else:
            print('Unknown user prompt')
            msg = deserialized[query_result][fulfillmentText]

        print('Sent {0} to user'.format(msg))
        send_to_user(msg, authorisation, refresh_token)

def add_to_asana(asana_client, last_tasks, authorisation, refresh_token):
    print("Adding task to Asana")
    for task in last_tasks:
        task_params = {
            'assignee': '381674085905935',
        }
        task_params['name'] = task.title
        task_params_notes = "Description: " + task.description + "\n"
        if len(task.location_list) > 0:
            task_params_notes += "Locations: " + ", ".join(task.location_list) + "\n"
        if len(task.person_list) > 0:
            task_params_notes += "Persons: " + ", ".join(task.person_list) + "\n"
        if len(task.datetime_list) > 0:
            task_params_notes += "Dates: " + ", ".join(task.datetime_list) + "\n"
            task_params["due_on"] = task.datetime_list[0]
        task_params["notes"] = task_params_notes

        result = asana_client.tasks.create_in_workspace(756193103565834, task_params)
        print('Asana result:')
        print(result)
        # authorisation, refresh_token = send_to_user("Tasks added successfully!", authorisation, refresh_token)

def get_asana_tasks(asana_client, page_size):
    tasks = asana_client.get_collection("/tasks", { 'workspace': 756193103565834, 'assignee': 381674085905935 })
    tasks_list = list(tasks)
    tasks_list_cast = []
    
    for task in tasks_list:
        tasks_list_cast.append(Task(
            id = task['id'],
            title = task['name'],
            description = '',
            location_list = [],
            person_list = [],
            datetime_list = []
        ))

    return tasks_list_cast

def format_tasks_list(task_list):
    text = ""
    for task in range(len(task_list)):
        text += '{0}. {1}'.format(str(task + 1), task_list[task].title)
        
        if task_list[task].id is not None:
            text += ' (https://app.asana.com/0/{0}/{1})'.format(756193103565834, task_list[task].id)
        
        text += '\n'

    return text