#!/bin/bash
if [[ $IMAGE_TAG == "arm32v7" ]]; then
	docker run --rm --privileged multiarch/qemu-user-static:register
	wget https://github.com/multiarch/qemu-user-static/releases/download/v4.1.0-1/qemu-arm-static.tar.gz -O ./qemu-arm-static.tar.gz
	tar zxvf ./qemu-arm-static.tar.gz -C ./
fi
