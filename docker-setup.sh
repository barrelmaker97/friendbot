#!/bin/bash
if [[ $IMAGE_TAG == "arm" ]]; then
	docker run --rm --privileged multiarch/qemu-user-static:register
	wget https://github.com/multiarch/qemu-user-static/releases/download/v4.1.0-1/qemu-arm-static.tar.gz -O ./qemu-arm-static.tar.gz
	tar zxvf ./qemu-arm-static.tar.gz -C ./
fi
docker build -t barrelmaker97/friendbot:$IMAGE_TAG --build-arg BASE_IMAGE=$BASE_IMAGE .
docker run -d -p 127.0.0.1:5000:5000 -v $(realpath ./test_data/export):/export barrelmaker97/friendbot:$IMAGE_TAG
