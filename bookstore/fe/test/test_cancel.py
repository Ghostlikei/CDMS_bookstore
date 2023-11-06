import pytest
import uuid
from fe.access.new_buyer import register_new_buyer


class TestCancel:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.user_id = "test_cancel_{}".format(str(uuid.uuid1()))
        self.password = self.user_id
        self.buyer = register_new_buyer(self.user_id, self.password)
        self.order_id = "test_cancel_order_id_{}".format(str(uuid.uuid1()))
        yield

    def test_ok(self):
        code = self.buyer.cancel(self.order_id)
        assert code == 200

    def test_error_user_id(self):
        self.buyer.user_id = self.buyer.user_id + "_x"
        code = self.buyer.cancel(self.order_id)
        assert code != 200

    def test_error_password(self):
        self.buyer.password = self.buyer.password + "_x"
        code = self.buyer.cancel(self.order_id)
        assert code != 200
    def test_error_order_id(self):
        self.order_id = self.order_id + "_x"
        code = self.buyer.cancel(self.order_id)
        assert code != 200