#!/bin/bash
DOCKER_IMAGE="docker-image"
DOCKER_TAG="test"

docker build -t $DOCKER_IMAGE:$DOCKER_TAG .

docker run -d -p 8080:8080 ${DOCKER_IMAGE}:${DOCKER_TAG}

# DOCKER_CONTAINER_ID=$(${DOCKER_RUN_CMD})
# echo "${DOCKER_CONTAINER_ID}"

curl "http://localhost:8080/2015-03-31/functions/function/invocations" -d '{}'

# docker stop "${DOCKER_RUN_CMD}"
# docker rm "${DOCKER_RUN_CMD}"