# Chapter 2  Go 内部机制

## Go编译器
## Go的垃圾回收是如何工作的

`GODEBUG=gctrace=1 go run gcoll.go`

## 如何检测垃圾回收的运转情况
## 在Go中调用C
## 在C中调用Go
## panic() 和 recover()函数
## unsafe包
## 方便但又棘手的关键字defer
## Linux工具strace
## FreeBSD 和 macOS High Sierra常用的dtrace工具
## 查找Go环境的信息
## 节点树
## Go汇编


# ch3

映射（map）、数组、切片、指针、常量、循环以及Go处理时间与日期的技巧。

# ch4

- Go结构体和`struct`关键字,
- `new`和`make`的区别
> `new`和`make`最大的区别就是：`new`返回的是空的内存地址，即没有做初始化。另外，`make`仅可以用来创建映射，切片和通道，而且并不是返回指针。
- Go元组
- Go 字符串，runes，字节切片，以及字符串字面量
- Go的正则表达式
- Go的模式匹配
- `switch`语句
- 关于标准库`strings`的使用
- 计算高精度的**PI**值
- 实现一个**K-V存储**

说说字符、字节和`rune`之间的区别
- 
- `rune`: 一个类型为`int32`的值，因此他主要用来代表一个Unicode码点。Unicode码点是一个代表Unicode字符的数值。


# ch5

- 图和节点
- 分析算法复杂度
- Go的二叉树
- Go的哈希表
- Go的链表
- Go的双端链表
- Go的队列
- Go的栈
- Go标准库`container`包提供的数据结构
- Go生成随机数
- 构建随机字符串用作难以破解的密码



# ch6

# ch7


# ch8

+ Unix 进程
+ `flag` 包
+ `io.Reader`和`io.Writer` 接口的使用
+ 用 Go 的 `os/signal` 包处理 Unix **信号**
+ 在您的 Unix 系统工具中支持 Unix **管道**
+ 读取文本文件
+ 读取 CSV 文件
+ 写入文件
+ `bytes` 包
+ `syscall` 包的进阶使用
+ 遍历目录结构
+ Unix 文件权限



# ch9

* 进程，线程和Go协程之间的区别
* Go调度器
* 并发与并行
* 创建Go协程
* 创建通道
* 从通道读取或接收数据
* 往通道里写或发送数据
* 创建管道
* 等待你的Go协程结束