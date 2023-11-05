from pymongo.errors import PyMongoError
from be.model import error
from be.model import db_conn

class Search(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)
        
    def search(self, parameters, page, result_per_page):
        # todo!
        return 200, "test", "test"