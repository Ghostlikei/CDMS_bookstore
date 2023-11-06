import logging
import sqlite3 as sqlite
from pymongo import MongoClient

# 也许应当移动到配置文件中
connect_url = "mongodb://userName:daseCDMS2023@110.40.142.252:27017"

class Store:
    database: str

    def __init__(self, db_path):
        self.database = "be"
        self.init_tables()

    def init_tables(self):
        collections = ["user", "store", "order", "order_detail"]
        indexs = {
            "user": 'uid',
            "store": ['sid', 'bid'],
            "order": 'oid',
            "order_detail": ['oid', 'bid']
        }
        client = self.get_db_conn()
        db = client[self.database]
        # we use session to manage the transaction and rollback
        with client.start_session() as session:
            with session.start_transaction():
                try:
                    # create collections if not exist
                    collections_name = db.list_collection_names()
                    for collection in collections:
                        if collection not in collections_name:
                            logging.info(f"collection {collection} not exist, create it")
                            db.create_collection(collection)
                            index = indexs.get(collection, None)
                            if index is not None:
                                db[collection].create_index(index, unique = True)
                        else:
                            logging.info(f"collection {collection} already exist")
                    session.commit_transaction()
                except Exception as e:
                    # rollback if error
                    logging.error(e)
                    session.abort_transaction()
                pass

    def get_db_conn(self) -> MongoClient:
        client = MongoClient(connect_url)
        return client


database_instance: Store = Store("")


def init_database(db_path):
    global database_instance
    database_instance = Store(db_path)


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()
