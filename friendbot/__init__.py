import logging, os, pathlib
from zipfile import ZipFile
from flask import Flask
from friendbot import corpus

app = Flask(__name__)
zip_location = pathlib.Path(os.environ.get("EXPORT_ZIP"))
export = zip_location.parent / "export_unzip"

if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

with ZipFile(zip_location, "r") as zip_object:
    zip_object.extractall(export)

try:
    user_dict = corpus.getUserDict(export)
    users = user_dict.keys()
    app.logger.info("Users loaded from export")
except Exception as ex:
    msg = f"An exception of type {type(ex).__name__} occurred. Users not loaded!"
    app.logger.error(msg)

try:
    channel_dict = corpus.getChannelDict(export)
    channels = channel_dict.keys()
    app.logger.info("Channels loaded from export")
except Exception as ex:
    msg = f"An exception of type {type(ex).__name__} occurred. Channels not loaded!"
    app.logger.error(msg)

app.logger.info("Warming up cache...")
corpus.generateSentence(export, "None", "None", user_dict, channel_dict)
count = 1
for user in users:
    for channel in channels:
        try:
            corpus.generateSentence(export, user, channel, user_dict, channel_dict)
            count += 1
        except KeyError as ex:
            pass
msg = f"Generated {count} models for {len(users)} users in {len(channels)} channels"
app.logger.info(msg)

app.config["EXPORT"] = export
app.config["USER_DICT"] = user_dict
app.config["USERS"] = users
app.config["CHANNEL_DICT"] = channel_dict
app.config["CHANNELS"] = channels

from friendbot import routes
