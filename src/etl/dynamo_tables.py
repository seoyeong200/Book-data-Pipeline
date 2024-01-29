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
        - if the current table is related to meta table, 
            update the date and status info of the given category.
        - otherwise, just add a single item to the table.
        """
        try:
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
                        UpdateExpression="set #attrName1 = :attrValue1, #attrName2 = :attrValue2",
                        ExpressionAttributeNames={
                            "#attrName1": "latest_date",
                            "#attrName2": "job_status"
                        },
                        ExpressionAttributeValues={
                            ':attrValue1': get_date(),
                            ':attrValue2': info['status'],
                        },
                        ReturnValues="UPDATED_NEW",
                    )
            else:
                self.table.put_item(info)

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
            if response["Count"] == 0: 
                logger.info(
                    "Category %s hasn't been made in metatable yet.",
                    category
                )
                return False

            scrapped_date = response["Items"][0]["latest_date"]
            scrapped_status = response["Items"][0]["job_status"]
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