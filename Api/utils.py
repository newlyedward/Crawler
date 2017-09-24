# -*- coding: utf-8 -*-
import os
import requests
import logging
from logging.handlers import TimedRotatingFileHandler
from lxml import etree
from configparser import ConfigParser


# ------------------------ logging ----------------------------------
class LogHandler(logging.Logger):
    """
    LogHandler
    """

    def __init__(self, name, level=logging.DEBUG):
        self.name = name
        self.level = level
        logging.Logger.__init__(self, self.name, level=level)
        self.__setFileHandler__()
        self.__setStreamHandler__(logging.WARN)

    def __setFileHandler__(self, level=None):
        """
        set file handler
        :param level:
        :return:
        """
        file_name = './log/%s' % self.name
        # 设置日志回滚, 保存在log目录, 一天保存一个文件, 保留15天
        file_handler = TimedRotatingFileHandler(filename=file_name, when='D', interval=1, backupCount=15)
        file_handler.suffix = '%Y%m%d.log'
        if not level:
            file_handler.setLevel(self.level)
        else:
            file_handler.setLevel(level)
        formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')

        file_handler.setFormatter(formatter)
        self.addHandler(file_handler)

    def __setStreamHandler__(self, level=None):
        """
        set stream handler
        :param level:
        :return:
        """
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
        stream_handler.setFormatter(formatter)
        if not level:
            stream_handler.setLevel(self.level)
        else:
            stream_handler.setLevel(level)
        self.addHandler(stream_handler)


# ---------------------- config ------------------------------------------


def get_congfig_file(file_name='Config.ini'):
    file_name = os.path.join(os.getcwd(), file_name)
    fp = open(file_name, 'w')
    return fp


def get_congfig_handle(file_name='Config.ini'):
    config = ConfigParser()
    file_name = os.path.join(os.getcwd(), file_name)
    config.read(file_name)
    return config


if __name__ == '__main__':
    # from pymongo import MongoClient
    # client = MongoClient('192.168.2.130', 27017)
    # db = client.http_header
    # db.user_agent.insert_many([{'user_agent': ua} for ua in ua_list])
    # db.user_agent.create_index({"user_agent": 1}, {"unique": True, "dropDups": True})

    todo = 0
    if todo:
        import redis
        conn = redis.Redis('192.168.2.130', 6379, decode_responses=True)

        ua_list = get_ua_list()
        conn.sadd('user_agent', *ua_list)

    log = LogHandler(os.path.basename(__file__))
    log.debug('this is a debug msg')
    log.info('this is a info msg')
    log.warning('this is a warning msg')
    log.error('this is a error msg')
    log.fatal('this is a fatal msg')
    log.critical('this is a critical msg')
