#!/bin/bash
docker network create build_net
docker run -d --name redis --network build_net redis:alpine
