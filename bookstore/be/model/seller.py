# import sqlite3 as sqlite
from be.model import error
from be.model import db_conn
from pymongo.errors import PyMongoError
import pymongo
import jieba

class Seller(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)


    def add_book(
        self,
        user_id: str,
        store_id: str,
        book_id: str,
        book_info_str: str,
        stock_level: int,
        price: float,
        title: str,
        content: str,
        tags: str,
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)
            
            content_words = jieba.lcut_for_search(content)
            content_segmented = " ".join(content_words)
            
            store_collection = self.db["store"]
            store_data = {
                "owner": user_id,
                "sid": store_id,
                "bid": book_id,
                # "book_info": 'str',
                "stock_level": stock_level,
                "price": price,
                "title": title,
                "content": content,
                "content_seg": content_segmented,
                "tags": tags,
            }
            store_collection.insert_one(store_data)
        except PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(
        self, user_id: str, store_id: str, book_id: str, add_stock_level: int
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            store_collection = self.db["store"] # database name
            store_collection.update_one(
                {"sid": store_id, "bid": book_id},
                {"$inc": {"stock_level": add_stock_level}}
            )
        except PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            user_store_collection = self.db["user"]
            user_store_collection.update_one({"uid": user_id},{"$set":{"sid":store_id}})
        except PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def handle_order(self,user_id: str, store_id : str, order_id: str):

        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.order_id_exist(order_id):
                print(f"eo: {order_id}")
                return error.error_invalid_order_id(order_id)
            order_collection = self.db["order"]
            desired_state = "ToShip"
            order = order_collection.find_one({"oid": order_id})
            if order["state"] == desired_state:
                # 更新状态为Shipped
                update_result = order_collection.update_one(
                    {"oid": order_id},
                    {"$set": {"state": "Shipped"}}
                )
                if update_result.modified_count > 0:
                    return 200 , "ok"
                else:
                    raise pymongo.errors.OperationFailure("Order update failed")
            else:
                return error.error_wrong_state(order_id)
        except PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
