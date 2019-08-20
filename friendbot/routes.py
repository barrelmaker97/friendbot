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
        return jsonify(text="Channel not found")
    try:
        userID = corpus.getUserID(params[1])
    except:
        return jsonify(text="User not found")
    fulltext = corpus.generateCorpus(export, channel, userID)
    sentence = corpus.generateSentence(fulltext)
    return jsonify(text=sentence)
