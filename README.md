[![Build Status](https://travis-ci.org/barrelmaker97/friendbot.svg?branch=master)](https://travis-ci.org/barrelmaker97/friendbot)
[![Coverage Status](https://coveralls.io/repos/github/barrelmaker97/friendbot/badge.svg?branch=master)](https://coveralls.io/github/barrelmaker97/friendbot?branch=master)
# friendbot
Friendbot is a Markov-chain based chatbot which uses Slack messages as its corpus. It reads in messages from a Slack data export, generates a corpus from them, and feeds this to a markov chain generator to naively simulate a conversation. It is a WSGI application, built with [Flask](https://github.com/pallets/flask), designed to be served with a WSGI HTTP server such as [Gunicorn](https://github.com/benoitc/gunicorn). The sentences which it generates can be accessed via a REST API.

- [Installation](#installation)
- [API](#api)

## Installation
```
pip install friendbot
```

## API
