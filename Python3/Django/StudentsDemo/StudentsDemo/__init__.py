# import pymysql
# pymysql.install_as_MySQLdb()   #Django 3.0 不适用   需要按照



from .celery import app as celery_app
__all__ = ['celery_app']