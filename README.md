[![Version](https://img.shields.io/pypi/v/friendbot.svg)](https://pypi.python.org/pypi/friendbot)
[![Build Status](https://travis-ci.org/barrelmaker97/friendbot.svg?branch=master)](https://travis-ci.org/barrelmaker97/friendbot)
[![Coverage Status](https://coveralls.io/repos/github/barrelmaker97/friendbot/badge.svg?branch=master)](https://coveralls.io/github/barrelmaker97/friendbot?branch=master)
[![Python versions](https://img.shields.io/pypi/pyversions/friendbot.svg)](https://pypi.python.org/pypi/friendbot)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# friendbot
Friendbot is a Markov-chain based chatbot which uses Slack messages as its corpus. It reads in messages from a Slack data export, generates a corpus from them, and feeds this to a markov chain generator to naively simulate a conversation. It is a WSGI application, built with [Flask](https://github.com/pallets/flask), designed to be served with a WSGI HTTP server such as [Gunicorn](https://github.com/benoitc/gunicorn). The sentences which it generates can be accessed via a REST API.

## Installation
```
pip install friendbot
```

## API
### /sentence
This endpoint accepts HTTP `POST` requests in the form of `application/x-www-form-urlencoded` and returns a sentence generated using the provided parameters. It reads the `text` key of the `POST`ed data and splits the value into arguments in the form of Slack channels `<#CHANNEL>` or users `<@USER>`. These are used to narrow the selection of messages friendbot will read to generate its corpus. These arguments can be in any order and can also be left blank to include all channels/users. In most cases, responses from this endpoint will return a 200 status code, regardless of whether an error has occurred. This is because unfortunately, [Slack does not follow the HTTP spec](https://api.slack.com/slash-commands#responding_with_errors) and uses 200 to indicate that a request has been received even if an error occurs.

### /action
This endpoint accepts HTTP `POST` requests in the form of `application/x-www-form-urlencoded`, extracts a JSON payload, and takes the action specified in the JSON. This is used interprets interactions with Friendbot messages. These include sending the generated sentence to the channel, shuffling to generate a new sentence, and cancelling the sentence generation.
