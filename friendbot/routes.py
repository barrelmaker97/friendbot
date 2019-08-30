from flask import request, jsonify
from friendbot import app, corpus

export = app.config['EXPORT_DIR']

try:
    channels = corpus.getChannels(export)
    app.logger.info("Channels loaded from export")
except Exception as ex:
    ex_name = "An exception of type {} occurred.".format(type(ex).__name__)
    app.logger.error("{} Channels not loaded!".format(ex_name))

try:
    users = corpus.getUsers(export)
    user_dict = corpus.getUserDict(export)
    app.logger.info("Users loaded from export")
except Exception as ex:
    ex_name = "An exception of type {} occurred.".format(type(ex).__name__)
    app.logger.error("{} Users not loaded!".format(ex_name))


@app.route("/sentence", methods=['POST'])
def create_sentence():
    data = request.form
    params = data['text'].split()
    if(len(params) == 0):
        req_channel = "all"
        req_user = "all"
    else:
        req_channel = params[0]
        req_user = params[1]
    msg = "/sentence from {} Channel: {} User: {}".format(
            request.host, req_channel, req_user)
    app.logger.info(msg)
    try:
        channel = corpus.verifyChannel(req_channel, channels)
        user = corpus.verifyUser(req_user, users)
    except Exception as ex:
        message = str(ex)
        app.logger.error(message)
        resp = jsonify(text=message)
        resp.headers['Friendbot-Error'] = 'True'
        return resp
    fulltext = corpus.generateCorpus(export, channel, user, user_dict)
    num_lines = len(fulltext.splitlines(True))
    sentence = corpus.generateSentence(fulltext)
    resp = jsonify(text=sentence)
    resp.headers['Friendbot-Error'] = 'False'
    resp.headers['Friendbot-Corpus-Lines'] = num_lines
    return resp
