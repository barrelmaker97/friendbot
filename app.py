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
    if request.method == 'POST':
        data = request.form # a multidict containing POST data
        params = data['text'].split()
        channel = friend.getChannel(params[0])
        userID = friend.getUserID(params[1])
        corpus = friend.generateCorpus("../export", channel, userID)
        sentences = friend.generateSentence(corpus, 1)
        return sentences[0]

if __name__ == '__main__':
    app.run()
