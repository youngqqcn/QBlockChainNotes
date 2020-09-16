#!coding:utf8

#author:fhh
#date:2020/5/28
#description:  定时监控
import json

import time
import logging

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

from src.config.constant import WithdrawStatus, MYSQL_CONNECT_INFO
from src.model.model import WithdrawOrder
from src.monitor.comman import handler

engine = create_engine(MYSQL_CONNECT_INFO,
                       pool_size=5, pool_pre_ping=True, pool_recycle=120)

SessionCls = sessionmaker(bind=engine,
                          autoflush=False,   #关于 autoflush https://www.jianshu.com/p/b219c3dd4d1e
                          autocommit=True# 自动提交
                          )
session = SessionCls()


logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s | %(filename)s:%(funcName)s:%(lineno)d | %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


def main():

    while True:
        try:

            all_items = session.query(WithdrawOrder.serial_id)\
                                .filter( and_(WithdrawOrder.transaction_status != WithdrawStatus.transaction_status.NOTYET,
                                              WithdrawOrder.order_status == WithdrawStatus.order_status.PROCESSING,
                                              WithdrawOrder.notify_times >= 5))\
                                .order_by(WithdrawOrder.notify_times)\
                                .all()

            logger.info(f'all_serial_id :{all_items}')

            for item in all_items:
                try:
                    handler( session, item.serial_id, logger)
                except Exception as e:
                    logger.error(e)  #出错了 , 继续其他的
                except:
                    logger.error('unknow error')


            for i in range(60):
                logger.info('sleeping...')
                time.sleep(10)

        except Exception as e:
            logger.error( f'main() ERROR:{e} ')
            time.sleep( 60)
            pass


if __name__ == '__main__':


     main()