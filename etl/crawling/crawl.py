# from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from getter import *
# from mysql_dml import *

class BookDataScrapper:
   def __init__(self, chrome) -> None:
      self.driver = chrome
      self.driver.implicitly_wait(30)

   def crawl_books(self):
      category = get_category()

      for code in category:
        # if code=='소설': continue
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

                # sql = """SELECT COUNT(*) FROM items WHERE book_id = '""" + bid + """';"""
                # cursor.execute(sql)
                # result = cursor.fetchone()

                # if result[0] == 0: # bid가 sql에 이미 저장되어있지 않으면 세부내용스크래핑 start
                bsObject = BeautifulSoup(self.driver.page_source, 'html.parser')
                title, image, description, url, author = get_book_data(bsObject)
                return {'bid':bid, 
                            'title':title, 
                            'author':"'"+author+"'", 
                            'image':"'"+image+"'", 
                            'rank':str(20*(page-1)+index+1), 
                            'description':description, 
                            'category':code}
                    # try:
                    #   save_data({'bid':bid, 
                    #             'title':title, 
                    #             'author':"'"+author+"'", 
                    #             'image':"'"+image+"'", 
                    #             'rank':str(20*(page-1)+index+1), 
                    #             'description':description, 
                    #             'category':code})
                    # except:
                    #   print(title, "sql 실패")

# if __name__=="__main__":
#   scrapper = BookDataScrapper()
#   scrapper.crawl_books()




'''
def login():
  driver.get('https://www.naver.com/')
  time.sleep(1)

  # 로그인 버튼을 찾고 클릭합니다
  login_btn = driver.find_element_by_class_name('link_login')
  login_btn.click()
  time.sleep(1)

  # id, pw 입력할 곳을 찾습니다.
  tag_id = driver.find_element_by_name('id')
  tag_pw = driver.find_element_by_name('pw')
  tag_id.clear()
  time.sleep(1)

  # id 입력
  tag_id.click()
  pyperclip.copy('아이디')
  tag_id.send_keys(Keys.CONTROL, 'v')
  time.sleep(1)

  # pw 입력
  tag_pw.click()
  pyperclip.copy('비번#')
  tag_pw.send_keys(Keys.CONTROL, 'v')
  time.sleep(1)

  # 로그인 버튼을 클릭합니다
  login_btn = driver.find_element_by_id('log.login')
  login_btn.click()
'''