# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd
from datetime import datetime

from settings import *


def tdx_future_basic(tdx_dir=TDX_DIR):
    file_name = os.path.join(tdx_dir, 'T0002\hq_cache\code2name.ini')
    df = pd.read_csv(file_name,
                     index_col=0, names=['code', 'name', 'market'], header=None,
                     encoding='gb2312', usecols=[0, 1, 2])
    df.loc[df['market'] == 'CZ', 'market'] = 'cffex'
    df.loc[df['market'] == 'QD', 'market'] = 'dce'
    df.loc[df['market'] == 'QZ', 'market'] = 'czce'
    df.loc[df['market'] == 'QS', 'market'] = 'shfe'
    return df


def build_tdx_hq_dir(tdx_dir=TDX_DIR, market='dlce', period='day'):
    tdx_hq_dir = os.path.join(tdx_dir, 'vipdoc', MARKET_DIR[market], PERIOD_DIR[period])
    assert os.path.exists(tdx_hq_dir)
    return tdx_hq_dir


def int2date(x):
    return datetime(int(x / 10000), int(x % 10000 / 100), x % 100)


def int2time(x):
    year = int(x / 2048) + 2004
    month = int(x % 2048 / 100)
    day = x % 2048 % 100
    return datetime(year, month, day)


def tdx_future_day_hq(ticker, tdx_dir=TDX_DIR, market='dlce', period='day'):
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

    dt = np.dtype({'names': names, 'offsets': offsets, 'formats': formats}, align=True)
    hq_day_df = pd.DataFrame(np.fromfile(hq_path, dt))
    hq_day_df.index = pd.to_datetime(hq_day_df.date.astype('str'), errors='coerce')
    hq_day_df.pop('date')
    return hq_day_df


def tdx_future_min_hq(ticker, tdx_dir=TDX_DIR, market='dlce', period='5min'):
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

    # f = open("temp", "rb")  # reopen the file
    # f.seek(256, os.SEEK_SET)  # seek
    #
    # x = np.fromfile(f, dtype=np.int)  # read the data into numpy

    names = 'date', 'time', 'open', 'high', 'low', 'close', 'openInt', 'volume', 'comment'
    formats = 'u2', 'u2', 'f4', 'f4', 'f4', 'f4', 'i4', 'i4', 'i4'
    offsets = (0, 2) + tuple(range(4, 31, 4))

    dt = np.dtype({'names': names, 'offsets': offsets, 'formats': formats}, align=True)
    hq_min_df = pd.DataFrame(np.fromfile(hq_path, dt))
    hq_min_df.index = hq_min_df.date.transform(int2time) + pd.to_timedelta(hq_min_df.time, unit='m')
    hq_min_df.pop('date')
    hq_min_df.pop('time')
    return hq_min_df


def save_future_hq(tdx_dir=TDX_DIR, market='dce', period='day'):
    tdx_fdhq_dir = build_tdx_hq_dir(tdx_dir, market, period)
    pass


if __name__ == '__main__':
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    future_dir = os.path.join(base_dir, 'future')
    if not os.path.exists(future_dir):
        os.mkdir(future_dir)

    todo = 1
    if todo:
        df = tdx_future_basic()
        file_name = os.path.join(future_dir, 'future_basic.h5')
        df.to_hdf(file_name, 'table', complevel=5, complib='blosc')

    # todo = 1
    # if todo:
    #     save_future_hq(tdx_dir=TDX_DIR, market='dce', period='5min')

    # df = tdx_future_day_hq('ML8', period='day')
    # df.to_hdf('ML8.day.h5', 'table')
    # print(df.tail(10))
    #
    # df = tdx_future_min_hq('ML8', period='1min')
    # print(df.tail(10))
    # df.to_hdf('ML8.lc1.h5', 'table')

    # print(tdx_future_basic())
