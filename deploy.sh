#!/bin/bash
echo "$DOCKER_PASSWORD" | docker login -u "barrelmaker97" --password-stdin
docker push barrelmaker97/friendbot:amd64
docker push barrelmaker97/friendbot:arm
