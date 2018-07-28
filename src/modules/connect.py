import re
import os
import json
import asana
import urllib
import numpy as np

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
base = "https://clean-sprint-app.intheloop.io"
user = 'user_507'

def refresh_token(auth, refresh):
    data = json.dumps({
        "accessToken": auth,
        "refreshToken": refresh
    }).encode("utf-8")

    r = urllib.request.Request(base + '/api/v1/comment/chat', data)
    r.add_header("Content-Type",
                 'application/json')
    r.add_header("Authorization", "Bearer " + auth)
    res = urllib.request.urlopen(r).read()
    authorisation = json.loads(res)["accessToken"]
    refresh_token = json.loads(res)["refreshToken"]
    return authorisation, refresh_token

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
        auth, refresh=refresh_token(auth, refresh)
        req = urllib.request.Request(base + '/api/v1/comment/chat', data)
        req.add_header("Content-Type",
                       'application/json')
        req.add_header("Authorization", "Bearer " + auth)
        response = urllib.request.urlopen(req).read()
    return auth, refresh


def start_serve(nn, mail_callback):
    # request na vsake tok časa da preveri keri so kej novi emaili
    sinceId = 17933766156402694
    asana_code = str(input("Vnesi asana code: "))
    last_tasks = []
    base = "https://clean-sprint-app.intheloop.io"
    authorisation = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMTEyIiwiYXRfaWQiOiIxMTJfOTBkZWFkNDQtZDRhZi0zZDY0LTY0YjgtZDY0N2M0ZTcwNDc3IiwibmJmIjoxNTMyNzY3MTc1LCJleHAiOjE1MzI3NzA3NzUsImlhdCI6MTUzMjc2NzE3NX0.VjDWYiKS3ja5dClZw6cSPYxc0RVFyDiRQzYNeGFaq78'
    user = 'user_507'
    refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMTEyIiwiYXRfaWQiOiIxMTJfNTk1ZDdlMmUtZDQyYy1mNjVhLThiODEtMmY0MjE2YTY4YTQ2IiwibmJmIjoxNTMyNzY2Mzk1LCJleHAiOjE1MzI3Njk5OTUsImlhdCI6MTUzMjc2NjM5NX0.cCCwviQt2KzTDDGfVML-0Ihjk4yZyBmui8YQyuNo6kI"

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
            authorisation, refresh_token = refresh_token(authorisation, refresh_token)
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
                last_tasks = mail_callback(nn, sentences, content)
                print("Got an email")
                if (len(last_tasks) > 0):
                    if (len(last_tasks) > 1):
                        comment_text = "Found " + str(len(last_tasks)) + " tasks in your latest email:\n"
                    else:
                        comment_text = "Found 1 task in your latest email:\n"
                    for task in last_tasks:
                        comment_text += " - " + task.title + "\n"
                    authorisation, refresh_token = send_to_user(comment_text, authorisation, refresh_token)

                    ## DEBUGGING
                    add_to_asana(asana_code, last_tasks, authorisation, refresh_token)

            elif (type == "CommentChat"):
                addtask = response["resources"][0]["comment"]["snippet"].strip().split()[0]

                if (addtask == "asana"):
                    if len(last_tasks) > 0:
                        add_to_asana(asana_code, last_tasks, authorisation, refresh_token)

def add_to_asana(asana_code, last_tasks, authorisation, refresh_token):
    print("adding task to asana...")
    client = asana.Client.oauth(
        client_id='759566842403050',
        client_secret='6316248cc3531236f6796574ef8bcc4a',
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
    )

    client.session.fetch_token(code=asana_code)
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

        result = client.tasks.create_in_workspace(756193103565834, task_params)
        authorisation, refresh_token = send_to_user("Tasks added successfully!", authorisation, refresh_token)