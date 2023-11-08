import pytest
import uuid
from fe.access.new_buyer import register_new_buyer
from fe.test.gen_book_data import GenBook
from fe.access.new_seller import register_new_seller
class TestConfirm:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.user_id = "test_confirm_user_id_{}".format(str(uuid.uuid1()))
        self.password = self.user_id
        self.buyer = register_new_buyer(self.user_id, self.password)
        # self.order_id = "test_confirm_order_id_{}".format(str(uuid.uuid1()))
        self.seller_id = "test_confirm_seller_id_{}".format(str(uuid.uuid1()))
        # self.seller_password = self.seller_id
        # self.seller = register_new_seller(self.seller_id, self.seller_password)
        self.store_id = "test_confirm_store_id_{}".format(str(uuid.uuid1()))
        self.gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False)
        self.seller = self.gen_book.seller
        assert ok
        status_code, self.order_id = self.buyer.new_order(self.store_id, buy_book_list)
        assert status_code == 200
        code = self.buyer.add_funds(100000000000)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.seller.handle_order(self.seller_id,self.store_id,self.order_id)
        assert code == 200
        yield

    def test_ok(self):
        code = self.buyer.confirm(self.order_id)
        assert code == 200

    def test_error_user_id(self):
        self.buyer.user_id = self.buyer.user_id + "_x"
        code = self.buyer.confirm(self.order_id)
        assert code != 200

    def test_error_password(self):
        self.buyer.password = self.buyer.password + "_x"
        code = self.buyer.confirm(self.order_id)
        assert code != 200

    def test_error_order_id(self):
        self.order_id = self.order_id + "_x"
        code = self.buyer.confirm(self.order_id)
        assert code != 200