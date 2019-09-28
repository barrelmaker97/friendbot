#!/bin/bash
if [[ $IMAGE_TAG == "arm32v7" ]]; then
	docker run --rm --privileged multiarch/qemu-user-static:register
fi
docker build -t barrelmaker97/friendbot:$IMAGE_TAG --build-arg BASE_IMAGE=$BASE_IMAGE .
docker run -d -p 127.0.0.1:5000:5000 -v $(realpath ./test_data/export):/export barrelmaker97/friendbot:$IMAGE_TAG
