#!coding:utf8

#author:yqq
#date:2020/5/7 0007 15:49
#description:   钱包模块
# 1) 使用 BIP44 规范管理私钥
# 2) 提供添加地址的接口, 比如每次生成100个,  需要关联项目方, 并更新地址池, 和私钥池


# coding:utf8
#!coding:utf8

#author:yqq
#date:2020/4/30 0030 16:48
#description:  充币相关 API
#    1)  提币订单接收接口


import logging
import signal

from src.api.handlers.handler_base import BaseHandler
from src.lib.log import LogFormatter
import tornado.ioloop
import tornado.web
import tornado.httpserver
import platform
import tornado.log
import tornado.options
# from tornado.options import options, define
# from src.lib.base_handler import BaseHandler

from src.api.handlers.address_handler import GenerateAddress, QueryAddress, QueryAddAddressOrder

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)


class MainHandler(BaseHandler):
    """
       @api {GET或POST} http://192.168.10.174/api/wallet/ping  1.1.ping测试
       @apiVersion 0.0.1
       @apiName  ping
       @apiGroup 1.PG_Wallet
       @apiDescription  ping测试

       @apiParam  None 无

       @apiSuccessExample Response-Success:
           HTTP 1.1/ 200
           pong

       @apiErrorExample Response-Fail:
           HTTP 1.1/ 404


       """

    def get(self):
        self.write("pong")

    def post(self):
        self.write("pong")


def make_app():
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/ping", MainHandler),
        (r"/addaddresses", GenerateAddress),
        (r"/queryaddresses", QueryAddress),
        (r"/queryaddaddressesorder", QueryAddAddressOrder),
        # (r"/flushaddresses", FlushAddressToRedis ),

    ], debug=False)
    return application


def main():



    #加载用户的API_KEY到redis
    BaseHandler.loading_api_key_to_redis()


    tornado.options.define("port", default="59000", help="the port to listen", type=int)

    tornado.options.parse_command_line()  # 启动应用前面的设置项目
    [i.setFormatter(LogFormatter()) for i in logging.getLogger().handlers]

    app = make_app()


    http_server = tornado.httpserver.HTTPServer(app, decompress_request=True, no_keep_alive=True)
    http_server.listen(tornado.options.options.port, address='0.0.0.0')
    sysstr = platform.system()

    # 优雅退出
    def gracefully_stop(signum, frame):
        def do_stop():
            logger.info('tornado instance had stop gracefully! ')
            tornado.ioloop.IOLoop.current().stop()

        tornado.ioloop.IOLoop.current().add_callback_from_signal(do_stop)
    signal.signal(signal.SIGTERM, gracefully_stop)
    signal.signal(signal.SIGINT, gracefully_stop)
    if (sysstr != "Windows"):
        signal.signal(signal.SIGHUP, gracefully_stop)


    logger.info(f'tornado listening on port {tornado.options.options.port}...')
    if (sysstr == "Windows"):
        http_server.start(1)  # 使用单进程
    else:
        http_server.start(0)  # 使用多进程
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
