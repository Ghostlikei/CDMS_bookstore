import logging
from pymongo import MongoClient

# 也许应当移动到配置文件中
connect_url = "mongodb://userName:daseCDMS2023@110.40.142.252:27017"

class Store:
    database: str

    def __init__(self, connect_url):
        self.database = "be"
        print(connect_url)
        self.client = MongoClient(connect_url)
        self.init_tables()

    def init_tables(self):
        collections = ["user", "store", "order", "order_detail", "order_archive"]
        indexs = {
            "user": ['uid'],
            "store": [['sid', 'bid'], [('content', "text")]],
            "order": ['oid', 'sid', 'uid'],
            "order_detail": [['oid', 'bid']],
            "order_archive": ['oid', 'sid', 'uid']
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
                                for idx, ii in enumerate(index):
                                    isUnique = False
                                    if idx == 0: isUnique = True
                                    db[collection].create_index(ii, unique=isUnique)
                        else:
                            logging.info(f"collection {collection} already exist")
                    session.commit_transaction()
                except Exception as e:
                    # rollback if error
                    logging.error(e)
                    session.abort_transaction()
                pass

    def get_db_conn(self) -> MongoClient:
        return self.client


database_instance: Store = Store(connect_url)


def init_database(connect_url):
    global database_instance
    database_instance = Store(connect_url)


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()
