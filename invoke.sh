#!/bin/bash
DOCKER_IMAGE="docker-image"
DOCKER_TAG="test"
CATEGORY_LIST_JSON_PATH="./src/etl/utils/static/book_category_url.json"

concurrency_level=$1

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

    echo "category ${category} is finished in ${container_name}"
}

concurrency_level() {
    local level=$1
    local category_lists=($(jq ". | keys[]" ${CATEGORY_LIST_JSON_PATH}))
    for (( j=$level; j<${#category_lists[@]}; j+=$concurrency_level )); do
        category=${category_lists[j]}
        port=$((8080 + level))
        run_container "$category" "$port" "scrapping_container_${level}"
    done &
}

for (( i=0; i<=$concurrency_level; i+=1 )); do
    concurrency_level "$i"
done

wait

