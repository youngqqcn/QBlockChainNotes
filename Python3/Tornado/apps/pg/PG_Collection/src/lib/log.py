#!coding:utf8

#author:yqq
#date:2020/4/30 0030 16:48
#description:
import tornado.log



# 格式化日志输出格式
# 默认是这种的: [I 160807 09:27:17 web:1971] 200 GET / (::1) 7.00ms
# 自定义格式: [2020-02-19 09:38:01,892 执行文件名:执行函数名:执行行数 日志等级] 内容消息
# 常用命令代码
# %(name)s Logger的名字
# %(levelno)s 数字形式的日志级别
# %(levelname)s 文本形式的日志级别
# %(pathname)s 调用日志输出函数的模块的完整路径名，可能没有
# %(filename)s 调用日志输出函数的模块的文件名
# %(module)s 调用日志输出函数的模块名
# %(funcName)s 调用日志输出函数的函数名
# %(lineno)d 调用日志输出函数的语句所在的代码行
# %(created)f 当前时间，用UNIX标准的表示时间的浮 点数表示
# %(relativeCreated)d 输出日志信息时的，自Logger创建以 来的毫秒数
# %(asctime)s 字符串形式的当前时间。默认格式是 “2003-07-08 16:49:45,896”。逗号后面的是毫秒
# %(thread)d 线程ID。可能没有
# %(threadName)s 线程名。可能没有
# %(process)d 进程ID。可能没有
# %(message)s用户输出的消息
class LogFormatter(tornado.log.LogFormatter):
    def __init__(self):
        super(LogFormatter, self).__init__(
            # fmt='%(color)s[%(asctime)s %(filename)s:%(funcName)s:%(lineno)d %(levelname)s]%(end_color)s %(message)s',
            # fmt='%(color)s[%(asctime)s | %(pathname)s | PID %(process)d |func %(funcName)s | line %(lineno)d | %(levelname)s]%(end_color)s %(message)s',
            # fmt='%(color)s[%(asctime)s %(module)s :%(funcName)s:%(lineno)d %(levelname)s]%(end_color)s %(message)s',
            # datefmt= None, #'%Y-%m-%d %H:%M:%S',
            #

            fmt='%(color)s[%(asctime)s |  %(levelname)s | %(filename)s |%(funcName)s:%(lineno)d ]%(end_color)s %(message)s',
            datefmt=""  # 设为空, 显示出毫秒
        )


import logging
def get_default_logger(log_level=logging.INFO):
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s | %(levelname)s | %(filename)s |%(funcName)s:%(lineno)d] %(message)s')
    return logging.getLogger(__name__)