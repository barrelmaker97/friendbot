from zipfile import ZipFile
from flask import Flask
from friendbot import utils
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
import logging
import os
import pathlib
import redis
import time

app = Flask(__name__)

# Add prometheus wsgi middleware to route /metrics requests
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})

if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

# Check for signing secret
signing_secret = os.environ.get("SLACK_SIGNING_SECRET")
if signing_secret:
    app.logger.info("Signing secret loaded")
else:
    app.logger.warning("Signing secret not set! Requests will not be verified")

# Check for specific export location
export_zip = os.environ.get("EXPORT_ZIP")
if export_zip:
    zip_location = pathlib.Path(export_zip).resolve()
else:
    zip_location = pathlib.Path("/export.zip").resolve()
export = zip_location.parent / "export_unzip"
with ZipFile(zip_location, "r") as zip_object:
    zip_object.extractall(export)

# Try to load users from export
app.logger.info("Loading Users...")
try:
    user_dict = utils.get_user_dict(export)
    users = user_dict.keys()
    app.logger.info("Users loaded from export")
except Exception as ex:
    msg = f"An exception of type {type(ex).__name__} occurred. Users not loaded!"
    app.logger.error(msg)

# Try to load channels from export
app.logger.info("Loading Channels...")
try:
    channel_dict = utils.get_channel_dict(export)
    channels = channel_dict.keys()
    app.logger.info("Channels loaded from export")
except Exception as ex:
    msg = f"An exception of type {type(ex).__name__} occurred. Channels not loaded!"
    app.logger.error(msg)

# Check if Redis is available
app.logger.info("Checking Redis connection...")
cache = redis.Redis(host="redis", port=6379)
redis_error_msg = "Could not connect to Redis cache. This will impact performance"
try:
    if not cache.ping():
        app.logger.warning(redis_error_msg)
    else:
        app.logger.info("Redis connected")
except redis.exceptions.ConnectionError as e:
    app.logger.warning(redis_error_msg)

# Warm up text model cache
app.logger.info("Warming up text model cache...")
start_time = time.time()
utils.create_sentence(export, "None", "None", user_dict, channel_dict, cache)
count = 1
for user in users:
    for channel in channels:
        try:
            utils.create_sentence(export, user, channel, user_dict, channel_dict, cache)
            count += 1
        except KeyError as ex:
            pass
warmup_time = round(time.time() - start_time, 3)
msg = f"Generated {count} models for {len(users)} users in {len(channels)} channels in {warmup_time}s"
app.logger.info(msg)

app.config["EXPORT"] = export
app.config["USER_DICT"] = user_dict
app.config["USERS"] = users
app.config["CHANNEL_DICT"] = channel_dict
app.config["CHANNELS"] = channels
app.config["SLACK_SIGNING_SECRET"] = signing_secret
app.config["REDIS_CACHE"] = cache

from friendbot import routes
