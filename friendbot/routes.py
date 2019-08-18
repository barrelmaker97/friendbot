from flask import request
from friendbot import app, corpus

@app.route('/sentence', methods = ['POST'])
def create_sentence():
    data = request.form
    params = data['text'].split()
    channel = corpus.getChannel(params[0])
    userID = corpus.getUserID(params[1])
    fulltext = corpus.generateCorpus("../export", channel, userID)
    sentence = corpus.generateSentence(fulltext)
    return sentence
