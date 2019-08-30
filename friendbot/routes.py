from flask import request, jsonify
from friendbot import app, corpus

export = app.config['EXPORT_DIR']

try:
    channels = corpus.getChannels(export)
    channel_dict = corpus.getChannelDict(export)
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
        channel = ""
        user = ""
    else:
        try:
            channel = corpus.verifyChannel(params[0], channels)
            user = corpus.verifyUser(params[1], users)
        except Exception as ex:
            message = str(ex)
            app.logger.error(message)
            resp = jsonify(text=message)
            resp.headers['Friendbot-Error'] = 'True'
            return resp
    fulltext = corpus.generateCorpus(
            export, channel, user, channel_dict, user_dict)
    num_lines = len(fulltext.splitlines(True))
    sentence = corpus.generateSentence(fulltext)
    resp = jsonify(text=sentence)
    resp.headers['Friendbot-Error'] = 'False'
    resp.headers['Friendbot-Corpus-Lines'] = num_lines
    msg = "/sentence from {} Channel: {} User: {}".format(
            request.host, channel, user)
    app.logger.info(msg)
    return resp
