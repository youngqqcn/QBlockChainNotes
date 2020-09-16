
import redis
from django.contrib.auth import authenticate
from django.utils.encoding import smart_text
from rest_framework import serializers, status
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.response import Response
from rest_framework_jwt.compat import PasswordField, get_username_field, Serializer
from rest_framework_jwt.serializers import VerificationBaseSerializer
from rest_framework_jwt.views import JSONWebTokenAPIView

from PG_Client.settings import REDIS_HOST, REDIS_PORT, REDIS_API_KEY_DB_NAME, ENV_NAME
from clientadmin.models import WithdrawOrder, Deposit, CollectionRecords, Address, CollectionConfig, Project, \
    CollectionFeeConfig, WithdrawConfig, UserTokenBalances, UserAddressBalances, Subaddress, AssetDailyReport, \
    UserOperationLog
from clientadmin.utils import jwt_response_payload_handler, jwt_response_payload_error_handler, \
    jwt_response_payload_code_error_handler, jwt_response_payload_frequently_error_handler
from calendar import timegm
from datetime import datetime, timedelta
import jwt
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _
from rest_framework import exceptions
from rest_framework_jwt.settings import api_settings


jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

rds = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_API_KEY_DB_NAME,
                                  decode_responses=True)

class WithdrawOrderSerializer(serializers.ModelSerializer):
    """
    提币视图序列化
    """

    class Meta:
        model = WithdrawOrder
        fields = ['serial_id', 'order_id','token_name', 'amount',
                    'order_status','transaction_status','notify_status','notify_times',
                    'block_height','tx_confirmations','from_addr', 'to_addr', 'tx_hash',
                    'block_time','complete_time','memo','remark']


class DepositSerializer(serializers.ModelSerializer):
    """
    充币视图序列化
    """

    class Meta:
        model = Deposit
        fields = ['token_name','amount',
                   'from_addr', 'to_addr','block_time','tx_confirmations',
                    'block_height','tx_hash','memo',]


class CollectionRecordsSerializer(serializers.ModelSerializer):
    """
    归集视图序列化
    """

    class Meta:
        model = CollectionRecords
        fields = ['token_name' ,  'amount','collection_type',
                    'complete_time','transaction_status',
                    'from_address', 'to_address', 'block_height',
                  'tx_confirmations' ,'tx_hash','block_time']


class AddressSerializer(serializers.ModelSerializer):
    """
    地址管理序列化
    """

    class Meta:
        model = Address
        fields = ['token_name', 'address_nums', 'uncharged_address_nums', 'update_time',]

class SubaddressSerializer(serializers.ModelSerializer):
    """
    子地址序列化
    """

    class Meta:
        model = Subaddress
        fields = ['address', 'token_name',]

class CollectionConfigSerializer(serializers.ModelSerializer):
    """
    归集配置序列化
    """
    collection_dst_addr = serializers.CharField(read_only=True)
    token_name = serializers.CharField(required=True, help_text='币种')
    class Meta:
        model = CollectionConfig
        fields = ['id', 'collection_dst_addr','token_name', 'min_amount_to_collect']

class CollectionFeeConfigSerializer(serializers.ModelSerializer):
    """
    手续费配置序列化
    """

    class Meta:
        model = CollectionFeeConfig
        fields = ['token_name', 'address']

class WithdrawConfigSerializer(serializers.ModelSerializer):
    """
    提币配置序列化
    """
    address = serializers.CharField(read_only=True)
    #传用户名则开启,否则为pro_id
    pro_id = serializers.CharField(read_only=True)
    token_name = serializers.CharField(required=True, help_text='币种')
    # id = serializers.IntegerField(help_text='提币配置id')

    class Meta:
        model = WithdrawConfig
        fields = ['id', 'pro_id', 'token_name', 'address', 'min_amount', 'max_amount', 'balance_threshold_to_sms']


class UsersSerializer(serializers.ModelSerializer):
    """
    用户信息序列化
    """

    class Meta:
        model = Project
        fields = ['pro_name', 'tel_no', 'email']


