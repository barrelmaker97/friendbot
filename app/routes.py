from flask import request
from app import app, corpus

@app.route('/', methods = ['POST'])
def sentence():
    data = request.form
    params = data['text'].split()
    channel = corpus.getChannel(params[0])
    userID = corpus.getUserID(params[1])
    fulltext = corpus.generateCorpus("../export", channel, userID)
    sentence = corpus.generateSentence(fulltext)
    return sentence
