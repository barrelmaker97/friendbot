from pathlib import Path
import json
import re
import sys
import markovify

names = {
        "<@UCF55PTPV>" : "Nolan",
        "<@UCFDECFUM>" : "Ailysh",
        "<@UCEH553R6>" : "Matt",
        "<@UCF2BKUG4>" : "Ryan",
        "<@UCF90GYUA>" : "Jake",
        "<@UCF58F6LB>" : "Caroline",
        "<@UCGQSFL5C>" : "Grace",
        "<@UCGK09UJ2>" : "Halley",
        "<@UCGA2GQJ3>" : "Maegan",
        "<@UCGA0K9PZ>" : "Trevor",
        "<@UCFEBHEAH>" : "Jason",
        "<@UCGT4D0EQ>" : "Hannah",
        "<@UCF7J89HA>" : "Josh",
        "<@UCHA3NA8N>" : "Sophia",
        "<@UCEMX3DRP>" : "Jill",
        "<@UCGA9N1K9>" : "Dan",
        "<@UCJR5HL3F>" : "Fiona",
        "<@UDH10MC7K>" : "Olsi"
        }

rev_names = {
        "nolan" : "UCF55PTPV",
        "ailysh" : "UCFDECFUM",
        "matt" : "UCEH553R6",
        "ryan" : "UCF2BKUG4",
        "jake" : "UCF90GYUA",
        "caroline" : "UCF58F6LB",
        "grace" : "UCGQSFL5C",
        "halley" : "UCGK09UJ2",
        "maegan" : "UCGA2GQJ3",
        "trevor" : "UCGA0K9PZ",
        "jason" : "UCFEBHEAH",
        "hannah" : "UCGT4D0EQ",
        "josh" : "UCF7J89HA",
        "sophia" : "UCHA3NA8N",
        "jill" : "UCEMX3DRP",
        "dan" : "UCGA9N1K9",
        "fiona" : "UCJR5HL3F",
        "olsi" : "UDH10MC7K",
        "all" : ""
        }

def getUserID(user):
    try:
        return rev_names[user]
    except:
        return None

def getChannel(channel):
    try:
        if (channel == "all"):
            return ""
        else:
            return channel
    except:
        return None

def readJsonFile(path):
    with open(path) as f:
        return json.load(f)

def generateCorpus(export, channel, userID):
    channel_directory = "{}/{}".format(export, channel)
    pathlist = Path(channel_directory).glob('**/*.json')
    regex = re.compile(r'<(?:[^"\\]|\\.)*>', re.IGNORECASE)
    fulltext = ""
    for path in pathlist:
        path_in_str = str(path)
        data = readJsonFile(path_in_str)
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
    try:
        export = sys.argv[1]
    except:
        print("Please provide a Slack export directory")
        sys.exit(1)
    userID = getUserID(sys.argv[2])
    channel = getChannel(sys.argv[3])
    corpus = generateCorpus(export, channel, userID)
    print("Number of lines in corpus: {}".format(len(corpus.splitlines(True))))
    sentence = generateSentence(corpus)
    print(sentence)
