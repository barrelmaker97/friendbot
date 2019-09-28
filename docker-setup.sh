#!/bin/bash
if [[ $IMAGE_TAG == "arm32v7" ]]; then
	docker run --rm --privileged multiarch/qemu-user-static:register
fi
