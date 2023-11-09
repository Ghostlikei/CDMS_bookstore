from pymongo.errors import PyMongoError
from be.model import error
from be.model import db_conn
import re

class Search(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)
        
    def search(self, parameters, page, result_per_page):
        try:
            store_collection = self.db["store"]
            # parse parameters
            store_id = parameters.get("scope", None)
            title = parameters.get("title", None)
            tags = parameters.get("tags", None)
            content = parameters.get("content", None)
            # build query
            condition_list = []
            if store_id is not None:
                if not self.store_id_exist(store_id):
                    error_msg = error.error_non_exist_store_id(store_id) 
                    return error_msg[0], error_msg[1], []
                condition_list.append({"sid": store_id})
            if title is not None:
                condition_list.append({"title": re.compile(title)})
            if tags is not None:
                condition_list.append({"tags": {"$in": tags}})
            if content is not None:
                condition_list.append({"$text": {"$search": content}})
            if len(condition_list) == 0:
                return error.error_empty_search_parameters()
            query = {"$and": condition_list}
            results = list(store_collection.find(query, {"_id": 0, "owner": 0, "content_seg": 0}).skip((page - 1) * result_per_page).limit(result_per_page))
            print(results)
        except PyMongoError as e:
            return 528, "{}".format(str(e)), []
        except BaseException as e:
            return 530, "{}".format(str(e)), []
        return 200, "ok", results