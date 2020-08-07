from friendbot import app, corpus, messages
import requests
import flask
import ujson
import hmac
import hashlib

export = app.config["EXPORT"]
channel_dict = app.config["CHANNEL_DICT"]
channels = app.config["CHANNELS"]
user_dict = app.config["USER_DICT"]
users = app.config["USERS"]
signing_secret = app.config["SLACK_SIGNING_SECRET"]


@app.route("/action", methods=["POST"])
def action_endpoint():
    if signing_secret is not None:
        validate_request(flask.request)
    data = flask.request.form["payload"]
    json_data = ujson.loads(data)
    button_value = json_data["actions"][0]["value"]
    button_text = json_data["actions"][0]["text"]["text"]
    response_url = json_data["response_url"]
    user_id = json_data["user"]["id"]
    real_name = user_dict[user_id]
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
    headers = {
        "Content-type": "application/json",
        "Accept": "text/plain",
        "Friendbot-Error": str(error),
    }
    requests.post(response_url, data=payload, headers=headers)
    msg = f"{real_name} ({user_id}) pressed {button_text}"
    if error:
        app.logger.error(msg)
    else:
        app.logger.info(msg)
    return ("", 200)


@app.route("/sentence", methods=["POST"])
def sentence_endpoint():
    if signing_secret is not None:
        validate_request(flask.request)
    try:
        user_id = flask.request.form["user_id"]
        if user_id == "healthcheck":
            real_name = "Health Check"
        else:
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
                msg = f"Failed to parse argument {param}"
                app.logger.error(msg)
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
    msg = f"{real_name} ({user_id}) generated a sentence; C: {channel} U: {user}"
    app.logger.info(msg)
    return resp


@app.route("/export", methods=["POST"])
def export_endpoint():
    app.logger.info("Recieved export")
    f = flask.request.files["export"]
    return ("", 200)


def validate_request(request):
    try:
        request_body = request.get_data().decode("utf-8")
        timestamp = request.headers["X-Slack-Request-Timestamp"]
        slack_signature = request.headers["X-Slack-Signature"]
        slack_basestring = f"v0:{timestamp}:{request_body}".encode("utf-8")
        slack_signing_secret = bytes(signing_secret, "utf-8")
        my_signature = (
            "v0="
            + hmac.new(
                slack_signing_secret, slack_basestring, hashlib.sha256
            ).hexdigest()
        )
        assert hmac.compare_digest(my_signature, slack_signature)
        return True
    except Exception as ex:
        app.logger.error("Request verification failed!")
        return False
