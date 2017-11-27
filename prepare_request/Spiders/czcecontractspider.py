# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis import defaults
from scrapy_redis.spiders import RedisSpider
from scrapy.spiders import CrawlSpider
import re
from ..items import VarietyItem
from utils import LogHandler

log = LogHandler('CzceContractSpider')


class DceContractSpider(RedisSpider, CrawlSpider):
    name = "CzceContractSpider"
    allowed_domains = ["czce.com.cn"]
    start_urls = ['http://www.czce.com.cn/portal/sspz/xm/A090201index_1.htm']

    def start_requests(self):
        """Returns a batch of start requests from redis."""
        use_set = self.settings.getbool('REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
        add_urls = self.server.sadd if use_set else self.server.lpush
        add_urls(self.redis_key, *self.start_urls)
        return self.next_requests()

    def parse(self, response):
        variety_urls = response.xpath('//div[@id="dropmenu3"]/a//@href').extract()

        self.parse_variety(response)

        for relative_url in variety_urls[1:]:
            variety_url = response.urljoin(relative_url)
            yield scrapy.Request(url=variety_url, callback=self.parse_variety)



    def parse_variety(self, response):
        relative_url = response.xpath('//div[@id="dropmenu1"]/a//@href').extract_first()
        variety_url = response.urljoin(relative_url)
        if variety_url:
            yield scrapy.Request(url=variety_url, callback=self.parse_contract)
        else:
            log.warning('Fetch url from %s is none' % response.url)

    def parse_contract(self, response):
        selectors = response.xpath('//div[@id="BodyLabel"]/table/tbody/tr/td')

        if not selectors:
            log.warning('Find nothing in %s' % response.url)
            return

        items = []
        for selector in selectors:   # 处理后空格没有，要将\xa0 \n \t 替换成空格
            inputstring = selector.xpath('string(.)').extract_first()
            outputstring = ''.join(inputstring.split())
            items.append(outputstring)

        # 棉花解析 items len=31 13,14连接为一个字符串
        if len(items) == 31:
            items[13] += items[14]
            items.pop(14)

        # 甲醇有调整过的合约，交易单位从50吨/手 调整至 10吨/手
        # //div[@id="BodyLabel"]/table/tbody/tr[2]/td/div/table/tbody/tr/td

        # 早籼稻  //div[@id="BodyLabel"]/div[1]/table/tbody/tr/td
        # 菜籽粕 //div/div[1]/table/tbody/tr/td
        # 菜籽 //div/font/div/table/tbody/tr/td
        # 粳稻 //div/div/div/table/tbody/tr/td
        # 棉纱 还需要向下爬
        # 铁合金 一个页面两个合约

        keys = items[::2]
        values = items[1::2]

        variety_dict = dict(zip(keys, values))

        czce_variety_item = VarietyItem()

        try:
            czce_variety_item['variety'] = variety_dict['交易品种']
            czce_variety_item['varietyid'] = variety_dict['交易代码']
            czce_variety_item['trading_time'] = variety_dict['交易时间']

            czce_variety_item['market'] = variety_dict['上市交易所']
        except KeyError:
            log.warning('can not get all data from %s' % response.url)

        try:
            czce_variety_item['delivery'] = variety_dict['最后交割日']
        except KeyError:
            czce_variety_item['delivery'] = variety_dict['交割日期']
            log.warning('chinese key of delivery months is different in %s' % response.url)

        try:
            czce_variety_item['delivery_months'] = variety_dict['合约交割月份']
        except KeyError:
            czce_variety_item['delivery_months'] = variety_dict['合约月份']
            log.warning('chinese key of delivery months is different in %s' % response.url)

        try:
            czce_variety_item['minimum_margin'] = float(re.search('\d+', variety_dict['最低交易保证金']).group(0)) / 100
        except KeyError:
            czce_variety_item['minimum_margin'] = float(re.search('\d+', variety_dict['交易保证金']).group(0)) / 100
            log.warning('chinese key of minimum margin is different in %s' % response.url)

        try:
            # 鸡蛋 合约月份倒数第4个交易日
            czce_variety_item['end'] = int(re.search('\d+', variety_dict['最后交易日']).group(0))
        except AttributeError:
            from utils import chinese2digits
            nums = re.search('[一|二|三|四|五|六|七|八|九|十]+', variety_dict['最后交易日']).group(0)
            czce_variety_item['end'] = chinese2digits(nums)
            log.info('Chinese num in %s of %s' % (variety_dict['最后交易日'], response.url))

        yield czce_variety_item
