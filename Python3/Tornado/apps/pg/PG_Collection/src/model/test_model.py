#!coding:utf8

#author:yqq
#date:2020/5/6 0006 16:48
#description:   测试 modle
# 关于  unittest 使用方法:  https://blog.51cto.com/2681882/2123613
# 1) 使用 TestSuite 可以控制测试用例的执行顺序
# 2) 如何让多个用例共用setup、teardown , 使用 setUpClass, tearDownClass
# 3) 如何跳过用例, unittest.skip(reason)、unittest.skipIf(condition,reason)、 unittest.skipUnless(condition,reason)
# 4) 如何生成html格式的测试报告:  使用HTMLTestRunner代替默认的TextTestRunner()




#sqlalchemy使用, 请参考: https://www.cnblogs.com/liu-yao/p/5342656.html
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# from .model import ORMBase, WithdrawOrder, Project
# from src.model.model import  ORMBase, CollectionFeeConfig, CollectionRecords, CollectionConfig
from src.config.constant import MYSQL_CONNECT_INFO
from src.model.model import  *

# import pytest
import unittest


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
                                  autoflush=True,
                                  # autocommit=True  # 自动提交
                                  autocommit=False  # 自动提交
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

        # assert 1 == 1




if __name__ == '__main__':

    test_funcs = [ TestModels('test_create_all_table'),
                   ]

    suite = unittest.TestSuite(  )
    suite.addTests(test_funcs)


    runner = unittest.TextTestRunner()
    runner.run(test=suite)

    unittest.main()

