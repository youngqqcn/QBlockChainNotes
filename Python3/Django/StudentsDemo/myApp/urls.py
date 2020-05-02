
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

    path(r'students/all', views.students_details, name='students_details'),
    path(r'students/add_default', views.add_default_student, name='add_default_student'),
    path(r'students/add_default_by_manager', views.add_default_student_use_manager, name='add_default_student_by_manager'),
    path(r'students/page/<int:page_index>', views.show_students_page, name='show_students_page'),
    path(r'students/search', views.search_student, name='search_student'),
    path(r'grades/seach_relate', views.search_relate, name='search_relate'),
    path(r'grades/girlmorethanboy', views.search_student_by_F, name='search_student_by_F'),
    path(r'students/older_student', views.search_student_by_Q, name='search_student_by_Q'),
]