import logging
from zipfile import ZipFile
from flask import Flask
from os import environ, path
from friendbot import corpus

app = Flask(__name__)

if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

with ZipFile("/export", "r") as zip_object:
    zip_object.extractall("/export_unzip")
app.config["EXPORT"] = "/export_unzip"

try:
    app.config["CHANNEL_DICT"] = corpus.getChannelDict(app.config["EXPORT"])
    app.config["CHANNELS"] = app.config["CHANNEL_DICT"].keys()
    app.logger.info("Channels loaded from export")
except Exception as ex:
    msg = "An exception of type {} occurred. Channels not loaded!"
    format_msg = msg.format(type(ex).__name__)
    app.logger.error(format_msg)

try:
    app.config["USER_DICT"] = corpus.getUserDict(app.config["EXPORT"])
    app.config["USERS"] = app.config["USER_DICT"].keys()
    app.logger.info("Users loaded from export")
except Exception as ex:
    msg = "An exception of type {} occurred. Users not loaded!"
    format_msg = msg.format(type(ex).__name__)
    app.logger.error(format_msg)

from friendbot import routes
