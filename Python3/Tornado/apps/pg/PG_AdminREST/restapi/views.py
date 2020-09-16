import ed25519
import os
import random
import string
# from binascii import hexlify
from binascii import hexlify
import redis
import re
from django.contrib.auth.backends import ModelBackend
import datetime
from cryptography.fernet import Fernet
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, authentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework import viewsets
import hmac, base64, struct, time
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import JSONWebTokenAPIView
from PG_AdminREST.settings import REGEX_MOBILE, REDIS_HOST, REDIS_PORT, REDIS_LOG_CODE_DB_NAME_CACHE, ENV_NAME, \
    REGEX_KEY, REDIS_USER_TOKEN_DB_NAME, REGEX_EMAIL, REDIS_API_KEY__DB_NAME, g_MNEMONIC, DEBUG
from lib.my_bip44.wrapper import gen_bip44_subaddr_from_mnemonic
from lib.seng_mq import send_order_id_to_msq
from restapi.models import WithdrawOrder, Deposit, CollectionRecords, Address, CollectionConfig, Project, \
    WithdrawConfig, CollectionFeeConfig, UserAddressBalances, UserTokenBalances, Subaddress, AssetDailyReport, \
    UserOperationLog, AddAddressOrder, DjangoAdminLog, GoogleCode
from restapi.mythrottle import LoginBeforeThrottle
from restapi.serializers import WithdrawOrderSerializer, DepositSerializer, \
    CollectionRecordsSerializer, AddressSerializer, CollectionConfigSerializer, UsersSerializer, \
    WithdrawConfigSerializer, CollectionFeeConfigSerializer, CustomJWTSerializer, \
    MyJSONWebTokenSerializer, SubaddressSerializer, UserAddressBalancesSerializer, UserTokenBalancesSerializer, \
    AssetDailyReportSerializer, UserOperationLogSerializer, MyRefreshJSONWebTokenSerializer, \
    MyJSONWebTokenAuthentication, AddAddressOrderSerializer, AdminOperationLogSerializer
from rest_framework import permissions
import hashlib
from PG_AdminREST.settings import g_IS_MAINNET
import logging
logger = logging.getLogger(__name__)

if DEBUG == False:
    from bitcoin import SelectParams
    from bitcoin.wallet import CBitcoinAddress

jwt_decode_handler = api_settings.JWT_DECODE_HANDLER

# Create your views here.

all_token = ['HTDF', 'ETH', 'USDT', 'BTC', 'BTU']
audit_status_choices = ['REJECTED', 'PASSED']
HRC20FEE = ['BTU']
ERC20FEE = ['USDT']

is_superuser = 1
is_active = 1
admin_encrypt_key = 'z1skeYKtJf6ZaSmKRlz7J3pSy_pdZ0wXQohhscdPY4U='

user_status = ["未激活", '正常', '已冻结', '已禁用']


__all__ = ['MyBigDateList', 'CustomBackend', 'UsersViewSet', 'WithdrawOrderViewSet', 'DepositViewSet'
           , 'CollectionRecordsViewSet', 'AddressViewSet', 'SubaddressViewSet', 'CollectionConfigViewSet'
           , 'WithdrawConfigViewSet', 'CollectionFeeConfigViewSet', 'UserAddressBalancesViewSet',
           'UserTokenBalancesViewSet', 'AssetDailyReportViewSet', 'UserOperationLogViewSet',
           'AddAddressOrderViewSet', 'Reset', 'ResetKey', 'ResetGoogleCode', 'ObtainJSONWebToken',
           'RefreshJSONWebToken', 'AdminReset', 'AdminOperationLogViewSet']


if DEBUG == False:
    def is_valid_addr(address: str, token_name: str) -> bool:

        try:
            if token_name == 'HTDF' or token_name == 'BTU':
                return len(address) == 43 and  address.startswith('htdf1') and address.islower()
            elif token_name == 'ETH' or token_name == 'USDT':
                return len(address) == 42 and  address.startswith('0x') and  int(address, base=16)
            elif token_name == 'BTC':
                if g_IS_MAINNET:
                    SelectParams('mainnet')
                    addr = CBitcoinAddress(s = address)
                else:
                    SelectParams('testnet')
                    addr = CBitcoinAddress(s = address)

                assert addr is not None , 'addr is None'

                #如果没有抛异常直接返回即可
                return True
            else:
                raise RuntimeError(f"unknow token_name: {token_name}")
        except Exception as e:
            print(f'is_valid_addr() , {address} is invalid address, error:{e}')
            return False

        pass

def add_addr(pro_id, addr_index, token_name):
    mnemonic = g_MNEMONIC
    nettype = 'mainnet'
    if not g_IS_MAINNET:
        nettype = 'testnet'

    return gen_bip44_subaddr_from_mnemonic(mnemonic=mnemonic,
                                    coin_type=token_name,
                                    account_index=pro_id,
                                    address_index=addr_index,
                                    nettype=nettype)

def withdraw_add_addr(kwargs):

    token_name = kwargs["data"]["token_name"]
    if token_name in ERC20FEE:
        token_name = 'ETH'
    elif token_name in HRC20FEE:
        token_name = 'HTDF'

    addr_index = 0
    pro_id = kwargs["data"]["pro_id"]

    kwargs["data"]["address"] = add_addr(pro_id, addr_index, token_name)
    print(f'withdraw_add_addr success: {kwargs["data"]["address"]}')
    return kwargs

def encrypt_p(password):
    f = Fernet(admin_encrypt_key)
    p1 = password.encode()
    token = f.encrypt(p1)
    p2 = token.decode()
    return p2

def decrypt_p(password):
    f = Fernet(admin_encrypt_key)
    p1 = password.encode()
    token = f.decrypt(p1)
    p2 = token.decode()
    return p2

def check_data(self):
    """
    检查前端输入参数
    :param self:
    :return:
    """
    try:

        offset = self.request.GET.get("offset")
        limit = self.request.GET.get("limit")
        first_time = self.request.GET.get("first_time")
        end_time = self.request.GET.get("end_time")

        if first_time == None:
            first_time = ''

        if (not re.match(REGEX_KEY, first_time)) or (not re.match(REGEX_KEY, end_time)):
            return None, None
        if (not limit.isdigit()) or (not offset.isdigit()):
            return False

        # if not offset.isdigit():
        #     return False
        return first_time, end_time
    except Exception as e:
        print(f'check_data : {e}')
        return False

def MyBigDateList(self, request, *args, **kwargs):
    try:
        #自制优化分页器
        lenght = -1

        limit = int(request.query_params['limit'])
        offset = int(request.query_params['offset'])
        search = request.query_params['search']
        pro_id = request.query_params['pro_id']
        token_name = request.query_params['token_name']

        if search != '' or pro_id != '' or token_name != '' :
            query = self.get_queryset()
        else:
            all_query = self.get_queryset()
            lenght = all_query.len
            query = all_query[offset:offset+limit]


        queryset = self.filter_queryset(query)
        serializer = self.get_serializer(queryset, many=True)

        if lenght == -1:
            lenght = len(serializer.data)
            data = serializer.data[offset:offset + limit]
        else:
            data = serializer.data

        now_count = len(data)
        jdata = { "count" : lenght, "now_count" : now_count, "results" : data }

        return Response(jdata)
    except Exception as e:
        print(f'MyBigDateList error : {e}')
        return ({"Error":"参数错误!"})

