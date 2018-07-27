import urllib
import json
import re

base = "https://clean-sprint-app.intheloop.io"
authorisation='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1X2lkIjoiMTEyIiwiYXRfaWQiOiIxMTJfZDE5MzdiZjEtZTk5MS1mMDdlLTMyYmQtNjNmNmY4ZDM1NzNkIiwibmJmIjoxNTMyNjc4MzUyLCJleHAiOjE1MzI2ODE5NTIsImlhdCI6MTUzMjY3ODM1Mn0.WUYBYPoOj9yVx8_peoSSIymG4AKNMrp0Aiv7VlaFS-k'
user = 'user_507'

# request na vsake tok časa da preveri keri so kej novi emaili
sinceId = 17917142106750716
while True:
    data = urllib.parse.urlencode(
        {'offset': 0,
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
            req.add_header("Authorization",authorisation)
            response = urllib.request.urlopen(req).read()
            print("extracting...")
