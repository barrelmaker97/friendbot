[![Version](https://img.shields.io/pypi/v/friendbot.svg)](https://pypi.python.org/pypi/friendbot)
[![Build Status](https://travis-ci.org/barrelmaker97/friendbot.svg?branch=master)](https://travis-ci.org/barrelmaker97/friendbot)
[![Coverage Status](https://coveralls.io/repos/github/barrelmaker97/friendbot/badge.svg?branch=master)](https://coveralls.io/github/barrelmaker97/friendbot?branch=master)
[![Support Python versions](https://img.shields.io/pypi/pyversions/friendbot.svg)](https://pypi.python.org/pypi/friendbot)
# friendbot
Friendbot is a Markov-chain based chatbot which uses Slack messages as its corpus. It reads in messages from a Slack data export, generates a corpus from them, and feeds this to a markov chain generator to naively simulate a conversation. It is a WSGI application, built with [Flask](https://github.com/pallets/flask), designed to be served with a WSGI HTTP server such as [Gunicorn](https://github.com/benoitc/gunicorn). The sentences which it generates can be accessed via a REST API.

## Installation
```
pip install friendbot
```

## API
### /sentence
This endpoint accepts HTTP `POST` requests in the form of `application/x-www-form-urlencoded`. It reads the `text` key and parses the first word into a channel and the second word into a name. Both of these values can be set to `all` to include all channels/names. It returns a sentence generated using the provided parameters.
