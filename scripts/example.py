### MongoDB 数据库连接示例
# mongosh mongodb://userName:daseCDMS2023@110.40.142.252:27017

from pymongo import MongoClient

# 连接到 MongoDB
### 用户名: userName
### 密码: daseCDMS2023
client = MongoClient('mongodb://userName:daseCDMS2023@110.40.142.252:27017')
db = client['book']
collection = db['book']
# 查询集合中的前五个文档
cursor = collection.find().limit(5)

# 遍历结果集并打印文档
for document in cursor:
    print(document)