class UserAddressBalancesSerializer(serializers.ModelSerializer):
    """
    用户资地址产序列化
    """

    class Meta:
        model = UserAddressBalances
        fields = ['token_name', 'address', 'balance', 'update_time']


class UserTokenBalancesSerializer(serializers.ModelSerializer):
    """
    用户币种资产序列化
    """

    class Meta:
        model = UserTokenBalances
        fields = ['token_name', 'withdraw_address', 'withdraw_balance', 'update_time']

class AssetDailyReportSerializer(serializers.ModelSerializer):
    """
    日报表序列化
    """

    class Meta:
        model = AssetDailyReport
        fields = ['token_name', 'deposit_amount', 'withdraw_amount',
                  'collectionRecords_amount', 'all_balance', 'update_time']


class UserOperationLogSerializer(serializers.ModelSerializer):
    """
    用户操作日志
    """

    class Meta:
        model = UserOperationLog
        fields = ['operation_time', 'function_name', 'operation_type',
                  'update_before_value', 'last_after_value', 'operation_status']

class CustomJWTSerializer(JSONWebTokenAPIView):
    def options(self, request, *args, **kwargs):
        return Response(f'请求方式错误',status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        #重写
        try:
            if serializer.is_valid():
                user = serializer.object.get('user') or request.user
                token = serializer.object.get('token')

                if user.username == None:
                    # 真正成功登录返回
                    UserOperationLog.objects.create(pro_id=user, function_name='登录',
                                                    operation_time=datetime.now(),
                                                    operation_type='LOGIN', operation_status='SUCCESS')
                    print("login success")
                print("1")
                response_data = jwt_response_payload_handler(token, user, request)
                response = Response(response_data)
                if api_settings.JWT_AUTH_COOKIE:
                    expiration = (datetime.utcnow() +
                                  api_settings.JWT_EXPIRATION_DELTA)
                    response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                        token,
                                        expires=expiration,
                                        httponly=True)
                return response
        except Exception as e:
            print(e)
            if str(e) == "400":
                response_data = jwt_response_payload_code_error_handler(request)
            elif str(e) == "429":
                response_data = jwt_response_payload_frequently_error_handler(request)
            else:
                response_data = jwt_response_payload_error_handler(request)

            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)



class MyJSONWebTokenSerializer(Serializer):
    """
    重写jwt 序列化验证
    Serializer class used to validate a username and password.

    'username' is identified by the custom UserModel.USERNAME_FIELD.

    Returns a JSON Web Token that can be used to authenticate later calls.
    """
    def __init__(self, *args, **kwargs):
        """
        Dynamically add the USERNAME_FIELD to self.fields.
        """
        super(MyJSONWebTokenSerializer, self).__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField()
        self.fields['password'] = PasswordField(write_only=True)

    @property
    def username_field(self):
        return get_username_field()

    def validate(self, attrs):
        #重写
        try:
            code = self.initial_data["code"]
        except Exception as e:
            print(f'google_code is None : {e}')
            code = 'None'

        credentials = {

            self.username_field: attrs.get(self.username_field),
            'password': attrs.get('password'),
            #新增判断字段
            'tel_no': self.initial_data["tel_no"],
            'code' : code
        }
        #重写结束
        if all(credentials.values()):
            user = authenticate(**credentials)

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise serializers.ValidationError(msg)


                payload = jwt_payload_handler(user)
                token = jwt_encode_handler(payload)

                #重写
                if user.username == None:
                    #user.username 为None 为成功登录状态
                    url = f'{ENV_NAME}_token_{user.pro_id}'
                    rds.set(url, token)
                    rds.expire(url, 60*60)

                return {
                    'token': token,
                    'user': user
                }
            else:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "{username_field}" and "password".')
            msg = msg.format(username_field=self.username_field)
            raise serializers.ValidationError(msg)


