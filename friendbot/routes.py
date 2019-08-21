from flask import request, jsonify
from friendbot import app, corpus

export = app.config['EXPORT_DIR']

@app.route('/sentence', methods = ['POST'])
def create_sentence():
    data = request.form
    params = data['text'].split()
    try:
        channel = corpus.getChannel(params[0], export)
    except:
        resp = jsonify(text="Error: Channel not found")
        resp.headers['Friendbot-Error'] = 'True'
        return resp
    try:
        userID = corpus.getUserID(params[1])
    except:
        resp = jsonify(text="Error: User not found")
        resp.headers['Friendbot-Error'] = 'True'
        return resp
    fulltext = corpus.generateCorpus(export, channel, userID)
    sentence = corpus.generateSentence(fulltext)
    resp = jsonify(text=sentence)
    resp.headers['Friendbot-Error'] = 'False'
    return resp
