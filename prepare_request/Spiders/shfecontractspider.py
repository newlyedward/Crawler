# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis import defaults
from scrapy_redis.spiders import RedisSpider
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re
from ..items import VarietyItem
from utils import LogHandler

log = LogHandler('ShfeContractSpider')


class DceContractSpider(RedisSpider, CrawlSpider):
    name = "ShfeContractSpider"
    allowed_domains = ["shfe.com.cn"]
    start_urls = ['http://www.shfe.com.cn/products/cu/']

    def start_requests(self):
        """Returns a batch of start requests from redis."""
        use_set = self.settings.getbool('REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
        add_urls = self.server.sadd if use_set else self.server.lpush
        add_urls(self.redis_key, *self.start_urls)
        return self.next_requests()

    def parse(self, response):
        variety_urls = response.xpath('//div[@class="came box fl"]/ul/li/a/@href').extract()
        for relative_url in variety_urls:
            variety_url = response.urljoin(relative_url)
            yield scrapy.Request(url=variety_url, callback=self.parse_variety)

    def parse_variety(self, response):
        relative_url = response.xpath('//div[@class="heyue_big"]/a[@class="kk1"]/@href').extract_first()
        variety_url = response.urljoin(relative_url)
        if variety_url:
            yield scrapy.Request(url=variety_url, callback=self.parse_contract)
        else:
            log.warning('Fetch url from %s is none' % response.url)

    def parse_contract(self, response):

        selectors = response.xpath('//table/tbody/tr/td')

        if not selectors:
            log.warning('Find nothing in %s' % response.url)
            return

        items = []
        for selector in selectors:
            inputstring = selector.xpath('string(.)').extract_first()
            outputstring = u''.join(inputstring.split())
            items.append(outputstring)

        keys = items[::2]
        values = items[1::2]

        variety_dict = dict(zip(keys, values))

        shfe_variety_item = VarietyItem()

        try:
            shfe_variety_item['variety'] = variety_dict['交易品种']
            shfe_variety_item['varietyid'] = variety_dict['交易代码']
            shfe_variety_item['trading_time'] = variety_dict['交易时间'].strip()
            shfe_variety_item['delivery'] = variety_dict['交割日期']
            shfe_variety_item['market'] = variety_dict['上市交易所']
        except KeyError:
            log.warning('can not get all data from %s' % response.url)

        try:
            shfe_variety_item['delivery_months'] = variety_dict['合约交割月份']
        except KeyError:
            shfe_variety_item['delivery_months'] = variety_dict['合约月份']
            log.warning('chinese key of delivery months is different in %s' % response.url)

        try:
            shfe_variety_item['minimum_margin'] = float(re.search('\d+', variety_dict['最低交易保证金']).group(0)) / 100
        except KeyError:
            shfe_variety_item['minimum_margin'] = float(re.search('\d+', variety_dict['交易保证金']).group(0)) / 100
            log.warning('chinese key of minimum margin is different in %s' % response.url)

        try:
            # 鸡蛋 合约月份倒数第4个交易日
            shfe_variety_item['end'] = int(re.search('\d+', variety_dict['最后交易日']).group(0))
        except AttributeError:
            from utils import chinese2digits
            nums = re.search('[一|二|三|四|五|六|七|八|九|十]+', variety_dict['最后交易日']).group(0)
            shfe_variety_item['end'] = chinese2digits(nums)
            log.info('Chinese num in %s of %s' % (variety_dict['最后交易日'], response.url))

        yield shfe_variety_item
