
from django.urls import path
from . import views


# Django 3.0 中不再使用正则表达式, 获取模板中的变量
# https://docs.djangoproject.com/en/3.0/intro/tutorial03/#namespacing-url-names


urlpatterns = [
    path(r'', views.index),
    # path(r'^(\d+)/$', views.detail)
    path(r'page/<int:num>/', views.detail, name='detail'),
    path(r'grades/all', views.grades_details, name='grades_details'),
    path(r'grades/<int:grade_id>', views.get_grade_students, name='get_grade_students'),

    path(r'students/all', views.students_details, name='students_details')
]