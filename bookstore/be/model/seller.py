# import sqlite3 as sqlite
from pymongo import MongoClient
from be.model import error
from be.model import db_conn
from pymongo.errors import PyMongoError

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
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            store_collection = self.db["store"]
            store_data = {
                "sid": store_id,
                "bid": book_id,
                # "book_info": 'str',
                "stock_level": stock_level,
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
