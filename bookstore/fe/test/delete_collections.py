from pymongo import MongoClient

connect_url = "mongodb://userName:daseCDMS2023@110.40.142.252:27017"

client = MongoClient(connect_url)

db = client["be"]

collection_names = ["order", "store" ,"user" ,"order_detail"]

for collection_name in collection_names:
    collection = db[collection_name]

    # 删除符合特定条件的文档
    delete_filter = {}
    result = collection.delete_many(delete_filter)