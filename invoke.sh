#!/bin/bash
DOCKER_IMAGE="docker-image"
DOCKER_TAG="test"
CATEGORY_LIST_JSON_PATH="./src/etl/utils/static/book_category_url.json"

echo "docker local test"
# docker-image:test 이미지 기반으로 컨테이너 exec
# docker build -t $DOCKER_IMAGE:$DOCKER_TAG .

run_container() {
    local category=$1
    local port=$2
    local container_name=$3

    docker run -d -p ${port}:8080 \
        --env-file .env -v ./src/etl:/var/task \
        --name ${container_name} ${DOCKER_IMAGE}:${DOCKER_TAG}

    tmp="${category%\"}"
    tmp="${tmp#\"}"
    curl "http://localhost:${port}/2015-03-31/functions/function/invocations" -d "{\"category\": [\"$tmp\"]}"

    docker stop ${container_name}
    docker rm ${container_name}

    echo "${container_name} finished"
}

category_lists=($(jq ". | keys[]" ${CATEGORY_LIST_JSON_PATH}))

for (( i=0; i<${#category_lists[@]}; i+=3 )); do
    category=${category_lists[i]}
    run_container "$category" "8080" "scrapping_container1"
done &

for (( i=1; i<${#category_lists[@]}; i+=3 )); do
    category=${category_lists[i]}
    run_container "$category" "8081" "scrapping_container2"
done &

for (( i=2; i<${#category_lists[@]}; i+=3 )); do
    category=${category_lists[i]}
    run_container "$category" "8082" "scrapping_container3"
done &

wait

