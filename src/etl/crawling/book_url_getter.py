import os, json
from bs4 import BeautifulSoup

from src.etl.utils.config import get_workdir


class BookURLGetter:
    def __init__(self, chrome: object, category: list) -> None:
        self.driver = chrome
        self.workdir = get_workdir()
        self.category = category
        self.book_category_url = {}
        self.book_page_url = []

    def get_book_category_url(self):
        return self.book_category_url
    
    def get_book_page_url(self):
        return self.book_page_url

    def get_category_scrapper(self) -> list:
        """
        static json file로 카페고리 별 url 정보 저장되어있는 데이터 리턴
        """
        book_category_filename = "etl/utils/static/book_category_url.json"
        with open(os.path.join(self.workdir, book_category_filename)) as f:
            url = json.load(f)
        self.book_category_url = url[self.category]
        
    def get_book_page_urls_scrapper(self) -> list:
        """
        각 책의 상세 웹페이지 주소 추출, 리스트로 리턴
        """
        self.get_category_scrapper()
        for category_name, category_url in self.book_category_url.items():
            for page in range(1, 4):
                search_url = category_url+f'&tab=top100&list_type=list&sort_type=publishday&page={page}'
                self.driver.get(search_url)
                book_page_urls = self.get_book_page_url_scrapper(BeautifulSoup(self.driver.page_source, 'html.parser'))
                self.book_page_url.append((category_name, page, book_page_urls))

    @staticmethod
    def get_book_page_url_scrapper(bsObject):
        """
        책의 상세 웹페이지 주소를 추출, 리턴
        """
        book_page_urls = []
        for index in range(0, 20): 
            dl_data = bsObject.find('dt', {'id':"book_title_"+str(index)})
            if dl_data==None or dl_data.find('img',{'class':"adult"}) : #성인 인증 도서
                break #건너뛰기
            link = dl_data.select('a')[0].get('href')
            book_page_urls.append(link)

        return book_page_urls
