#!coding:utf8

#author:yqq
#date:2020/5/6 0006 16:48
#description:   测试 modle
# 关于  unittest 使用方法:  https://blog.51cto.com/2681882/2123613
# 1) 使用 TestSuite 可以控制测试用例的执行顺序
# 2) 如何让多个用例共用setup、teardown , 使用 setUpClass, tearDownClass
# 3) 如何跳过用例, unittest.skip(reason)、unittest.skipIf(condition,reason)、 unittest.skipUnless(condition,reason)
# 4) 如何生成html格式的测试报告:  使用HTMLTestRunner代替默认的TextTestRunner()



#参考: https://www.cnblogs.com/liu-yao/p/5342656.html
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config.constant import MYSQL_CONNECT_INFO
from src.model.model import  ORMBase, WithdrawOrder, Project
import unittest
import random
import string
import datetime
import time


class TestModels(unittest.TestCase):
    # def addCleanup(self):
    #     这是清理函数
        # pass

    def setUp(self):
        """
        每个用例执行前调用此方法
        :return:
        """
        # mqsend(serial_id)
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
                                  autocommit=True# 自动提交
                                  #  autocommit=False#自动提交
                                  )

        cls.session = SessionCls()

        print('setUpClass()')


    def test_create_all_table(self):
        """
        创建所有表表结构, 如果表已经存在,则忽略
        :return:
        """
        # engine = create_engine("mysql+pymysql://root:eWFuZ3FpbmdxaW5n@192.168.10.29:3306/pg_database_dev",
        #                        max_overflow=0,
        #                        pool_size=5)

        print('test_create_all_table')
        ORMBase.metadata.create_all(self.engine)  # 创建所有表结构

        # assert 1 == 1


    def test_insert_data_WithdrawOrder(self):
        """
        测试 向 tb_withdraw_order 中插入数据
        :return:
        """
        # engine = create_engine("mysql+pymysql://root:eWFuZ3FpbmdxaW5n@192.168.10.29:3306/pg_database_dev",
        #                        max_overflow=0,
        #                        pool_size=5)
        print('test_insert_data_WithdrawOrder')

        try:
            all_instances = []
            for i in range(10000):
                order = WithdrawOrder(serial_id= str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))) + str(int(time.perf_counter_ns()))[-7:] ,
                                      order_id=''.join(random.sample(population=string.digits * 10, k=15)),
                                      pro_id=random.randint(0, 100),
                                      token_name= random.choice(seq=['BTC', 'ETH', 'USDT', 'HTDF']),
                                      callback_url='http://127.0.0.1:9999/testcallback/test' + \
                                                   ''.join(random.sample(population=string.ascii_lowercase * 10, k=43)),
                                      from_addr=''.join(random.sample(population=string.ascii_lowercase * 10, k=43)),
                                      to_addr=''.join(random.sample(population=string.ascii_lowercase * 10, k=43)),
                                      memo='',
                                      amount=random.uniform(0.00001, 9999999),  #生成浮点数
                                      block_height=0,
                                      tx_hash='',
                                      tx_confirmations=0,
                                      order_status= random.choice(["PROCESSING", "SUCCESS", "FAIL"]),
                                      transaction_status=random.choice(["NOTYET", "PENDING", "FAIL", "SUCCESS"]),
                                      notify_status=random.choice(["NOYET", "FISRTSUCCESS", "FIRSTFAIL", "SECONDSUCCESS", "SECONDFAIL"]),
                                      notify_times=random.randint(1, 10),
                                      block_time=datetime.datetime.now(),
                                      complete_time=datetime.datetime.now(),
                                      remark=''
                                      )
                # session.add(instance=order, _warn=True)
                all_instances.append(order)

            self.session.add_all(instances=all_instances)

            # self.session.commit()
            self.session.flush()

        except Exception as e:
            print(f"error{e}")
            pass

    def test_query_data_WithdrawOrder(self):

        # sqlalchemy使用, 请参考: https://www.cnblogs.com/liu-yao/p/5342656.html
        orders = self.session.query(WithdrawOrder).filter_by(pro_id=3).all()
        # print(deposit_txs)
        for tx in orders:
            print(tx)

        pass


    def test_insert_data_Project(self):
        """
            测试 向 tb_withdraw_order 中插入数据
            :return:
            """
        # engine = create_engine("mysql+pymysql://root:eWFuZ3FpbmdxaW5n@192.168.10.29:3306/pg_database_dev",
        #                        max_overflow=0,
        #                        pool_size=5)
        print('test_insert_data_Project')



        try:
            all_instances = []
            import datetime
            for i in range(100):
                proj = Project(  # project_id 不设置,  默认自增即可
                    pro_name=''.join(random.sample(population=string.ascii_lowercase * 10, k=43)),
                    tel_no=''.join(random.sample(population=string.digits * 10, k=11)),
                    email='test@' + ''.join(random.sample(population=string.ascii_lowercase * 10, k=11)),
                    api_key_hash=''.join(random.sample(population=string.ascii_lowercase * 10, k=64)),
                    app_id=''.join(random.sample(population=string.ascii_lowercase * 10, k=20)),
                    create_time=datetime.datetime.now(),
                    account_status=random.randint(0, 4)
                )
                # session.add(instance=order, _warn=True)
                all_instances.append(proj)

            self.session.add_all(instances=all_instances)

            # self.session.commit()
            self.session.flush()

        except Exception as e:
            print(f"error: {e}")
            pass

        pass
    def test_user_api(self):
        # try:
        #     all_instances = []
        #
        #     order = WithdrawOrder(serial_id= str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))) + str(int(time.perf_counter_ns()))[-7:] ,
        #                           order_id=''.join(random.sample(population=string.digits * 10, k=15)),
        #                           project_id=random.randint(0, 100),
        #                           token_name= 'HTDF',
        #                           callback_url='http://127.0.0.1:9999/testcallback/test' + \
        #                                        ''.join(random.sample(population=string.ascii_lowercase * 10, k=43)),
        #                           from_addr='htdf1jrh6kxrcr0fd8gfgdwna8yyr9tkt99ggmz9ja2',
        #                           to_addr='htdf1sg5av8alu6fqe06nuag9ctcgawrlzsj5szhcrx',
        #                           memo='',
        #                           amount=0.5,  #生成浮点数
        #                           block_height=0,
        #                           tx_hash='',
        #                           tx_confirmations=0,
        #                           transaction_status='',
        #                           order_status='',
        #                           notify_status='',
        #                           block_time=datetime.datetime.now(),
        #                           complete_time=datetime.datetime.now(),
        #                           remark=''
        #                           )
        #         # session.add(instance=order, _warn=True)
        #     all_instances.append(order)
        #     self.session.add_all(instances=all_instances)
        #
        #     self.session.commit()
        #
        # except Exception as e:
        #     print(f"error{e}")
        #     pass
        serial_id = "202005101215118187804"
        data = {
            # "serial_id": orders[0].serial_id
            'serial_id': serial_id
        }
        self.assertEqual(mqsend(data),True)
        print()

    def test_sql(self):

        self.assertEqual(test_add(), True)
        self.assertEqual(test_delete(), True)
        self.assertEqual(test_add(), True)
        self.assertEqual(test_update(), True)
        self.assertEqual(test_query(), True)
        print()
if __name__ == '__main__':
    test_funcs = [

        # TestModels('test_user_api'),
        TestModels('test_create_all_table'),

        TestModels('test_insert_data_WithdrawOrder'),
        TestModels('test_query_data_WithdrawOrder'),
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