from zipfile import ZipFile
from flask import Flask
from friendbot import corpus
import logging
import os
import pathlib
import redis

app = Flask(__name__)

if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

# Check for signing secret
signing_secret = os.environ.get("SLACK_SIGNING_SECRET")
if signing_secret is None:
    app.logger.warning("Signing secret not set! Requests will not be verified")
else:
    app.logger.info("Signing secret loaded")

# Check for specific export location
zip_location_env = os.environ.get("EXPORT_ZIP")
if zip_location_env is None:
    zip_location = pathlib.Path("/export.zip").resolve()
else:
    zip_location = pathlib.Path(os.environ.get("EXPORT_ZIP")).resolve()
export = zip_location.parent / "export_unzip"
with ZipFile(zip_location, "r") as zip_object:
    zip_object.extractall(export)

# Try to load users from export
try:
    user_dict = corpus.getUserDict(export)
    users = user_dict.keys()
    app.logger.info("Users loaded from export")
except Exception as ex:
    msg = f"An exception of type {type(ex).__name__} occurred. Users not loaded!"
    app.logger.error(msg)

# Try to load channels from export
try:
    channel_dict = corpus.getChannelDict(export)
    channels = channel_dict.keys()
    app.logger.info("Channels loaded from export")
except Exception as ex:
    msg = f"An exception of type {type(ex).__name__} occurred. Channels not loaded!"
    app.logger.error(msg)

# Check if Redis is available
cache = redis.Redis(host="redis", port=6379)
try:
    if not cache.ping():
        msg = "Could not connect to Redis cache. This will impact performance"
        app.logger.warning(msg)
except redis.exceptions.ConnectionError as e:
    msg = "Could not connect to Redis cache. This will impact performance"
    app.logger.warning(msg)

app.logger.info("Warming up cache...")
corpus.generateSentence(export, "None", "None", user_dict, channel_dict, cache)
count = 1
for user in users:
    for channel in channels:
        try:
            corpus.generateSentence(
                export, user, channel, user_dict, channel_dict, cache
            )
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
app.config["SLACK_SIGNING_SECRET"] = signing_secret
app.config["REDIS_CACHE"] = cache

from friendbot import routes
