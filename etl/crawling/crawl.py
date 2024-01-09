from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from getter import *
# from etl.crawling.getter import *
# from mysql_dml import *

class BookDataScrapper:
   def __init__(self, chrome) -> None:
      self.driver = chrome
      self.driver.implicitly_wait(30)

   def crawl_books(self):
      category = get_category()
      print(category)

      for code in category:
        print (f"현재 카테고리 이름: {code}")
        for page in range(1,3):
            url = category[code]+'&tab=top100&list_type=list&sort_type=publishday&page={page}'.format(page=page)
            # 네이버의 베스트셀러 웹페이지 정보
            self.driver.get(url)
            bsObject = BeautifulSoup(self.driver.page_source, 'html.parser')

            book_page_urls = get_book_page_urls(bsObject)
            
            #리스트로 받아온 책의 각 세부 url 안에 들어가서 순위, 제목, 저자, 이미지, 책내용 받아오기
            for index, book_page_url in enumerate(book_page_urls):

                self.driver.get(book_page_url)
                bid = book_page_url.split("bid=")[1]
                print(bid)

                bsObject = BeautifulSoup(self.driver.page_source, 'html.parser')
                book_data = get_book_data(bsObject)

                if book_data is None: continue
                
                title, subtitle, author, description, image = book_data
                return {'bid':bid, 
                        'title':title, 
                        'subtitle':subtitle,
                        'author':"'"+author+"'", 
                        'image':"'"+image+"'", 
                        'rank':str(20*(page-1)+index+1), 
                        'description':description, 
                        'category':code}

if __name__=="__main__":
  driver = webdriver.Chrome()
  scrapper = BookDataScrapper(driver)
  data = scrapper.crawl_books()
  print(data)
