# CDMS_bookstore
CDMS Course from DaSE: Project 1 

=======
- [requirements](https://github.com/Ghostlikei/CDMS_bookstore/blob/main/bookstore.md)

## Private Information

- mongodb remote connection

```sh
mongosh mongodb://userName:daseCDMS2023@110.40.142.252:27017
```


## 数据库结构（r 0.9）

在云服务器上有两个数据库`book`和`be`，与原代码中的含义一致，它们的结构如下：
`book`数据库只有一个collection，`book`，它是`book_lx.db`的拷贝，其中的格式与`/bookstore/fe/access/book.py/Book`保持一致。`book`数据库更多用于进行bench，而不在实际程序中使用。

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

`be`数据库比较复杂，它包含这么几个collection，分别是`user`, `store`, `order`, `order_detail`,`order_archive`具体为

```
class User:
    _uid, # mongodb 默认建立
    uid, # uid上建立唯一索引
    password,
    balance,
    token,
    terminal,
    sid, # 用户拥有的store_id，如果用户仅仅作为买家注册，那么此项为空
```

`store`集合虽然看起来叫书店，但其实是用来表示书店和书的关系。
```
class Store:
    _uid, # mongodb 默认建立
    # (sid, bid)上建立复合索引（唯一）
    sid, # store_id
    bid, # book_id
    stock_level,
    price, # 定价
    owner # 拥有者的用户uid
    # 以及书本的元数据，包括：
    title,
    tags,
    content,
    content_seg, # 建立全文索引
```
也可以在`store`中用一个列表存放所有的书本，但我觉得这样的方法可以保证上架/下架商品的CRUD操作更快。

```
class Order:
    _uid, 
    oid # 在此处oid=uid，uid由用户，商店和随机生成的字符串组成
    uid # 买家uid，建立索引
    sid # 书店id，建立索引
    state, # 订单状态：待付款(Pending)，待发货(ToShip)，待收货(Shipped)
    total_price, # 订单总价
    time, # 下单时间
class OrderDetail:
    # (oid, bid)建立复合索引
    oid,
    bid,
    count,
    price, # 单价
```

同样的，也可以在`Order`中用一个列表存放所有的书本；但由于一个订单可能包含不同种类的不同数量的书本，这样设计可以加速CRUD操作。

```
class OrderArchive:
    _uid, 
    oid # 和Order一致
    uid # 买家uid
    sid # 书店id，建立索引
    state, # 订单状态：已收货(Received)，已取消(Cancelled)
    total_price, # 订单总价
    time, # 下单时间
```
`OrderArchive`用于存储已经完成的订单（与书本的关系），将未完成的订单与已完成的订单分别存储的原因基于下面的事实：
- 随着时间和用户的增加，未完成的订单数远小于已完成的订单
- 在订单未完成时，我们会频繁地对订单进行CRUD操作，包括更改订单状态，删除订单等
- 对于用户而言，用户在订单未完成时查询订单的频率一般高于查询已完成的订单

因此，分开存储两种订单有助于我们缩小CRUD操作进行的文档集合的大小，提升操作效率

上面的设计应该可以保证完成绝大多数功能，唯一需要再研究的是如何实现效率较高的搜索功能
