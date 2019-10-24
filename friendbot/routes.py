from friendbot import app, corpus
import requests
import flask
import json

export = app.config["EXPORT"]
channel_dict = app.config["CHANNEL_DICT"]
channels = app.config["CHANNELS"]
user_dict = app.config["USER_DICT"]
users = app.config["USERS"]


@app.route("/action", methods=["POST"])
def action_endpoint():
    data = flask.request.form["payload"]
    json_data = json.loads(data)
    button_value = json_data["actions"][0]["value"]
    button_text = json_data["actions"][0]["text"]["text"]
    response_url = json_data["response_url"]
    user_id = json_data["user"]["id"]
    real_name = user_dict[user_id]
    headers = {"Content-type": "application/json", "Accept": "text/plain"}
    error = False
    if button_text == "Send":
        payload = actionSend(button_value, real_name)
    elif button_text == "Shuffle":
        params = button_value.split()
        sentence = corpus.generateSentence(
            export, params[0], params[1], user_dict, channel_dict
        )
        payload = createPrompt(sentence, params[0], params[1])
    elif button_text == "Cancel":
        payload = actionCancel()
    else:
        error = True
        payload = errorMessage()
    headers.update({"Friendbot-Error": str(error)})
    requests.post(response_url, data=payload, headers=headers)
    msg = "{} ({}) pressed {}"
    format_msg = msg.format(real_name, user_id, button_text)
    if error:
        app.logger.error(format_msg)
    else:
        app.logger.info(format_msg)
    return ("", 200)


@app.route("/sentence", methods=["POST"])
def sentence_endpoint():
    user_id = flask.request.form["user_id"]
    real_name = user_dict[user_id]
    params = flask.request.form["text"].split()
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
    sentence = corpus.generateSentence(export, user, channel, user_dict, channel_dict)
    payload = createPrompt(sentence, user, channel)
    resp = flask.Response(payload, mimetype="application/json")
    error = False
    resp.headers["Friendbot-Error"] = str(error)
    resp.headers["Friendbot-User"] = user
    resp.headers["Friendbot-Channel"] = channel
    msg = "{} ({}) generated a sentence; Channel: {} User: {}"
    format_msg = msg.format(real_name, user_id, channel, user)
    if error:
        app.logger.error(format_msg)
    else:
        app.logger.info(format_msg)
    return resp


@app.route("/status", methods=["GET"])
def status_endpoint():
    return ("", 200)


@app.route("/export", methods=["GET", "POST"])
def export_endpoint():
    return ("", 200)


def errorResponse(ex):
    message = str(ex)
    app.logger.error(message)
    resp = flask.jsonify(text=message)
    resp.headers["Friendbot-Error"] = "True"
    return resp


def errorMessage():
    payload = {
        "response_type": "ephemeral",
        "replace_original": False,
        "text": "Sorry, that didn't work. Please try again.",
    }
    return json.dumps(payload)


def actionCancel():
    payload = {"delete_original": True}
    return json.dumps(payload)


def actionSend(sentence, real_name):
    context_msg = "Sent by {}".format(real_name)
    payload = {
        "delete_original": True,
        "response_type": "in_channel",
        "blocks": [
            {"type": "section", "text": {"type": "plain_text", "text": sentence}},
            {
                "type": "context",
                "elements": [{"type": "plain_text", "text": context_msg}],
            },
        ],
    }
    return json.dumps(payload)


def createPrompt(sentence, user, channel):
    payload = {
        "replace_original": True,
        "response_type": "ephemeral",
        "blocks": [
            {"type": "section", "text": {"type": "plain_text", "text": sentence}},
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "emoji": True, "text": "Send"},
                        "style": "primary",
                        "value": sentence,
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": "Shuffle",
                        },
                        "value": "{} {}".format(user, channel),
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "emoji": True, "text": "Cancel"},
                        "style": "danger",
                        "value": "cancel",
                    },
                ],
            },
        ],
    }
    return json.dumps(payload)
