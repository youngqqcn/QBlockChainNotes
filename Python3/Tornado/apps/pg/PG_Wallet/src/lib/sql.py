#!coding:utf8

#author:yqq
#date:2020/4/30 0030 17:11
#description:


import os
import pymysql
SQL_PASSWD = os.environ.get('SQL_PWD')

def open(host : str,usr : str, passwd : str,db_name : str):
    conn = pymysql.connect(host=host, user=usr,
                password=passwd, db=db_name,
                charset='utf8', cursorclass=pymysql.cursors.DictCursor)

    return conn

def close(conn):
    conn.close()

def execute(conn,cmd):
    cur = conn.cursor()
    cur.execute(cmd)
    conn.commit()  #fixed bug by yqq 2019-05-01
    return cur.fetchall()

def run(cmd):
    conn = open()
    result = execute(conn,cmd)
    close(conn)
    return result

def get_column_values(conn,table_name,column_name):
    cmd = "SELECT {0} FROM {1}".format(column_name,table_name)
    return execute(conn,cmd)
    
def main():
    host = '192.168.10.29'
    usr = 'root'
    passwd = 'eWFuZ3FpbmdxaW5n'
    dbname = 'test_1'
    conn = open(host=host, usr=usr, passwd=passwd, db_name=dbname )
    print(get_column_values(conn,'t_test_student','name'))
    close(conn)

if __name__ == "__main__":
    main()
    
    
