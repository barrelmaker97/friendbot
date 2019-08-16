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


def generateCorpus(export, channel, userID):
    channel_directory = "{}/{}".format(export, channel)
    pathlist = Path(channel_directory).glob('**/*.json')
    regex = re.compile(r'<(?:[^"\\]|\\.)*>', re.IGNORECASE)
    fulltext = ""
    for path in pathlist:
        path_in_str = str(path)
        with open(path_in_str, encoding="utf8") as f:
            data = json.load(f)
            for message in data:
                subtype = message.get('subtype')
                if(subtype != "bot_message"):
                    text = str(message.get('text'))
                    for name in names:
                        text = text.replace(name, names[name])
                    text = regex.sub("", text)
                    if(text != ""):
                        if(userID == ""):
                            if(type(text) == str):
                                text += "\n"
                                fulltext += text
                        else:
                            user = message.get('user')
                            if (user == userID):
                                text += "\n"
                                fulltext += text
    return fulltext

def generateSentence(corpus, count):
    sentences = []
    text_model = markovify.NewlineText(corpus)
    for i in range(count):
        sentence = text_model.make_sentence(tries=100)
        if(type(sentence) == str):
            sentences.append(sentence)
    return sentences

if __name__ == '__main__':
    # Reading arguments
    try:
        export = sys.argv[1]
    except:
        print("Please provide a Slack export directory")
        sys.exit(1)
    userID = getUserID(sys.argv[2])
    channel = getChannel(sys.argv[3])
    try:
        count = int(sys.argv[4])
    except:
        count = 10
    corpus = generateCorpus(export, channel, userID)
    sentences = generateSentence(corpus, count)
    for sentence in sentences:
        print(sentence)
