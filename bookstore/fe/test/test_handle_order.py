import pytest
from fe.access.new_buyer import register_new_buyer
from fe.test.gen_book_data import GenBook
import uuid


class TestHandleOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.buyer_id = "test_handle_order_user_{}".format(str(uuid.uuid1()))
        self.store_id = "test_handle_order_store_{}".format(str(uuid.uuid1()))
        self.seller_id = "test_handle_order_seller_{}".format(str(uuid.uuid1()))
        self.password = self.buyer_id
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.gen_book = GenBook(self.seller_id, self.store_id)
        # add order in advance
        ok, buy_book_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False)
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_list)
        assert code == 200
        self.order_id = order_id
        code = self.buyer.add_funds(100000000000)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        yield

    # note user_id is seller_id
    def test_error_user_id(self):
        code = self.gen_book.seller.handle_order(
            self.gen_book.user_id + "_x", self.store_id, self.order_id
        )
        assert code != 200

    def test_error_store_id(self):
        code = self.gen_book.seller.handle_order(
            self.gen_book.user_id, self.store_id + "_x", self.order_id
        )
        assert code != 200

    def test_error_order_id(self):
        code = self.gen_book.seller.handle_order(
            self.gen_book.user_id, self.store_id, self.order_id + "_x"
        )
        assert code != 200

    def test_ok(self):
        code = self.gen_book.seller.handle_order(self.gen_book.user_id, self.store_id, self.order_id)
        assert code == 200
