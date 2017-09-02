# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd
import datetime as dt

from utils import get_congfig_handle, LogHandler
from settings import *

log = LogHandler('tdx_hq')


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


def _build_tdx_hq_dir(tdx_dir, market='dlce', period='day'):
    tdx_hq_dir = os.path.join(tdx_dir, 'vipdoc', MARKET_DIR[market], PERIOD_DIR[period])
    assert os.path.exists(tdx_hq_dir)
    return tdx_hq_dir


# def int2date(x):
#     return dt.datetime(int(x / 10000), int(x % 10000 / 100), x % 100)


def _int2date(x):
    year = int(x / 2048) + 2004
    month = int(x % 2048 / 100)
    day = x % 2048 % 100
    return dt.datetime(year, month, day)


def _tdx_future_day_hq(file_handler):
    names = 'date', 'open', 'high', 'low', 'close', 'openInt', 'volume', 'comment'
    offsets = tuple(range(0, 31, 4))
    formats = 'i4', 'f4', 'f4', 'f4', 'f4', 'i4', 'i4', 'i4'

    dt_types = np.dtype({'names': names, 'offsets': offsets, 'formats': formats}, align=True)
    hq_day_df = pd.DataFrame(np.fromfile(file_handler, dt_types))
    hq_day_df.index = pd.to_datetime(hq_day_df.date.astype('str'), errors='coerce')
    hq_day_df.pop('date')
    return hq_day_df


def tdx_future_day_hq(code, tdx_dir, market='dlce', period='day', update=dt.datetime(1970, 1, 1)):
    """
    :param update: 最后更新日期
    :param code: IL8 主力合约 IL9 期货指数 I1801
    :param tdx_dir: 通达信目录
    :param market: 交易市场
    :param period: 周期
    :return: 返回
    """

    tdx_hq_dir = _build_tdx_hq_dir(tdx_dir, market, period)
    hq_filename = EXCHANGE2TDX_CODE[market] + '#' + code + PERIOD_EXT[period]
    hq_path = os.path.join(tdx_hq_dir, hq_filename)

    if not os.path.exists(hq_path):
        return None

    f = open(hq_path, "rb")

    f.seek(0, 0)
    begin = np.fromfile(f, dtype=np.int32, count=1)
    begin = dt.datetime.strptime(begin.astype(str)[0], '%Y%m%d')

    f.seek(-32, 2)
    end = np.fromfile(f, dtype=np.int32, count=1)
    end = dt.datetime.strptime(end.astype(str)[0], '%Y%m%d')

    if update < begin:
        f.seek(0, 0)
        return _tdx_future_day_hq(f)
    elif update > end:
        return None
    else:
        delta = (end - update)
        factor = delta.days
        try:
            f.seek(-32 * factor, 2)
        except OSError:
            f.seek(0, 0)
            log.warning('%s trade recoders are few and factor = %d is too big.', code, factor)
        hq_day_df = _tdx_future_day_hq(f)
        return hq_day_df[hq_day_df.index > update]


def tdx_future_min_hq(code, tdx_dir, market='dlce', period='5min', update=dt.datetime(1970, 1, 1)):
    """
    :param code: IL8 主力合约 IL9 期货指数 I1801
    :param tdx_dir: 通达信目录
    :param market: 交易市场
    :param period: 周期
    :return: 返回
    """

    tdx_hq_dir = _build_tdx_hq_dir(tdx_dir, market, period)
    hq_filename = EXCHANGE2TDX_CODE[market] + '#' + code + PERIOD_EXT[period]
    hq_path = os.path.join(tdx_hq_dir, hq_filename)

    if not os.path.exists(hq_path):
        return None

    names = 'date', 'time', 'open', 'high', 'low', 'close', 'openInt', 'volume', 'comment'
    formats = 'u2', 'u2', 'f4', 'f4', 'f4', 'f4', 'i4', 'i4', 'i4'
    offsets = (0, 2) + tuple(range(4, 31, 4))

    dt_types = np.dtype({'names': names, 'offsets': offsets, 'formats': formats}, align=True)
    hq_min_df = pd.DataFrame(np.fromfile(hq_path, dt_types))
    hq_min_df.index = hq_min_df.date.transform(_int2date) + pd.to_timedelta(hq_min_df.time, unit='m')
    hq_min_df.pop('date')
    hq_min_df.pop('time')
    return hq_min_df


def save_future_hq(tdx_dir, market='dlce', period='day'):
    future_hq_dir = os.path.join(future_dir, market.lower(), period.lower())
    if not os.path.exists(future_hq_dir):
        os.makedirs(future_hq_dir)

    # dt.datetime.fromtimestamp(os.path.getctime(future_hq_dir))

    if period == 'day':
        tdx_future_hq_func = tdx_future_day_hq
    elif period in ['1min', '5min']:
        tdx_future_hq_func = tdx_future_min_hq
    else:
        log.info('Wrong period -- %', period)
        return None

    # read code list
    file_name = os.path.join(future_dir, 'dlse_contracts.h5')

    # 整体全部读出，因为还不知道如何修改h5文件中单独的一列
    # futures = pd.read_hdf(file_name, 'table', columns=['update', 'end', 'update'])
    contracts = pd.read_hdf(file_name, 'table')
    contracts = contracts[contracts['end'] > contracts['update']]

    for code, update in zip(contracts.index, contracts['update']):
        log.info("======= get %s %s hq =======" % (code, period))
        file_string = os.path.join(future_hq_dir, code + '.h5')

        # if os.path.exists(file_string):
        #     pass
        # else:
        df = tdx_future_hq_func(code, tdx_dir, market, period, update)
        if not isinstance(df, pd.DataFrame) or len(df) == 0:
            log.info("======= There is no %s %s hq =======" % (code, period))
            continue
        df.to_hdf(file_string, 'table', format='table', append=True, complevel=5, complib='blosc')
        contracts.loc[code, 'update'] = df.index.max()

    contracts.to_hdf(file_name, 'table', format='table', data_columns=True, complevel=5, complib='blosc')


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

    to_do = 0
    if to_do:
        save_future_hq(tdx_dir, market='dlce', period='day')

    df = tdx_future_day_hq('JL8', tdx_dir, period='day')
    file_string = r'J:\h5\future\dlce\day\JL8.h5'
    df.to_hdf(file_string, 'table', format='table', append=True, complevel=5, complib='blosc')
    print(df.head())
    print(df.tail())

    # df.to_hdf('ML8.day.h5', 'table')
    # print(df.tail(10))
    #
    # df = tdx_future_min_hq('ML8', period='1min')
    # print(df.tail(10))
    # df.to_hdf('ML8.lc1.h5', 'table')

    # print(tdx_future_basic())
