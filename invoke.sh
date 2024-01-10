#!/bin/bash
DOCKER_IMAGE="docker-image"
DOCKER_TAG="test"
PORT=8080

echo "docker local test"
docker build -t $DOCKER_IMAGE:$DOCKER_TAG .
docker run -d -p ${PORT}:${PORT} --env-file .env ${DOCKER_IMAGE}:${DOCKER_TAG}

curl "http://localhost:${PORT}/2015-03-31/functions/function/invocations" -d '{}'