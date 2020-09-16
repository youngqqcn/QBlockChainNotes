#!coding:utf8

#author:yqq
#date:2020/5/9 0009 10:44
#description:



class BalanceNotEnoughException(Exception):
    """
    出币地址的余额不够
    """
    pass


class TxBroadcastFailedException(Exception):
    """
    交易广播失败
    """
    pass


class SendMsgToMQFailedException(Exception):
    """
    发送消息到消息队列失败了
    """
    pass



class InvalidParametersException(Exception):
    """
    参数类型不对
    """
    pass

class MqBodyException(Exception):
    """
    MQ接收类型错误
    """
    pass

class SqlCDUSException(Exception):
    """
    SQL错误处理
    """
    pass

class MonitorFailedException(Exception):
    """
    监控失败，没有监控到tx_hash
    """
    pass

class NotifyFailedException(Exception):
    """
    通知失败
    """
    pass

class UpdateDatabaseException(Exception):
    """
    更新数据库异常
    """
    pass

class  HttpConnectionError(Exception):
    """
    连接异常
    """
    pass

