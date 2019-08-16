from flask import Flask
from flask import request
import friend

app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def user():
    if request.method == 'GET':
        channel = friend.getChannel("all")
        userID = friend.getUserID("all")
        corpus = friend.generateCorpus("../export", channel, userID)
        sentences = friend.generateSentence(corpus, 1)
        return sentences[0]
    if request.method == 'GET':
        data = request.form # a multidict containing POST data

if __name__ == '__main__':
    app.run()
