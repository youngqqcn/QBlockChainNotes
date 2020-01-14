## Python3

### 迭代器

> https://www.runoob.com/python3/python3-iterator-generator.html

```python
#!coding:utf8

#author:yqq
#date:2020/1/14 0014 15:21
#description:

class MyNumber:

    def __init__(self, init_number = 1 , bound_number = 99999):
        self.n  = init_number
        self.bound = bound_number

    def __iter__(self):  #实现  __iter__ 方法
        return self 

    def __next__(self): #实现  __next__ 方法
        x = self.n
        if x > self.bound:
            raise StopIteration
        self.n += 1
        return  x

def main():

    num_iter = MyNumber(init_number=9, bound_number=888)
    print(  next(num_iter)  )
    print(  next(num_iter)  )
    print(  next(num_iter)  )

    # for i in num_iter:
    #     print(i)

    # while True:
    #     print(next(num_iter))

    while True:
        try:
            print(next(num_iter))
        except StopIteration:
            print('over')
            break
        except  Exception as e:
            print(f'error: {e}')

    pass


if __name__ == '__main__':

    main()
```





### yield 和 生成器(generator)

- 列表生成器

  ```python
  >>> [i for i in range(10)]
  [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
  ```

- 生成器函数

  ```python
  #!coding:utf8
  
  #author:yqq
  #date:2020/1/14 0014 15:29
  #description:
  #  对于yield的理解:
  #      生成器函数遇到 yield, 立即返回, 并保存现场(保存了变量的值), 下次再次从yield后的语句执行
  #    换句话说: yield保存了函数执行过程中的 "中间状态"  下次再次从"中间状态" 继续执行
  
  
  def my_fib(nmax = 99):
      """
      :param nmax: 最大数, 防止无限生成下去
      :return:
      """
  
      counter  =  nmax
  
      a , b = 0, 1
      yield a   # 第一个数 0
      yield b   # 第二个数  1
      for i in range(counter):
          yield a + b
          a, b = b, a + b
  
  
  
  def main():
  
      fib_gen = my_fib()
      # print(next(fib_gen))
      # print(next(fib_gen))
      # print(next(fib_gen))
      # print(next(fib_gen))
      # print(next(fib_gen))
      for n in fib_gen:
          print(n)
  
      pass
  
  
  if __name__ == '__main__':
  
      main()
  ```



###  基于生成器的协程 

使用 `@asyncio.coroutine`  修饰函数

> 此装饰器 **已弃用** 并计划觉得 Python 3.10 中移除。

```python

import asyncio

@asyncio.coroutine
def old_style_coroutine():
    print('old_style_coroutine()')
    yield from asyncio.sleep(1)

async def main():
    await old_style_coroutine()

asyncio.run( main() )
```



### async 和 await

从 Python3.7开始 使用  `async和await` 代替 `@asyncio.coroutine` 和`yield from`

> asyncio官方文档: https://docs.python.org/zh-cn/3/library/asyncio.html
>
> https://www.cnblogs.com/dhcn/p/9032461.html



```python
#!coding:utf8

#author:yqq
#date:2020/1/14 0014 11:49
#description:

import requests
import asyncio
import time



async def test2(i):
    print('\n')
    print('------进入test2-------------')
    print('-------开始 await  other_test()------')
    r = await other_test(i)
    print('-------结束 await  other_test()------')
    print(i,r)
    print('----------结束test2------------------')
    print('\n')

async def other_test(i):
    print('\n')
    print('-----------进入 other_test()-----------')
    print('开始 http  get 请求')
    r = requests.get(i)
    print('结束 http get请求')
    print(i)

    print('开始 休眠 4s')
    if 'sina' in i:
        await asyncio.sleep(5)  #挂起当前协程, 让出cpu给其他协程(继续事件循环)
    await asyncio.sleep(0.1)  #挂起当前协程, 让出cpu给其他协程(继续事件循环)
    # time.sleep(4)  #如果改成 time.sleep(4)  则完全是同步方式(顺序执行) 会阻塞事件循环
    print(f'\033[32m 结束 {i} 休眠 \033[0m')
    print(time.time()-start)
    print('--------结束other_test------------------')
    print('\n')
    return r

url = ["https://www.jd.com",
       "https://www.sina.com",
       "https://www.baidu.com"]

print('开始创建事件循环 ')
loop = asyncio.get_event_loop()

print('开始生成 task')
task = [asyncio.ensure_future(test2(i)) for i in url]

start = time.time()

print('开始运行事件循环')
loop.run_until_complete(asyncio.wait(task))

print('\n')
print('结束运行事件循环')
endtime = time.time()-start


print(endtime)

print('关闭事件循环')
loop.close()
```



### 异步echo_server

```python



from curio import run, spawn
from curio.socket import *

async def echo_server(address):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(5)
    print('Server listening at', address)
    async with sock:
        while True:
            client, addr = await sock.accept()
            await spawn(echo_client, client, addr)

async def echo_client(client, addr):
    print('Connection from', addr)
    async with client:
         while True:
             data = await client.recv(100000)
             if not data:
                 break
             await client.sendall(data)
    print('Connection closed')

if __name__ == '__main__':
    run(echo_server, ('',25000))

```



