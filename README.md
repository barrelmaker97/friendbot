[![Build Status](https://travis-ci.org/barrelmaker97/friendbot.svg?branch=master)](https://travis-ci.org/barrelmaker97/friendbot)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# friendbot
Friendbot is a Markov-chain based chatbot which uses Slack messages as its corpus. It reads in messages from a Slack data export, generates a corpus from them, and feeds this to a markov chain generator to naively simulate a conversation. It is built with [Flask](https://github.com/pallets/flask), served by [Gunicorn](https://github.com/benoitc/gunicorn), and run in Docker. The sentences which it generates can be accessed via an API which is designed to connect to the existing Slack API.

## Installation
```
docker run -d -p <your chosen port>:5000 -v <your slack export>:/export barrelmaker97/friendbot
```

## API
### /sentence
This endpoint accepts HTTP `POST` requests in the form of `application/x-www-form-urlencoded` and returns a sentence generated using the provided parameters. It reads the `text` key of the `POST`ed data and splits the value into arguments in the form of Slack channels `<#CHANNEL>` or users `<@USER>`. These are used to narrow the selection of messages Friendbot will read to generate its corpus. These arguments can be in any order and can also be left blank to include all channels/users. In most cases, responses from this endpoint will return a 200 status code, regardless of whether an error has occurred. This is because unfortunately, [Slack does not follow the HTTP spec](https://api.slack.com/slash-commands#responding_with_errors) and uses 200 to indicate that a request has been received even if an error occurs.

### /action
This endpoint accepts HTTP `POST` requests in the form of `application/x-www-form-urlencoded`, extracts a JSON payload, sends a `POST` request to the Slack API based on the interaction that initiated the request, and returns a 200 status code. This provides the interactive component of Friendbot messages. These interactions consist of sending a generated sentence to the channel, shuffling to generate a new sentence, and cancelling sentence generation.
