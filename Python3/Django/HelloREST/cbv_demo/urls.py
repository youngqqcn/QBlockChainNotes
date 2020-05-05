#!coding:utf8

'''
descriptions: none
author: yqq
date: 2020/5/5 22:03
'''
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views



app_name = 'cbv_demo'
urlpatterns = [
    path(r'hellocbv/', views.HelloCBV.as_view(), name='hellocbv'),
    path(r'books/', views.BooksAPI.as_view(), name='books'),
    # path(r'book/', views.BookAPI.as_view(), name='book'),
    path(r'book/<int:bookid>', csrf_exempt(views.BookAPI.as_view()), name='book'),

]