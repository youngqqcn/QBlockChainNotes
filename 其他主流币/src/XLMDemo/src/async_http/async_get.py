#!coding:utf8

#author:yqq
#date:2020/1/14 0014 11:15
#description:




def main():
    import aiohttp
    import asyncio

    """
        aiohttp:发送http请求
        1.创建一个ClientSession对象
        2.通过ClientSession对象去发送请求（get, post, delete等）
        3.await 异步等待返回结果
    """

    async def main():
        url = 'http://httpbin.org/get'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                print(res.status)
                print(await res.text())

    loop = asyncio.get_event_loop()
    task = loop.create_task(main())
    loop.run_until_complete(task)



    pass


if __name__ == '__main__':

    main()