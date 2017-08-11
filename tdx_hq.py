# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd

TDX_DIR = r'J:\TDX\vipdoc'

EXCHANGE2TDX_CODE = {'cffex': '47',  # 47：中金所
                     'czce': '28',  # 28：郑州商品交易所
                     'dce': '29',  # 29：大连商品交易所
                     'shfe': '30',  # 30：上海期货交易所
                     }

MARKET_DIR = {'cffex': 'ds',  # 中金所
              'czce': 'ds',  # 郑州商品交易所
              'dce': 'ds',  # 大连商品交易所
              'shfe': 'ds',  # 上海期货交易所
              'sse': 'sh',  # 上海证券交易所
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


def build_tdx_hq_dir(tdx_dir=TDX_DIR, market='dce', period='day'):
    tdx_hq_dir = os.path.join(tdx_dir, MARKET_DIR[market], PERIOD_DIR[period])
    assert os.path.exists(tdx_hq_dir)
    return tdx_hq_dir


def tdx_future_hq(ticker, tdx_dir=TDX_DIR, market='dce', period='day'):
    """
    :param ticker: IL8 主力合约 IL9 期货指数 I1801
    :param tdx_dir: 通达信目录
    :param market: 交易市场
    :param period: 周期
    :return: 返回
    """

    tdx_hq_dir = build_tdx_hq_dir(tdx_dir, market, period)
    hq_filename = EXCHANGE2TDX_CODE[market] + '#' + ticker + PERIOD_EXT[period]
    hq_path = os.path.join(tdx_hq_dir, hq_filename)

    assert os.path.exists(hq_path)

    names = 'date', 'open', 'high', 'low', 'close', 'openInt', 'volume', 'comment'
    offsets = tuple(range(0, 31, 4))
    formats = 'i4', 'f4', 'f4', 'f4', 'f4', 'i4', 'i4', 'i4'

    dt = np.dtype({'names': names, 'offsets': offsets, 'formats': formats},
                  align=True)
    return pd.DataFrame(np.fromfile(hq_path, dt))


if __name__ == '__main__':
    df = tdx_future_hq('IL8', tdx_dir=r'J:\vipdoc')
    print(df.tail(100))