class MyRefreshJSONWebTokenSerializer(VerificationBaseSerializer):
    """
    Refresh an access token.
    重写jwt token 刷新 ###为了单点登录
    """

    def validate(self, attrs):

        token = attrs['token']

        payload = self._check_payload(token=token)
        user = self._check_user(payload=payload)
        # Get and check 'orig_iat'
        orig_iat = payload.get('orig_iat')

        # 刷新token频率 为30分钟一次
        url = f'{ENV_NAME}_refresh_times_{user.pro_id}'
        is_exist = rds.get(url)
        if is_exist:
            msg = _('只能每30分钟一次刷新token')
            raise serializers.ValidationError(msg)

        if orig_iat:
            # Verify expiration
            refresh_limit = api_settings.JWT_REFRESH_EXPIRATION_DELTA

            if isinstance(refresh_limit, timedelta):
                refresh_limit = (refresh_limit.days * 24 * 3600 +
                                 refresh_limit.seconds)

            expiration_timestamp = orig_iat + int(refresh_limit)
            now_timestamp = timegm(datetime.utcnow().utctimetuple())

            if now_timestamp > expiration_timestamp:
                msg = _('Refresh has expired.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('orig_iat field is required.')
            raise serializers.ValidationError(msg)

        new_payload = jwt_payload_handler(user)
        new_payload['orig_iat'] = orig_iat

        #额外添加
        url = f'{ENV_NAME}_token_{user.pro_id}'
        rds.set(url, jwt_encode_handler(new_payload))
        rds.expire(url, 60*60)

        url = f'{ENV_NAME}_refresh_times_{user.pro_id}'
        rds.set(url, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        rds.expire(url, 60 * 30)

        return {
            'token': jwt_encode_handler(new_payload),
            'user': user
        }


class MyBaseJSONWebTokenAuthentication(BaseAuthentication):
    """
    Token based authentication using the JSON Web Token standard.
    重写jwt 单点登录token问题  用redis做状态
    """

    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication.  Otherwise returns `None`.
        """
        jwt_value = self.get_jwt_value(request)
        if jwt_value is None:
            return None

        try:
            payload = jwt_decode_handler(jwt_value)
        except jwt.ExpiredSignature:
            msg = _('Signature has expired.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()

        # redis 判定jwt token 状态
        url = f'{ENV_NAME}_token_{payload["pro_id"]}'
        is_exist = rds.get(url)
        if is_exist:
            if is_exist == jwt_value.decode("utf8"):
                pass
            else:
                raise exceptions.AuthenticationFailed('Signature has expired.')
        else:
            raise exceptions.AuthenticationFailed('Signature has expired.')

        user = self.authenticate_credentials(payload)

        return (user, jwt_value)

    def authenticate_credentials(self, payload):
        """
        Returns an active user that matches the payload's user id and email.
        """
        User = get_user_model()
        username = jwt_get_username_from_payload(payload)

        if not username:
            msg = _('Invalid payload.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            msg = _('Invalid signature.')
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = _('User account is disabled.')
            raise exceptions.AuthenticationFailed(msg)

        return user

#做转接,继承
class MyJSONWebTokenAuthentication(MyBaseJSONWebTokenAuthentication):
    """
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string specified in the setting
    `JWT_AUTH_HEADER_PREFIX`. For example:

        Authorization: JWT eyJhbGciOiAiSFMyNTYiLCAidHlwIj
    """
    www_authenticate_realm = 'api'

    def get_jwt_value(self, request):
        auth = get_authorization_header(request).split()
        auth_header_prefix = api_settings.JWT_AUTH_HEADER_PREFIX.lower()

        if not auth:
            if api_settings.JWT_AUTH_COOKIE:
                return request.COOKIES.get(api_settings.JWT_AUTH_COOKIE)
            return None

        if smart_text(auth[0].lower()) != auth_header_prefix:
            return None

        if len(auth) == 1:
            msg = _('Invalid Authorization header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid Authorization header. Credentials string '
                    'should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        return auth[1]

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return '{0} realm="{1}"'.format(api_settings.JWT_AUTH_HEADER_PREFIX, self.www_authenticate_realm)