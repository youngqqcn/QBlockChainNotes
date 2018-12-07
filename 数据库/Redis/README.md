# Redis介绍
Redis是一个开源的使用ANSI C语言编写、支持网络、可基于内存亦可持久化的日志型、Key-Value数据库，并提供多种语言的API

# 数据类型

## String
- set
- get
- strlen
- setx
- setnx
- setrange
- mset
- msetnx
- incr
- incrby
- decr
- decrby
- append

## Hash
- hset
- hmset
- hget
- hgetall
- hmget
- hsetnx
- hvals
- hexists
- hlen
- hkeys

## List
- lpush
- lpop
- lindex
- rpush
- rpop
- ltrim
- lset
- lrange
- llen
- linsert
- blpop     如果没有,则阻塞timeout
- brpop 如果没有,则阻塞timeout
- brpoplpush


## Set
- sadd
- srem
- smembers
- sismember
- scard
- smove
- spop
- srandmember
- sdiff             差集
- sunion      并集
- sinter     交集
- sunionstore
- sdiffstore
- sinterstore




## Sorted set

- zadd
- zsocre
- zcard
- zcount
- zincrby
- zinterstore
- zrange
- zrangebyscore  //例如 zrangebyscore g 70 100 withscores LIMIT 0 2
- zrangebylex //可以用来排序(电话号码排序, 姓名排序)
- zrank
- zrem
- zremrangebylex
- zremrangebyrank   //删除给定排名区间的所有成员
- zremrangebyscore  //删除给定分数区间的所有成员
- zrevrange //返回成员 分数从高到底排序
- zrevrangebyscore  //返回指定分数区间的所有成员 , 分数从高到低排序(例如: zrevrangebyscore g 100 80 withscores)
- zunionstore
- zscan

## (pub/sub)发布和订阅

## 事务
- MULTI 开始事务
- EXEC  执行队列中所有的命令
- DISCARD 清空命令队列
- WATCH 当某个事务需要按条件执行时，就要使用这个命令将给定的键设置为受监控的。
- UNWATCH清除所有先前为一个事务监控的键。


单个 Redis 命令的执行是原子性的，但 Redis 没有在事务上增加任何维持原子性的机制，所以 Redis 事务的执行并不是原子性的。

事务可以理解为一个打包的批量执行脚本，但批量指令并非原子化的操作，中间某条指令的失败不会导致前面已做指令的回滚，也不会造成后续的指令不做。

> Redis不支持回滚: 基本上是程序员的错,就算回滚, 也没用.  

> ACID:  原子性（Atomicity）、一致性（Consistency）、隔离性（Isolation）、持久性（Durability）。一个支持事务（Transaction）


## 乐观锁
WATCH 可以用来监听事务中的队列中的命令，在EXEC之前，一旦发现有一个命令被修改了的 , 那么整个事务就会终止， EXEC返回一个 Null ，提示用户事务失败了。

# 应用场景
- 1、会话缓存（最常用）
- 2、消息队列，比如支付
- 3、活动排行榜或计数
- 4、发布、订阅消息（消息通知）
- 5、商品列表、评论列表等

# C++使用(linux/window)


# go使用
