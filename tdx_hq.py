# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd
import datetime as dt

from utils import get_congfig_handle, get_congfig_file
from settings import *


def tdx_future_basic(tdx_dir):
    file_name = os.path.join(tdx_dir, 'T0002\hq_cache\code2name.ini')
    df = pd.read_csv(file_name,
                     index_col=0, names=['code', 'name', 'market'], header=None,
                     encoding='gb2312', usecols=[0, 1, 2])
    df.loc[df['market'] == 'CZ', 'market'] = 'cffex'
    df.loc[df['market'] == 'QD', 'market'] = 'dce'
    df.loc[df['market'] == 'QZ', 'market'] = 'czce'
    df.loc[df['market'] == 'QS', 'market'] = 'shfe'
    return df


def build_tdx_hq_dir(tdx_dir, market='dlce', period='day'):
    tdx_hq_dir = os.path.join(tdx_dir, 'vipdoc', MARKET_DIR[market], PERIOD_DIR[period])
    assert os.path.exists(tdx_hq_dir)
    return tdx_hq_dir


# def int2date(x):
#     return dt.datetime(int(x / 10000), int(x % 10000 / 100), x % 100)


def int2date(x):
    year = int(x / 2048) + 2004
    month = int(x % 2048 / 100)
    day = x % 2048 % 100
    return dt.datetime(year, month, day)


def tdx_future_day_hq(code, tdx_dir, market='dlce', period='day'):
    """
    :param code: IL8 主力合约 IL9 期货指数 I1801
    :param tdx_dir: 通达信目录
    :param market: 交易市场
    :param period: 周期
    :return: 返回
    """

    tdx_hq_dir = build_tdx_hq_dir(tdx_dir, market, period)
    hq_filename = EXCHANGE2TDX_CODE[market] + '#' + code + PERIOD_EXT[period]
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


def tdx_future_min_hq(code, tdx_dir, market='dlce', period='5min'):
    """
    :param code: IL8 主力合约 IL9 期货指数 I1801
    :param tdx_dir: 通达信目录
    :param market: 交易市场
    :param period: 周期
    :return: 返回
    """

    tdx_hq_dir = build_tdx_hq_dir(tdx_dir, market, period)
    hq_filename = EXCHANGE2TDX_CODE[market] + '#' + code + PERIOD_EXT[period]
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
    hq_min_df.index = hq_min_df.date.transform(int2date) + pd.to_timedelta(hq_min_df.time, unit='m')
    hq_min_df.pop('date')
    hq_min_df.pop('time')
    return hq_min_df


def save_future_hq(tdx_dir, market='dlce', period='day'):
    config = get_congfig_handle()
    last_update = config.get(market.upper(), period.lower() + '_update')
    date_format = '%Y-%m-%d'

    if last_update:
        last_update = dt.datetime.strptime(last_update, date_format)
    else:
        print("never download %s %s hq", market, period)
        last_update = dt.datetime(1970, 1, 1)

    # put different hq in different market
    future_mkt_dir = os.path.join(future_dir, market.lower(), period.lower())
    if not os.path.exists(future_mkt_dir):
        os.makedirs(future_mkt_dir)

    tdx_fdhq_dir = build_tdx_hq_dir(tdx_dir, market, period)
    assert os.path.exists(tdx_fdhq_dir)

    # if period == 'day':
    #     tdx_future_hq_func = tdx_future_day_hq
    # elif period in ['1min', '5min']:
    #     tdx_future_hq_func = tdx_future_min_hq
    # else:
    #     print('Wrong period -- %', period)
    #     return None

    # # read code list
    # file_name = os.path.join(future_dir, 'dlse_contracts.h5')
    #
    # if last_update:
    #     futures = pd.read_hdf(file_name, 'table', columns=['code'], where='end > dt.datetime.now()')
    # else:
    #     futures = pd.read_hdf(file_name, 'table', columns=['code'])
    #
    # for code in futures.code:
    #     print("======= get %s %s hq =======", code, period)
    #     file_string = os.path.join(tdx_fdhq_dir, code)
    #
    #     if os.path.exists(file_string):
    #         pass
    #     else:
    #         df = tdx_future_hq_func(code, tdx_dir, market, period)
    #         if df:
    #             print("======= There is no %s %s hq =======", code, period)
    #             continue
    #         df_future.to_hdf(file_name, 'table', format='table', data_columns=True, complevel=5, complib='blosc')

    last_update = dt.datetime.now().strftime(date_format)
    config.set(market.upper(), period.lower() + '_update', last_update)
    fp = get_congfig_file()
    config.write(fp)
    fp.close()


if __name__ == '__main__':
    config = get_congfig_handle()
    base_dir = config.get('FinData', 'base_dir')
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    future_dir = os.path.join(base_dir, 'future')
    if not os.path.exists(future_dir):
        os.mkdir(future_dir)

    tdx_dir = config.get('TDX', 'tdx_dir')

    to_do = 0
    if to_do:
        df = tdx_future_basic(tdx_dir)
        file_name = os.path.join(future_dir, 'future_basic.h5')
        df.to_hdf(file_name, 'table', complevel=5, complib='blosc')

    to_do = 1
    if to_do:
        save_future_hq(tdx_dir, market='dlce', period='5min')

        # df = tdx_future_day_hq('ML8', period='day')
        # df.to_hdf('ML8.day.h5', 'table')
        # print(df.tail(10))
        #
        # df = tdx_future_min_hq('ML8', period='1min')
        # print(df.tail(10))
        # df.to_hdf('ML8.lc1.h5', 'table')

        # print(tdx_future_basic())