def MyList(self, request, *args, **kwargs):


    queryset = self.filter_queryset(self.get_queryset())
    serializer = self.get_serializer(queryset, many=True)
    if 'limit' in request.query_params:
        limit = int(request.query_params['limit'])
    else:
        limit = ''
    if 'offset' in request.query_params:
        offset = int(request.query_params['offset'])
    else:
        offset = ''
    lenght = len(serializer.data)

    if limit == '' and offset == '':
        data = serializer.data
    else:
        data = serializer.data[offset:offset + limit]
    jdata =  { "count" : lenght, "results" : data }

    return Response(jdata)

def CreatGoogleCode():
    slcLetter = [random.choice(string.ascii_letters) for i in range(16)]
    key = ''.join(slcLetter)
    return key

def GoogleAuth(key):
    """
    谷歌验证码
    # RFC 协议下有HOTP和TOTP   前者是计数 后者是计时 生成验证码
    # hopt 由 RFC 协议 RFC4266
    # google auth 用的是TOTP  而TOTP是在HOTP的基础上计时
    :return:
    """

    def get_hotp_token(secret, intervals_no):
        """This is where the magic happens."""

        key = base64.b32decode(normalize(secret), True)
        msg = struct.pack(">Q", intervals_no)

        h = bytearray(hmac.new(key, msg, hashlib.sha1).digest())
        o = h[19] & 15
        h = str((struct.unpack(">I", h[o:o + 4])[0] & 0x7fffffff) % 1000000)
        return prefix0(h)

    def get_totp_token(secret):
        """The TOTP token is just a HOTP token seeded with every 30 seconds."""
        return get_hotp_token(secret, intervals_no=int(time.time()) // 30)

    def normalize(key):
        """Normalizes secret by removing spaces and padding with = to a multiple of 8"""
        k2 = key.strip().replace(' ', '')
        k2 = k2.upper()  # skipped b/c b32decode has a foldcase argument
        if len(k2) % 8 != 0:
            k2 += '=' * (8 - len(k2) % 8)
        return k2

    def prefix0(h):
        """Prefixes code with leading zeros if missing."""
        if len(h) < 6:
            h = '0' * (6 - len(h)) + h
        return h

    return get_totp_token(key)

def IsChinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

def ValidPassword(pwd):
    """
    密码验证
    :param pwd:
    :return:
    """
    length = len(pwd)
    # 密码加密后长度等于100
    if length == 100:
        if not IsChinese(pwd):
            return True
        else:
            return False
    else:
        return False

class CustomBackend(ModelBackend):
    """
    管理员登录验证
    """

    def authenticate(self, request, username=None, password=None, code=None, **kwargs):
        try:

            if not username.isalnum():
                raise Exception("500")
            if not ValidPassword(password):
                raise Exception("500")
            if (not code.isdigit()) or len(code) != 6:
                raise Exception("400")

            password = decrypt_p(password)

            super_user = User.objects.get(username=username, is_superuser=is_superuser, is_active=is_active)
            if not super_user.check_password(password):
                raise Exception("500")

            rds = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_LOG_CODE_DB_NAME_CACHE, decode_responses=True)

            url = f'{ENV_NAME}_code_admin_' + str(super_user.id)
            key = rds.get(url)
            if key:
                gcode = GoogleAuth(key)
                if code == gcode:
                    return super_user

            # 重写jwt 返回出错在 serializer截获 500代表账号密码错误
            raise Exception("400")
        except Exception as e:
            print(f'authenticate error :{e}')
            if str(e) == "400":
                raise Exception("400")
            else:
                raise Exception('500')

class UsersViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    用户信息
    list:
        ###$ JWT 身份验证: { Authorization : JWT {token} }


        模糊搜索接口: /adminrest/Users/?search=HTDF
        可搜索参数: {'pro_name', 'pro_id'}

        limit: 条数
        offset: 位置
        search: 搜索
        first_time: 开始时间
        end_time: 结束时间
    create:
        JWT 身份验证: { Authorization : JWT {token} }

        创建接口: /adminrest/Users/
        创建参数: {"pro_name", "tel_no", "email", "status"} #四个必填

    update:
        JWT 身份验证: { Authorization : JWT {token} }

        修改接口: /adminrest/Users/{id}/
        修改参数: {"pro_name", "tel_no", "email", "status"} # 任选

        !!!请求方式只能为 : PUT    #partial_update无效

    partial_update:
        提示

        !!!: 无效接口


    """

    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UsersSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['pro_name',]
    filter_fields = ('account_status', 'pro_id',)


    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误', status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        first_time, end_time = check_data(self)
        if first_time == None and end_time == None:
            return Project.objects.all().order_by('-create_time')
        else:
            return Project.objects.filter(create_time__range=[first_time, end_time]).order_by('-create_time')

    def list(self, request, *args, **kwargs):
        return MyList(self=self, request=request)

    def creat_get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.

        重写get_serializer
        """

        is_exist = Project.objects.filter(pro_name=kwargs["data"]["pro_name"])
        if is_exist:
            #用户重复错误 代号001
            raise Exception("001")

        kwargs["data"]["account_status"] = kwargs["data"]["status"]

        select_rst = Project.objects.all().order_by('-pro_id').first()
        # 保证id不为0
        pro_id = select_rst.pro_id + 1

        kwargs["data"]["bip44_account_index"] = pro_id
        kwargs["data"]["create_time"] = datetime.datetime.now()
        # 创建apikey
        kwargs["data"]["api_key"] = hexlify(os.urandom(32)).decode('utf8')

        # 创建公私钥
        client_sign_key, client_verify_key = ed25519.create_keypair()
        server_sign_key, server_verify_key = ed25519.create_keypair()

        # 公私钥写入
        kwargs["data"]["client_sign_key"] = client_sign_key.to_ascii(encoding='hex').decode('utf8')
        kwargs["data"]["client_verify_key"] = client_verify_key.to_ascii(encoding="hex").decode('utf8')
        kwargs["data"]["server_sign_key"] = server_sign_key.to_ascii(encoding='hex').decode('utf8')
        kwargs["data"]["server_verify_key"] = server_verify_key.to_ascii(encoding="hex").decode('utf8')

        # redis写入
        rds = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_API_KEY__DB_NAME, decode_responses=True)
        url = kwargs["data"]["client_verify_key"] + ',' + str(pro_id)
        rds.set(kwargs["data"]["api_key"], url)
        print(f'apikey write success: {kwargs["data"]["api_key"]}')

        msgbytes = hashlib.md5(str(kwargs["data"]["tel_no"]).encode('utf8')).digest()
        kwargs["data"]["password"] = hexlify(msgbytes).decode('latin1')
        print(kwargs["data"]["password"])

        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def update_get_serializer(self, *args, **kwargs):
        #重写更新序列化保存
        if 'pro_name' in kwargs["data"]:
            is_exist = Project.objects.filter(pro_name=kwargs["data"]["pro_name"])
            if is_exist:
                # 用户重复错误 代号001
                raise Exception("001")
        else:
            kwargs["data"]["pro_name"] = args[0].pro_name

        if 'status' in kwargs["data"]:
            kwargs["data"]["account_status"] = kwargs["data"]["status"]
        else:
            kwargs["data"]["account_status"] = args[0].account_status

        if 'tel_no' in kwargs["data"]:
            kwargs["data"]["tel_no"] = kwargs["data"]["tel_no"]
        else:
            kwargs["data"]["tel_no"] = args[0].tel_no

        if 'email' in kwargs["data"]:
            kwargs["data"]["email"] = kwargs["data"]["email"]
        else:
            kwargs["data"]["email"] = args[0].email


        kwargs["data"]["api_key"] = args[0].api_key
        kwargs["data"]["create_time"] = args[0].create_time
        kwargs["data"]["bip44_account_index"] = args[0].bip44_account_index

        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def create(self, request, *args, **kwargs):

        try:
            if request.stream.method != 'POST':
                raise Exception("013")

            #重写创建用户
            #请求参数保护
            if len(request.data) != 4:
                raise Exception("002")

            for i in request.data:
                if not i in ["pro_name", "tel_no", "email", "status"]:
                    raise Exception("002")

            if not re.match(REGEX_MOBILE, request.data["tel_no"]):
                raise Exception("003")

            if not re.match(REGEX_EMAIL, request.data["email"]):
                raise Exception("004")

            if not request.data["status"] in ["0", "1", "2", "3"]:
                raise Exception("005")

            serializer = self.creat_get_serializer(data=request.data)
            #新增自定义参数

            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            # 配置ETH手续费地址
            address = gen_bip44_subaddr_from_mnemonic(mnemonic=g_MNEMONIC, coin_type='ETH',
                                                      account_index=serializer.instance.pro_id, address_index=100000000)
            CollectionFeeConfig.objects.create(pro_id=serializer.instance, token_name='ERC20FEE', address=address)

            headers = self.get_success_headers(serializer.data)

            url = f'创建用户:  用户名: {request.data["pro_name"]} 手机号: {request.data["tel_no"]} ' \
                  f'邮箱: {request.data["email"]}  状态: {user_status[int(request.data["status"])]}'
            DjangoAdminLog.objects.create(user=request.user, change_message=url, object_id=serializer.data["pro_id"],
                        object_repr=serializer.data["pro_name"], action_time=datetime.datetime.now(), action_flag='200')

            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        except Exception as e:
            if str(e) == "001":
                data = {"code": "用户名重复!"}
            elif str(e) == "002":
                data = {"code": "请求参数错误!"}
            elif str(e) == "003":
                data = {"code": "手机号非法!"}
            elif str(e) == "004":
                data = {"code": "邮箱非法!"}
            elif str(e) == "005":
                data = {"code": "输入状态有误!"}
            elif str(e) == "013":
                data = {"code": "请求方式错误!"}
            else:
                print(f'user creat error : {e}')
                data = {"code" : "参数不符合要求或未知错误!"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            if request.stream.method != 'PUT':
                raise Exception("013")

            if len(request.data) < 1:
                raise Exception("002")

            url = f'修改用户: '

            # 重写创建用户
            # 请求参数保护
            for i in request.data:
                if not i in ["pro_name", "tel_no", "email", "status"]:
                    raise Exception("002")

            user = Project.objects.get(pro_id=kwargs["pk"])

            if 'pro_name' in request.data:
                url += f' 用户名: 修改前: {user.pro_name} | 修改后: {request.data["pro_name"]}'

            if 'tel_no' in request.data:
                if not re.match(REGEX_MOBILE, request.data["tel_no"]):
                    raise Exception("003")
                url += f' 手机号: 修改前: {user.tel_no} | 修改后: {request.data["tel_no"]}'

            if 'email' in request.data:
                if not re.match(REGEX_EMAIL, request.data["email"]):
                    raise Exception("004")
                url += f' 邮箱: 修改前: {user.email} | 修改后: {request.data["email"]}'

            if 'status' in request.data:
                if not request.data["status"] in ["0", "1", "2", "3"]:
                    raise Exception("005")
                url += f' 状态: 修改前: {user_status[int(user.account_status)]} | 修改后: {user_status[int(request.data["status"])]}'


            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.update_get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)


            DjangoAdminLog.objects.create(user=request.user, change_message=url, object_id=serializer.data["pro_id"],
                    action_time=datetime.datetime.now(), action_flag='200', object_repr=serializer.data["pro_name"] )

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)

        except Exception as e:
            if str(e) == "001":
                data = {"code": "用户名重复!"}
            elif str(e) == "002":
                data = {"code": "请求参数错误!"}
            elif str(e) == "003":
                data = {"code": "手机号非法!"}
            elif str(e) == "004":
                data = {"code": "邮箱非法!"}
            elif str(e) == "005":
                data = {"code": "输入状态有误!"}
            elif str(e) == "013":
                data = {"code": "请求方式错误!"}
            else:
                print(f'user update error : {e}')
                data = {"code": "参数不符合要求或未知错误!"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

class WithdrawOrderViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    提币记录
    list:
        ###$ JWT 身份验证: { Authorization : JWT {token} }


        模糊搜索接口: /adminrest/WithdrawOrder/?search=HTDF
        可搜索参数: {'pro_id', 'token_name', 'serial_id', 'order_id'}

        limit: 条数
        offset: 位置
        search: 搜索
        first_time: 开始时间
        end_time: 结束时间
    """

    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = WithdrawOrderSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['serial_id', 'order_id', 'from_addr']
    filter_fields = ('pro_id','token_name')

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误', status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        first_time, end_time = check_data(self)
        if first_time == None or end_time == None:
            data = WithdrawOrder.objects.select_related('pro_id').all().order_by('-serial_id')
            data.len = WithdrawOrder.objects.all().count()
            return data
        else:
            data = WithdrawOrder.objects.select_related('pro_id').filter(complete_time__range=[first_time, end_time]).order_by('-serial_id')
            data.len = WithdrawOrder.objects.filter(complete_time__range=[first_time, end_time]).count()
            return data

    def list(self, request, *args, **kwargs):
        return MyBigDateList(self=self, request=request)

class DepositViewSet( mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    充币记录
    list:
        ###$ JWT 身份验证: { Authorization : JWT {token} }

        模糊搜索接口: /adminrest/Deposit/?search=HTDF
        可搜索参数: {'pro_id', 'token_name', 'from_addr', 'to_addr'}

        limit: 条数
        offset: 位置
        search: 搜索
        first_time: 开始时间
        end_time: 结束时间
    """

    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DepositSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['from_addr', 'to_addr', 'tx_hash']
    filter_fields = ('pro_id','token_name')

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误', status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        first_time, end_time = check_data(self)
        if first_time == None and end_time == None:
            data = Deposit.objects.select_related('pro_id').all().order_by('-block_time')
            data.len = Deposit.objects.all().count()
            return data
        else:
            data = Deposit.objects.select_related('pro_id').filter(block_time__range=[first_time, end_time]).order_by('-block_time')
            data.len = Deposit.objects.filter(block_time__range=[first_time, end_time]).count()
            return data

    def list(self, request, *args, **kwargs):
        return MyBigDateList(self=self, request=request)

class CollectionRecordsViewSet( mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    归集记录
    list:
        ###$ JWT 身份验证: { Authorization : JWT {token} }

        模糊搜索接口: /adminrest/CollectionRecords/?search=HTDF
        可搜索参数: {'token_name', 'pro_id', 'from_address', 'to_address', 'tx_hash'}

        limit: 条数
        offset: 位置
        search: 搜索
        first_time: 开始时间
        end_time: 结束时间

    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CollectionRecordsSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['from_address', 'to_address', 'tx_hash']
    filter_fields = ('pro_id','token_name')

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误', status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        first_time, end_time = check_data(self)
        if first_time == None and end_time == None:
            data = CollectionRecords.objects.all().order_by('-complete_time')
            data.len = CollectionRecords.objects.select_related('pro_id').all().count()
            return data
        else:
            data = CollectionRecords.objects.select_related('pro_id').filter(complete_time__range=[first_time, end_time]).order_by('-complete_time')
            data.len = CollectionRecords.objects.filter(complete_time__range=[first_time, end_time]).count()
            return data

    def list(self, request, *args, **kwargs):
        return MyBigDateList(self=self, request=request)

class AddressViewSet( mixins.ListModelMixin, viewsets.GenericViewSet):
    """

    地址管理
    list:
        ###$ JWT 身份验证: { Authorization : JWT {token} }

        模糊搜索接口: /adminrest/Address/?search=HTDF
        可搜索参数: {'token_name', 'pro_id'}

        limit: 条数
        offset: 位置
        search: 搜索
        first_time: 开始时间
        end_time: 结束时间
    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AddressSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['token_name', 'pro_id__pro_id']
    filter_fields = ('pro_id','token_name')

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误', status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):

        first_time, end_time = check_data(self)
        if first_time == None and end_time == None:
            return Address.objects.select_related('pro_id').all().order_by('-update_time')
        else:
            return Address.objects.select_related('pro_id').filter(update_time__range=[first_time, end_time]).order_by('-update_time')

    def list(self, request, *args, **kwargs):
        return MyList(self=self, request=request)

class SubaddressViewSet( mixins.ListModelMixin, viewsets.GenericViewSet):
    """

    子地址
    list:
        ###$ JWT 身份验证: { Authorization : JWT {token} }

        模糊搜索接口: /adminrest/Subaddress/?search=HTDF
        可搜索参数: {'address', 'token_name'}

        精确搜索接口: /adminrest/Subaddress/?pro_id=1
        可搜索参数: {'pro_id'}

        limit: 条数
        offset: 位置
        search: 搜索
        first_time: 开始时间
        end_time: 结束时间

    """

    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = SubaddressSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['address',]
    filter_fields = ('pro_id', 'token_name',)

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误', status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        first_time, end_time = check_data(self)
        if first_time == None and end_time == None:
            data = Subaddress.objects.all().order_by('-create_time')
            data.len = Subaddress.objects.all().count()
            return data
        else:
            data = Subaddress.objects.filter(create_time__range=[first_time, end_time]).order_by('-create_time')
            data.len = Subaddress.objects.filter(create_time__range=[first_time, end_time]).count()
            return data

    def list(self, request, *args, **kwargs):
        return MyBigDateList(self=self, request=request)

class CollectionConfigViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    归集配置
    ----只有GET,PUT方式可访问, ----PATCH不可访问, ----id为归集配置id
    list:
        ###$ JWT 身份验证: { Authorization : JWT {token} }

        模糊搜索接口: /adminrest/CollectionConfig/?search=HTDF
        可搜索参数: {'pro_id', 'token_name'}

        精确搜索接口: /adminrest/CollectionConfig/?pro_id=1
        可搜索参数: {'pro_id'}

        limit: 条数
        offset: 位置
        search: 搜索
        first_time: 开始时间
        end_time: 结束时间
    create:
        JWT 身份验证: { Authorization : JWT {token} }

        创建接口: /adminrest/CollectionConfig/
        创建参数: {'pro_id', 'token_name', "min_amount_to_collect", 'collection_dst_addr'} #四个必填

    update:
        JWT 身份验证: { Authorization : JWT {token} }

        修改接口: /adminrest/CollectionConfig/{id}/
        修改参数: {'token_name', "min_amount_to_collect"} #两个必须填

        !!!请求方式只能为 : PUT    #partial_update无效

    partial_update:
        提示

        !!!: 无效接口

    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CollectionConfigSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['pro_id__pro_id', 'token_name']
    filter_fields = ('pro_id',)

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误', status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return CollectionConfig.objects.all()

    def list(self, request, *args, **kwargs):
        return MyList(self=self, request=request)

    def update_get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.

        重写get_serializer
        """

        kwargs["data"]["pro_id"] = args[0].pro_id_id
        kwargs["data"]["collection_dst_addr"] = args[0].collection_dst_addr
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        try:
            if request.stream.method != 'POST':
                raise Exception("013")

            if len(request.data) != 4:
                raise Exception("002")

            for i in request.data:
                if not i in ['pro_id', 'token_name', "min_amount_to_collect", 'collection_dst_addr']:
                    raise Exception("002")

            # 内容验证
            if float(request.data["min_amount_to_collect"]) < 0.001:
                raise Exception("006")

            if not request.data["token_name"] in all_token:
                raise Exception("007")

            if not request.data["pro_id"].isdigit():
                raise Exception("008")

            is_exist = Project.objects.filter(pro_id=request.data["pro_id"])
            if not is_exist:
                raise Exception("008")

            # 非开发模式开启 地址验证
            if DEBUG == False:
                if not is_valid_addr(token_name=request.data["token_name"], address=request.data["collection_dst_addr"]):
                    raise Exception("010")

            if request.data["token_name"] == 'USDT' or request.data["token_name"] == 'BTU':
                if request.data["token_name"] == 'USDT':
                    token_name = 'ETH'
                else:
                    token_name = 'HTDF'

                is_exist = CollectionConfig.objects.filter(pro_id=request.data["pro_id"], token_name=token_name)
                if not is_exist:
                    raise Exception("009")


            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            headers = self.get_success_headers(serializer.data)

            #生成hrc20代币手续费地址
            if request.data["token_name"] in HRC20FEE:
                address = add_addr(pro_id=request.data["pro_id"], addr_index=100000000, token_name='HTDF')
                CollectionFeeConfig.objects.create(pro_id=serializer.instance.pro_id, token_name='HRC20FEE', address=address)

            url = f'创建归集配置:  项目方: {request.data["pro_id"]} 币种: {request.data["token_name"]} ' \
                  f'最小归集金额: {request.data["min_amount_to_collect"]}  归集地址: {request.data["collection_dst_addr"]}'
            DjangoAdminLog.objects.create(user=request.user, change_message=url, object_id=serializer.data["pro_id"],
                                          action_time=datetime.datetime.now(), action_flag='200')
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            if str(e) == "002":
                data = {"code": "请求参数错误!"}
            elif str(e) == "006":
                data = {"code": "最小金额错误!"}
            elif str(e) == "007":
                data = {"code": "币种错误!"}
            elif str(e) == "008":
                data = {"code": "pro_id非法!"}
            elif str(e) == "009":
                data = {"code": "该币种不能独立创建!"}
            elif str(e) == "010":
                data = {"code": "地址格式错误!"}
            elif str(e) == "013":
                data = {"code": "请求方式错误!"}
            else:
                data = {"code": "输入币种重复或未知错误!"}
                print(f'creat CollectionConfig error: {e}')
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            if request.stream.method != 'PUT':
                raise Exception("013")

            partial = kwargs.pop('partial', False)
            instance = self.get_object()

            if len(request.data) != 2:
                raise Exception("002")

            # TODO:重写部分安全保护
            for i in request.data:
                if not i in ['token_name', "min_amount_to_collect"]:
                    raise Exception("002")

            # TODO:提币地址,安全保护
            if "collection_dst_addr" in request.data:
                raise Exception("999")

            if "pro_id" in request.data:
                raise Exception("999")

            # 内容验证
            if float(request.data["min_amount_to_collect"]) < 0.001:
                raise Exception("006")

            if not request.data["token_name"] in all_token:
                raise Exception("007")

            if instance.token_name != request.data["token_name"]:
                raise Exception("007")

            user = CollectionConfig.objects.get(id=kwargs["pk"])

            serializer = self.update_get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            url = f'修改归集配置:  币种: {request.data["token_name"]}  最小归集金额: 修改前: {user.min_amount_to_collect} ' \
                  f'| 修改后: {request.data["min_amount_to_collect"]}'

            DjangoAdminLog.objects.create(user=request.user, change_message=url, object_id=serializer.data["pro_id"],
                                          action_time=datetime.datetime.now(), action_flag='200')

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)
        except Exception as e:
            if str(e) == "002":
                data = {"code": "请求参数错误!"}
            elif str(e) == "006":
                data = {"code": "最小金额错误!"}
            elif str(e) == "007":
                data = {"code": "币种错误!"}
            elif str(e) == "999":
                data = {"code": "危险操作!"}
            elif str(e) == "013":
                data = {"code": "请求方式错误!"}
            else:
                data = {"code": "输入币种重复或未知错误!"}
                print(f'update CollectionConfig error: {e}')

            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

class WithdrawConfigViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    提币配置
    ----只有GET,PUT方式可访问, ----PATCH不可访问, ----id为提币配置id
    list:
        ###$ JWT 身份验证: { Authorization : JWT {token} }

        模糊搜索接口: /adminrest/WithdrawConfig/?search=HTDF
        可搜索参数: {'pro_id', 'token_name'}

        精确搜索接口: /adminrest/WithdrawConfig/?pro_id=1
        可搜索参数: {'pro_id'}

        limit: 条数
        offset: 位置
        search: 搜索
        first_time: 开始时间
        end_time: 结束时间

    create:
        JWT 身份验证: { Authorization : JWT {token} }

        创建接口: /adminrest/WithdrawConfig/
        创建参数: {'pro_id', 'token_name', "min_amount", 'max_amount', 'balance_threshold_to_sms'}
        #五个必填

    update:
        JWT 身份验证: { Authorization : JWT {token} }

        修改接口: /adminrest/WithdrawConfig/{id}/
        修改参数: {"token_name", "min_amount", "max_amount", "balance_threshold_to_sms"}
        # token_name必要,其他任选

        !!!请求方式只能为 : PUT    #partial_update无效

    partial_update:
        提示

        !!!: 无效接口


    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = WithdrawConfigSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['pro_id__pro_id', 'token_name']
    filter_fields = ('pro_id',)


    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误', status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return WithdrawConfig.objects.all()

    def list(self, request, *args, **kwargs):
        return MyList(self=self, request=request)

    def creat_get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        kwargs = withdraw_add_addr(kwargs)

        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def update_get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        kwargs["data"]["address"] = args[0].address
        kwargs["data"]["pro_id"] = args[0].pro_id_id

        if 'min_amount' in kwargs["data"]:
            pass
        else:
            kwargs["data"]["min_amount"] = args[0].min_amount

        if 'max_amount' in kwargs["data"]:
            pass
        else:
            kwargs["data"]["max_amount"] = args[0].max_amount

        if 'balance_threshold_to_sms' in kwargs["data"]:
            pass
        else:
            kwargs["data"]["balance_threshold_to_sms"] = args[0].balance_threshold_to_sms

        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def create(self, request, *args, **kwargs):

        try:

            if request.stream.method != 'POST':
                raise Exception("013")

            if len(request.data) != 5:
                raise Exception("002")

            for i in request.data:
                if not i in ['pro_id', 'token_name', "min_amount", 'max_amount', 'balance_threshold_to_sms']:
                    raise Exception("002")

            # 内容验证
            if float(request.data["min_amount"]) < 0.001:
                raise Exception("006")

            if float(request.data["max_amount"]) < 0.001:
                raise Exception("011")

            if float(request.data["min_amount"]) >= float(request.data["max_amount"]):
                raise Exception("006")

            if float(request.data["balance_threshold_to_sms"]) < 0:
                raise Exception("012")

            if not request.data["token_name"] in all_token:
                raise Exception("007")

            # TODO:提币地址,安全保护
            if "address" in request.data:
                raise Exception("999")

            if not request.data["pro_id"].isdigit():
                raise Exception("008")

            is_exist = Project.objects.filter(pro_id=request.data["pro_id"])
            if not is_exist:
                raise Exception("008")

            if request.data["token_name"] == 'USDT' or request.data["token_name"] == 'BTU':
                if request.data["token_name"] == 'USDT':
                    token_name = 'ETH'
                else:
                    token_name = 'HTDF'

                is_exist = WithdrawConfig.objects.filter(pro_id=request.data["pro_id"], token_name=token_name)
                if not is_exist:
                    raise Exception("009")

            serializer = self.creat_get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)

            url = f'创建提币配置:  项目方: {request.data["pro_id"]} 币种: {request.data["token_name"]} ' \
                  f'最小提币金额: {request.data["min_amount"]}  最大提币金额: {request.data["max_amount"]} ' \
                  f'短信阈值: {request.data["balance_threshold_to_sms"]}'
            DjangoAdminLog.objects.create(user=request.user, change_message=url, object_id=serializer.data["pro_id"],
                                          action_time=datetime.datetime.now(), action_flag='200')

            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        except Exception as e:
            if str(e) == "002":
                data = {"code": "请求参数错误!"}
            elif str(e) == "006":
                data = {"code": "最小金额错误!"}
            elif str(e) == "007":
                data = {"code": "币种错误!"}
            elif str(e) == "008":
                data = {"code": "pro_id非法!"}
            elif str(e) == "009":
                data = {"code": "该币种不能独立创建!"}
            elif str(e) == "011":
                data = {"code": "最大金额错误!"}
            elif str(e) == "012":
                data = {"code": "短信阈值格式错误!"}
            elif str(e) == "013":
                data = {"code": "请求方式错误!"}
            elif str(e) == "999":
                data = {"code": "危险操作!"}
            else:
                data = {"code": "输入币种重复或未知错误!"}
                print(f'creat WithdrawConfig error: {e}')
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            if request.stream.method != 'PUT':
                raise Exception("013")

            if len(request.data) < 2:
                raise Exception("002")

            if not "token_name" in request.data:
                raise Exception("002")

            # TODO:提币地址,安全保护
            if "address" in request.data:
                raise Exception("999")
            if "pro_id" in request.data:
                raise Exception("999")

            # TODO:重写部分安全保护
            for i in request.data:
                if not i in ["token_name", "min_amount", "max_amount", "balance_threshold_to_sms"]:
                    raise Exception("002")

            # 内容验证
            if 'min_amount' in request.data:
                if float(request.data["min_amount"]) < 0.001:
                    raise Exception("006")
            if 'max_amount' in request.data:
                if float(request.data["max_amount"]) < 0.001:
                    raise Exception("011")

            if 'balance_threshold_to_sms' in request.data:
                if float(request.data["balance_threshold_to_sms"]) < 0:
                    raise Exception("012")

            if not request.data["token_name"] in all_token:
                raise Exception("007")

            user = WithdrawConfig.objects.get(id=kwargs["pk"])

            partial = kwargs.pop('partial', False)
            instance = self.get_object()

            if instance.token_name != request.data["token_name"]:
                raise Exception("007")

            serializer = self.update_get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            url = f'修改提币配置:  币种: {request.data["token_name"]}  最小提币金额: 修改前: {user.min_amount} ' \
                  f'| 修改后: {request.data["min_amount"]}  最大提币金额: 修改前: {user.max_amount} ' \
                  f'| 修改后: {request.data["max_amount"]}  短信阈值: 修改前: {user.balance_threshold_to_sms} ' \
                  f'| 修改后: {request.data["balance_threshold_to_sms"]}'

            DjangoAdminLog.objects.create(user=request.user, change_message=url, object_id=serializer.data["pro_id"],
                                          action_time=datetime.datetime.now(), action_flag='200')

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)
        except Exception as e:
            if str(e) == "002":
                data = {"code": "请求参数错误!"}
            elif str(e) == "006":
                data = {"code": "最小金额错误!"}
            elif str(e) == "007":
                data = {"code": "币种错误!"}
            elif str(e) == "999":
                data = {"code": "危险操作!"}
            elif str(e) == "013":
                data = {"code": "请求方式错误!"}
            elif str(e) == "011":
                data = {"code": "最大金额错误!"}
            elif str(e) == "012":
                data = {"code": "短信阈值格式错误!"}
            else:
                data = {"code": "输入币种重复或未知错误!"}
                print(f'creat CollectionConfig error: {e}')
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

