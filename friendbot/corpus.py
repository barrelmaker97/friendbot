from pathlib import Path
import json
import re
import markovify

regex = re.compile(r'<(?:[^"\\]|\\.)*>', re.IGNORECASE)


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
        result = re.search("<.(.*)>", arg)
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
        return json.load(f)


def generateCorpus(export, channel, userID, channel_dict, user_dict):
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


def generateSentence(corpus):
    text_model = markovify.NewlineText(corpus)
    sentence = text_model.make_sentence(tries=100)
    if type(sentence) == str:
        return sentence
