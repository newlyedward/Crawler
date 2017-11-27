# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

# chn2eng = {'品种': 'variety',  # 玉米
#            '交易品种': 'variety',  # 玉米
#            '交易代码': 'varietyid',  # A
#            '合约代码': 'code',  # a1703
#            '交易单位': 'unit',  # 10(吨/手)
#            '报价单位': 'currency',  # 元（人民币）/吨
#            '最小变动价位': 'tick_size',  # 1元/吨 / 1
#            '合约月份': 'delivery_months',  # 1、3、5、7、9、11月
#            '交易时间': 'tradeing time',  # 每周一至周五上午9:00-11:30，下午13:30-15:00，以及交易所规定的其他时间
#            '开始交易日': 'begin',    # 20020315
#            '最后交易日': 'end',  # 20030314 / 合约月份第10个交易日
#            '最后交割日': 'delivery',  # 20030321
#            '交割等级': '',    # 大连商品交易所玉米淀粉交割质量标准
#            '交割地点': '',    # 大连商品交易所玉米淀粉指定交割仓库
#            '最低交易保证金': '',   # 合约价值的5%
#            '交割方式': '',  # 实物交割
#            '上市交易所': 'market',   # 大连商品交易所
#
#            }


class VarietyItem(scrapy.Item):
    variety = scrapy.Field()
    varietyid = scrapy.Field()
    market = scrapy.Field()
    delivery_months = scrapy.Field()
    end = scrapy.Field()
    delivery = scrapy.Field()
    trading_time = scrapy.Field()
    minimum_margin = scrapy.Field()