class CollectionFeeConfigViewSet( mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    手续费配置

    list:
        ###$ JWT 身份验证: { Authorization : JWT {token} }

        模糊搜索接口: /adminrest/CollectionFeeConfig/?search=HTDF
        可搜索参数: {'pro_id', 'token_name'}

        精确搜索接口: /adminrest/CollectionFeeConfig/?audit_status=1
        可搜索参数: {'pro_id'}

        limit: 条数
        offset: 位置
        search: 搜索
        first_time: 开始时间
        end_time: 结束时间

    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CollectionFeeConfigSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['pro_id__pro_id', 'token_name']
    filter_fields = ('pro_id',)


    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误', status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return CollectionFeeConfig.objects.all()

    def list(self, request, *args, **kwargs):
        return MyList(self=self, request=request)

class UserAddressBalancesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    用户地址资产
    list:
        ###$ JWT 身份验证: { Authorization : JWT {token} }


        模糊搜索接口: /adminrest/UserAddressBalances/?search=HTDF
        可搜索参数: {'token_name', 'address'}

        limit: 条数
        offset: 位置
        search: 搜索
        first_time: 开始时间
        end_time: 结束时间

    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserAddressBalancesSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]

    search_fields = ['address',]
    filter_fields = ('pro_id', 'token_name',)

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误', status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        first_time, end_time = check_data(self)
        if first_time == None and end_time == None:
            data = UserAddressBalances.objects.all().values("pro_id", "token_name", "address", "balance", "update_time").order_by('-update_time')
            data.len = UserAddressBalances.objects.all().values("pro_id", "token_name", "address", "balance", "update_time").count()
            return data
        else:
            # TODO:特殊写法,自带orm会带id去查询,导致各种报错,故以此解决问题之根本
            data = UserAddressBalances.objects.filter(update_time__range=[first_time, end_time]).values("pro_id", "token_name",
                                        "address", "balance", "update_time").order_by('-update_time')
            data.len = UserAddressBalances.objects.filter(update_time__range=[first_time, end_time]).values("pro_id", "token_name",
                                        "address", "balance", "update_time").count()
            return data

    def list(self, request, *args, **kwargs):
        return MyBigDateList(self=self, request=request)

