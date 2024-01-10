from etl.utils.config import *
import json


class BookURLGetter:
    def __init__(self, category) -> None:
        self.workdir = get_workdir()
        self.categpry = category
        self.book_category_url = {}
        self.book_page_url = []

    def get_category(self) -> list:
        """
        static json file로 카페고리 별 url 정보 저장되어있는 데이터 리턴
        """
        book_category_filename = "etl/utils/static/book_category_url.json"
        with open(os.path.join(self.workdir, book_category_filename)) as f:
            url = json.load(f)
        self.book_category_url = url[self.categpry]

    def get_book_page_urls(self) -> list:
        """
        각 책의 상세 웹페이지 주소 추출, 리스트로 리턴
        """
        self.get_category()
        print(self.book_category_url)
        for category_name, url in self.book_category_url.items():
            print(category_name, url)

if __name__ == "__main__":
    test = BookURLGetter("소설")
    test.get_book_page_urls()