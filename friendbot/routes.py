from flask import request, jsonify
from friendbot import app, corpus
import json

export = app.config['EXPORT_DIR']

try:
    channel_dict = corpus.getChannelDict(export)
    channels = channel_dict.keys()
    app.logger.info("Channels loaded from export")
except Exception as ex:
    ex_name = "An exception of type {} occurred.".format(type(ex).__name__)
    app.logger.error("{} Channels not loaded!".format(ex_name))

try:
    user_dict = corpus.getUserDict(export)
    users = user_dict.keys()
    app.logger.info("Users loaded from export")
except Exception as ex:
    ex_name = "An exception of type {} occurred.".format(type(ex).__name__)
    app.logger.error("{} Users not loaded!".format(ex_name))


@app.route("/action", methods=['POST'])
def take_action():
    data = request.get_data().decode('utf8')
    json_data = json.loads(data)
    button_value = json_data['actions'][0]['value']
    msg = "/action {}".format(button_value)
    app.logger.info(msg)
    return ('', 204)


@app.route("/sentence", methods=['POST'])
def create_sentence():
    data = request.form
    params = data['text'].split()
    channel = "None"
    user = "None"
    for param in params:
        try:
            channel = corpus.parseArg(param, channels)
        except Exception:
            try:
                user = corpus.parseArg(param, users)
            except Exception as ex:
                return errorResponse(ex)
    fulltext = corpus.generateCorpus(
            export, channel, user, channel_dict, user_dict)
    num_lines = len(fulltext.splitlines(True))
    sentence = corpus.generateSentence(fulltext)
    resp = createResponse(sentence)
    error = 'False'
    resp.headers['Friendbot-Error'] = error
    resp.headers['Friendbot-Corpus-Lines'] = num_lines
    resp.headers['Friendbot-User'] = user
    resp.headers['Friendbot-Channel'] = channel
    msg = "/sentence Channel: {} User: {} Error: {} Lines: {}"
    msg.format(channel, user, error, num_lines)
    app.logger.info(msg)
    return resp


def errorResponse(ex):
    message = str(ex)
    app.logger.error(message)
    resp = jsonify(text=message)
    resp.headers['Friendbot-Error'] = 'True'
    return resp


def createResponse(sentence):
    resp_data = {
            "response_type": "ephemeral",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": sentence
                        }
                    },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "emoji": True,
                                "text": "Send"
                                },
                            "style": "primary",
                            "value": "click_me_123"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "emoji": True,
                                "text": "Shuffle"
                                },
                            "value": "click_me_123"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "emoji": True,
                                "text": "Cancel"
                                },
                            "style": "danger",
                            "value": "click_me_123"
                            }
                        ]
                    }
                ]
            }
    return jsonify(resp_data)
