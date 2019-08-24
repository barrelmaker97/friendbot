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

def interpretName(name, names):
    if (name == "all"):
        return ""
    try:
        user_id = names[name]
        return user_id
    except:
        raise Exception("User with name {} not found".format(name))

def interpretChannel(channel_name, export):
    if (channel_name == "all"):
        return ""
    channels = []
    channels_file = "{}/channels.json".format(export)
    data = _readJsonFile(channels_file)
    for channel in data:
        name = channel.get('name')
        channels.append(name)
    if(channel_name in channels):
        return channel_name
    else:
        raise Exception("Channel {} not found".format(channel_name))

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
    channel = interpretChannel(sys.argv[1], export)
    userID = interpretName(sys.argv[2], names)
    corpus = generateCorpus(export, channel, userID, userIDs)
    print("Number of lines in corpus: {}".format(len(corpus.splitlines(True))))
    sentence = generateSentence(corpus)
    print(sentence)
