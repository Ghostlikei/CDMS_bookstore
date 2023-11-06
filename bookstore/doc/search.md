## 搜索图书

#### URL

POST http://[address]/search

#### Request

Body:

```json
{
  "parameters": {
      "title": "$标题关键字$",
      "tags": "$标签关键字$",
      "catalog": "$目录关键字$",
      "content": "$内容关键字$",
      "scope": "$store_id"
  },
  "page": 1,
  "result_per_page": 10
}
```

| key      | 类型   | 描述       | 是否可为空 |
| -------- | ------ | ---------- | ---------- |
| page  | int | 搜索结果的第几页 | N          |
| result_per_page | int | 每页的搜索结果数量     | N          |
| parameters | dict | 搜索参数 | N |

有关paramerters的具体解释

- scope 项可以为某个store_id，也可以为null，如果为null说明是全站搜索
- 其它项均为搜索参数，可以为null也可以为字符串，如果为字符串则进行复合条件的搜索

#### Response

Status Code:

| 码   | 描述                 |
| ---- | -------------------- |
| 200  | 搜索成功             |
| 513  | 商店不存在(店内搜索) |