import pytest
import requests
import uuid
from fe.access.new_buyer import register_new_buyer
from fe.test.gen_book_data import GenBook
from fe.access.search import Search

class TestSearch:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.user_id = "test_search_{}".format(str(uuid.uuid1()))
        self.password = self.user_id
        self.buyer = register_new_buyer(self.user_id, self.password)
        self.store_id = "test_search_id_{}".format(str(uuid.uuid1()))
        self.gen_book = GenBook(self.seller_id, self.store_id)
        ok, book_list = GenBook.gen(non_exist_book_id=False, low_stock_level=False)
        assert ok
        search = Search()
        yield

    def test_store_search_books(self):
        search_parameters = {
            "title": "1",
            "tags": "2",
            "catalog": "3",
            "content": "4",
            "scope": self.store_id
        }
        page = 1
        result_per_page = 10
        status_code,response = self.search.search(search_parameters, page, result_per_page)
        assert status_code == 200

    def test_all_search_books(self):
        search_parameters = {
            "title": "1",
            "tags": "2",
            "catalog": "3",
            "content": "4",
        }
        page = 1
        result_per_page = 10
        status_code, response = self.search.search(search_parameters, page, result_per_page)
        assert status_code == 200

    def test_search_nonexistent_store(self):
        self.store_id = self.store_id + "_x"
        search_parameters = {
            "title": "1",
            "tags": "2",
            "catalog": "3",
            "content": "4",
            "scope": self.store_id
        }
        page = 1
        result_per_page = 10

        status_code, response = self.search.search(search_parameters, page, result_per_page)

        assert response.status_code == 513

