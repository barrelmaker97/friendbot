from os import environ, path
from pathlib import Path
import json
import re
import sys
import markovify

def getUserIDs(export):
    names = {}
    users_file = "{}/users.json".format(export)
    data = _readJsonFile(users_file)
    for user in data:
        realName = user.get('real_name')
        if(realName):
            userID = user.get('id')
            format_userID = "<@{}>".format(userID)
            names.update({format_userID : realName})
    return names

def getUserIDsRev(export):
    rev_names = {}
    users_file = "{}/users.json".format(export)
    data = _readJsonFile(users_file)
    for user in data:
        realName = user.get('real_name')
        if(realName):
            userID = user.get('id')
            first_name = realName.split()[0]
            rev_names.update({first_name.lower() : userID})
    return rev_names

def interpretName(user, rev_names):
    if (user == "all"):
        return ""
    try:
        userID = rev_names[user]
        return userID
    except:
        raise Exception("User {} not found".format(user))

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
    names = getUserIDs(export)
    rev_names = getUserIDsRev(export)
    channel = interpretChannel(sys.argv[1], export)
    userID = interpretName(sys.argv[2], rev_names)
    corpus = generateCorpus(export, channel, userID, names)
    print("Number of lines in corpus: {}".format(len(corpus.splitlines(True))))
    sentence = generateSentence(corpus)
    print(sentence)
