[![Coverage Status](https://coveralls.io/repos/github/barrelmaker97/friendbot/badge.svg?branch=master)](https://coveralls.io/github/barrelmaker97/friendbot?branch=master)
[![CodeFactor](https://www.codefactor.io/repository/github/barrelmaker97/friendbot/badge/master)](https://www.codefactor.io/repository/github/barrelmaker97/friendbot/overview/master)

# friendbot
Friendbot is a Markov-chain based chatbot which uses Slack messages as its corpus. It reads in messages from a Slack data export, generates a corpus from them, and feeds this to a markov chain generator to naively simulate a conversation. It is built with [Flask](https://palletsprojects.com/p/flask/), served by [Gunicorn](https://gunicorn.org/), cached by [Redis](https://redis.io/), and run in Docker. The sentences which it generates can be accessed via an API which is designed to connect to the existing Slack API.

## Installation
Download the `docker-compose.yaml` file (or clone this repo), and start by letting Friendbot know the location of your Slack export zip file by running
```
FB_EXPORT=<path to your Slack export> docker compose-up -d
```

## Configuration
All config is done via environment variables, listed below:

* `FRIENDBOT_LOG_LEVEL`: _Optional_. Friendbot's log level (*Options:* `debug`, `info`, `warning`, `error`, `critical`) (*Default:* `info`)
* `FRIENDBOT_EXPORT_ZIP` _Optional_. Path (inside Friendbot) to zip file containing the Slack Export (*Default:* `/export.zip`)
* `FRIENDBOT_REDIS_HOST` _Optional_. Hostname of Redis instance used for cache. (*Default:* `redis`)
* `FRIENDBOT_REDIS_PORT` _Optional_. Port number of Redis instance used for cache. (*Default:* `6379`)
* `FRIENDBOT_SIGNING_SECRET` _Optional_. Signing Secret recieved from Slack that Friendbot can use to verify requests.

## API
### /sentence
This endpoint accepts HTTP `POST` requests sentence generated using the export data. It reads the `text` key of the `POST`ed form and splits the value into arguments in the form of Slack channels `<#CHANNEL>` or users `<@USER>`. These are used to narrow the selection of messages Friendbot will read to generate its corpus. These arguments can be in any order and can also be left blank to include all channels/users. In most cases, responses from this endpoint will return a 200 status code, regardless of whether an error has occurred. This is because [Slack does not follow the HTTP spec](https://api.slack.com/slash-commands#responding_with_errors) and uses 200 to indicate that a request has been received even if an error occurs.

### /action
This endpoint accepts HTTP `POST` requests in the form of `application/x-www-form-urlencoded`, extracts a JSON payload, sends a `POST` request to the Slack API based on the interaction that initiated the request, and returns a 200 status code. This provides the interactive component of Friendbot messages. These interactions consist of sending a generated sentence to the channel, shuffling to generate a new sentence, and cancelling sentence generation.

### /metrics
This endpoint accepts HTTP `GET` requests and returns metrics about Friendbot in a format that can be consumed by Prometheus.

### /health
This endpoint accepts HTTP `GET` requests and returns 200 as long as the application is healthy. Used for Docker healthchecking.

## Requirements
* Docker
* Docker Compose
