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

`be`数据库比较复杂，它包含这么几个collection，分别是`user`, `store`, `order`, `order_detail`,`order_archive`，`book`具体为
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
    orders, # 未完成的订单
    oldOrders, # 已完成的订单
```

`store`集合虽然看起来叫书店，但其实是用来表示书店和书的关系。
```
class Store:
    _uid, # mongodb 默认建立
    # (sid, bid)上建立复合索引
    sid = _uid,
    bid,
    stock_level,
    price, # 定价
    owner # 拥有者的用户uid
    # 以及书本的元数据，包括：
    title,
    tags,
    catelog,
    content,
    # 以上元数据建立全文索引
```
也可以在`store`中用一个列表存放所有的书本，但我觉得这样的方法可以保证上架/下架商品的CRUD操作更快。

```
class Order:
    _uid, # mongodb 默认建立
    oid = _uid
    uid # 买家uid
    sid # 书店id
    # 以及一些其它的信息，没想好
    state, # 订单状态：待付款，待发货，待收货，已收货
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

```
class OrderArchive:
    oid,
    bid,
    sid, # 商店id
    count,
    price,
```
`OrderArchive`用于存储已经完成的订单（与书本的关系），将未完成的订单与已完成的订单分别存储的原因基于下面的事实：
- 随着时间和用户的增加，未完成的订单数远小于已完成的订单
- 在订单未完成时，我们会频繁地对订单进行CRUD操作，包括更改订单状态，删除订单等
- 对于用户而言，用户在订单未完成时查询订单的频率一般高于查询已完成的订单

因此，分开存储两种订单有助于我们缩小CRUD操作进行的文档集合的大小，提升操作效率

上面的设计应该可以保证完成绝大多数功能，唯一需要再研究的是如何实现效率较高的搜索功能
