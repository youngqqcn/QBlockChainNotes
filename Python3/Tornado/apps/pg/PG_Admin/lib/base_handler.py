import tornado.web
import tornado.httpserver
import time
import json


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
    def success_ret_with_data(data):
        t = int(time.time() * 1000)
        ret = {
            "err_code": 0,
            "err_msg": None,
            "timestamp": t,
            "data" : data
        }
        return ret


    @staticmethod
    def error_ret_with_data(err_code : int, err_msg : str, data):
        t = int(time.time() * 1000)
        ret = {
            "err_code": err_code ,
            "err_msg" : err_msg,
            "timestamp": t,
            "data" : data
        }
        return ret

    def get_argument_from_json(self, str):
        str2dict = json.loads(self.request.body)
        return str2dict[str] if str in str2dict.keys() else False


if __name__ == '__main__':
    pass

