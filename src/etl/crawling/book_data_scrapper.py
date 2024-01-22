from bs4 import BeautifulSoup
import time, random
from ratelimit import limits, sleep_and_retry


class BookDataScrapper():
   def __init__(self, chrome: object, book_page_url: list) -> None:
      self.driver = chrome
      self.book_page_url = book_page_url
   
   @sleep_and_retry
   @limits(calls=1, period=2) # one request per 2 secs
   def crawl_books(self): 
      """
      리스트로 받아온 책의 각 세부 url 안에 들어가서 순위, 제목, 저자, 이미지, 책내용 받아오기
      """
      for index, item in enumerate(self.book_page_url):
            print(item)
            code, page, urls = item
            for url in urls:
               time.sleep(random.uniform(1, 3))
               self.driver.get(url)
               bid = url.split("bid=")[1]
               book_data = self.get_book_data(BeautifulSoup(self.driver.page_source, 'html.parser'))
               if book_data is None: continue
               
               title, subtitle, author, description, image = book_data

               yield {'bid':bid, 
                     'title':title, 
                     'subtitle':subtitle,
                     'author':"'"+author+"'", 
                     'image':"'"+image+"'", 
                     'rank':str(20*(page-1)+index+1), 
                     'description':description, 
                     'category':code}

   @staticmethod
   def get_book_data(bsObject):
      def get_text(tag: str, class_name: str) -> str:
         element = bsObject.find(tag, {'class': class_name})
         return element.text if element else ''

      title = get_text('h2', 'bookTitle_book_name__JuBQ2')
      subtitle = get_text('span', 'bookTitle_sub_title__B0uMS')
      author = get_text('span', 'bookTitle_inner_content__REoK1')
      description = get_text('div', 'bookIntro_introduce_area__NJbWv')
      try:
         image = bsObject.find('div', {'class': 'bookImage_img_wrap__HWUgc'}).find('img')['src']
      except:
         image = ''

      return [title, subtitle, author, description, image]  

