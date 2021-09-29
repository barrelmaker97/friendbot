#!/bin/ash
pip install --upgrade pip --no-cache-dir
pip install -r requirements.txt --no-cache-dir
adduser --disabled-password --gecos "" --uid "1234" "friendbot"
rm /install.sh /requirements.txt
