from scrapy_redis.spiders import RedisSpider
from scrapy_redis import defaults
from ..items import UserAgentItem
from UserAgent import settings


class UserAgentSpdier(RedisSpider):
    name = 'UserAgentSpider'
    start_urls = ['https://techblog.willshouse.com/2012/01/03/most-common-user-agents/']

    def start_requests(self):
        """Returns a batch of start requests from redis."""
        use_set = self.settings.getbool('REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
        add_urls = self.server.sadd if use_set else self.server.lpush
        add_urls(self.redis_key, *self.start_urls)
        return self.next_requests()

    def parse(self, response):
        ua_items = UserAgentItem()
        ua_list = response.xpath('//textarea[@class="get-the-list"]/text()').extract_first().splitlines()

        ua_items['user_agent'] = ua_list
        yield ua_items
