# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from .items import DceVarietyItem
# import sys
# sys.path.append('G:/Code/Crawler')
from utils import LogHandler

log = LogHandler('pipelines')

# class RedisPipeline(object):
#     def process_item(self, item, spider):
#         if isinstance(item, UserAgentItem):
#             key = spider.name.replace('Spider', '')
#             spider.server.sadd(key, *item['user_agent'])
#         return item


class MongoDceVarietyPipeline(object):
    collection = 'variety'

    def __init__(self, mongo_host, mongo_port, mongo_db):
        self.mongo_host = mongo_host
        self.mongo_port = mongo_port
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_host=crawler.settings.get('MONGODB_HOST'),
            mongo_port=crawler.settings.get('MONGODB_PORT'),
            mongo_db=crawler.settings.get('MONGODB_DB')
        )

    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_host, self.mongo_port)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, DceVarietyItem):
            self.db[self.collection].update({'varietyid': item['varietyid']},
                                            {'$set': dict(item)}, upsert=True)
            log.info('Update variety %s' % item['varietyid'])
            return item
