from flask import request, jsonify
from friendbot import app, corpus

export = app.config['EXPORT_DIR']
try:
    userIDs = corpus.getUserIDs(export)
    app.logger.info("User IDs loaded from export")
except Exception as ex:
    ex_name = "An exception of type {} occurred.".format(type(ex).__name__)
    app.logger.error("{} User IDs not loaded!".format(ex_name))

try:
    names = corpus.getNames(export)
    app.logger.info("Names loaded from export")
except Exception as ex:
    ex_name = "An exception of type {} occurred.".format(type(ex).__name__)
    app.logger.error("{} Names not loaded!".format(ex_name))

try:
    channels = corpus.getChannels(export)
    app.logger.info("Channels loaded from export")
except Exception as ex:
    ex_name = "An exception of type {} occurred.".format(type(ex).__name__)
    app.logger.error("{} Channels not loaded!".format(ex_name))


@app.route("/sentence", methods=['POST'])
def create_sentence():
    app.logger.info("Request at /sentence from {}".format(request.host))
    data = request.form
    params = data['text'].split()
    try:
        channel = corpus.interpretChannel(params[0], channels)
    except Exception as ex:
        ex_name = "An exception of type {} occurred.".format(type(ex).__name__)
        app.logger.error("{} Channel not found!".format(ex_name))
        resp = jsonify(text="Error: Channel not found")
        resp.headers['Friendbot-Error'] = 'True'
        return resp
    try:
        userID = corpus.interpretName(params[1], names)
    except Exception as ex:
        ex_name = "An exception of type {} occurred.".format(type(ex).__name__)
        app.logger.error("{} User not found!".format(ex_name))
        resp = jsonify(text="Error: User not found")
        resp.headers['Friendbot-Error'] = 'True'
        return resp
    fulltext = corpus.generateCorpus(export, channel, userID, userIDs)
    sentence = corpus.generateSentence(fulltext)
    resp = jsonify(text=sentence)
    resp.headers['Friendbot-Error'] = 'False'
    return resp
