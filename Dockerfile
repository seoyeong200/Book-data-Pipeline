FROM sykim98/aws-lambda-python-web-scrapping:0.1.0
RUN pip install requests \ 
    pip install boto3
COPY etl ${LAMBDA_TASK_ROOT}/etl
CMD [ "handler.handler" ]