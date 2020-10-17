from zipfile import ZipFile
from flask import Flask
from friendbot import utils
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app, Gauge
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
if signing_secret := os.environ.get("SLACK_SIGNING_SECRET"):
    app.logger.info("Signing secret loaded")
else:
    app.logger.warning("Signing secret not set! Requests will not be verified")

# Check for specific export location
if export_zip := os.environ.get("EXPORT_ZIP"):
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
    user_gauge = Gauge("friendbot_slack_users", "Number of Users Detected in Export")
    user_gauge.set(len(users))
except Exception as ex:
    msg = f"An exception of type {type(ex).__name__} occurred. Users not loaded!"
    app.logger.error(msg)
    app.logger.debug(ex)

# Try to load channels from export
app.logger.info("Loading Channels...")
try:
    channel_dict = utils.get_channel_dict(export)
    channels = channel_dict.keys()
    app.logger.info("Channels loaded from export")
    channel_gauge = Gauge("friendbot_slack_channels", "Number of Channels Detected in Export")
    channel_gauge.set(len(channels))
except Exception as ex:
    msg = f"An exception of type {type(ex).__name__} occurred. Channels not loaded!"
    app.logger.error(msg)
    app.logger.debug(ex)

# Check if Redis is available and warm up cache
if not (redis_host := os.environ.get("FRIENDBOT_REDIS_HOST")):
    redis_host = "redis"
if not (redis_port := os.environ.get("FRIENDBOT_REDIS_PORT")):
    redis_port = 6379
app.logger.info("Checking Redis connection...")
cache = redis.Redis(host=redis_host, port=redis_port)
redis_error_msg = "Could not connect to Redis cache. This will impact performance"
try:
    if cache.ping():
        app.logger.info("Redis connected")
        app.logger.info("Warming up text model cache...")
        start_time = time.time()
        utils.create_sentence(export, "None", "None", user_dict, channel_dict, cache)
        count = 1
        for user in users:
            for channel in channels:
                try:
                    utils.create_sentence(
                        export, user, channel, user_dict, channel_dict, cache
                    )
                    count += 1
                except KeyError as ex:
                    app.logger.debug(ex)
        warmup_time = round(time.time() - start_time, 3)
        msg = f"Generated {count} models for {len(users)} users in {len(channels)} channels in {warmup_time}s"
        app.logger.info(msg)
    else:
        raise redis.exceptions.ConnectionError
except redis.exceptions.ConnectionError as ex:
    app.logger.warning(redis_error_msg)
    app.logger.debug(ex)

app.config["EXPORT"] = export
app.config["USER_DICT"] = user_dict
app.config["USERS"] = users
app.config["CHANNEL_DICT"] = channel_dict
app.config["CHANNELS"] = channels
app.config["SLACK_SIGNING_SECRET"] = signing_secret
app.config["REDIS_CACHE"] = cache

from friendbot import routes
