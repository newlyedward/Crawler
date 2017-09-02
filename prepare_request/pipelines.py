# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from .items import UserAgentItem


class RedisPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, UserAgentItem):
            key = spider.name.replace('Spider', '')
            spider.server.sadd(key, *item['user_agent'])
        return item
