import time
import flask
import ujson
import requests
from prometheus_client import Summary
from friendbot import app, utils, messages

export = app.config["EXPORT"]
signing_secret = app.config["FRIENDBOT_SIGNING_SECRET"]
cache = app.config["REDIS_CACHE"]
models = export["models"]

length_summary = Summary("friendbot_request_time", "Length of Friendbot Requests")


@app.route("/action", methods=["POST"])
def action_endpoint():
    start_time = time.time()
    if signing_secret:
        valid, valid_err = utils.validate_request(flask.request, signing_secret)
        if not valid:
            app.logger.error(valid_err)
            return ("", 400)
    data = ujson.loads(flask.request.form["payload"])
    button_text = data["actions"][0]["text"]["text"]
    error = False
    if button_text == "Send":
        user_id = data["user"]["id"]
        real_name = export["users"][user_id]
        payload = messages.send_message(data["actions"][0]["value"], real_name)
    elif button_text == "Shuffle":
        params = data["actions"][0]["value"].split()
        sentence = utils.get_sentence(models, params[0], params[1], cache)
        payload = messages.prompt_message(sentence, params[0], params[1])
    elif button_text == "Cancel":
        payload = messages.cancel_message()
    else:
        error = True
        payload = messages.error_message()
    headers = {"Content-type": "application/json", "Accept": "text/plain"}
    req_time = time.time() - start_time
    req_time_ms = round(req_time * 1000, 3)
    length_summary.observe(req_time)
    requests.post(data["response_url"], data=payload, headers=headers)
    user_id = data["user"]["id"]
    real_name = export["users"][user_id]
    msg = f"{real_name} ({user_id}) pressed {button_text} {req_time_ms}ms"
    if error:
        app.logger.error(msg)
    else:
        app.logger.info(msg)
    return ("", 200)


@app.route("/sentence", methods=["POST"])
def sentence_endpoint():
    start_time = time.time()
    if signing_secret:
        valid, valid_err = utils.validate_request(flask.request, signing_secret)
        if not valid:
            app.logger.error(valid_err)
            return ("", 400)
    try:
        user_id = flask.request.form["user_id"]
        real_name = export["users"][user_id]
    except Exception as ex:
        msg = "Cannot find user_id of request sender"
        app.logger.error(msg)
        app.logger.debug(ex)
        resp = flask.Response(messages.error_message(), mimetype="application/json")
        resp.headers["Friendbot-Error"] = "True"
        return resp
    params = flask.request.form["text"].split()
    channel = "None"
    user = "None"
    for param in params:
        try:
            channel = utils.parse_argument(param, export["channels"].keys())
        except Exception:
            try:
                user = utils.parse_argument(param, export["users"].keys())
            except Exception as ex:
                msg = f"Failed to parse argument {param}"
                app.logger.error(msg)
                app.logger.debug(ex)
                resp = flask.Response(
                    messages.error_message(), mimetype="application/json"
                )
                resp.headers["Friendbot-Error"] = "True"
                return resp
    sentence = utils.get_sentence(models, user, channel, cache)
    payload = messages.prompt_message(sentence, user, channel)
    resp = flask.Response(payload, mimetype="application/json")
    resp.headers["Friendbot-Error"] = "False"
    resp.headers["Friendbot-User"] = user
    resp.headers["Friendbot-Channel"] = channel
    req_time = time.time() - start_time
    req_time_ms = round(req_time * 1000, 3)
    length_summary.observe(req_time)
    msg = f"{real_name} ({user_id}) generated a sentence; C: {channel} U: {user} {req_time_ms}ms"
    app.logger.info(msg)
    return resp


@app.route("/health", methods=["GET"])
def health_endpoint():
    start_time = time.time()
    sentence = utils.get_sentence(models, "None", "None", cache)
    resp = flask.Response(
        messages.health_message(sentence), mimetype="application/json"
    )
    req_time = time.time() - start_time
    req_time_ms = round(req_time * 1000, 3)
    length_summary.observe(req_time)
    app.logger.debug(f"Health Check Successful {req_time_ms}ms")
    return resp
