import urllib
import json
import re
import asana
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
base = "https://clean-sprint-app.intheloop.io"
authorisation = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMTEyIiwiYXRfaWQiOiIxMTJfZDE5MzdiZjEtZTk5MS1mMDdlLTMyYmQtNjNmNmY4ZDM1NzNkIiwibmJmIjoxNTMyNjc4MzUyLCJleHAiOjE1MzI2ODE5NTIsImlhdCI6MTUzMjY3ODM1Mn0.WUYBYPoOj9yVx8_peoSSIymG4AKNMrp0Aiv7VlaFS-k'
user = 'user_507'
# asana = {"data": {"id": 381674085905935,
#                  "workspaces": [{"id": 609331104373920, "name": "Private"},
#                                 {"id": 756193103565834, "name": "Sicilija"}]}}

def start_serve(mail_callback):
    # request na vsake tok časa da preveri keri so kej novi emaili
    sinceId = 17917142106750716

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
                mail_callback(sentences)

                print("Got an email")
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
                    "comment": json.dumps(sentences),
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
                print("extracting...")
            elif (type == "CommentChat"):
                addtask = response["resources"][0]["comment"]["snippet"].trim().split()[0]

                if (addtask == "asana"):
                    print("adding task to asana...")
                    client = asana.Client.oauth(
                        client_id='759566842403050',
                        client_secret='6316248cc3531236f6796574ef8bcc4a',
                        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
                    )

                    client.session.fetch_token(code="0/6abffce3c47301527dfd6389c3531122")
                    result = client.tasks.create_in_workspace(756193103565834, {
                        'name': 'Learn to use Nunchucks',
                        'notes': 'This is a test task created with the python-asana client.',
                        'assignee': '381674085905935'
                    })
