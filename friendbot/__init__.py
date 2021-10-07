import os
import time
import redis
import logging
import markovify
from flask import Flask
from friendbot import utils
from prometheus_client import make_wsgi_app, Gauge
from werkzeug.middleware.dispatcher import DispatcherMiddleware

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
        signing_secret = f.readline().replace("\n", "")
    app.logger.info("Signing secret loaded")
else:
    app.logger.warning("Signing secret not set! Requests will not be verified")

# Check export size
export_zip = os.environ.get("FRIENDBOT_EXPORT_ZIP", "/home/friendbot/export.zip")
export_size = os.stat(export_zip).st_size
export_size_gauge = Gauge("friendbot_export_size", "Size of export file in bytes")
export_size_gauge.set(export_size)

# Load export
app.logger.info(f"Loading export data from {export_zip}")
load_start_time = time.time()
users, channels, message_data = utils.read_export(export_zip)
load_time = round(time.time() - load_start_time, 3)
app.logger.info(f"Loaded {export_size} bytes of data in {load_time}s")

message_count = len([item for sublist in message_data.values() for item in sublist])
message_gauge = Gauge("friendbot_slack_messages", "Number of Messages Loaded from Export")
message_gauge.set(message_count)

user_count = len(users.keys())
user_gauge = Gauge("friendbot_slack_users", "Number of Users Loaded from Export")
user_gauge.set(user_count)

channel_count = len(channels.keys())
channel_gauge = Gauge("friendbot_slack_channels", "Number of Channels Loaded from Export")
channel_gauge.set(channel_count)
app.logger.info(f"Loaded {message_count} messages from {user_count} users in {channel_count} channels")

# Generate text models
model_start_time = time.time()
app.logger.info("Generating text models...")
models = {}
all_users = list(users.keys())
all_channels = list(channels.keys())
all_users.append("None")
all_channels.append("None")
for user in all_users:
    for channel in all_channels:
        if fulltext := utils.generate_corpus(users, channels, user, channel, message_data):
            try:
                text_model = markovify.NewlineText(fulltext, retain_original=False).compile(inplace=True)
            except KeyError as ex:
                if str(ex) == "('___BEGIN__', '___BEGIN__')":
                    msg = f"Combination of user {user} in channel {channel} did not produce enough data to create a model"
                    app.logger.debug(msg)
            model_name = f"{user}_{channel}"
            models.update({model_name: text_model.to_json()})
model_time = round(time.time() - model_start_time, 3)

model_count = len(models.keys())
app.logger.info(f"{model_count} text models generated in {model_time}s")
model_gauge = Gauge("friendbot_text_models", "Number of Text Models Generated")
model_gauge.set(model_count)

# Check if Redis is available and warm up cache
app.logger.info("Checking Redis connection...")
redis_host = os.environ.get("FRIENDBOT_REDIS_HOST", "redis")
redis_port = os.environ.get("FRIENDBOT_REDIS_PORT", 6379)
cache = redis.Redis(host=redis_host, port=redis_port)
tries = 4
delay = 2
connected = False
for count in range(tries):
    try:
        if cache.ping():
            app.logger.info("Redis connected")
            app.logger.info("Warming up Redis cache...")
            warmup_start_time = time.time()
            for user in all_users:
                for channel in all_channels:
                    utils.get_sentence(models, user, channel, cache)
            warmup_time = round(time.time() - warmup_start_time, 3)
            msg = f"Warmed up Redis cache in {warmup_time}s"
            app.logger.info(msg)
            connected = True
            break
        else:
            raise redis.exceptions.ConnectionError
    except redis.exceptions.ConnectionError as ex:
        app.logger.warning(f"Attempt {count+1} of {tries}: Connection to Redis at {redis_host}:{redis_port} failed. Trying again in {delay}s")
        app.logger.debug(ex)
        time.sleep(delay)
if not connected:
    app.logger.warning("Could not connect to Redis cache. This will impact performance")

# Create Export Data Object
export_data = {}
export_data['users'] = users
export_data['channels'] = channels
export_data['models'] = models

app.config["EXPORT"] = export_data
app.config["FRIENDBOT_SIGNING_SECRET"] = signing_secret
app.config["REDIS_CACHE"] = cache

from friendbot import routes
