from pathlib import Path
import redis
import ujson
import re
import sys
import markovify

regex = re.compile(r'<(?:[^"\\]|\\.)*>', re.IGNORECASE)
cache = redis.Redis(host="redis", port=6379)


def getUserDict(export):
    user_dict = {}
    users_file = "{}/users.json".format(export)
    data = _readJsonFile(users_file)
    for user in data:
        real_name = user.get("real_name")
        if real_name:
            user_id = user.get("id")
            user_dict.update({user_id: real_name})
    return user_dict


def getChannelDict(export):
    channel_dict = {}
    channels_file = "{}/channels.json".format(export)
    data = _readJsonFile(channels_file)
    for channel in data:
        name = channel.get("name")
        if name:
            channel_id = channel.get("id")
            channel_dict.update({channel_id: name})
    return channel_dict


def parseArg(arg, options):
    try:
        fix = arg.replace("&lt;", "<")
        fix = fix.replace("&gt;", ">")
        result = re.search("<.(.*)>", fix)
        clean = result.group(1)
        params = clean.split("|")
        final = params[0]
    except Exception:
        raise Exception("Could not parse argument {}".format(arg))
    if final in options:
        return final
    else:
        raise Exception("Argument {} not found".format(final))


def _readJsonFile(path):
    with open(path) as f:
        return ujson.load(f)


def _generateCorpus(export, userID, channel, user_dict, channel_dict):
    if channel == "None":
        channel_directory = export
    else:
        channel_directory = "{}/{}".format(export, channel_dict[channel])
    pathlist = Path(channel_directory).glob("**/*.json")
    fulltext = ""
    for path in pathlist:
        path_in_str = str(path)
        data = _readJsonFile(path_in_str)
        for message in data:
            subtype = message.get("subtype")
            if subtype != "bot_message":
                text = str(message.get("text"))
                if "<@U" in text:
                    for user in user_dict:
                        format_user = "<@{}>".format(user)
                        text = text.replace(format_user, user_dict[user])
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


def generateSentence(export, user, channel, user_dict, channel_dict):
    text_model = generateTextModel(export, user, channel, user_dict, channel_dict)
    sentence = text_model.make_sentence(tries=100)
    if type(sentence) == str:
        return sentence


def generateTextModel(export, user, channel, user_dict, channel_dict):
    model_name = "{}_{}".format(user, channel)
    model_exists: bytes = cache.exists(model_name)
    if model_exists == 0:
        fulltext = _generateCorpus(export, user, channel, user_dict, channel_dict)
        text_model = markovify.NewlineText(fulltext)
        cache.set(model_name, ujson.dumps(text_model.to_json()))
    else:
        raw_data: bytes = cache.get(model_name)
        text_model = markovify.Text.from_json(ujson.loads(raw_data))
    return text_model


def basic_run(export):
    channel = "None"
    user = "None"
    channel_dict = getChannelDict(export)
    channels = channel_dict.keys()
    user_dict = getUserDict(export)
    users = user_dict.keys()
    sentence = generateSentence(export, channel, user, channel_dict, user_dict)
    print(sentence)


if __name__ == "__main__":
    basic_run(sys.argv[1])
