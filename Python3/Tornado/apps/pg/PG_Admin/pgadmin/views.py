import base64
import hashlib
import hmac
import random
import string
import struct
import time
import ed25519
import os
import re
from binascii import hexlify

import pymysql
import redis
from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from PG_Admin.settings import REGEX_MOBILE, REDIS_HOST, REDIS_PORT, REDIS_API_KEY_DB_NAME, REDIS_API_KEY_DB_NAME_CACHE, \
    ENV_NAME
from pgadmin.models import Project, GoogleCode
from django.contrib.auth.models import User
from config.config import config

db = pymysql.connect(host=config.MYSQL_HOST, user=config.MYSQL_USERNAME, password=config.MYSQL_PWD,
                     port=config.MYSQL_PORT, database=f'pg_database_{ENV_NAME.lower()}',
                     autocommit=True, read_timeout=10, write_timeout=10)

cursor = db.cursor()



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
        # k2 = k2.upper()	# skipped b/c b32decode has a foldcase argument
        if len(k2) % 8 != 0:
            k2 += '=' * (8 - len(k2) % 8)
        return k2

    def prefix0(h):
        """Prefixes code with leading zeros if missing."""
        if len(h) < 6:
            h = '0' * (6 - len(h)) + h
        return h

    return get_totp_token(key)

