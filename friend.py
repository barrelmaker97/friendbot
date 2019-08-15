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
        "sopia" : "UCHA3NA8N",
        "jill" : "UCEMX3DRP",
        "dan" : "UCGA9N1K9",
        "fiona" : "UCJR5HL3F",
        "olsi" : "UDH10MC7K",
        "all" : ""
        }

# Reading arguments
try:
    userID = rev_names[sys.argv[1]]
except:
    print("Please select a user or all")
    sys.exit(1)
try:
    if (sys.argv[2] == "all"):
        channel = ""
    else:
        channel = sys.argv[2]
except:
    print("Please select a channel or all")
    sys.exit(1)
try:
    sentences = int(sys.argv[3])
except:
    sentences = 10

directory_in_str = "../export"
channel_directory = directory_in_str.format(channel)
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
                if(userID == ""):
                    text = message.get('text')
                    if(type(text) == str):
                        for name in names:
                            text = text.replace(name, names[name])
                        text = regex.sub("", text)
                        text += "\n"
                        fulltext += text
                else:
                    user = message.get('user')
                    if (user == userID):
                        text = message.get('text')
                        text = regex.sub("", text)
                        text += "\n"
                        fulltext += text

text_model = markovify.NewlineText(fulltext)

for i in range(sentences):
    sentence = text_model.make_sentence()
    if(type(sentence) == str):
        print(sentence)
