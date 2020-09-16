import random
import string
from config.config import config
# import pymysql
import redis
import re
from django.contrib.auth.backends import ModelBackend
import datetime
from rest_framework import filters, status, authentication, pagination
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework import viewsets
import hmac, base64, struct, time
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import JSONWebTokenAPIView
from PG_Client.settings import REGEX_MOBILE, REDIS_HOST, REDIS_PORT, REDIS_API_KEY_DB_NAME_CACHE, ENV_NAME, REGEX_KEY, \
    REDIS_API_KEY_DB_NAME
from clientadmin.models import WithdrawOrder, Deposit, CollectionRecords, Address, CollectionConfig, Project, \
    WithdrawConfig, CollectionFeeConfig, UserAddressBalances, UserTokenBalances, Subaddress, AssetDailyReport, \
    UserOperationLog, GoogleCode
from clientadmin.mythrottle import LoginBeforeThrottle
from clientadmin.serializers import WithdrawOrderSerializer, DepositSerializer, \
    CollectionRecordsSerializer, AddressSerializer, CollectionConfigSerializer, UsersSerializer, \
    WithdrawConfigSerializer, CollectionFeeConfigSerializer, CustomJWTSerializer, \
    MyJSONWebTokenSerializer, SubaddressSerializer, UserAddressBalancesSerializer, UserTokenBalancesSerializer, \
    AssetDailyReportSerializer, UserOperationLogSerializer, MyRefreshJSONWebTokenSerializer, \
    MyJSONWebTokenAuthentication
from rest_framework import permissions
import hashlib
from rest_framework_extensions.cache.mixins import ListCacheResponseMixin

jwt_decode_handler = api_settings.JWT_DECODE_HANDLER

# Create your views here.

# all_token = ['HTDF', 'ETH', 'USDT', 'BTC']


# db = pymysql.connect(host=config.MYSQL_HOST, user=config.MYSQL_USERNAME, password=config.MYSQL_PWD,
#                      port=config.MYSQL_PORT, database=f'pg_database_{ENV_NAME.lower()}',
#                      autocommit=True, read_timeout=10, write_timeout=10)
#
# cursor = db.cursor()



def check_data(self):
    try:
        offset = self.request.GET.get("offset")
        limit = self.request.GET.get("limit")
        first_time = self.request.GET.get("first_time")
        end_time = self.request.GET.get("end_time")

        if (not re.match(REGEX_KEY, first_time)) or (not re.match(REGEX_KEY, end_time)):
            return None,None
        if (not limit.isdigit()) or (not offset.isdigit()):
            return False

        # if not offset.isdigit():
        #     return False
        return first_time, end_time
    except Exception as e:
        print(f'check_data : {e}')
        return False

class PageSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

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
    jdata = {"count": lenght, "results": data}
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
        k2 = k2.upper()	# skipped b/c b32decode has a foldcase argument
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
    """
    length = len(pwd)
    #密码加密后长度等于32
    if length == 32:
        if not IsChinese(pwd):
            if pwd.isalnum():
                return True
            else:
                return False
        else:return False
    else:return False

def custom_check_password(user, pwd):
    try:
        if user.password == pwd:
            return user
        return False
    except Exception as e:
        print(e)
        return False

def get_verification_code_on_first_login(rds, user, username):
    secret = CreatGoogleCode()
    url = f'{ENV_NAME}_code_' + username
    rds.set(url, secret)
    user.username = secret
    UserOperationLog.objects.create(pro_id=user, function_name='登录', operation_time=datetime.datetime.now(),
                                    operation_type='LOGIN_NO_GCODE', operation_status='SUCCESS',
                                    update_before_value='首次登录或重置谷歌验证码')
    return user

def get_verification_code_lost(rds, user, username):
    secret = CreatGoogleCode()
    url = f'{ENV_NAME}_code_' + username
    rds.set(url, secret)
    user.username = secret
    UserOperationLog.objects.create(pro_id=user, function_name='登录',
                                    operation_time=datetime.datetime.now(),
                                    operation_type='LOGIN_NO_GCODE', operation_status='SUCCESS',
                                    update_before_value='验证码错过,未验证,重新获取验证码!')
    return user

class CustomBackend(ModelBackend):
    """
    自定义用户验证规则
    """
    def authenticate(self, request, username=None, password=None, tel_no=None, code='None', **kwargs):
        try:
            #username 为项目方名称
            if username == None:
                username = kwargs["pro_id"]

            if tel_no == None:
                tel_no = request.POST["tel_no"]

            if request != None:
                if 'code' in request.POST:
                    code = request.POST["code"]

            if not tel_no.isdigit():
                raise Exception("500")
            if not re.match(REGEX_MOBILE, tel_no):
                raise Exception("500")
            if not ValidPassword(password):
                raise Exception("500")


            user = Project.objects.get(pro_name=username, tel_no=tel_no, account_status=1)
            if custom_check_password(user, password):
                username = str(user.pro_id)
                rds = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_API_KEY_DB_NAME_CACHE,
                                  decode_responses=True)
                url = f'{ENV_NAME}_login_' + username
                res = rds.get(url)
                if res:
                    # 重写jwt 返回出错在 serializer截获 429代表登录频繁
                    raise Exception("429")

                if code == 'None':
                    url = f'{ENV_NAME}_code_' + username
                    key = rds.get(url)
                    if key:
                        url = f'{ENV_NAME}_first_login_' + username
                        first_login = rds.get(url)
                        if first_login:
                            # 重写jwt 返回出错在 serializer截获 400代表谷歌验证码错误
                            raise Exception("400")
                        #验证码错过
                        return get_verification_code_lost(rds=rds, user=user, username=username)
                    #首次登录没有验证码
                    return get_verification_code_on_first_login(rds=rds, user=user, username=username)

                else:
                    if (not code.isdigit()) or len(code) != 6:
                        raise Exception("400")

                    url = f'{ENV_NAME}_code_' + username
                    key = rds.get(url)
                    if key:
                        gcode = GoogleAuth(key)
                        if code == gcode:

                            #判断是否首次带验证码登录
                            url = f'{ENV_NAME}_first_login_' + username
                            is_first_login = rds.get(url)
                            if is_first_login:
                                pass
                            else:
                                rds.set(url, str(datetime.datetime.now()))
                                # sql = """insert into tb_google_code (pro_id, `key`, logined)
                                #                                         value('%s', '%s', %d) """ % (username, key, 1)
                                # cursor.execute(sql)
                                # db.commit()
                                GoogleCode.objects.create(pro_id=user, key=key, logined=1)


                            url = f'{ENV_NAME}_login_' + username
                            rds.set(url, str(datetime.datetime.now()))
                            rds.expire(url, 10)

                            return user

                        url = f'{ENV_NAME}_first_login_' + username
                        first_login = rds.get(url)
                        if first_login:
                            raise Exception("400")
                        # 验证码错过
                        return get_verification_code_lost(rds=rds, user=user, username=username)
                    # 首次登录没有验证码
                    return get_verification_code_on_first_login(rds=rds, user=user, username=username)

            # 重写jwt 返回出错在 serializer截获 500代表账号密码错误
            raise Exception("500")
        except Exception as e:
            print(f'authenticate error :{e}')
            raise Exception(e)

