#
#
# from cryptography.fernet import Fernet
#
# #js url= https=//www.npmjs.com/package/fernet
# #python url=
#
# admin_encrypt_key = 'M8HutVPQc5kp9M6UlPM9xd6KWOS8dy_x32ffp-sS__o='
#
#
# def encrypt_p(password):
#     f = Fernet(admin_encrypt_key)
#     p1 = password.encode()
#     token = f.encrypt(p1)
#     p2 = token.decode()
#     return p2
#
# def decrypt_p(password):
#     f = Fernet(admin_encrypt_key)
#     p1 = password.encode()
#     token = f.decrypt(p1)
#     p2 = token.decode()
#     return p2
#
# # a = encrypt_p("admin123456")
# # print(a)
#
# c = "gAAAAABfIn4IAAECAwQFBgcICQoLDA0OD-pPmB6OM8YgjFnllSvtkqvCaI0kww_a_3CsnRJWeZlr1HIKNPW-ddqQAXAhYdTPdA=="
# key = decrypt_p(c)
# print(key)


# import json
# import os
# import time
#
# from django.http import HttpResponse, JsonResponse
# from rest_framework.response import Response
# from rest_framework.views import APIView
#
# from restapi.models import Deposit
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PG_AdminREST.settings")
# # 导入Django
# import django
# # 运行Django项目
# django.setup()
#
# class test(APIView):
#
#     def get(self, request):
#         s = time.time()
#         res = Deposit.objects.values('pro_id', 'token_name','amount',
#                            'from_addr', 'to_addr','block_time','tx_confirmations',
#                             'block_height','tx_hash','memo',)
#         lenght = Deposit.objects.all().count()
#         jdata = {
#             "len": lenght,
#             "res": res
#         }
#         e = time.time()
#         print(e-s)
#         return JsonResponse(data=json.dumps(jdata))
