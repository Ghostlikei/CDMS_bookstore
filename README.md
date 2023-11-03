# CDMS_bookstore
CDMS Course from DaSE: Project 1 

=======
- [requirements](https://github.com/Ghostlikei/CDMS_bookstore/blob/main/bookstore.md)

## Private Information

- mongodb remote connection

```sh
mongosh mongodb://userName:daseCDMS2023@110.40.142.252:27017
```


## 数据库结构（暂行）

在云服务器上有两个数据库`book`和`be`，与原代码中的含义一致，它们的结构如下：
`book`数据库只有一个collection，`book`，它是`book_lx.db`的拷贝，其中的格式与`/bookstore/fe/access/book.py/Book`保持一致。
```
class Book:
    id: str
    title: str
    author: str
    publisher: str
    original_title: str
    translator: str
    pub_year: str
    pages: int
    price: int
    binding: str
    isbn: str
    author_intro: str
    book_intro: str
    content: str
    tags: [str]
    pictures: [bytes]
```

`be`数据库比较复杂，它包含这么几个collection，分别是`user`, `store`, `order`, `order_detail`，具体为
```
class User:
    _uid, # mongodb 默认建立
    #uid上建立索引
    uid,
    password,
    balance,
    token,
    terminal,
    sid, # 目前不清楚一个用户是否能开多个书店，暂定只能开一个书店，这一项为null或store的sid
```

`store`集合虽然看起来叫书店，但其实是用来表示书店和书的关系。
```
class Store:
    _uid, # mongodb 默认建立
    # (sid, bid)上建立复合索引
    sid = _uid,
    bid,
    stock_level,
    owner # 拥有者的用户uid
```
也可以在`store`中用一个列表存放所有的书本，但我觉得这样的方法可以保证上架/下架商品的CRUD操作更快。

```
class Order:
    _uid, # mongodb 默认建立
    oid = _uid
    user_id # 买家uid
    store_id # 书店id
    # 以及一些其它的信息，没想好
```

```
class OrderDetail:
    # (oid, bid)建立复合索引
    oid,
    bid,
    count,
    price, # 单价
```

同样的，也可以在`Order`中用一个列表存放所有的书本；但由于一个订单可能包含不同种类的不同数量的书本，这样设计可以加速CRUD操作。

上面的设计应该可以保证完成绝大多数功能，唯一需要再研究的是如何实现效率较高的搜索功能