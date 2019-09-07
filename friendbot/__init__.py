import logging
from flask import Flask
from os import environ, path

app = Flask(__name__)

if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

app.config["EXPORT_DIR"] = path.expanduser(environ["EXPORT_DIR"])
app.logger.info("Export can be found at {}".format(app.config["EXPORT_DIR"]))

from friendbot import routes
