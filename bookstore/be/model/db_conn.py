from be.model import store


class DBConn:
    def __init__(self):
        self.conn = store.get_db_conn()
        self.db = self.conn["be"]

    def user_id_exist(self, user_id):
        user_collection = self.db["user"]
        user = user_collection.find_one({"uid": user_id})
        return user is not None

    def book_id_exist(self, store_id, book_id):
        store_collection = self.db["store"]
        book = store_collection.find_one({"sid": store_id, "bid": book_id})
        return book is not None

    def store_id_exist(self, store_id):
        store_collection = self.db["user"]
        store = store_collection.find_one({"sid": store_id})
        return store is not None
