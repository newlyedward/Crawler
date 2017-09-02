# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis import defaults
from scrapy_redis.spiders import RedisSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor


class DceContractSpider(RedisSpider):
    name = "DceContractSpider"
    allowed_domains = ["dce.com.cn"]
    start_urls = ['http://www.dce.com.cn/']

    # 提取期货各品种信息的页面，合约规则，合约信息，交易参数
    rules = (Rule(
        LinkExtractor(allow='dalianshangpin/sspz/[^qd].+/index.html', restrict_css='.pzzx_left', unique=True)
        , callback='parse_variety'),)

    def start_requests(self):
        """Returns a batch of start requests from redis."""
        use_set = self.settings.getbool('REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
        add_urls = self.server.sadd if use_set else self.server.lpush
        add_urls(self.redis_key, *self.start_urls)
        return self.next_requests()

    def parse_variety(self, response):
        relative_url = response.xpath('//div/ul/li/a[contains(@title, "期货合约")]/@href').extract_first()
        variety_url = response.urljoin(relative_url)
        yield scrapy.Request(url=variety_url, callback=self.parse_contract)
        # 还需要提取其他链接

    def pare_contract(self, response):
        contract_info = response.xpath('//table[1]/tbody/tr/td/p/text()').extract()
        contract_info = contract_info[1::2]
        pass
