from flask import Flask
from flask import request
import friend

app = Flask(__name__)

@app.route('/', methods = ['POST'])
def sentence():
    data = request.form
    params = data['text'].split()
    channel = friend.getChannel(params[0])
    userID = friend.getUserID(params[1])
    corpus = friend.generateCorpus("../export", channel, userID)
    sentence = friend.generateSentence(corpus)
    return sentence

if __name__ == '__main__':
    app.run()
