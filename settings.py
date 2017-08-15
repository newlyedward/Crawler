# -*- coding: utf-8 -*-
base_dir = "J:\h5"

MARKET_LIST = ('cffe',  # 中金所
               'zcce',  # 郑州商品交易所
               'dlce',  # 大连商品交易所
               'shfe',  # 上海期货交易所
               'shse',  # 上海证券交易所
               'szse',  # 深圳证券交易所
               )

# --------------------- TDX ------------------------------------------

TDX_DIR = r'J:\TDX'

EXCHANGE2TDX_CODE = {MARKET_LIST[0]: '47',  # 47：中金所
                     MARKET_LIST[1]: '28',  # 28：郑州商品交易所
                     MARKET_LIST[2]: '29',  # 29：大连商品交易所
                     MARKET_LIST[3]: '30',  # 30：上海期货交易所
                     }

MARKET_DIR = {'cffe': 'ds',  # 中金所
              'zcce': 'ds',  # 郑州商品交易所
              'dlce': 'ds',  # 大连商品交易所
              'shfe': 'ds',  # 上海期货交易所
              'shse': 'sh',  # 上海证券交易所
              'szse': 'sz',  # 深圳证券交易所
              }

PERIOD_DIR = {'day': 'lday',  # 日线
              '5min': 'fzline',  # 5分钟
              '1min': 'minline'
              }

PERIOD_EXT = {'day': '.day',  # 日线
              '5min': '.lc5',  # 5分钟
              '1min': '.lc1'
              }