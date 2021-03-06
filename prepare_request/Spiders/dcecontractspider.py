# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis import defaults
from scrapy_redis.spiders import RedisSpider
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re
from ..items import VarietyItem
from utils import LogHandler

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

        selectors = response.xpath(
            '//div[@id="zoom"]/descendant::table[@class="MsoNormalTable"][1]/tbody/tr/td')

        if not selectors:
            selectors = response.xpath(
                '//div[@id="zoom"]/descendant::table[1]/tbody/tr/td')

        if not selectors:
            log.warning('Find nothing in %s' % response.url)
            return

        items = []
        for selector in selectors:
            items.append(selector.xpath('string(.)').extract_first().strip())

        keys = items[::2]
        values = items[1::2]

        variety_dict = dict(zip(keys, values))

        dce_variety_item = VarietyItem()

        try:
            dce_variety_item['variety'] = variety_dict['交易品种']
            dce_variety_item['varietyid'] = variety_dict['交易代码']
            dce_variety_item['trading_time'] = re.findall('\d+:\d{2}', variety_dict['交易时间'])
            dce_variety_item['delivery'] = int(re.search('\d+', variety_dict['最后交割日']).group(0))
            dce_variety_item['market'] = variety_dict['上市交易所']
        except KeyError:
            log.warning('can not get all data from %s' % response.url)

        try:
            dce_variety_item['delivery_months'] = list(map(int, re.findall('\d{1,2}', variety_dict['合约月份'])))
        except KeyError:
            dce_variety_item['delivery_months'] = list(map(int, re.findall('\d{1,2}', variety_dict['合约交割月份'])))
            log.warning('chinese key of delivery months is different in %s' % response.url)

        try:
            dce_variety_item['minimum_margin'] = float(re.search('\d+', variety_dict['最低交易保证金']).group(0)) / 100
        except KeyError:
            dce_variety_item['minimum_margin'] = float(re.search('\d+', variety_dict['交易保证金']).group(0)) / 100
            log.warning('chinese key of minimum margin is different in %s' % response.url)

        try:
            #鸡蛋 合约月份倒数第4个交易日
            dce_variety_item['end'] = int(re.search('\d+', variety_dict['最后交易日']).group(0))
        except AttributeError:
            from utils import chinese2digits
            nums = re.search('[一|二|三|四|五|六|七|八|九|十]+', variety_dict['最后交易日']).group(0)
            dce_variety_item['end'] = chinese2digits(nums)
            log.info('Chinese num in %s of %s' % (variety_dict['最后交易日'], response.url))

        dce_variety_item['delivery'] += dce_variety_item['end']
        yield dce_variety_item