class UserTokenBalancesViewSet( mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    用户币种资产
    list:
        ###$ JWT 身份验证: { Authorization : JWT {token} }

        模糊搜索接口: /adminrest/UserTokenBalances/?search=HTDF
        可搜索参数: {'token_name', 'withdraw_address', 'pro_id'}

        limit: 条数
        offset: 位置
        search: 搜索
        first_time: 开始时间
        end_time: 结束时间

    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserTokenBalancesSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['withdraw_address', ]
    filter_fields = ('pro_id', 'token_name',)

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误', status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        first_time, end_time = check_data(self)
        if first_time == None and end_time == None:
            return UserTokenBalances.objects.select_related('pro_id').all().order_by('-update_time')
        else:
            return UserTokenBalances.objects.select_related('pro_id').filter(update_time__range=[first_time, end_time]).order_by('-update_time')

    def list(self, request, *args, **kwargs):
        return MyList(self=self, request=request)

class AssetDailyReportViewSet( mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    资产日报表
    list:
        ###$ JWT 身份验证: { Authorization : JWT {token} }

        模糊搜索接口: /adminrest/AssetDailyReport/?search=HTDF
        可搜索参数: {'token_name', 'pro_id'}

        limit: 条数
        offset: 位置
        search: 搜索
        first_time: 开始时间
        end_time: 结束时间

    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    throttle_scope = 'AssetDailyReport'
    serializer_class = AssetDailyReportSerializer

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['token_name', 'pro_id__pro_id']
    filter_fields = ('pro_id', 'token_name',)

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误', status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        first_time, end_time = check_data(self)
        if first_time == None and end_time == None:
            data = AssetDailyReport.objects.select_related('pro_id').all().order_by('-update_time')
            data.len = AssetDailyReport.objects.all().count()
            return data
        else:
            data = AssetDailyReport.objects.select_related('pro_id').filter(update_time__range=[first_time, end_time]).order_by('-update_time')
            data.len = AssetDailyReport.objects.filter(update_time__range=[first_time, end_time]).count()
            return data

    def list(self, request, *args, **kwargs):
        return MyBigDateList(self=self, request=request)

class UserOperationLogViewSet( mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    用户操作日志
    list:
        ###$ JWT 身份验证: { Authorization : JWT {token} }

        模糊搜索接口: /adminrest/UserOperationLog/?search=HTDF
        可搜索参数: {'operation_time', 'function_name', 'pro_id'}

        limit: 条数
        offset: 位置
        search: 搜索
        first_time: 开始时间
        end_time: 结束时间

    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserOperationLogSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['operation_time', 'function_name']
    filter_fields = ('pro_id',)


    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误', status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        first_time, end_time = check_data(self)
        if first_time == None and end_time == None:
            return UserOperationLog.objects.select_related('pro_id').all().order_by('-operation_time')
        else:
            return UserOperationLog.objects.select_related('pro_id').filter(operation_time__range=[first_time, end_time]).order_by('-operation_time')

    def list(self, request, *args, **kwargs):
        return MyList(self=self, request=request)

class AddAddressOrderViewSet( mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    地址审核接口
    list:
        ###$ JWT 身份验证: { Authorization : JWT {token} }

        模糊搜索接口: /adminrest/AddAddressOrder/?search=HTDF
        可搜索参数: {'pro_id', 'order_id', 'token_name'}

        精确搜索接口: /adminrest/AddAddressOrder/?audit_status=1
        可搜索参数: {'audit_status'}

        |  limit |  条数  |
        | offset |  位置  |
        | search |  搜索  |
        | first_time | 开始时间 |
        | end_time | 结束时间 |

    update:
        JWT 身份验证: { Authorization : JWT {token} }

        修改接口: /adminrest/AddAddressOrder/{id}/
        修改参数: {"audit_status", "remark"} #两个必须填

        !!!请求方式只能为 : PUT    #partial_update无效

    partial_update:
        提示

        !!!: 无效接口

    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AddAddressOrderSerializer

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['order_id',]
    filter_fields = ('audit_status', 'token_name', 'pro_id')

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误', status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        first_time, end_time = check_data(self)
        if first_time == None and end_time == None:
            return AddAddressOrder.objects.select_related('pro_id').all().order_by('-order_create_time')
        else:
            return AddAddressOrder.objects.select_related('pro_id').filter(order_create_time__range=[first_time, end_time]).order_by('-order_create_time')

    def list(self, request, *args, **kwargs):
        return MyList(self=self, request=request)

    def update_get_serializer(self, args, kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """

        update_rst = AddAddressOrder.objects.filter(order_id=args["pk"]).first()
        if update_rst:
            if kwargs["audit_status"] == "PASSED":
                update_rst.audit_status = 'PASSED'
                update_rst.remark = kwargs["remark"]
                update_rst.audit_complete_time = datetime.datetime.now()
                update_rst.save()

                data = {"order_id": args["pk"], "audit_complete_time": int(datetime.datetime.now().timestamp())}
                print(f'data : {data}')
                send_order_id_to_msq(data)
                print(f'send_order_msq : success')

            else:
                update_rst.order_complete_time = datetime.datetime.now()
                update_rst.audit_complete_time = datetime.datetime.now()
                update_rst.order_status = 'FAIL'
                update_rst.audit_status = 'REJECTED'
                update_rst.remark = kwargs["remark"]
                update_rst.save()
                print(f'AddAddressOrder fail order_id:{args["pk"]}')

            return True

        raise Exception("002")

    def update(self, request, *args, **kwargs):

        try:
            #判方式
            if request.stream.method != 'PUT':
                raise Exception("013")
            #判长度
            if len(request.data) != 2:
                raise Exception("002")
            #判请求参数
            for i in request.data:
                if not i in ["audit_status", "remark"]:
                    raise Exception("002")

            if not request.data["audit_status"] in audit_status_choices:
                raise Exception("002")

            is_exist = AddAddressOrder.objects.filter(Q(order_id=kwargs["pk"]), Q(audit_status='PASSED') | Q(audit_status="REJECTED")).exists()
            if is_exist:
                raise Exception("014")

            rst = self.update_get_serializer(kwargs, request.data)
            if rst:
                data = {"code": "修改成功!"}

                url = f'修改地址审核:  订单号: {kwargs["pk"]}  审核状态: 修改前: 待审核 ' \
                      f'| 修改后: {request.data["audit_status"]} 备注: 修改前: 空 | 修改后: {request.data["remark"]}'

                DjangoAdminLog.objects.create(user=request.user, change_message=url,
                                              object_id=kwargs["pk"],
                                              action_time=datetime.datetime.now(), action_flag='200')

                return Response(data=data, status=status.HTTP_200_OK)

            raise Exception("rst = None, 代码错误!")

        except Exception as e:
            if str(e) == "002":
                data = {"code": "请求参数错误!"}
            elif str(e) == "013":
                data = {"code": "请求方式错误!"}
            elif str(e) == "014":
                data = {"code": "该订单已审核过!"}
            else:
                data = {"code": "未知错误!"}
                print(f'update AddAddressOrder error: {e}')

            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

class Reset(APIView):
    """
    修改密码

    update :
        ###$ JWT 身份验证: { Authorization : JWT {token} }

        superpassword: 为aes加密
        password和password_two 为md5加密

        修改接口: /adminrest/reset/
        修改参数: {'superusername', 'superpassword', "tel_no", 'pro_id', 'password', 'password_two', 'code'}
        #必选
        !!!请求方式只能为 : PUT    #partial_update无效

    partial_update:
        提示

        !!!: 无效接口


    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误', status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        # 获取参数
        try:
            if len(request.data) != 7:
                raise Exception("002")

            for i in request.data:
                if not i in ['superusername', 'superpassword', "tel_no", 'pro_id',
                             'password', 'password_two', 'code']:
                    raise Exception("002")

            superusername = request.data["superusername"]
            superpassword = request.data["superpassword"]
            tel_no = request.data["tel_no"]
            pro_id = request.data["pro_id"]
            password = request.data["password"]
            password_two = request.data["password_two"]
            code = request.data["code"]

            if not pro_id.isdigit():
                raise Exception("008")

            if not re.match(REGEX_MOBILE, tel_no):
                raise Exception("003")

            if password != password_two:
                raise Exception("021")

            if len(password) != 32:
                raise Exception("022")

            # 管理员用户密码验证

            CustomBackend.authenticate(self, request,username=superusername, password=superpassword,
                                                  code=code)

            # #前端修改用户密码加密为md5
            # msgbytes = hashlib.md5(str(password).encode('utf8')).digest()
            # make_passwd = hexlify(msgbytes).decode('latin1')

            # 修改密码为新密码
            user = Project.objects.filter(pro_id=pro_id, tel_no=tel_no).first()
            if user:
                user.password = password
                user.save()
            else:
                raise Exception("008")

            rds2 = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_USER_TOKEN_DB_NAME,
                               decode_responses=True)
            url = f'{ENV_NAME}_token_{user.pro_id}'
            rds2.delete(url)

            data = {"code": "修改密码成功!"}

            url = f'修改用户密码:  项目方: {pro_id}  手机号: {tel_no}'

            DjangoAdminLog.objects.create(user=request.user, change_message=url,
                                          object_id=pro_id,
                                          action_time=datetime.datetime.now(), action_flag='200')

            # 返回数据
            return Response(data=data, status=status.HTTP_200_OK)

        except Exception as e:
            if str(e) == "002":
                data = {"code": "请求参数错误!"}
            elif str(e) == "008":
                data = {"code": "pro_id非法!"}
            elif str(e) == "003":
                data = {"code": "手机号非法!"}
            elif str(e) == "500":
                data = {"code": "账号密码错误!"}
            elif str(e) == "400":
                data = {"code": "验证码错误!"}
            elif str(e) == "021":
                data = {"code": "密码不一致!"}
            elif str(e) == "022":
                data = {"code": "新密码格式错误!"}
            else:
                data = {"code": "未知错误!"}
                print(f'Reset error : {e}')

            return Response(status=status.HTTP_400_BAD_REQUEST, data=data)

class ResetKey(APIView):
    """

    update :
        ###$ JWT 身份验证: { Authorization : JWT {token} }

        superpassword: 为aes加密

        修改接口: /adminrest/resetkey/
        修改参数: { 'superusername', 'superpassword', "tel_no", 'pro_id', 'code'}
        #必选
        !!!请求方式只能为 : PUT    #partial_update无效

    partial_update:
        提示

        !!!: 无效接口


    """

    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误', status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):

        try:
            if len(request.data) != 5:
                raise Exception("002")

            for i in request.data:
                if not i in ['superusername', 'superpassword', "tel_no", 'pro_id', 'code']:
                    raise Exception("002")

            superusername = request.data["superusername"]
            superpassword = request.data["superpassword"]
            tel_no = request.data["tel_no"]
            pro_id = request.data["pro_id"]
            code = request.data["code"]

            if not re.match(REGEX_MOBILE, tel_no):
                raise Exception("003")

            if not pro_id.isdigit():
                raise Exception("008")

            CustomBackend.authenticate(self, request=None, username=superusername, password=superpassword,
                                       code=code)

            user = Project.objects.filter(pro_id=pro_id, tel_no=tel_no).first()
            if user:

                # 创建apikey
                api_key = hexlify(os.urandom(32)).decode('utf8')

                # 创建公私钥
                client_sign_key, client_verify_key = ed25519.create_keypair()
                server_sign_key, server_verify_key = ed25519.create_keypair()

                # 公私钥写入
                client_sign_key = client_sign_key.to_ascii(encoding='hex').decode('utf8')
                client_verify_key = client_verify_key.to_ascii(encoding="hex").decode('utf8')
                server_sign_key = server_sign_key.to_ascii(encoding='hex').decode('utf8')
                server_verify_key = server_verify_key.to_ascii(encoding="hex").decode('utf8')

                # redis
                rds = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_API_KEY__DB_NAME, decode_responses=True)
                rds.delete(user.api_key)

                user.api_key = api_key
                user.client_sign_key = client_sign_key
                user.client_verify_key = client_verify_key
                user.server_sign_key = server_sign_key
                user.server_verify_key = server_verify_key
                user.save()

                url = client_verify_key + ',' + str(pro_id)
                rds.set(api_key, url)

                data = {"code":"重置成功!"}

                url = f'重置用户密钥:  项目方: {pro_id}  手机号: {tel_no}'

                DjangoAdminLog.objects.create(user=request.user, change_message=url,
                                              object_id=pro_id,
                                              action_time=datetime.datetime.now(), action_flag='200')

                return Response(status=status.HTTP_200_OK, data=data)

            else:
                raise Exception('008')

        except Exception as e:
            if str(e) == "002":
                data = {"code": "请求参数错误!"}
            elif str(e) == "008":
                data = {"code": "pro_id非法!"}
            elif str(e) == "003":
                data = {"code": "手机号非法!"}
            elif str(e) == "500":
                data = {"code": "账号密码错误!"}
            elif str(e) == "400":
                data = {"code": "验证码错误!"}
            else:
                data = {"code": "未知错误!"}
                print(f'ResetKey error : {e}')

            return Response(status=status.HTTP_400_BAD_REQUEST, data=data)

class ResetGoogleCode(APIView):
    """
    update :
        ###$ JWT 身份验证: { Authorization : JWT {token} }

        superpassword: 为aes加密

        修改接口: /adminrest/resetgooglecode/
        修改参数: {'superusername', 'superpassword', "tel_no", 'pro_id', 'code'}
        #必选
        !!!请求方式只能为 : PUT    #partial_update无效

    partial_update:
        提示

        !!!: 无效接口

    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误', status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            if len(request.data) != 5:
                raise Exception("002")

            for i in request.data:
                if not i in ['superusername', 'superpassword', "tel_no", 'pro_id', 'code']:
                    raise Exception("002")

            superusername = request.data["superusername"]
            superpassword = request.data["superpassword"]
            tel_no = request.data["tel_no"]
            pro_id = request.data["pro_id"]
            code = request.data["code"]

            if not re.match(REGEX_MOBILE, tel_no):
                raise Exception("003")

            if not pro_id.isdigit():
                raise Exception("008")

            CustomBackend.authenticate(self, request=None, username=superusername, password=superpassword,
                                       code=code)

            user = Project.objects.filter(pro_id=pro_id, tel_no=tel_no).first()
            if user:
                rds = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_LOG_CODE_DB_NAME_CACHE, decode_responses=True)
                url = f'{ENV_NAME}_code_' + pro_id
                rds.delete(url)
                url = f'{ENV_NAME}_first_login_' + pro_id
                rds.delete(url)

                GoogleCode.objects.filter(pro_id=pro_id).delete()

                data = {"code": "重置成功!"}

                url = f'重置用户谷歌验证码:  项目方: {pro_id}  手机号: {tel_no}'

                DjangoAdminLog.objects.create(user=request.user, change_message=url,
                                              object_id=pro_id,
                                              action_time=datetime.datetime.now(), action_flag='200')
                return Response(status=status.HTTP_200_OK, data=data)

            raise Exception('008')

        except Exception as e:
            if str(e) == "002":
                data = {"code": "请求参数错误!"}
            elif str(e) == "008":
                data = {"code": "pro_id非法!"}
            elif str(e) == "003":
                data = {"code": "手机号非法!"}
            elif str(e) == "500":
                data = {"code": "账号密码错误!"}
            elif str(e) == "400":
                data = {"code": "验证码错误!"}
            else:
                data = {"code": "未知错误!"}
                print(f'ResetKey error : {e}')

            return Response(status=status.HTTP_400_BAD_REQUEST, data=data)

class ObtainJSONWebToken(CustomJWTSerializer):
    """
    提示:
        !!!此为POST 登录接口 /adminrest/login/

        密钥: z1skeYKtJf6ZaSmKRlz7J3pSy_pdZ0wXQohhscdPY4U=
        json 参数:
        {
            #必填
            "username": "admin",
            "password": "gAAAAABfHpEK_WdtNYILCCSnrrgm4t57dhvouKw4eCxf5qjVycy
            XcJ7LIpTefsjLF-98Am8nqVRNty-jxc4xobMlgOWZUuRyuQ==",
            "code" : "681721"
        }

    """
    throttle_classes = [LoginBeforeThrottle]
    # 重写jwt登录验证
    serializer_class = MyJSONWebTokenSerializer

obtain_jwt_token = ObtainJSONWebToken.as_view()

class RefreshJSONWebToken(JSONWebTokenAPIView):
    """
        ###$ JWT 身份验证: { Authorization : JWT {token} }


        !!!此为POST 刷新token接口 /adminrest/refresh/

        密钥: z1skeYKtJf6ZaSmKRlz7J3pSy_pdZ0wXQohhscdPY4U=
        json 参数:
        {
            #必填
            "token":""
        }
    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = MyRefreshJSONWebTokenSerializer

Refresh_jwt_token = RefreshJSONWebToken.as_view()

class AdminReset(APIView):
    """
    修改超级管理员密码

    update :
        ###$ JWT 身份验证: { Authorization : JWT {token} }

        superpassword: 为aes加密
        password和password_two 为aes加密

        修改接口: /adminrest/adminreset/
        修改参数: {'superusername', 'superpassword', 'password', 'password_two', 'code'}
        #必选
        !!!请求方式只能为 : PUT    #partial_update无效

    partial_update:
        提示

        !!!: 无效接口


    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误', status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        # 获取参数
        try:
            if len(request.data) != 5:
                raise Exception("002")

            for i in request.data:
                if not i in ['superusername', 'superpassword',
                             'password', 'password_two', 'code']:
                    raise Exception("002")

            superusername = request.data["superusername"]
            superpassword = request.data["superpassword"]
            password = request.data["password"]
            password_two = request.data["password_two"]
            code = request.data["code"]

            if password != password_two:
                raise Exception("021")

            if (not code.isdigit()) or len(code) != 6:
                raise Exception("400")

            # 管理员用户密码验证

            user = CustomBackend.authenticate(self, request, username=superusername, password=superpassword,
                                                  code=code)

            password = decrypt_p(password)
            if not (8<=len(password)<=16):
                raise Exception('022')

            # 修改密码为新密码
            if user:
                user.password = make_password(password, None, 'pbkdf2_sha256')
                user.save()

            rds2 = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_USER_TOKEN_DB_NAME,
                               decode_responses=True)
            url = f'{ENV_NAME}_admin_token_{user.id}'
            rds2.delete(url)

            data = {"code": "修改密码成功!"}

            url = f'修改管理员密码:  管理员 : {user.id} '

            DjangoAdminLog.objects.create(user=request.user, change_message=url,
                                          object_id=user.id,
                                          action_time=datetime.datetime.now(), action_flag='200')
            # 返回数据
            return Response(data=data, status=status.HTTP_200_OK)

        except Exception as e:
            if str(e) == "002":
                data = {"code": "请求参数错误!"}
            elif str(e) == "008":
                data = {"code": "pro_id非法!"}
            elif str(e) == "003":
                data = {"code": "手机号非法!"}
            elif str(e) == "500":
                data = {"code": "账号密码错误!"}
            elif str(e) == "400":
                data = {"code": "验证码错误!"}
            elif str(e) == "021":
                data = {"code": "密码不一致!"}
            elif str(e) == "022":
                data = {"code": "新密码格式错误!"}
            else:
                data = {"code": "未知错误!"}
                print(f'ResetKey error : {e}')

            return Response(status=status.HTTP_400_BAD_REQUEST, data=data)

class AdminOperationLogViewSet( mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    管理员操作日志
    list:
        ###$ JWT 身份验证: { Authorization : JWT {token} }

        模糊搜索接口: /adminrest/AdminOperationLog/?search=HTDF
        可搜索参数: {'action_time', 'object_id', 'object_repr'}

        limit: 条数
        offset: 位置
        search: 搜索
        first_time: 开始时间
        end_time: 结束时间

    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AdminOperationLogSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['action_time', 'object_id', 'object_repr']
    filter_fields = ('user',)

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误', status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        first_time, end_time = check_data(self)
        if first_time == None and end_time == None:
            return DjangoAdminLog.objects.all().order_by('-action_time')
        else:
            return DjangoAdminLog.objects.filter(action_time__range=[first_time, end_time]).order_by('-action_time')

    def list(self, request, *args, **kwargs):
        return MyList(self=self, request=request)