class UsersViewSet(ListCacheResponseMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    用户信息
    """

    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UsersSerializer


    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误',status=status.HTTP_400_BAD_REQUEST)

    #重写查询,返回用户自己资源
    def get_queryset(self):
        return Project.objects.filter(pro_id=self.request.user.pro_id)

class WithdrawOrderViewSet(ListCacheResponseMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    提币记录
    """

    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = WithdrawOrderSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['token_name', 'complete_time']

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误',status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        first_time, end_time = check_data(self)
        if first_time == None or end_time == None:
            return WithdrawOrder.objects.filter(pro_id=self.request.user.pro_id).order_by('-serial_id')
        else:
            return WithdrawOrder.objects.filter(pro_id=self.request.user.pro_id, block_time__range=[first_time, end_time]).order_by('-serial_id')

    def list(self, request, *args, **kwargs):
        return MyList(self=self, request=request)

class DepositViewSet(ListCacheResponseMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    充币记录
    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DepositSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['token_name',]

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误',status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        first_time, end_time = check_data(self)
        if first_time == None and end_time == None:
            return Deposit.objects.filter(pro_id=self.request.user.pro_id).order_by('-block_time')
        else:
            return Deposit.objects.filter(pro_id=self.request.user.pro_id, block_time__range=[first_time, end_time]).order_by('-block_time')

    def list(self, request, *args, **kwargs):
        return MyList(self=self, request=request)

class CollectionRecordsViewSet(ListCacheResponseMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    归集记录
    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CollectionRecordsSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['token_name', 'block_time', 'from_address', 'to_address', 'tx_hash']

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误',status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        first_time, end_time = check_data(self)
        if first_time == None and end_time == None:
            return CollectionRecords.objects.filter(pro_id=self.request.user.pro_id).order_by('-complete_time')
        else:
            return CollectionRecords.objects.filter(pro_id=self.request.user.pro_id, block_time__range=[first_time, end_time]).order_by('-complete_time')

    def list(self, request, *args, **kwargs):
        return MyList(self=self, request=request)

class AddressViewSet(ListCacheResponseMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """

    地址管理

    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AddressSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['token_name',]
    pagination_class = PageSetPagination

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误',status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        user = self.request.user.pro_id
        return Address.objects.filter(pro_id=user)

class SubaddressViewSet(ListCacheResponseMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """

    子地址

    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = SubaddressSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['address', 'token_name']

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误', status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        first_time, end_time = check_data(self)
        if first_time == None and end_time == None:
            return Subaddress.objects.filter(pro_id=self.request.user.pro_id).order_by('-create_time')
        else:
            return Subaddress.objects.filter(pro_id=self.request.user.pro_id, create_time__range=[first_time, end_time]).order_by('-create_time')

    def list(self, request, *args, **kwargs):
        return MyList(self=self, request=request)

class CollectionConfigViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    归集配置
    ----只有GET,PUT方式可访问, ----PATCH不可访问, ----id为归集配置id
    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CollectionConfigSerializer

    
    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误',status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return CollectionConfig.objects.filter(pro_id=self.request.user.pro_id)

    def update(self, request, *args, **kwargs):
        try:
            if request.stream.method != 'PUT':
                return Response({"code": "请求方式错误"}, status=status.HTTP_400_BAD_REQUEST)

            partial = kwargs.pop('partial', False)
            instance = self.get_object()

            #每天修改归集配置次数
            rds = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_API_KEY_DB_NAME_CACHE, decode_responses=True)
            is_cache = rds.get(f'{ENV_NAME}_update_collectionconfig_user_{instance.pro_id_id}_{instance.token_name}')
            if is_cache:
                return Response({"code": "每天每个币种只能修改一次"}, status=status.HTTP_400_BAD_REQUEST)

            #取出之前的最小金额
            update_before_value = f'币种: {instance.token_name} ,最小归集金额: {instance.min_amount_to_collect}'

            #TODO:重写部分安全保护
            for i in request.data:
                if not i in ['token_name', "min_amount_to_collect"]:
                    return Response({"code": "未知错误"}, status=status.HTTP_400_BAD_REQUEST)
            #内容验证

            if float(request.data["min_amount_to_collect"]) < 0.001:
                return Response({"code": "最小金额错误"}, status=status.HTTP_400_BAD_REQUEST)

            # TODO:提币地址,安全保护
            if "collection_dst_addr" in request.data:
                return Response({"code": "危险地址错误"}, status=status.HTTP_400_BAD_REQUEST)
            if "pro_id" in request.data:
                return Response({"code": "用户错误"}, status=status.HTTP_400_BAD_REQUEST)

            #TODO:双重保护
            if instance.pro_id != request.user:
                return Response({"code" : "用户错误"}, status=status.HTTP_400_BAD_REQUEST)

            if instance.token_name != request.data["token_name"]:
                return Response({"code" : "币种错误"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            rds.set(f'{ENV_NAME}_update_collectionconfig_user_{instance.pro_id_id}_{instance.token_name}',
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            rds.expire(f'{ENV_NAME}_update_collectionconfig_user_{instance.pro_id_id}_{instance.token_name}', 24 * 60 * 60)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            last_after_value = f'币种: {instance.token_name} ,最小归集金额: {request.data["min_amount_to_collect"]}'
            UserOperationLog.objects.create(pro_id=instance.pro_id, function_name='归集配置',update_before_value=update_before_value,
            last_after_value=last_after_value, operation_type='UPDATE', operation_status='SUCCESS', operation_time=datetime.datetime.now())


            return Response(serializer.data)
        except Exception as e:
            print(f'update withdrawconfig error: {e}')
            return Response({"code": 'error'}, status=status.HTTP_400_BAD_REQUEST)

class WithdrawConfigViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    提币配置
    ----只有GET,PUT方式可访问, ----PATCH不可访问, ----id为提币配置id

    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = WithdrawConfigSerializer
    
    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误',status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return WithdrawConfig.objects.filter(pro_id=self.request.user.pro_id)

    def update(self, request, *args, **kwargs):
        try:
            if request.stream.method != 'PUT':
                return Response({"code": "请求方式错误"}, status=status.HTTP_400_BAD_REQUEST)
            partial = kwargs.pop('partial', False)
            instance = self.get_object()

            # 每天修改提币配置次数
            rds = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_API_KEY_DB_NAME_CACHE, decode_responses=True)
            is_cache = rds.get(f'{ENV_NAME}_update_withdrawconfig_user_{instance.pro_id_id}_{instance.token_name}')
            if is_cache:
                return Response({"code": "每天每个币种只能修改一次"}, status=status.HTTP_400_BAD_REQUEST)

            update_before_value = f'币种: {instance.token_name}, 最小提币金额: {instance.min_amount}, ' \
            f'最大提币金额: {instance.max_amount}, 短信通知阈值: {instance.balance_threshold_to_sms}'

            #TODO:重写部分安全保护
            for i in request.data:
                if not i in ["token_name", "min_amount", "max_amount", "balance_threshold_to_sms"]:
                    return Response({"code": "未知错误"}, status=status.HTTP_400_BAD_REQUEST)
            #内容验证

            if float(request.data["min_amount"]) < 0.001:
                return Response({"code": "最小金额错误"}, status=status.HTTP_400_BAD_REQUEST)

            if float(request.data["max_amount"]) < 0.001:
                return Response({"code": "最大金额错误"}, status=status.HTTP_400_BAD_REQUEST)

            if float(request.data["min_amount"]) >= float(request.data["max_amount"]):
                return Response({"code": "最小金额错误"}, status=status.HTTP_400_BAD_REQUEST)

            if float(request.data["balance_threshold_to_sms"]) < 0:
                return Response({"code": "短信通知阈值错误"}, status=status.HTTP_400_BAD_REQUEST)

            # TODO:提币地址,安全保护
            if "address" in request.data:
                return Response({"code": "危险地址错误"}, status=status.HTTP_400_BAD_REQUEST)
            if "pro_id" in request.data:
                return Response({"code": "用户错误"}, status=status.HTTP_400_BAD_REQUEST)

            #TODO:双重保护
            if instance.pro_id != request.user:
                return Response({"code" : "用户错误"}, status=status.HTTP_400_BAD_REQUEST)

            if instance.token_name != request.data["token_name"]:
                return Response({"code" : "币种错误"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            rds.set(f'{ENV_NAME}_update_withdrawconfig_user_{instance.pro_id_id}_{instance.token_name}',
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            rds.expire(f'{ENV_NAME}_update_withdrawconfig_user_{instance.pro_id_id}_{instance.token_name}', 24 * 60 * 60)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            last_after_value = f'币种: {request.data["token_name"]}, 最小提币金额: {request.data["min_amount"]}, ' \
                                  f'最大提币金额: {request.data["max_amount"]}, 短信通知阈值: {request.data["balance_threshold_to_sms"]}'
            UserOperationLog.objects.create(pro_id=instance.pro_id, function_name='提币配置',operation_time=datetime.datetime.now(),
                                            update_before_value=update_before_value,
                                            last_after_value=last_after_value,
                                            operation_type='UPDATE', operation_status='SUCCESS')

            return Response(serializer.data)
        except Exception as e:
            print(f'update withdrawconfig error: {e}')
            return Response({"code": 'error'}, status=status.HTTP_400_BAD_REQUEST)

class CollectionFeeConfigViewSet(ListCacheResponseMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    手续费配置
    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CollectionFeeConfigSerializer

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误',status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return CollectionFeeConfig.objects.filter(pro_id=self.request.user.pro_id)

class UserAddressBalancesViewSet(ListCacheResponseMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    用户地址资产
    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserAddressBalancesSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['token_name', 'address', 'update_time']

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误',status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        first_time, end_time = check_data(self)
        if first_time == None and end_time == None:
            return UserAddressBalances.objects.filter(pro_id=self.request.user.pro_id).values(
                "token_name","address","balance","update_time").order_by('-update_time')
        else:
            #TODO:特殊写法,自带orm会带id去查询,导致各种报错,故以此解决问题之根本
            return UserAddressBalances.objects.filter(pro_id=self.request.user.pro_id,
            update_time__range=[first_time, end_time]).values("token_name","address","balance","update_time").order_by('-update_time')

    def list(self, request, *args, **kwargs):
        return MyList(self=self, request=request)

class UserTokenBalancesViewSet(ListCacheResponseMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    用户币种资产
    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserTokenBalancesSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['token_name', 'withdraw_address', 'update_time']
    pagination_class = PageSetPagination

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误',status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        user = self.request.user.pro_id
        return UserTokenBalances.objects.filter(pro_id=user)

class AssetDailyReportViewSet(ListCacheResponseMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    资产日报表
    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    throttle_scope = 'AssetDailyReport'
    serializer_class = AssetDailyReportSerializer
    pagination_class = PageSetPagination

    filter_backends = [filters.SearchFilter]
    search_fields = ['token_name', 'update_time']

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误',status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        user = self.request.user.pro_id
        today = datetime.datetime.now().date()

        # first_time, end_time = check_data(self)
        # if first_time == None and end_time == None:
        #     return AssetDailyReport.objects.filter(pro_id=user, update_time__gte=today)
        # else:
        return AssetDailyReport.objects.filter(pro_id=user, update_time__gte=today).order_by('-update_time')

class UserOperationLogViewSet(ListCacheResponseMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    用户操作日志
    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserOperationLogSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['operation_time', 'function_name']

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误', status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        first_time, end_time = check_data(self)
        if first_time == None and end_time == None:
            return UserOperationLog.objects.filter(pro_id=self.request.user.pro_id).order_by('-operation_time')
        else:
            return UserOperationLog.objects.filter(pro_id=self.request.user.pro_id, operation_time__range=[first_time, end_time]).order_by('-operation_time')

    def list(self, request, *args, **kwargs):
        return MyList(self=self, request=request)

class Reset(APIView):
    """
    修改密码
    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误',status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        # 获取参数
        try:
            new_password = request.data["new_password"]
            password_verify = request.data["password_verify"]
            tel_no = request.data["tel_no"]
            password = request.data["password"]
            code = request.data["code"]

            if (not code.isdigit()):
                raise Exception("验证码错误!")

            if not re.match(REGEX_MOBILE, tel_no):
                raise Exception("手机号非法!")

            if request.user.tel_no != tel_no:
                raise Exception("非法用户!")

            if new_password != password_verify:
                raise Exception("两次密码输入不一致!")

            if new_password == password:
                raise Exception("新老密码一致!")

            if not ValidPassword(new_password):
                raise Exception("新密码非法!")

            if not ValidPassword(password):
                raise Exception("旧密码非法!")

            # 用户密码验证
            try:
                user = CustomBackend.authenticate(self, request, username=request.user.pro_name, password=password, code=code, tel_no=tel_no)
            except Exception as e:
                print(e)
                if str(e) == "400":
                    raise Exception("谷歌验证码错误!")
                elif str(e) == "429":
                    raise Exception("请求频繁!")
                else:
                    raise Exception("参数错误,请检查!")

            # 每天修改密码次数
            rds = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_API_KEY_DB_NAME_CACHE,
                              decode_responses=True)
            is_cache = rds.get(f'{ENV_NAME}_update_resetpasswd_user_{user.pro_id}')
            if is_cache:
                raise Exception("每天只能修改一次")


            # 修改密码为新密码
            make_passwd = new_password

            user = Project.objects.filter(pro_id=user.pro_id, tel_no=tel_no).first()
            user.password = make_passwd
            user.save()

            rds.set(f'{ENV_NAME}_update_resetpasswd_user_{user.pro_id}', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            rds.expire(f'{ENV_NAME}_update_resetpasswd_user_{user.pro_id}', 24 * 60 * 60)

            rds2 = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_API_KEY_DB_NAME,
                              decode_responses=True)
            url = f'{ENV_NAME}_token_{user.pro_id}'
            rds2.delete(url)

            data = {"code": "修改密码成功!"}
            UserOperationLog.objects.create(pro_id=user, function_name='修改密码', operation_time=datetime.datetime.now(),
                                            operation_type='UPDATE', operation_status='SUCCESS')

            # 返回数据
            return Response(data=data, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response(data={"code" : str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ObtainJSONWebToken(CustomJWTSerializer):
    """
    用户登录接口---- pro_id 为项目方id, ---- password 为密码

    """
    throttle_classes = [LoginBeforeThrottle]
    #重写jwt登录验证
    serializer_class = MyJSONWebTokenSerializer

obtain_jwt_token = ObtainJSONWebToken.as_view()


class RefreshJSONWebToken(JSONWebTokenAPIView):
    """
    jwt token 续签
    """
    authentication_classes = (MyJSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = MyRefreshJSONWebTokenSerializer


Refresh_jwt_token = RefreshJSONWebToken.as_view()


class Code_Verify(APIView):

    throttle_classes = [LoginBeforeThrottle]

    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误',status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):

        try:
            if len(request.data) != 2:
                raise Exception("002")

            for i in request.data:
                if not i in ['code', 'pro_id']:
                    raise Exception("002")

            code = request.data["code"]
            pro_id = request.data["pro_id"]

            if not pro_id.isdigit() or len(pro_id) > 2:
                raise Exception("008")

            if (not code.isdigit()) or len(code) != 6:
                raise Exception("400")

            rds = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_API_KEY_DB_NAME_CACHE,
                              decode_responses=True)
            url = f'{ENV_NAME}_code_' + pro_id
            key = rds.get(url)
            if key:
                gcode = GoogleAuth(key)
                if code == gcode:
                    data = {"code":"success"}
                    return Response(data=data, status=status.HTTP_200_OK)
                data = {"code":"fail"}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

            raise Exception("008")

        except Exception as e:
            if str(e) == "002":
                data = {"code": "请求参数错误!"}
            elif str(e) == "008":
                data = {"code": "pro_id非法!"}
            elif str(e) == "400":
                data = {"code": "验证码错误!"}
            else:
                data = {"code": "未知错误!"}
                print(f'Code_Verify error : {e}')

            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)






