#!coding:utf8

#author:yqq
#date:2020/5/8 0008 16:46
#description:


#参考: https://www.cnblogs.com/liu-yao/p/5342656.html
from sqlalchemy import create_engine, func, and_
from sqlalchemy.orm import sessionmaker

from src.config.constant import MYSQL_CONNECT_INFO
from src.model.model import ORMBase, Address

import unittest

import random
import string
import datetime


class TestModels(unittest.TestCase):
    # def addCleanup(self):
    #     这是清理函数
        # pass

    def setUp(self):
        """
        每个用例执行前调用此方法
        :return:
        """
        print('setUp()')
        pass

    def tearDown(self):
        print('tearDown()')

    @classmethod
    def tearDownClass(cls):
        """
        类
        :return:
        """
        print('tearDownClass()')
        pass

    # def shortDescription(self):
    #     pass


    @classmethod
    def setUpClass(cls):
        """
        在初始化类之前, 执行这个函数
        :return:
        "Hook method for setting up class fixture before running tests in the class."
        """
        cls.engine = create_engine(MYSQL_CONNECT_INFO,
                               max_overflow=0,
                               pool_size=5)
        SessionCls = sessionmaker(bind=cls.engine,
                                  autoflush=False,   #关于 autoflush https://www.jianshu.com/p/b219c3dd4d1e
                                  autocommit=False# 自动提交
                                  #  autocommit=False#自动提交
                                  )

        cls.session = SessionCls()

        print('setUpClass()')


    def test_create_all_table(self):
        """
        创建所有表表结构, 如果表已经存在,则忽略
        :return:
        """
        # engine = create_engine("mysql+pymysql://root:eWFuZ3FpbmdxaW5n@192.168.10.29:3306/pg_database",
        #                        max_overflow=0,
        #                        pool_size=5)

        print('test_create_all_table')
        ORMBase.metadata.create_all(self.engine)  # 创建所有表结构

    def test_insert_address(self):

        all_addr = []
        for i in range(1000):
            addr = Address(address='htdf1' + ''.join(random.sample(population=string.ascii_lowercase * 10, k=41)),
                           token_name='HTDF',
                           pro_id = random.choice(range(0, 100)),
                           account_index = 0,
                           address_index= i,
                           create_time=datetime.datetime.now())

            all_addr.append( addr )

        self.session.add_all(instances=all_addr)
        self.session.commit()

    def test_query_address(self):
        ret = self.session.query(func.max(Address.address_index)).filter(
            and_(Address.pro_id == 99999, Address.token_name == 'HTDF')).first()
        print(ret)


if __name__ == '__main__':
    test_funcs = [
        TestModels('test_create_all_table'),
        # TestModels('test_insert_data_WithdrawOrder'),
        # TestModels('test_query_data_WithdrawOrder'),
        # TestModels('test_insert_data_Project')
    ]

    suite = unittest.TestSuite()
    suite.addTests(test_funcs)

    runner = unittest.TextTestRunner()
    runner.run(test=suite)

    # unittest.main()

    #
    # unittest.main()
    pass