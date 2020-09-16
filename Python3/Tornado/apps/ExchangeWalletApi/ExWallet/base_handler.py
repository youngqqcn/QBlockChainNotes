import tornado.httpserver
import time

class BaseHandler(tornado.web.RequestHandler):
    AllowHeaders = set(['X-Requested-With', 'Ng-Path', 'Ak-Admin-Skey', 'Ak-Token'])

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT")
        self.set_header("Access-Control-Allow-Headers", ",".join(hd for hd in BaseHandler.AllowHeaders))
        
    def options(self):
        self.set_status(204)
        self.finish()

    @staticmethod
    def success_ret():
        t = int(time.time() * 1000)
        ret = {"success": "true", "sysTime": t}
        return ret

    @staticmethod
    def success_ret_with_data(data):
        ret = BaseHandler.success_ret()
        ret["jsonrpc"] = "2.0"
        ret["id"] = 0,
        ret["result"] = data
        return ret

    @staticmethod
    def error_ret():
        #t = int(time.time() * 1000)
        ret = {"success": "false", "sysTime": time.asctime()}
        return ret
    
    @staticmethod
    def error_ret_with_data(data):
        ret = BaseHandler.error_ret()
        ret["result"] = data
        return ret

    def get_argument_from_json(self, str):
        from utils import json2dict
        str2dict = json2dict(self.request.body)
        return str2dict[str] if str in str2dict.keys() else False
