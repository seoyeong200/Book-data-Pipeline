MASTER_DOCKER="infrastructure-spark-master-1"
WORKER_DOCKER="infrastructure-spark-worker-a-1"

# build image
# docker build -t book-data-pipeline-spark:0.1.0 .

docker-compose up -d
# python /opt/spark-apps/src/setup.py bdist_wheel && \
CMD="pip3 install -e /opt/spark-apps/src && \
python /opt/spark-apps/src/setup.py bdist_wheel && \
/opt/spark/bin/spark-submit --master spark://spark-master:7077 \
--driver-memory 1G \
--executor-memory 1G \
--py-files /opt/spark-apps/src/etl/apps/preprocess.py \
/opt/spark-apps/src/etl/apps/main.py --process calculate" 

docker exec -it "${WORKER_DOCKER}" /bin/bash -c "${CMD}"
