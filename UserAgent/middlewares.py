# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import redis


class RedisMiddleWare(object):
    def __init__(self, host, port, key):
        self.host = host
        self.port = port
        self.key = key
        self.client = []

    @classmethod
    def from_crawler(cls, crawler):                   #__init__输入参数，不是class的变量
        return cls(
            host=crawler.settings.get('REDIS_HOST'),
            port=crawler.settings.get('REDIS_PORT'),
            key=crawler.settings.get('REDIS_KEYNAME'),
        )

    def open_spider(self, spider):
        self.client = redis.Redis(host=self.host, port=self.port, db=0, decode_responses=True)


class UserAgentMiddleware(object):
    """This middleware allows spiders to override the user_agent"""

    def __init__(self, user_agent='Scrapy'):
        self.user_agent = user_agent

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler.settings['USER_AGENT'])
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        return o

    def spider_opened(self, spider):
        self.user_agent = getattr(spider, 'user_agent', self.user_agent)

    def process_request(self, request, spider):
        if self.user_agent:
            request.headers.setdefault(b'User-Agent', self.user_agent)
