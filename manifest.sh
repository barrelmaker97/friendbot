export DOCKER_CLI_EXPERIMENTAL=enabled
docker manifest create barrelmaker97/friendbot:latest \
	barrelmaker97/friendbot:amd64 \
	barrelmaker97/friendbot:arm
docker manifest annotate barrelmaker97/my-image:latest \
	barrelmaker97/friendbot:amd64 --arch amd64 \
	barrelmaker97/friendbot:arm --arch arm
docker manifext push barrelmaker97/friendbot:latest
