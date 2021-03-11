from zipfile import ZipFile
from flask import Flask
from friendbot import utils
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app, Gauge
from collections import defaultdict
import markovify
import logging
import os
import pathlib
import redis
import time
import ujson
import sys

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
load_start_time = time.time()
export_zip = os.environ.get("FRIENDBOT_EXPORT_ZIP", "/export.zip")
app.logger.info(f"Loading export data from {export_zip}")
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
                for item in file_data:
                    if not item.get("subtype"):
                        for key in list(item.keys()):
                            if key not in ["text", "user"]:
                                item.pop(key, None)
                        message_data[str(filename.parent)].append(item)
                        message_count += 1

load_time = round(time.time() - load_start_time, 3)
export_size = sys.getsizeof(ujson.dumps(export_data))
app.logger.info(f"Loaded {export_size} bytes of data in {load_time}s")

app.logger.info(f"{message_count} messages loaded from export")
message_gauge = Gauge("friendbot_slack_messages", "Number of Messages Loaded from Export")
message_gauge.set(message_count)

user_count = len(export_data["users"].keys())
app.logger.info(f"{user_count} users loaded from export")
user_gauge = Gauge("friendbot_slack_users", "Number of Users Loaded from Export")
user_gauge.set(user_count)

channel_count = len(export_data["channels"].keys())
app.logger.info(f"{channel_count} channels loaded from export")
channel_gauge = Gauge("friendbot_slack_channels", "Number of Channels Loaded from Export")
channel_gauge.set(channel_count)

# Generate text models
models = {}
all_users = list(export_data["users"].keys())
all_channels = list(export_data["channels"].keys())
all_users.append("None")
all_channels.append("None")
for user in all_users:
    for channel in all_channels:
        if fulltext := utils.generate_corpus(export_data, user, channel, message_data):
            try:
                text_model = markovify.NewlineText(fulltext)
            except KeyError as ex:
                if str(ex) == "('___BEGIN__', '___BEGIN__')":
                    msg = f"Combination of user {user} in channel {channel} did not produce enough data to create a model"
                    app.logger.debug(msg)
                    pass
            model_name = f"{user}_{channel}"
            models.update({model_name: text_model.to_json()})
export_data.update({"models": models})

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
            count = 0
            for user in all_users:
                for channel in all_channels:
                    utils.get_sentence(export_data, user, channel, cache)
                    count += 1
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
