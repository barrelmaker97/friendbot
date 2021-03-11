from multiprocessing import Process
import redis
import re
import markovify
import hmac
import hashlib
import time

regex = re.compile(r'<(?:[^"\\]|\\.)*>', re.IGNORECASE)


def parse_argument(arg, options):
    try:
        fix = arg.replace("&lt;", "<").replace("&gt;", ">")
        clean = re.search("<.(.*)>", fix).group(1)
        final = clean.split("|")[0]
    except Exception:
        raise Exception(f"Could not parse argument {arg}")
    if final in options:
        return final
    raise Exception(f"Argument {final} not found")


def generate_corpus(export, userID, channel, messages):
    fulltext = ""
    if channel == "None":
        data = [item for sublist in messages.values() for item in sublist]
    else:
        data = messages[export["channels"].get(channel)]
    for message in data:
        text = str(message.get("text"))
        if "<@U" in text:
            for user in export["users"]:
                text = text.replace(f"<@{user}>", export["users"].get(user))
        text = regex.sub("", text)
        if text:
            if userID == "None":
                text += "\n"
                fulltext += text
            else:
                user = message.get("user")
                if user == userID:
                    text += "\n"
                    fulltext += text
    return fulltext


def create_sentence(export, user, channel, cache):
    model_name = f"{user}_{channel}"
    try:
        if cache.exists(model_name):
            raw_data = cache.get(model_name)
            text_model = markovify.Text.from_json(raw_data)
        else:
            text_model = markovify.Text.from_json(export["models"].get(model_name))
            cache.set(model_name, text_model.to_json())
    except redis.exceptions.ConnectionError as ex:
        text_model = markovify.Text.from_json(export["models"].get(model_name))
    sentence = text_model.make_sentence(tries=100)
    if isinstance(sentence, str):
        return sentence


def pregen_sentence(export, user, channel, cache):
    pregen_name = f"{user}_{channel}_pregen"
    pregen_sentence = create_sentence(export, user, channel, cache)
    try:
        cache.set(pregen_name, pregen_sentence)
    except redis.exceptions.ConnectionError as ex:
        pass


def validate_request(request, signing_secret):
    max_time = 5  # This is in minutes
    try:
        request_body = request.get_data().decode("utf-8")
        timestamp = request.headers["X-Slack-Request-Timestamp"]
        if abs(time.time() - int(timestamp)) > 60 * max_time:
            err = f"Request verification failed! Request older than {max_time} minutes"
            return (False, err)
        slack_signature = request.headers["X-Slack-Signature"]
        slack_basestring = f"v0:{timestamp}:{request_body}".encode("utf-8")
        slack_signing_secret = bytes(signing_secret, "utf-8")
        my_signature = hmac.new(
            slack_signing_secret, slack_basestring, hashlib.sha256
        ).hexdigest()
        assert hmac.compare_digest(f"v0={my_signature}", slack_signature)
        return (True, "")
    except Exception as ex:
        err = "Request verification failed! Signature did not match"
        return (False, err)


def get_sentence(export, user, channel, cache):
    pregen_name = f"{user}_{channel}_pregen"
    try:
        if cache.exists(pregen_name):
            sentence = cache.get(pregen_name).decode("utf-8")
            cache.delete(pregen_name)
        else:
            sentence = create_sentence(export, user, channel, cache)
    except redis.exceptions.ConnectionError as ex:
        sentence = create_sentence(export, user, channel, cache)
    pregen_process = Process(
        target=pregen_sentence, args=(export, user, channel, cache)
    )
    pregen_process.start()
    return sentence
