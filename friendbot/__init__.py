from zipfile import ZipFile
from flask import Flask
from friendbot import utils
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app, Gauge
from collections import defaultdict
import logging
import os
import pathlib
import redis
import time
import ujson

app = Flask(__name__)

# Add prometheus wsgi middleware to route /metrics requests
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})

if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

# Check for signing secret
signing_secret = None
if signing_secret_file := os.environ.get("FRIENDBOT_SECRET_FILE"):
    with open(signing_secret_file, "r") as f:
        signing_secret = f.readline().replace('\n', '')
    app.logger.info("Signing secret loaded")
else:
    app.logger.warning("Signing secret not set! Requests will not be verified")

# Check for specific export location
app.logger.info("Loading export data...")
export_zip = os.environ.get("FRIENDBOT_EXPORT_ZIP", "/export.zip")
zip_location = pathlib.Path(export_zip).resolve()
export_data = {}
message_data = defaultdict(list)
message_count = 0
with ZipFile(zip_location, "r") as zip_object:
    for name in zip_object.namelist():
        filename = pathlib.PurePath(name)
        if filename.match("*.json"):
            file_data = ujson.load(zip_object.open(name))
            if len(filename.parents) == 1:
                data_dict = {}
                for item in file_data:
                    if filename.stem == "users":
                        if real_name := item.get("real_name"):
                            data_dict.update({item.get("id"): real_name})
                    if filename.stem == "channels":
                        if name := item.get("name"):
                            data_dict.update({item.get("id"): name})
                export_data[filename.stem] = data_dict
            else:
                for message in file_data:
                    if not message.get("subtype"):
                        message.pop("blocks", None)
                        message_data[str(filename.parent)].append(message)
                        message_count += 1
export_data["messages"] = message_data
app.logger.info("Export data loaded")
app.logger.info(f"{message_count} messages loaded from export")

user_count = len(export_data["users"].keys())
app.logger.info(f"{user_count} users loaded from export")
user_gauge = Gauge("friendbot_slack_users", "Number of Users Detected in Export")
user_gauge.set(user_count)

channel_count = len(export_data["channels"].keys())
app.logger.info(f"{channel_count} channels loaded from export")
channel_gauge = Gauge("friendbot_slack_channels", "Number of Channels Detected in Export")
channel_gauge.set(channel_count)

# Check if Redis is available and warm up cache
if not (redis_host := os.environ.get("FRIENDBOT_REDIS_HOST")):
    redis_host = "redis"
if not (redis_port := os.environ.get("FRIENDBOT_REDIS_PORT")):
    redis_port = 6379
app.logger.info("Checking Redis connection...")
cache = redis.Redis(host=redis_host, port=redis_port)
tries = 4
delay = 2
counter = 0
connected = False
while counter < tries:
    try:
        if cache.ping():
            app.logger.info("Redis connected")
            app.logger.info("Warming up text model cache...")
            start_time = time.time()
            utils.create_sentence(export_data, "None", "None", cache)
            count = 1
            for user in export_data["users"]:
                for channel in export_data["channels"]:
                    try:
                        utils.create_sentence(export_data, user, channel, cache)
                        count += 1
                    except KeyError as ex:
                        app.logger.debug(ex)
            warmup_time = round(time.time() - start_time, 3)
            msg = f"Generated {count} models in {warmup_time}s"
            app.logger.info(msg)
            connected = True
            break
        else:
            raise redis.exceptions.ConnectionError
    except redis.exceptions.ConnectionError as ex:
        app.logger.warning(f"Attempt {counter+1} of {tries}: Redis connection failed. Trying again in {delay} seconds")
        app.logger.debug(ex)
        time.sleep(delay)
        counter += 1
if not connected:
    app.logger.warning("Could not connect to Redis cache. This will impact performance")

app.config["EXPORT"] = export_data
app.config["FRIENDBOT_SIGNING_SECRET"] = signing_secret
app.config["REDIS_CACHE"] = cache

from friendbot import routes
