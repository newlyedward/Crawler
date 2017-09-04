# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis import defaults
from scrapy_redis.spiders import RedisSpider
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import DceVarietyItem
from utils import  LogHandler

log = LogHandler('DceContractSpider')


class DceContractSpider(RedisSpider, CrawlSpider):
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

    def parse_contract(self, response):
        selectors = response.xpath('//div[@id="zoom"]/descendant::table[1]/tbody/tr/td/p')
        items = []
        for selector in selectors:
            items.append(selector.xpath('string(.)').extract_first().strip())

        keys = items[::2]
        values = items[1::2]

        variety_dict = dict(zip(keys, values))

        dce_varity_item = DceVarietyItem()
        try:
            dce_varity_item['variety'] = variety_dict['交易品种']
            dce_varity_item['symbol'] = variety_dict['交易代码']
            dce_varity_item['market'] = variety_dict['上市交易所']
        except KeyError:
            log.warning('can not get data from %s' % response.url)
        else:
            yield dce_varity_item
