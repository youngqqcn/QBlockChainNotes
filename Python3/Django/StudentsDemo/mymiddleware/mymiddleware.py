#!coding:utf8

'''
descriptions: none
author: yqq
date: 2020/5/3 17:36
'''


from django.utils.deprecation import MiddlewareMixin


class MyMiddle(MiddlewareMixin):

    def process_request(self, request):
        print(f"中间件测试,  自定义, 请求方法: {request.method}")

    def process_response(self, request, response):
        print(f'中间件 , 响应参数: {response}')
        return response
