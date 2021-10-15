import re
import time
import hmac
import json
import pathlib
import hashlib
import markovify
from zipfile import ZipFile
from multiprocessing import Process
from collections import defaultdict

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


def generate_models(users, channels, messages):
    models = {}
    all_users = list(users.keys())
    all_channels = list(channels.keys())
    all_users.append("None")
    all_channels.append("None")
    for user in all_users:
        for channel in all_channels:
            if fulltext := generate_corpus(users, channels, user, channel, messages):
                try:
                    text_model = markovify.NewlineText(fulltext, retain_original=False).compile(inplace=True)
                except KeyError:
                    pass
                model_name = f"{user}:{channel}"
                models.update({model_name: text_model.to_json()})
    return models


def read_export(location):
    zip_location = pathlib.Path(location).resolve()
    users = {}
    channels = {}
    messages = defaultdict(list)
    with ZipFile(zip_location, "r") as zip_object:
        for name in zip_object.namelist():
            filename = pathlib.PurePath(name)
            if filename.match("*.json"):
                file_data = json.load(zip_object.open(name))
                if len(filename.parents) == 1:
                    if filename.stem == "users":
                        for item in file_data:
                            if real_name := item.get("real_name"):
                                users.update({item.get("id"): real_name})
                    elif filename.stem == "channels":
                        for item in file_data:
                            if name := item.get("name"):
                                channels.update({item.get("id"): name})
                else:
                    for item in file_data:
                        if not item.get("subtype"):
                            for key in list(item.keys()):
                                if key not in ["text", "user"]:
                                    item.pop(key, None)
                            messages[str(filename.parent)].append(item)
    return users, channels, messages


def generate_corpus(users, channels, userID, channel, messages):
    fulltext = ""
    if channel == "None":
        data = [item for sublist in messages.values() for item in sublist]
    else:
        data = messages[channels.get(channel)]
    for message in data:
        text = str(message.get("text"))
        if "<@U" in text:
            for user in users:
                text = text.replace(f"<@{user}>", users.get(user))
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


def get_sentence(user, channel, cache):
    sentence_name = f"{user}:{channel}:sentence"
    cache_process = Process(target=cache_sentence, args=(user, channel, cache))
    if raw_sentence := cache.rpop(sentence_name):
        try:
            sentence = raw_sentence.decode("utf-8")
        except Exception:
            sentence = create_sentence(user, channel, cache)
    else:
        sentence = create_sentence(user, channel, cache)
    cache_process.start()
    return sentence


def create_sentence(user, channel, cache):
    model_name = f"{user}:{channel}"
    if cache.exists(model_name):
        model = cache.get(model_name)
        loaded_model = markovify.Text.from_json(model)
        sentence = loaded_model.make_sentence(tries=100)
        if isinstance(sentence, str):
            return sentence


def cache_sentence(user, channel, cache):
    sentence_name = f"{user}:{channel}:sentence"
    while cache.llen(sentence_name) < 10:
        if sentence := create_sentence(user, channel, cache):
            cache.lpush(sentence_name, sentence)
        else:
            break


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
    except Exception:
        err = "Request verification failed! Signature did not match"
        return (False, err)
