import logging
from zipfile import ZipFile
from flask import Flask
from friendbot import corpus

app = Flask(__name__)

if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

export = "/export_unzip"
with ZipFile("/export", "r") as zip_object:
    zip_object.extractall("/export_unzip")

try:
    user_dict = corpus.getUserDict(export)
    users = user_dict.keys()
    app.logger.info("Users loaded from export")
except Exception as ex:
    msg = "An exception of type {} occurred. Users not loaded!"
    format_msg = msg.format(type(ex).__name__)
    app.logger.error(format_msg)

try:
    channel_dict = corpus.getChannelDict(export)
    channels = channel_dict.keys()
    app.logger.info("Channels loaded from export")
except Exception as ex:
    msg = "An exception of type {} occurred. Channels not loaded!"
    format_msg = msg.format(type(ex).__name__)
    app.logger.error(format_msg)

count = 1
for user in users:
    for channel in channels:
        app.logger.info("Generating model for {} {}".format(user, channel))
        try:
            corpus.generateTextModel(export, user, channel, user_dict, channel_dict)
            count += 1
        except KeyError as ex:
            pass
app.logger.info("Generated {} models".format(count))

app.config["EXPORT"] = export
app.config["USER_DICT"] = user_dict
app.config["USERS"] = users
app.config["CHANNEL_DICT"] = channel_dict
app.config["CHANNELS"] = channels

from friendbot import routes
