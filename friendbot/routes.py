from flask import request
from friendbot import app, corpus

export = app.config['EXPORT_DIR']

@app.route('/sentence', methods = ['POST'])
def create_sentence():
    data = request.form
    params = data['text'].split()
    try:
        channel = corpus.getChannel(params[0], export)
        userID = corpus.getUserID(params[1])
    except:
        return "Bad request", 400
    fulltext = corpus.generateCorpus(export, channel, userID)
    sentence = corpus.generateSentence(fulltext)
    return sentence
