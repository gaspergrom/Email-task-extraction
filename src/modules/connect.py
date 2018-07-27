import re
import os
import json
import asana
import urllib
import numpy as np

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
base = "https://clean-sprint-app.intheloop.io"
authorisation = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMTEyIiwiYXRfaWQiOiIxMTJfZDE5MzdiZjEtZTk5MS1mMDdlLTMyYmQtNjNmNmY4ZDM1NzNkIiwibmJmIjoxNTMyNjc4MzUyLCJleHAiOjE1MzI2ODE5NTIsImlhdCI6MTUzMjY3ODM1Mn0.WUYBYPoOj9yVx8_peoSSIymG4AKNMrp0Aiv7VlaFS-k'
user = 'user_507'


# asana = {"data": {"id": 381674085905935,
#                  "workspaces": [{"id": 609331104373920, "name": "Private"},
#                                 {"id": 756193103565834, "name": "Sicilija"}]}}
def send_to_user(msg):
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
    req.add_header("Authorization", authorisation)
    response = urllib.request.urlopen(req).read()


def start_serve(nn, mail_callback):
    # request na vsake tok časa da preveri keri so kej novi emaili
    sinceId = 17933766156402694
    asana_code = str(input("Vnesi asana code: "))
    last_tasks = []

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
        req.add_header("Authorization", authorisation)
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
                last_tasks = np.array(mail_callback(nn, sentences))
                print("Got an email")
                if (len(last_tasks) > 0):
                    if (len(last_tasks) > 1):
                        comment_text = "Found 1 task in your latest email:\n"
                    else:
                        comment_text = "Found " + str(len(last_tasks)) + " tasks in your latest email:\n"
                    for task in last_tasks:
                        comment_text += " - " + task.description
                    send_to_user(comment_text)

            elif (type == "CommentChat"):
                addtask = response["resources"][0]["comment"]["snippet"].strip().split()[0]

                if (addtask == "asana"):
                    if len(last_tasks) > 0:
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
                            task_params.title = task.title
                            task_params_notes = "Description: " + task.description + "\n"
                            if len(task.location_list) > 0:
                                task_params_notes += "Locations: " + ", ".join(task.location_list) + "\n"
                            if len(task.person_list) > 0:
                                task_params_notes += "Persons: " + ", ".join(task.person_list) + "\n"
                            if len(task.date_list) > 0:
                                task_params_notes += "Dates: " + ", ".join(task.date_list) + "\n"
                                task_params["due_on"] = task.date_list[0]
                            if len(task.time_list) > 0:
                                task_params_notes += "Times: " + ", ".join(task.time_list) + "\n"
                            task_params["notes"] = task_params_notes

                            result = client.tasks.create_in_workspace(756193103565834, task_params)
                            send_to_user("Tasks added successfully!")
