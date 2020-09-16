#!coding:utf8

#author:yqq
#date:2019/10/11 0011 13:44
#description:
from pprint import pprint

import tornado.ioloop
import tornado.web

import tornado.log
import logging

import tornado.options
import time
import json
logging.basicConfig(level=logging.DEBUG)  # 设置日志级别




class MainHandler(tornado.web.RequestHandler):

    def get(self):
        # time.sleep(50)
        # print('accept')
        logging.info("accept")
        logging.error("error infomations...............")
        logging.info("acccccccccccccccccccccccpt")
        logging.warning("waring.........")
        time.sleep( 60 * 5 )
        data = {'result': "hello world"}
        self.write( json.dumps(data))

    def post(self):
        print("fff")
        # self.get()
        print(self.request.body)
        parmas = json.loads( self.request.body )
        # pprint(json.dumps(indent=4))
        logging.info(  json.dumps(parmas, indent=4)  )
        if not isinstance(parmas,dict):
            logging.error("类型不是dict")


        logging.info("")
        ret_data = {
            "err_code": 0,
            "err_msg":None,
            "data":{
                "success" : True
            },
            "timestamp": time.time()
        }
        self.write( json.dumps(ret_data) )






def make_app():
    return tornado.web.Application([
        # (r"/", MainHandler),
        (r"/notify/withdraw", MainHandler),

    ], debug=False)




# 格式化日志输出格式
# 默认是这种的：[I 160807 09:27:17 web:1971] 200 GET / (::1) 7.00ms
# 格式化成这种的：[2016-08-07 09:38:01 执行文件名:执行函数名:执行行数 日志等级] 内容消息
class LogFormatter(tornado.log.LogFormatter):
    def __init__(self):
        super(LogFormatter, self).__init__(
            fmt='%(color)s[%(asctime)s %(filename)s:%(funcName)s:%(lineno)d %(levelname)s]%(end_color)s %(message)s',
            # datefmt= None, #'%Y-%m-%d %H:%M:%S',
            datefmt=""

        )


if __name__ == "__main__":
    tornado.options.parse_command_line()  # 启动应用前面的设置项目
    [i.setFormatter(LogFormatter()) for i in logging.getLogger().handlers]
    app = make_app()
    app.listen(8001)
    logging.info('started')
    tornado.ioloop.IOLoop.current().start()
