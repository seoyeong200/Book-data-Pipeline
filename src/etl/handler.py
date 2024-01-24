from selenium import webdriver
from tempfile import mkdtemp

import boto3
import json
import os

from crawling.book_data_scrapper import BookDataScrapper
from crawling.book_url_getter import BookURLGetter
from dynamo_tables import DynamoTables


dynamodb = boto3.resource('dynamodb')

def handler(event=None, context=None, chrome=None):

    def driver_getter(chrome=None):
        if chrome is None:
            options = webdriver.ChromeOptions()
            service = webdriver.ChromeService("/opt/chromedriver")

            options.binary_location = '/opt/chrome/chrome'
            options.add_argument("--headless=new")
            options.add_argument('--no-sandbox')
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1280x1696")
            options.add_argument("--single-process")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-dev-tools")
            options.add_argument("--no-zygote")
            options.add_argument(f"--user-data-dir={mkdtemp()}")
            options.add_argument(f"--data-path={mkdtemp()}")
            options.add_argument(f"--disk-cache-dir={mkdtemp()}")
            options.add_argument("--remote-debugging-port=9222")
            options.add_argument("--user-agent='Mozilla/5.0")

            return webdriver.Chrome(options=options, service=service)
        return chrome
    
    for c in event['category']:
        try:
            book_table = DynamoTables(dynamodb)
            meta_table = DynamoTables(dynamodb)

            if not book_table.exists("ingested_book_table") \
                or not meta_table.exists("metatable") \
                or meta_table.already_gathered_category(c):
                continue

            url_getter = BookURLGetter(chrome=driver_getter(), category=c)
            url_getter.get_book_page_urls_scrapper()
            book_page_url = url_getter.get_book_page_url()
            
            scrapper = BookDataScrapper(chrome=driver_getter(), book_page_url=book_page_url)
            for book_info in scrapper.crawl_books():
                print(book_info)
                book_table.add_item(Item=book_info)
            
            meta_table.add_item({'category': c, 'status': 'SUCCESS'})
        
        except:
            meta_table.add_item({'category': c, 'status': 'FAIL'})

    return

