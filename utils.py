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


log = LogHandler('utils')


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


# ---------------------- crawler utils--------------------------------

DEFAULT_HEADERS = {'Connection': 'keep-alive',
                   'Cache-Control': 'max-age=0',
                   'Upgrade-Insecure-Requests': '1',
                   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko)',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                   'Accept-Encoding': 'gzip, deflate, sdch',
                   'Accept-Language': 'zh-CN,zh;q=0.8',
                   }


def get_html_text(url, ua=''):
    headers = DEFAULT_HEADERS
    if ua:
        headers['User-Agent'] = ua

    try:
        resp = requests.get(url, headers, timeout=10)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        return resp.text
    except:
        return resp.status_code


def get_post_text(url, data=None, ua=''):
    headers = DEFAULT_HEADERS
    if ua:
        headers['User-Agent'] = ua

    try:
        resp = requests.post(url=url, data=data, headers=headers)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        return resp.text
    except:
        return resp.status_code


def get_html_tree(url, ua=''):
    headers = DEFAULT_HEADERS
    if ua:
        headers['User-Agent'] = ua

    try:
        resp = requests.get(url=url, headers=headers, timeout=30)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        return etree.HTML(resp.text)
    except:
        return resp.status_code


def get_ua_list():
    url = 'https://techblog.willshouse.com/2012/01/03/most-common-user-agents/'
    resp = get_html_tree(url)
    ua_list = resp.xpath('//textarea[@class="get-the-list"]/text()')[0].splitlines()
    return ua_list


chs_arabic_map = {u'零': 0, u'一': 1, u'二': 2, u'三': 3, u'四': 4,
                  u'五': 5, u'六': 6, u'七': 7, u'八': 8, u'九': 9,
                  u'十': 10, u'百': 100, u'千': 10 ** 3, u'万': 10 ** 4,
                  u'〇': 0, u'壹': 1, u'贰': 2, u'叁': 3, u'肆': 4,
                  u'伍': 5, u'陆': 6, u'柒': 7, u'捌': 8, u'玖': 9,
                  u'拾': 10, u'佰': 100, u'仟': 10 ** 3, u'萬': 10 ** 4,
                  u'亿': 10 ** 8, u'億': 10 ** 8, u'幺': 1,
                  u'０': 0, u'１': 1, u'２': 2, u'３': 3, u'４': 4,
                  u'５': 5, u'６': 6, u'７': 7, u'８': 8, u'９': 9}


def chinese2digits(chinese):
    """
    :param chinese: chinese numbers
    :return: digits

    >>> chinese2digits('九')
    9
    >>> chinese2digits('十一')
    11
    >>> chinese2digits('一百二十三')
    123
    >>> chinese2digits('一千二百零三')
    1203
    >>> chinese2digits('一万一千一百零一')
    11101
    >>> chinese2digits('十万零三千六百零九')
    103609
    >>> chinese2digits('一百二十三万四千五百六十七')
    1234567
    >>> chinese2digits('一千一百二十三万四千五百六十七')
    11234567
    >>> chinese2digits('一亿一千一百二十三万四千五百六十七')
    111234567
    >>> chinese2digits('一百零二亿五千零一万零一千零三十八')
    10250011038
    >>> chinese2digits('一千一百一十一亿一千一百二十三万四千五百六十七')
    111111234567
    """

    assert isinstance(chinese, str)

    result = 0
    tmp = 0
    hnd_mln = 0
    for count in range(len(chinese)):
        curr_char = chinese[count]
        curr_digit = chs_arabic_map.get(curr_char, None)
        # meet 「亿」 or 「億」
        if curr_digit == 10 ** 8:
            result = result + tmp
            result = result * curr_digit
            # get result before 「亿」 and store it into hnd_mln
            # reset `result`
            hnd_mln = hnd_mln * 10 ** 8 + result
            result = 0
            tmp = 0
        # meet 「万」 or 「萬」
        elif curr_digit == 10 ** 4:
            result = result + tmp
            result = result * curr_digit
            tmp = 0
        # meet 「十」, 「百」, 「千」 or their traditional version
        elif curr_digit >= 10:
            tmp = 1 if tmp == 0 else tmp
            result = result + curr_digit * tmp
            tmp = 0
        # meet single digit
        elif curr_digit is not None:
            tmp = tmp * 10 + curr_digit
        else:
            return result
    result = result + tmp
    result = result + hnd_mln
    return result


if __name__ == '__main__':
    # test for get_post_text
    # url = "http://www.dce.com.cn/dalianshangpin/sspz/487477/487481/1500303/index.html"
    # post_data = {'articleKey': '1500303',
    #              'columnId': '487481',
    #              'moduleId': '3',
    #              'struts.portlet.action': '/app/counting-front!saveInfo.action'}
    #
    # print(get_post_text(url=url, data=post_data))

    # test for get_ua_list


    # from pymongo import MongoClient
    # client = MongoClient('192.168.2.130', 27017)
    # db = client.http_header
    # db.user_agent.insert_many([{'user_agent': ua} for ua in ua_list])
    # db.user_agent.create_index({"user_agent": 1}, {"unique": True, "dropDups": True})

    todo = 0
    if todo:
        import redis

        conn = redis.Redis('192.168.2.88', 6379, decode_responses=True)

        ua_list = get_ua_list()
        conn.sadd('user_agent', *ua_list)

    log = LogHandler(os.path.basename(__file__))
    log.debug('this is a debug msg')
    log.info('this is a info msg')
    log.warning('this is a warning msg')
    log.error('this is a error msg')
    log.fatal('this is a fatal msg')
    log.critical('this is a critical msg')
