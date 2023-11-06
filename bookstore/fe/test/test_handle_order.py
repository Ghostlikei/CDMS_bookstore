import pytest
from fe.access.new_seller import register_new_seller
from fe.access import book
import uuid


class TestHandleOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.user_id = "test_handle_order_user_{}".format(str(uuid.uuid1()))
        self.store_id = "test_handle_order_store_{}".format(str(uuid.uuid1()))
        self.order_id = "test_handle_order_orderid_{}".format(str(uuid.uuid1()))
        self.password = self.user_id
        self.seller = register_new_seller(self.user_id, self.password)

        code = self.seller.create_store(self.store_id)
        assert code == 200
        yield

    def test_error_user_id(self):
        code = self.seller.handle_order(
            self.user_id + "_x", self.store_id, self.order_id
        )
        assert code != 200

    def test_error_store_id(self):
        code = self.seller.handle_order(
            self.user_id, self.store_id + "_x", self.order_id
        )
        assert code != 200

    def test_error_order_id(self):
        code = self.seller.handle_order(
            self.user_id, self.store_id, self.order_id + "_x"
        )
        assert code != 200

    def test_ok(self):
        code = self.seller.handle_order(self.user_id, self.store_id, self.order_id)
        assert code == 200
