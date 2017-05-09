# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import redis


class RedisPipeline(object):
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

    def process_item(self, item, spider):
        self.client.sadd(self.key, *item['user_agent'])
        return item
