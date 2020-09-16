import redis
import tornado.web
import tornado.httpserver
import time
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tornado.httpclient import HTTPError
import json
import time
from ed25519 import SigningKey, VerifyingKey

from src.config.constant import REDIS_HOST, REDIS_PORT, REDIS_API_KEY_DB_NAME, MYSQL_CONNECT_INFO
from src.model.model import Project


class BaseHandler(tornado.web.RequestHandler):
    AllowHeaders = set(['X-Requested-With', 'PG_API_KEY', 'PG_API_TIMESTAMP', 'PG_API_SIGNATURE'])

    def __init__(self, application, request, **kwargs):


        super().__init__(application=application, request=request, **kwargs)


    # def prepare(self):
    #     pass

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, POST")
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

    @classmethod
    def loading_api_key_to_redis(cls):
        engine = create_engine(MYSQL_CONNECT_INFO,
                               max_overflow=0,
                               pool_size=5)
        SessionCls = sessionmaker(bind=engine,
                                  autoflush=False,  # 关于 autoflush https://www.jianshu.com/p/b219c3dd4d1e
                                  autocommit=True  # 自动提交
                                  )

        session = SessionCls()
        rds = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_API_KEY_DB_NAME, decode_responses=True)

        projects = session.query(Project).all()
        if not (projects is not None and len(projects) > 0):
            print('not found any api_key from database to loading into redis')
        else:
            print(f'loading {len(projects)} api_key into redis ')
            for pro in projects:
                assert isinstance(pro, Project), 'pro is not Project instance'
                pro_id = pro.pro_id
                api_key = pro.api_key
                verify_key = pro.client_verify_key
                rds.set(api_key, verify_key + ',' + str(pro_id))
            print(f'successfully loaded {len(projects)} api_key into redis ')

        pass


    def get_argument_from_json(self, str):
        str2dict = json.loads(self.request.body)
        return str2dict[str] if str in str2dict.keys() else False


    def get_verify_key(self, api_key : str):
        rds = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_API_KEY_DB_NAME, decode_responses=True)
        value = rds.get(name=api_key)
        return value




def  sign_msg(sign_key : str, msg : bytes) -> any:
    sk = SigningKey(sk_s=sign_key.encode('latin1'), prefix='', encoding='hex')
    sig = sk.sign(msg=msg, prefix='', encoding='hex')
    return sig


def verify_sig(verify_key : str, sig : str, msg : bytes) -> bool:
    vk = VerifyingKey(vk_s=verify_key, prefix='', encoding='hex')
    try:
        vk.verify(sig=sig, msg=msg, prefix='', encoding='hex')
    except Exception as e:
        return False
    return True


def apiauth(fun):
    """
    对请求请求进行认证, 错误信息不应暴露细节
    :param fun:
    :return:
    """
    def wrapper(self, *args, **kwargs):

        try:
            if not ('PG_API_SIGNATURE' in self.request.headers
                    and 'PG_API_TIMESTAMP' in self.request.headers
                    and 'PG_API_KEY' in self.request.headers):
                raise Exception()

            sig = self.request.headers['PG_API_SIGNATURE']
            timestamp = self.request.headers['PG_API_TIMESTAMP']
            api_key = self.request.headers['PG_API_KEY']

            if not (len(sig) == 128 and str(sig).isalnum() and str(timestamp).isnumeric()
                    and len(api_key) == 64 and str(api_key).isalnum()):
                print('invalid headers')
                raise Exception()

            # 使用绝对值,
            if abs(int(time.time() * 1000) - int(timestamp)) > 2 * 60 * 1000:
                raise Exception('timestamp expired')

            value = self.get_verify_key(api_key)
            if value is None:
                raise Exception()

            items = value.split(',')
            verify_key = items[0]
            pro_id = items[1]

            msg = json.loads(self.request.body)
            # 判断  pro_id  和 api_key 是否对应
            if not ('pro_id' in msg and msg['pro_id'] == int(pro_id)):
                raise Exception()

            strdata = json.dumps(msg, separators=(',', ':'), sort_keys=True)
            api_name = self.request.uri[self.request.uri.rfind('/') + 1:]

            param = '|'.join([timestamp, api_name, strdata])
            print(param)
            msg = param.encode('utf8')
            if not verify_sig(verify_key=verify_key, sig=sig, msg=msg):
                raise Exception()

            return fun(self, *args, **kwargs)
        except Exception as e:
            self.write(self.error_ret_with_data(err_code=403, err_msg=str(f'invalid auth {e}'), data=None))
            return


    return wrapper






if __name__ == '__main__':
    pass

