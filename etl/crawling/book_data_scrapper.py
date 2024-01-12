from bs4 import BeautifulSoup

from etl.crawling.getter import *
from etl.crawling.book_url_getter import BookURLGetter

class BookDataScrapper(BookURLGetter):
   def __init__(self) -> None:
      pass
   
   def crawl_books(self): 
      """
      리스트로 받아온 책의 각 세부 url 안에 들어가서 순위, 제목, 저자, 이미지, 책내용 받아오기
      """
      for index, item in enumerate(self.book_page_url):
            code, page, url = item
            self.driver.get(url)
            bid = url.split("bid=")[1]

            book_data = get_book_data(BeautifulSoup(self.driver.page_source, 'html.parser'))

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
      title = bsObject.find('h2', {'class': 'bookTitle_book_name__JuBQ2'}).text
      subtitle = bsObject.find('span', {'class': 'bookTitle_sub_title__B0uMS'}).text
      author = bsObject.find('span', {'class': 'bookTitle_inner_content__REoK1'}).text
      description = bsObject.find('div', {'class': 'bookIntro_introduce_area__NJbWv'}).text
      image = bsObject.find('div', {'class': 'bookImage_img_wrap__HWUgc'}).find('img')['src']

      return [title, subtitle, author, description, image]  

if __name__=="__main__":
  driver = webdriver.Chrome()
  scrapper = BookDataScrapper(driver)
  data = scrapper.crawl_books()
  print(data)
