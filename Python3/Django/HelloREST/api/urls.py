#!coding:utf8

'''
descriptions: none
author: yqq
date: n 11:41
'''

from django.urls import path, re_path

from . import views
# import
# from app import views
# import views

app_name = 'api'


urlpatterns = [
    # path(r'index', views.index, name='index'),
    path(r'books', views.books, name='books'),
    path(r'book/<int:bookid>', views.book, name='book'),

]


