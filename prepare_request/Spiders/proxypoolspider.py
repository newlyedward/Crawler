# -*- coding: utf-8 -*-
from scrapy_redis.spiders import RedisSpider


class PorxyPoolSpider(RedisSpider):
    name = "Porxy_Pool"
    allowed_domains = ["xicidaili.com"]
    start_urls = ['http://xicidaili.com/']

    def parse(self, response):
        pass
