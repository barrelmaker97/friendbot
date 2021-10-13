import os
import sys
import time
import redis
import logging
from flask import Flask
from friendbot import utils
from prometheus_client import make_wsgi_app, Gauge
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)

# Read configuration from environment
signing_secret_file = os.environ.get("FRIENDBOT_SECRET_FILE")
export_zip = os.environ.get("FRIENDBOT_EXPORT_ZIP", "/home/friendbot/export.zip")
redis_host = os.environ.get("FRIENDBOT_REDIS_HOST", "redis")
redis_port = os.environ.get("FRIENDBOT_REDIS_PORT", 6379)

# Add prometheus wsgi middleware to route /metrics requests and create Gauges
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})
export_size_gauge = Gauge("friendbot_export_size", "Size of export file in bytes")
message_gauge = Gauge("friendbot_slack_messages", "Number of Messages Loaded from Export")
user_gauge = Gauge("friendbot_slack_users", "Number of Users Loaded from Export")
channel_gauge = Gauge("friendbot_slack_channels", "Number of Channels Loaded from Export")
model_gauge = Gauge("friendbot_text_models", "Number of Text Models Generated")

# Set log level
if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

# Check for signing secret
if signing_secret_file:
    with open(signing_secret_file, "r") as f:
        signing_secret = f.readline().replace("\n", "")
    app.logger.info("Signing secret loaded")
else:
    signing_secret = None
    app.logger.warning("Signing secret not set! Requests will not be verified")

# Load export and check size
app.logger.info(f"Loading export data from {export_zip}")
load_start_time = time.time()
users, channels, message_data = utils.read_export(export_zip)
load_time = round(time.time() - load_start_time, 3)
export_size = os.stat(export_zip).st_size
export_size_gauge.set(export_size)
app.logger.info(f"Loaded {export_size} bytes of data in {load_time}s")

# Print/Set Export metrics
message_count = len([item for sublist in message_data.values() for item in sublist])
user_count = len(users.keys())
channel_count = len(channels.keys())
message_gauge.set(message_count)
user_gauge.set(user_count)
channel_gauge.set(channel_count)
app.logger.info(f"Loaded {message_count} messages from {user_count} users in {channel_count} channels")

# Generate text models
app.logger.info("Generating text models...")
model_start_time = time.time()
models = utils.generate_models(users, channels, message_data)
model_time = round(time.time() - model_start_time, 3)
model_count = len(models.keys())
app.logger.info(f"{model_count} text models generated in {model_time}s")
model_gauge.set(model_count)

# Check if Redis is available and warm up cache
cache = redis.Redis(host=redis_host, port=redis_port)
try:
    cache.ping()
    app.logger.info("Warming up Redis cache...")
    warmup_start_time = time.time()
    for model in models:
        cache.set(model, models.get(model))
        params = model.split("_")
        utils.get_sentence(params[0], params[1], cache)
    cache.hmset("users", users)
    cache.hmset("channels", channels)
    warmup_time = round(time.time() - warmup_start_time, 3)
    msg = f"Warmed up Redis cache in {warmup_time}s"
    app.logger.info(msg)

except redis.exceptions.ConnectionError as ex:
    app.logger.warning("Could not connect to Redis cache. Exiting.")
    app.logger.debug(ex)
    sys.exit(1)

# Create Export Data Object
export_data = {}
export_data['users'] = users
export_data['channels'] = channels

app.config["EXPORT"] = export_data
app.config["FRIENDBOT_SIGNING_SECRET"] = signing_secret
app.config["REDIS_CACHE"] = cache

from friendbot import routes
