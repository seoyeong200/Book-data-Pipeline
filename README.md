# Book data pipeline Project
매주 인기있는 도서 중 사용자가 선호하는 책과 비슷한 책을 추천해주는 서비스를 위한 파이프라인입니다.



### Pipeline Architecture
~<img src="./document/architecture.png"> ~
→ deprecated. will be updated

매주 화요일 네이버 책으로부터 카테고리별 top100 책 정보를 스크래핑하여 <kbd>aws dynamodb</kbd> 에 수집합니다. 수집된 테이블 데이터는 <kbd>aws s3</kbd> 버킷에 export되고, <kbd>spark</kbd>를 통해 전처리와 줄거리 문서의 벡터화 작업이 진행됩니다.

요청받은 책에 대해 비슷한 책을 추천 결과로 반환합니다. 이는 네이버 책에 명시된 책 줄거리 문서 데이터 간의 유사성을 기반으로 합니다. 


### ETL process
~![img](document/etl_architecture.png)~
→ deprecated. will be updated

```bash
invoke.sh {concurrency_level}
```
- concurrency level개의 컨테이너가 동시 구동되어 해당 레벨만큼 scrapper가 병렬로 데이터 수집 작업을 진행합니다.
    - 데이터는 dynamoDB ingested_book_table에 수집됩니다.
    - 책의 카테고리 별 작업 status가 dynamoDB metatable에 업데이트됩니다.
- 데이터 수집 완료 후 ingested_book_table 데이터는 s3 bucket으로 export 됩니다.
- 로컬 환경에 spark container cluster가 생성됩니다.
- 수집된 데이터에 대한 transform 작업이 수행됩니다.
    - 줄거리 문서의 데이터 클리닝, 벡터화, tfidf 계산이 이루어지고, 로컬 머신 파일시스템에 parquet 형식으로 적재됩니다.


### project structure
```
.
├── Dockerfile                  // lambda with docker - contain packages, dependency which is needed for web scrapping
├── Dockerfile_from_scratch     // entire version of above file
├── infrastructure              // for local spark cluster
│   ├── Dockerfile              // spark image
│   ├── apps                    // data processing, modelling pyspark script 
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── preprocess.py
│   │   └── tfidf.py
│   ├── dev                     // spark local test environment (spark+jupyter)
│   │   ├── Dockerfile
│   │   └── docker-compose.yml
│   ├── docker-compose.yml
│   ├── docker-compose_deprecated.yml
│   ├── materials               // spark connector things for communicate with aws s3
│   │   ├── conf
│   │   │   ├── core-site.xml
│   │   │   └── spark-defaults.conf
│   │   └── jars
│   │       ├── aws-java-sdk-bundle-1.11.375.jar
│   │       └── hadoop-aws-3.2.0.jar
│   ├── spark-submit.sh         // execute spark cluster, submit data processing spark jobs
│   └── start-spark.sh          // spark cluster entrypoint shellscript
├── invoke.sh                   // project entrypoint - execute ETL pipeline
├── serverless.yml              // deploy lamdba in aws cluster
└── src
    ├── __init__.py
    ├── etl
    │   ├── __init__.py
    │   ├── crawling                      // scrapper object
    │   │   ├── __init__.py
    │   │   ├── book_data_scrapper.py 
    │   │   └── book_url_getter.py
    │   ├── dynamo_tables.py               // dynamoDB object
    │   ├── handler.py                     // lambda entrypoint
    │   └── utils                          // utility related codebase, static file that has lists of book category 
    │       ├── __init__.py
    │       ├── config.py
    │       └── static
    │           └── book_category_url.json
    └── test
        ├── __init__.py
        └── test_handler.py
```

