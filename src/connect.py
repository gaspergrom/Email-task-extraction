from flask import Flask
import json
app = Flask(__name__)

@app.route("/")
def home():
    return open(r'views/index.html', encoding='utf-8', errors='ignore').read()


@app.route("/extract")
def extract():
    return json.dumps({
            "title": "",
            "description": "",
            "time": "",
            "author": "",
            "location": "",
            "asana_link": "",
            "trello_link": "",
            "calendar_link": "",
            })