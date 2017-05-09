# -*- coding: utf-8 -*-
from scrapy_redis import defaults
from scrapy_redis.spiders import RedisSpider


class PorxyPoolSpider(RedisSpider):
    name = "PorxyPoolSpider"
    allowed_domains = ["xicidaili.com"]
    start_urls = ['http://xicidaili.com/']

    def start_requests(self):
        """Returns a batch of start requests from redis."""
        use_set = self.settings.getbool('REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
        add_urls = self.server.sadd if use_set else self.server.lpush
        add_urls(self.redis_key, *self.start_urls)
        return self.next_requests()

    def parse(self, response):
        pass
