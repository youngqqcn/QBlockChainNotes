#!coding:utf8

'''
descriptions: none
author: yqq
date: 2020/5/4 11:21
'''
from django.urls import path, re_path
from . import views


app_name = 'app'
urlpatterns = [
    path(r'', views.index, name='index'),
    path(r'booklist/', views.HelloListView.as_view(), name='booklist')

]

