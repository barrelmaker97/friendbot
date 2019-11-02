from friendbot import app, corpus, messages
import requests
import flask
import ujson

export = app.config["EXPORT"]
channel_dict = app.config["CHANNEL_DICT"]
channels = app.config["CHANNELS"]
user_dict = app.config["USER_DICT"]
users = app.config["USERS"]


@app.route("/action", methods=["POST"])
def action_endpoint():
    data = flask.request.form["payload"]
    json_data = ujson.loads(data)
    button_value = json_data["actions"][0]["value"]
    button_text = json_data["actions"][0]["text"]["text"]
    response_url = json_data["response_url"]
    user_id = json_data["user"]["id"]
    real_name = user_dict[user_id]
    headers = {"Content-type": "application/json", "Accept": "text/plain"}
    error = False
    if button_text == "Send":
        payload = messages.sendMessage(button_value, real_name)
    elif button_text == "Shuffle":
        params = button_value.split()
        sentence = corpus.generateSentence(
            export, params[0], params[1], user_dict, channel_dict
        )
        payload = messages.promptMessage(sentence, params[0], params[1])
    elif button_text == "Cancel":
        payload = messages.cancelMessage()
    else:
        error = True
        payload = messages.errorMessage()
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
    try:
        user_id = flask.request.form["user_id"]
        real_name = user_dict[user_id]
    except Exception as ex:
        msg = "Cannot find user_id of request sender"
        app.logger.error(msg)
        resp = flask.Response(messages.errorMessage(), mimetype="application/json")
        resp.headers["Friendbot-Error"] = "True"
        return resp
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
                msg = "Failed to parse argument {}"
                format_msg = msg.format(param)
                app.logger.error(format_msg)
                resp = flask.Response(
                    messages.errorMessage(), mimetype="application/json"
                )
                resp.headers["Friendbot-Error"] = "True"
                return resp
    sentence = corpus.generateSentence(export, user, channel, user_dict, channel_dict)
    payload = messages.promptMessage(sentence, user, channel)
    resp = flask.Response(payload, mimetype="application/json")
    resp.headers["Friendbot-Error"] = "False"
    resp.headers["Friendbot-User"] = user
    resp.headers["Friendbot-Channel"] = channel
    msg = "{} ({}) generated a sentence; Channel: {} User: {}"
    format_msg = msg.format(real_name, user_id, channel, user)
    app.logger.info(format_msg)
    return resp


@app.route("/status", methods=["GET"])
def status_endpoint():
    return ("", 200)


@app.route("/export", methods=["POST"])
def export_endpoint():
    app.logger.info("Recieved export")
    f = flask.request.files["export"]
    return ("", 200)
