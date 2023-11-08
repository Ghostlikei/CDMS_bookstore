import pytest
import uuid
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer


class TestListOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        # prepare buyer
        self.user_id = "test_list_order_{}".format(str(uuid.uuid1()))
        self.password = self.user_id
        self.buyer = register_new_buyer(self.user_id, self.password)
        # prepare store
        self.seller_id = "test_list_order_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_list_order_store_id_{}".format(str(uuid.uuid1()))
        self.gen_book = GenBook(self.seller_id, self.store_id)
        
        # add orders in advance
        self.num_orders = 5
        self.orders_id_list = []
        for _ in range(self.num_orders):
            ok, buy_book_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False)
            assert ok
            code, order_id = self.buyer.new_order(self.store_id, buy_book_list)
            assert code == 200
            self.orders_id_list.append(order_id)
        yield

    def test_ok(self):
        code, orders = self.buyer.list_orders(self)
        assert code == 200 # check the status code
        for order in orders: # check the list results, i.e. order_id
            order_id = order["order_id"]
            assert order_id in self.orders_id_list

    def test_error_user_id(self):
        self.buyer.user_id = self.buyer.user_id + "_x"
        code = self.buyer.list_orders(self)
        assert code != 200
    def test_error_password(self):
        self.buyer.password = self.buyer.password + "_x"
        code = self.buyer.list_orders(self)
        assert code != 200
