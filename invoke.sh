#!/bin/bash
DOCKER_IMAGE="docker-image"
DOCKER_TAG="test"

docker build -t $DOCKER_IMAGE:$DOCKER_TAG .
docker run -p 8080:8080 -d $DOCKER_IMAGE:$DOCKER_TAG

curl "http://localhost:8080/2015-03-31/functions/function/invocations" -d '{}'