def CodeAuth(code, username):
    if (not code.isdigit()):
        raise Exception("验证码错误")

    rds = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_API_KEY_DB_NAME_CACHE,
                      decode_responses=True)
    url = f'{ENV_NAME}_code_admin_' + str(username)
    key = rds.get(url)
    if key:
        gcode = GoogleAuth(key)
        if code != gcode:
            raise Exception('验证码错误!')
    else:
        secret = CreatGoogleCode()
        url = f'{ENV_NAME}_code_admin_' + str(username)
        rds.set(url, secret)

        sql = """insert into tb_google_code (pro_id, `key`, is_superuser) 
              value('%s', '%s', %d) """ % (
        str(username), secret, 1)
        cursor.execute(sql)
        db.commit()

        raise Exception(f'admin google key: {secret}, 请记住谷歌密钥,注意保管! 此次修改失败!!!')
    return True

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
    """""
    length = len(pwd)
    #密码长度大于8 小于16
    if (length >= 8 and length <= 16):
        if not IsChinese(pwd):
            return True
        else:return False
    else:return False

class ResetPasswd(View):

    def get(self, request):
        if request.user.is_anonymous == True or request.user.is_active == False or request.user.id == None or request.user.is_staff == False:
            if request.user.username == '':
                return HttpResponse(status=400, content=f'None page!')
        return render(request, 'resetpasswd.html')

    def post(self, request):
        if request.user.is_anonymous == True or request.user.is_active == False or request.user.id == None or request.user.is_staff == False:
            if request.user.username == '':
                return HttpResponse(status=400, content=f'None page!')

        try:
            superusername = request.POST.get("superusername")
            superpassword = request.POST.get("superpassword")
            username = request.POST.get("username")
            pro_id = request.POST.get("pro_id")
            password = request.POST.get("password")
            password_two = request.POST.get("password_two")
            code = request.POST.get("code")

            if not re.match(REGEX_MOBILE, username):
                raise Exception("手机号非法!")

            if not pro_id.isdigit():
                raise Exception("pro_id 不存在!")

            if password != password_two:
                raise Exception("两次密码输入不一致!")

            if not ValidPassword(password):
                raise Exception("新密码非法!")

            if not superusername.isalnum():
                raise Exception("管理员账号非法!")

            if not ValidPassword(superpassword):
                raise Exception("管理员密码非法!")

            try:
                super_user = User.objects.get(username=superusername, is_superuser=1)
                if super_user.check_password(superpassword):
                    pass
                else:
                    raise Exception
            except Exception as e:
                print(e)
                raise Exception("管理员账号密码错误!")

            if not CodeAuth(code=code, username=super_user.id):
                raise Exception("验证码错误!")

            msgbytes  = hashlib.md5(str(password).encode('utf8')).digest()
            make_passwd = hexlify(msgbytes).decode('latin1')

            user = Project.objects.filter(pro_id=pro_id, tel_no=username).first()
            if user:
                user.password = make_passwd
                user.save()
                return HttpResponse(status=200, content=f'{username} : 修改成功!')

            raise Exception("没有此用户!")

        except Exception as e:
            print(e)
            return HttpResponse(status=400, content=f'{e}')

class ResetKey(View):

    def get(self, request):
        if request.user.is_anonymous == True or request.user.is_active == False or request.user.id == None or request.user.is_staff == False:
            if request.user.username == '':
                return HttpResponse(status=400, content=f'None page!')
        return render(request, 'resetkey.html')

    def post(self, request):
        if request.user.is_anonymous == True or request.user.is_active == False or request.user.id == None or request.user.is_staff == False:
            if request.user.username == '':
                return HttpResponse(status=400, content=f'None page!')
        try:
            superusername = request.POST.get("superusername")
            superpassword = request.POST.get("superpassword")
            username = request.POST.get("username")
            pro_id = request.POST.get("pro_id")
            code = request.POST.get("code")

            if not re.match(REGEX_MOBILE, username):
                raise Exception("手机号非法!")

            if not pro_id.isdigit():
                raise Exception("pro_id 不存在!")

            if not superusername.isalnum():
                raise Exception("管理员账号非法!")

            if not ValidPassword(superpassword):
                raise Exception("管理员密码非法!")

            super_user = User.objects.get(username=superusername, is_superuser=1)
            if super_user.check_password(superpassword):
                pass
            else:
                raise Exception("管理员账号密码错误!")

            if not CodeAuth(code=code, username=super_user.id):
                raise Exception("验证码错误!")

            user = Project.objects.filter(pro_id=pro_id, tel_no=username).first()
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

                select_user = Project.objects.filter(pro_id=pro_id).first()

                if select_user:
                    # redis
                    rds = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_API_KEY_DB_NAME, decode_responses=True)
                    rds.delete(select_user.api_key)

                    select_user.api_key = api_key
                    select_user.client_sign_key = client_sign_key
                    select_user.client_verify_key = client_verify_key
                    select_user.server_sign_key = server_sign_key
                    select_user.server_verify_key = server_verify_key
                    select_user.save()

                    url = client_verify_key + ',' + str(pro_id)
                    rds.set(api_key, url)

                    return HttpResponse(status=200, content=f'{username} : 重置成功!')

                raise Exception('没有此用户!')

            else:
                raise Exception('没有此用户!')

        except Exception as e:
            print(e)
            return HttpResponse(status=400, content=f'{e}')

class ResetGoogleCode(View):

    def get(self, request):
        if request.user.is_anonymous == True or request.user.is_active == False or request.user.id == None or request.user.is_staff == False:
            if request.user.username == '':
                return HttpResponse(status=400, content=f'None page!')
        return render(request, 'resetgooglecode.html')

    def post(self, request):
        if request.user.is_anonymous == True or request.user.is_active == False or request.user.id == None or request.user.is_staff == False:
            if request.user.username == '':
                return HttpResponse(status=400, content=f'None page!')

        try:
            superusername = request.POST.get("superusername")
            superpassword = request.POST.get("superpassword")
            username = request.POST.get("username")
            pro_id = request.POST.get("pro_id")
            code = request.POST.get("code")

            if not re.match(REGEX_MOBILE, username):
                raise Exception("手机号非法!")

            if not pro_id.isdigit():
                raise Exception("pro_id 不存在!")

            if not superusername.isalnum():
                raise Exception("管理员账号非法!")

            if not ValidPassword(superpassword):
                raise Exception("管理员密码非法!")

            super_user = User.objects.get(username=superusername, is_superuser=1)
            if super_user.check_password(superpassword):
                pass
            else:
                raise Exception("管理员账号密码错误!")

            if not CodeAuth(code=code, username=super_user.id):
                raise Exception("验证码错误!")

            user = Project.objects.filter(pro_id=pro_id, tel_no=username).first()
            if user:
                rds = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_API_KEY_DB_NAME_CACHE, decode_responses=True)
                url = f'{ENV_NAME}_code_' + pro_id
                rds.delete(url)
                url = f'{ENV_NAME}_first_login_' + pro_id
                rds.delete(url)

                GoogleCode.objects.filter(pro_id=pro_id).delete()

                return HttpResponse(status=200, content=f'{username} : 重置成功!')

            raise Exception('没有此用户!')

        except Exception as e:
            print(e)
            return HttpResponse(status=400, content=f'{e}')
