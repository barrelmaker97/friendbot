from os import environ, path
from pathlib import Path
import json
import re
import sys
import markovify

def getUserIDs(export):
    user_ids = {}
    users_file = "{}/users.json".format(export)
    data = _readJsonFile(users_file)
    for user in data:
        real_name = user.get('real_name')
        if(real_name):
            user_id = user.get('id')
            format_user_id = "<@{}>".format(user_id)
            user_ids.update({format_user_id : real_name})
    return user_ids

def getNames(export):
    names = {}
    users_file = "{}/users.json".format(export)
    data = _readJsonFile(users_file)
    for user in data:
        real_name = user.get('real_name')
        if(real_name):
            user_id = user.get('id')
            first_name = real_name.split()[0]
            names.update({first_name.lower() : user_id})
    return names

def getChannels(export):
    channels = []
    channels_file = "{}/channels.json".format(export)
    data = _readJsonFile(channels_file)
    for channel in data:
        name = channel.get('name')
        channels.append(name)
    return channels

def interpretName(name, names):
    if (name == "all"):
        return ""
    try:
        user_id = names[name]
        return user_id
    except:
        raise Exception("User with name {} not found".format(name))

def interpretChannel(channel, channels):
    if (channel == "all"):
        return ""
    if(channel in channels):
        return channel
    else:
        raise Exception("Channel {} not found".format(channel))

def _readJsonFile(path):
    with open(path) as f:
        return json.load(f)

def generateCorpus(export, channel, userID, names):
    channel_directory = "{}/{}".format(export, channel)
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
                    for name in names:
                        text = text.replace(name, names[name])
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

if __name__ == '__main__':
    export = path.expanduser(environ['EXPORT_DIR'])
    userIDs = getUserIDs(export)
    names = getNames(export)
    channels = getChannels(export)
    channel = interpretChannel(sys.argv[1], channels)
    userID = interpretName(sys.argv[2], names)
    corpus = generateCorpus(export, channel, userID, userIDs)
    print("Number of lines in corpus: {}".format(len(corpus.splitlines(True))))
    sentence = generateSentence(corpus)
    print(sentence)
