from pathlib import Path
import redis
import json
import re
import sys
import markovify

regex = re.compile(r'<(?:[^"\\]|\\.)*>', re.IGNORECASE)


def get_user_dict(export):
    user_dict = {}
    data = _read_json_file(f"{export}/users.json")
    for user in data:
        if real_name := user.get("real_name"):
            user_id = user.get("id")
            user_dict.update({user_id: real_name})
    return user_dict


def get_channel_dict(export):
    channel_dict = {}
    data = _read_json_file(f"{export}/channels.json")
    for channel in data:
        if name := channel.get("name"):
            channel_id = channel.get("id")
            channel_dict.update({channel_id: name})
    return channel_dict


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


def _read_json_file(path):
    with open(path) as f:
        return json.load(f)


def _generate_corpus(export, userID, channel, user_dict, channel_dict):
    if channel == "None":
        channel_directory = export
    else:
        channel_directory = f"{export}/{channel_dict[channel]}"
    pathlist = Path(channel_directory).glob("**/*.json")
    fulltext = ""
    for path in pathlist:
        data = _read_json_file(str(path))
        for message in data:
            if message.get("subtype") != "bot_message":
                text = str(message.get("text"))
                if "<@U" in text:
                    for user in user_dict:
                        text = text.replace(f"<@{user}>", user_dict[user])
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


def create_sentence(export, user, channel, user_dict, channel_dict, cache):
    model_name = f"{user}_{channel}"
    try:
        if cache.exists(model_name):
            raw_data = cache.get(model_name)
            text_model = markovify.Text.from_json(raw_data)
        else:
            fulltext = _generate_corpus(export, user, channel, user_dict, channel_dict)
            text_model = markovify.NewlineText(fulltext)
            cache.set(model_name, text_model.to_json())
    except redis.exceptions.ConnectionError as e:
        fulltext = _generate_corpus(export, user, channel, user_dict, channel_dict)
        text_model = markovify.NewlineText(fulltext)
    sentence = text_model.make_sentence(tries=100)
    if isinstance(sentence, str):
        return sentence


def pregen_sentence(export, user, channel, user_dict, channel_dict, cache):
    pregen_name = f"{user}_{channel}_pregen"
    pregen_sentence = create_sentence(
        export, user, channel, user_dict, channel_dict, cache
    )
    try:
        cache.set(pregen_name, pregen_sentence)
    except redis.exceptions.ConnectionError as e:
        pass
