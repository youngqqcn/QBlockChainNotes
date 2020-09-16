# coding:utf8
#!coding:utf8

#author:yqq
#date:2020/4/30 0030 16:48
#description:  充币相关 API
#    1) 充币数据查询接口
#    2) 充币地址增加接口


import logging

from src.api.handlers.handler_base import BaseHandler
from src.lib.log import LogFormatter
import tornado.ioloop
import tornado.web
import tornado.httpserver
import platform
import tornado.log
import tornado.options
# from tornado.options import options, define
from src.api.handlers.query_deposit_data import QueryDepositData

logger = logging.getLogger(__name__)




class MainHandler(BaseHandler):
    """
       @api {GET或POST} http://192.168.10.174/api/deposit/ping  2.1.ping测试
       @apiVersion 0.0.1
       @apiName  ping
       @apiGroup 2.PG_Deposit
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
        (r"/getdepositdata", QueryDepositData)

    ], debug=False)
    return application


def main():

    #加载用户的API_KEY到redis
    BaseHandler.loading_api_key_to_redis()

    tornado.options.define("port", default="59001", help="the port to listen", type=int)

    tornado.options.parse_command_line()  # 启动应用前面的设置项目
    [i.setFormatter(LogFormatter()) for i in logging.getLogger().handlers]

    app = make_app()

    #HTTPS 相关配置
    # sslop={
    #        "certfile": os.path.join(os.path.abspath("."), "server.crt"),
    #        "keyfile": os.path.join(os.path.abspath("."), "server.key"),
    # }
    #
    # http_server = tornado.httpserver.HTTPServer(app, decompress_request=True, ssl_options=sslop, no_keep_alive=True)

    http_server = tornado.httpserver.HTTPServer(app, decompress_request=True, no_keep_alive=True)
    http_server.listen(tornado.options.options.port, address='0.0.0.0')
    sysstr = platform.system()

    logger.info(f'tornado listening on port {tornado.options.options.port}...')
    if (sysstr == "Windows"):
        http_server.start(1)  # 使用单进程
    else:
        http_server.start(0)  # 使用多进程
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
