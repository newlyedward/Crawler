# -*- coding: utf-8 -*-
import scrapy


class PorxyPoolSpider(scrapy.Spider):
    name = "Porxy_Pool"
    allowed_domains = ["xicidaili.com"]
    start_urls = ['http://xicidaili.com/']

    def parse(self, response):
        pass
