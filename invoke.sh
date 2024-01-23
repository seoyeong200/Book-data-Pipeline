#!/bin/bash
DOCKER_IMAGE="docker-image"
DOCKER_TAG="test"
PORT=8080
CONTAINER_NAME="scrapper-container"
CATEGORY_LIST_JSON_PATH="./src/etl/utils/static/book_category_url.json"

echo "docker local test"

# docker-image:test 이미지 기반으로 컨테이너 exec
# docker build -t $DOCKER_IMAGE:$DOCKER_TAG .

category_lists=($(jq ". | keys[]" ${CATEGORY_LIST_JSON_PATH}))

for c in ${category_lists[@]}; do
    echo $c
    docker run -d \
        -p ${PORT}:${PORT} \
        --env-file .env \
        -v ./src/etl:/var/task \
        --name ${CONTAINER_NAME} \
        ${DOCKER_IMAGE}:${DOCKER_TAG} \

    tmp="${c%\"}"
    tmp="${tmp#\"}"

    curl "http://localhost:8080/2015-03-31/functions/function/invocations" -d "{\"category\": [\"$tmp\"]}"

    docker stop ${CONTAINER_NAME} 
    docker rm ${CONTAINER_NAME} 
done

'''
docker run -d -p 8080:8080 --env-file .env -v ./src/etl:/var/task docker-image:test
curl "http://localhost:8080/2015-03-31/functions/function/invocations" -d '{"category" : ["취업", "IT"]}'
'''
