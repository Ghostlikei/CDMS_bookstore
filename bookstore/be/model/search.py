from pymongo.errors import PyMongoError
from be.model import error
from be.model import db_conn

class Search(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)
        
    def search(self, parameters, page, result_per_page):
        store_collection = self.db["store"]
        # parse parameters
        store_id = parameters.get("scope", None)
        title = parameters.get("title", None)
        tags = parameters.get("tags", None)
        catalog = parameters.get("catalog", None)
        content = parameters.get("content", None)
        
        # build query
        condition_list = []
        if store_id is not None:
            condition_list.append({"store_id": store_id})
        if title is not None:
            condition_list.append({"title": title})
        if tags is not None:
            condition_list.append({"tags": tags})
        if catalog is not None:
            condition_list.append({"catalog": catalog})
        if content is not None:
            condition_list.append({"content": content})
        if len(condition_list) == 0:
            return error.error_empty_search_parameters()
        query = {"$and": condition_list}
        print(query)
        results = list(store_collection.find(query, {"_id": 0, "owner": 0}).skip((page - 1) * result_per_page).limit(result_per_page))
        return 200, "ok", results