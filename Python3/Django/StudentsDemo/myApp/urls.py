
from django.urls import path
from . import views
from django.urls import re_path


# Django 3.0 中不再使用正则表达式, 获取模板中的变量
# https://docs.djangoproject.com/en/3.0/intro/tutorial03/#namespacing-url-names


app_name = 'this_is_app_name'
urlpatterns = [
    # path(r'', views.index),
    # path(r'^(\d+)/$', views.detail)
    path(r'page/<int:num>/', views.detail, name='detail'),
    path(r'grades/all', views.grades_details, name='grades_details'),
    path(r'grades/<int:grade_id>', views.get_grade_students, name='get_grade_students'),

    path(r'students/all', views.students_details, name='students_details'),
    path(r'students/add_default', views.add_default_student, name='add_default_student'),
    path(r'students/add_default_by_manager', views.add_default_student_use_manager, name='add_default_student_by_manager'),
    path(r'students/page/<int:page_index>', views.show_students_page, name='show_students_page'),
    path(r'students/search', views.search_student, name='search_student'),
    path(r'grades/seach_relate', views.search_relate, name='search_relate'),
    path(r'grades/girlmorethanboy', views.search_student_by_F, name='search_student_by_F'),
    path(r'students/older_student', views.search_student_by_Q, name='search_student_by_Q'),


    # re_path(r'good/test_re_path', views.test_re_path),
    path(r'request_props/', views.request_props, name='request_props'),

    path(r'get1', views.get_url_parameters),
    path(r'get2',  views.get_url_parameters2),

    path(r'showregister/', views.show_register, name='show_register'),
    path(r'register/', views.register, name='register'),  #POST请求

    path(r'showresponse/', views.show_response, name='show_response'),



    path(r'customcookie/', views.set_custom_cookies, name='set_custom_cookie'),


    path(r'test_redirect/', views.test_redirect, name='test_redirect'),

    path(r'jsonresponse/', views.json_response, name='json_response'),

    path(r'mainpage/', views.show_main_page, name='show_main_page'),
    path(r'show_login/', views.show_login_page, name='show_login_page'),
    path(r'user_login/', views.user_login, name='login'),
    path(r'user_logout/', views.user_logout, name='user_logout'),


    ############模板
    path(r'student_counter/', views.students_counter, name="students_counter"),


    #URL 反向解析 测试
    path(r'reverse_url_page/', views.show_reverse_url_page),
    path(r'reverse_url_test/<int:num>', views.reverse_url_test, name="reverse_url_test_x"),


    #模板继承
    path(r'template_externs/', views.template_externs, name='template_externs'),

    #HTML转义
    path(r'html_code/', views.html_code, name='html_code'),


    #CSRF
    path(r'show_test_csrf_page/', views.show_test_csrf_page, name='show_test_csrf_page'),
    path(r'test_csrf/', views.test_csrf, name='test_csrf'),
    #使用图片验证码
    path(r'verify_code_image/', views.verify_code_image, name='verify_code_image'), #生成图片


    path(r'static_asset_page/', views.static_page, name='static_page'),

    path(r'upload_file_page/', views.upload_file_page, name='upload_file_page'),
    path(r'upload_file/', views.upload_file, name='upload_file'),

    #分页
    path(r'student_paginator/<int:page_index>', views.student_paginator, name='student_paginator'),

    #ajax
    path(r'show_test_ajax_page/', views.show_test_ajax_page, name='show_test_ajax_page'),
    path(r'test_ajax/', views.test_ajax, name='test_ajax'),


    #测试富文本
    path(r'test_mcetext/', views.test_mctext, name='test_mctext'),

    #测试celery
    # path(r'test_celery/', views.test_celery, name='test_celery')


]

