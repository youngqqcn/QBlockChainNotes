"""
Created on Mon Mar 19 20:47:10 2018
@author: frank
"""

from config import SQL_IP_ADDR, SQL_PORT
from config import SQL_USRNAME
from config import SQL_PASSWD
from config import DBNAME

import pymysql

def open(host=SQL_IP_ADDR,usr=SQL_USRNAME,pw=SQL_PASSWD,db_name=DBNAME):
    #print(SQL_IP_ADDR)
    #print(SQL_PASSWD)
    #print(DBNAME)
    conn = pymysql.connect(host=host,
                            user=usr,
                            password=pw,
                            db=db_name,
                            charset='utf8',
                            cursorclass=pymysql.cursors.DictCursor)
    return conn

def close(conn):
    conn.close()

def execute(conn,cmd):
    cur = conn.cursor()
    cur.execute(cmd)
    conn.commit()  #fixed bug by yqq
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
    conn = open()
    print(get_column_values(conn,'t_eth_accounts','address'))
    close(conn)

if __name__ == "__main__":
    main()
    
    
