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
    data = request.form
    params = data['text'].split()
    if(len(params) == 0):
        req_channel = "all"
        req_user = "all"
    else:
        req_channel = params[0].lower()
        req_user = params[1].lower()
    msg = "/sentence from {} Channel: {} User: {}".format(
            request.host, req_channel, req_user)
    app.logger.info(msg)
    try:
        channel = corpus.interpretChannel(req_channel, channels)
    except Exception as ex:
        ex_name = "An exception of type {} occurred.".format(type(ex).__name__)
        app.logger.error("{} Channel not found!".format(ex_name))
        resp = jsonify(text="Error: Channel not found")
        resp.headers['Friendbot-Error'] = 'True'
        return resp
    try:
        userID = corpus.interpretName(req_user, names)
    except Exception as ex:
        ex_name = "An exception of type {} occurred.".format(type(ex).__name__)
        app.logger.error("{} User not found!".format(ex_name))
        resp = jsonify(text="Error: User not found")
        resp.headers['Friendbot-Error'] = 'True'
        return resp
    fulltext = corpus.generateCorpus(export, channel, userID, userIDs)
    num_lines = len(fulltext.splitlines(True))
    sentence = corpus.generateSentence(fulltext)
    resp = jsonify(text=sentence)
    resp.headers['Friendbot-Error'] = 'False'
    resp.headers['Friendbot-Corpus-Lines'] = num_lines
    return resp
