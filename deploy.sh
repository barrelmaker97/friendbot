#!/bin/bash
coveralls
echo "$DOCKER_PASSWORD" | docker login -u "barrelmaker97" --password-stdin
docker push barrelmaker97/friendbot:latest
