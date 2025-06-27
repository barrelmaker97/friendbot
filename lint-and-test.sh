#!/bin/bash

# Assumes that python packages have been installed
# and redis is running locally on port 6379
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
export FRIENDBOT_EXPORT_ZIP=./example-data/export.zip
export FRIENDBOT_SECRET_FILE=./example-data/example-secret
export FRIENDBOT_REDIS_HOST=localhost
export FRIENDBOT_REDIS_PORT=6379
coverage run -m behave
unset FRIENDBOT_SECRET_FILE
coverage run -m behave --exclude verify
coverage combine
coverage xml
