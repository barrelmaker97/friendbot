from pathlib import Path
import json
import re
import markovify


def getUserDict(export):
    user_dict = {}
    users_file = "{}/users.json".format(export)
    data = _readJsonFile(users_file)
    for user in data:
        real_name = user.get('real_name')
        if(real_name):
            user_id = user.get('id')
            format_user_id = "<@{}>".format(user_id)
            user_dict.update({format_user_id: real_name})
    return user_dict


def getChannelDict(export):
    channel_dict = {}
    channels_file = "{}/channels.json".format(export)
    data = _readJsonFile(channels_file)
    for channel in data:
        name = channel.get('name')
        if(name):
            channel_id = channel.get('id')
            channel_dict.update({channel_id: name})
    return channel_dict


def getUsers(export):
    users = []
    users_file = "{}/users.json".format(export)
    data = _readJsonFile(users_file)
    for user in data:
        user_id = user.get('id')
        users.append(user_id)
    return users


def getChannels(export):
    channels = []
    channels_file = "{}/channels.json".format(export)
    data = _readJsonFile(channels_file)
    for channel in data:
        channel_id = channel.get('id')
        channels.append(channel_id)
    return channels


def verifyUser(user, users):
    if (user == "all"):
        return ""
    try:
        result = re.search('<@(.*)>', user)
        clean = result.group(1)
    except Exception:
        raise Exception("Could not parse user ID {}".format(user))
    if(clean in users):
        return clean
    else:
        raise Exception("User {} not found".format(clean))


def verifyChannel(channel, channels):
    if (channel == "all"):
        return ""
    try:
        result = re.search('<#(.*)>', channel)
        clean = result.group(1)
    except Exception:
        raise Exception("Could not parse channel ID {}".format(channel))
    if(clean in channels):
        return clean
    else:
        raise Exception("Channel {} not found".format(channel))


def _readJsonFile(path):
    with open(path) as f:
        return json.load(f)


def generateCorpus(export, channel, userID, channel_dict, user_dict):
    if (channel):
        channel_directory = "{}/{}".format(export, channel_dict[channel])
    else:
        channel_directory = export
    pathlist = Path(channel_directory).glob('**/*.json')
    regex = re.compile(r'<(?:[^"\\]|\\.)*>', re.IGNORECASE)
    fulltext = ""
    for path in pathlist:
        path_in_str = str(path)
        data = _readJsonFile(path_in_str)
        for message in data:
            subtype = message.get('subtype')
            if(subtype != "bot_message"):
                text = str(message.get('text'))
                if("<@U" in text):
                    for user in user_dict:
                        text = text.replace(user, user_dict[user])
                text = regex.sub("", text)
                if(text):
                    if(not userID):
                        text += "\n"
                        fulltext += text
                    else:
                        user = message.get('user')
                        if (user == userID):
                            text += "\n"
                            fulltext += text
    return fulltext


def generateSentence(corpus):
    text_model = markovify.NewlineText(corpus)
    sentence = text_model.make_sentence(tries=100)
    if(type(sentence) == str):
        return sentence
