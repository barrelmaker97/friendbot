from flask import request, jsonify
from friendbot import app, corpus

export = app.config['EXPORT_DIR']

try:
    channel_dict = corpus.getChannelDict(export)
    channels = channel_dict.keys()
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
    channel = "None"
    user = "None"
    for param in params:
        try:
            channel = corpus.verifyChannel(param, channels)
        except Exception:
            try:
                user = corpus.verifyUser(param, users)
            except Exception as ex:
                return errorResponse(ex)
    fulltext = corpus.generateCorpus(
            export, channel, user, channel_dict, user_dict)
    num_lines = len(fulltext.splitlines(True))
    sentence = corpus.generateSentence(fulltext)
    resp = jsonify(text=sentence)
    resp.headers['Friendbot-Error'] = 'False'
    resp.headers['Friendbot-Corpus-Lines'] = num_lines
    resp.headers['Friendbot-User'] = user
    resp.headers['Friendbot-Channel'] = channel
    msg = "/sentence from {} Channel: {} User: {}".format(
            request.host, channel, user)
    app.logger.info(msg)
    return resp


def errorResponse(ex):
    message = str(ex)
    app.logger.error(message)
    resp = jsonify(text=message)
    resp.headers['Friendbot-Error'] = 'True'
    return resp
