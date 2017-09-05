# -*- coding: utf-8 -*-
MARKET_LIST = ('cffex',  # 中金所
               'czce',  # 郑州商品交易所
               'dce',  # 大连商品交易所
               'shfe',  # 上海期货交易所
               'shse',  # 上海证券交易所
               'szse',  # 深圳证券交易所
               )
# --------------------- TDX ------------------------------------------

EXCHANGE2TDX_CODE = {MARKET_LIST[0]: '47',  # 47：中金所
                     MARKET_LIST[1]: '28',  # 28：郑州商品交易所
                     MARKET_LIST[2]: '29',  # 29：大连商品交易所
                     MARKET_LIST[3]: '30',  # 30：上海期货交易所
                     }

MARKET_DIR = {'cffex': 'ds',  # 中金所
              'czce': 'ds',  # 郑州商品交易所
              'dce': 'ds',  # 大连商品交易所
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

# --------------------- dce ------------------------------------------
CONTRACTS_FILE = '_contracts.h5'
MEMBER_POS_BATCH_DIR = 'memberpos'

CONTRACTS_DCE_URL = 'http://www.dce.com.cn/publicweb/businessguidelines/queryContractInfo.html'
MEMBER_POS_BATCH_DCE_URL = 'http://www.dce.com.cn/publicweb/quotesdata/exportMemberDealPosiQuotesBatchData.html'

