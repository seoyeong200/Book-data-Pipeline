import logging
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

from utils.config import get_date, is_same_week


logger = logging.getLogger(__name__)


class DynamoTables():
    def __init__(self, dyn_resource) -> None:
        self.dyn_resource = dyn_resource
        self.table=None

    def exists(self, table_name):
        try:
            table = self.dyn_resource.Table(table_name)
            table.load()
            exists = True
        except ClientError as err:
            if err.response["Error"]["Code"] == "ResourceNotFoundException":
                exists = False
            else:
                logger.error(
                    "Couldn't check for existence of %s. Here's why: %s: %s",
                    table_name,
                    err.response["Error"]["Code"],
                    err.response["Error"]["Message"],
                )
                raise
        else:
            self.table = table
        return exists
    
    def write_batch(self, books):
        try:
            with self.table.batch_writer() as writer:
                for book in books:
                    writer.put_item(Item=book)
        except ClientError as err:
            logger.error(
                "Couln't load data into table %s. Here's why: %s %s",
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
    
    def get_response_of_category(self, category):
        return self.table.query(KeyConditionExpression=Key("category").eq(category))

    def add_item(self, info):
        """
        this method is tp add single item of given info parameter to the dynamo table.
        - if the current table is related to book table, just add single book item.
        - otherwise, if it's related to meta table, 
            update the date and status info of the given category.
        """
        try:
            if self.table.name == "ingested_book_table":
                self.table.put_item(
                    Item={
                        "bid": info["bid"],
                        "title": info["title"],
                        "subtitle": info["subtitle"],
                        "author": info["author"],
                        "image": info["image"],
                        "rank": info["rank"],
                        "description": info["description"],
                        "category": info["category"],
                    }
                )

            if self.table.name == "metatable":
                response = self.get_response_of_category(info['category'])
                if response["Count"] == 0:
                    self.table.put_item(
                        Item={
                            "category": info['category'],
                            "latest_date": get_date(),
                            "job_status": info['status']
                        }
                    )
                else:
                    self.table.update_item(
                        Key={"category":info['category']},
                        UpdateExpression="set #info.latest_date=:date_val, #info.job_status=:status_val",
                        ExpressionAttributeValues={
                            ":date_val": get_date(), 
                            ":status_val": info['status']
                        },
                        ExpressionAttributeNames={
                            "#info": "info"
                        },
                        ReturnValues="UPDATED_NEW",
                    )

        except ClientError as err:
            logger.error(
                "Couldn't add item of category %s to table %s. Here's why: %s: %s",
                info["category"],
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise


    def already_gathered_category(self, category):
        """
        this method is for check whether book data of 
        category parameter was already scrapped or not.
        """
        try:
            response = self.get_response_of_category(category)
            scrapped_date = response["Items"]["latest_date"]
            scrapped_status = response["Items"]["job_status"]
            if (is_same_week(scrapped_date) and scrapped_status == 'SUCCESS') \
                or not is_same_week(scrapped_date):
                return True

        except ClientError as err:
            logger.error(
                "Couldn't query movies released in %s from table %s. Here's why: %s %s",
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        else:
            return False