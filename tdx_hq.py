# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd
import datetime as dt
from pymongo import MongoClient

from utils import get_congfig_handle, LogHandler
from settings import *

log = LogHandler('tdx_hq')


class TdxQuotes(object):
    def __init__(self, market='dce', period='day'):
        self.period = ''
        self.tdx_hq_dir = ''
        self.set_period(period)
        self.market = market.lower()

        config = get_congfig_handle()

        self.tdx_dir = config.get('TDX', 'tdx_dir')

        mongo_host = config.get('Mongo', 'host')
        mongo_port = config.getint('Mongo', 'port')
        self.mongo = MongoClient(mongo_host, mongo_port)

        base_dir = config.get('FinData', 'base_dir')
        self.future_dir = os.path.join(base_dir, 'future')
        if not os.path.exists(self.future_dir):
            os.makedirs(self.future_dir)

    def set_period(self, period):
        self.period = period.lower()
        self.tdx_hq_dir = os.path.join(self.tdx_dir, 'vipdoc', MARKET_DIR[self.market], PERIOD_DIR[self.period])
        assert os.path.exists(self.tdx_hq_dir)

    def set_market(self, market):
        self.market = market.lower()
        self.tdx_hq_dir = os.path.join(self.tdx_dir, 'vipdoc', MARKET_DIR[self.market], PERIOD_DIR[self.period])
        assert os.path.exists(self.tdx_hq_dir)

    def tdx_future_basic(self):
        file_name = os.path.join(self.tdx_dir, 'T0002\hq_cache\code2name.ini')
        df = pd.read_csv(file_name,
                         index_col=0, names=['code', 'name', 'market'], header=None,
                         encoding='gb2312', usecols=[0, 1, 2])
        df.loc[df['market'] == 'CZ', 'market'] = 'cffex'
        df.loc[df['market'] == 'QD', 'market'] = 'dce'
        df.loc[df['market'] == 'QZ', 'market'] = 'czce'
        df.loc[df['market'] == 'QS', 'market'] = 'shfe'
        return df

    # def int2date(x):
    #     return dt.datetime(int(x / 10000), int(x % 10000 / 100), x % 100)

    def _int2date(self, x):
        year = int(x / 2048) + 2004
        month = int(x % 2048 / 100)
        day = x % 2048 % 100
        return dt.datetime(year, month, day)

    def _tdx_future_day_hq(self, file_handler):
        names = 'date', 'open', 'high', 'low', 'close', 'openInt', 'volume', 'comment'
        offsets = tuple(range(0, 31, 4))
        formats = 'i4', 'f4', 'f4', 'f4', 'f4', 'i4', 'i4', 'i4'

        dt_types = np.dtype({'names': names, 'offsets': offsets, 'formats': formats}, align=True)
        hq_day_df = pd.DataFrame(np.fromfile(file_handler, dt_types))
        hq_day_df.index = pd.to_datetime(hq_day_df.date.astype('str'), errors='coerce')
        hq_day_df.pop('date')
        return hq_day_df

    def tdx_future_day_hq(self, contractid, update=dt.datetime(1970, 1, 1)):
        """
        :param update: 最后更新日期
        :param contractid: IL8 主力合约 IL9 期货指数 I1801
        :param tdx_dir: 通达信目录
        :param market: 交易市场
        :param period: 周期
        :return: 返回
        """

        hq_filename = EXCHANGE2TDX_CODE[self.market] + '#' + contractid.upper() + PERIOD_EXT[self.period]
        hq_path = os.path.join(self.tdx_hq_dir, hq_filename)

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
            return self._tdx_future_day_hq(f)
        elif update > end:
            return None
        else:
            delta = (end - update)
            factor = delta.days
            try:
                f.seek(-32 * factor, 2)
            except OSError:
                f.seek(0, 0)
                log.warning('%s trade recoders are few and factor = %d is too big.', contractid, factor)
            hq_day_df = self._tdx_future_day_hq(f)
            return hq_day_df[hq_day_df.index > update]

    def tdx_future_min_hq(self, contractid, update=dt.datetime(1970, 1, 1)):
        """
        :param contractid: IL8 主力合约 IL9 期货指数 I1801
        :param tdx_dir: 通达信目录
        :param market: 交易市场
        :param period: 周期
        :return: 返回
        """

        hq_filename = EXCHANGE2TDX_CODE[self.market] + '#' + contractid.upper() + PERIOD_EXT[self.period]
        hq_path = os.path.join(self.tdx_hq_dir, hq_filename)

        if not os.path.exists(hq_path):
            return None

        names = 'date', 'time', 'open', 'high', 'low', 'close', 'openInt', 'volume', 'comment'
        formats = 'u2', 'u2', 'f4', 'f4', 'f4', 'f4', 'i4', 'i4', 'i4'
        offsets = (0, 2) + tuple(range(4, 31, 4))

        dt_types = np.dtype({'names': names, 'offsets': offsets, 'formats': formats}, align=True)
        hq_min_df = pd.DataFrame(np.fromfile(hq_path, dt_types))
        hq_min_df.index = hq_min_df.date.transform(self._int2date) + pd.to_timedelta(hq_min_df.time, unit='m')
        hq_min_df.pop('date')
        hq_min_df.pop('time')
        return hq_min_df

    def save_future_hq(self):
        future_hq_dir = os.path.join(self.future_dir, self.market, self.period)
        if not os.path.exists(future_hq_dir):
            os.makedirs(future_hq_dir)

        # dt.datetime.fromtimestamp(os.path.getctime(future_hq_dir))

        if self.period == 'day':
            tdx_future_hq_func = self.tdx_future_day_hq
        elif self.period in ['1min', '5min']:
            tdx_future_hq_func = self.tdx_future_min_hq
        else:
            log.info('Wrong period -- %', self.period)
            return None

        # read contractid list
        file_name = os.path.join(self.future_dir, 'dce_contracts.h5')

        # 整体全部读出，因为还不知道如何修改h5文件中单独的一列
        # futures = pd.read_hdf(file_name, 'table', columns=['update', 'end', 'update'])
        contracts = pd.read_hdf(file_name, 'table')
        contracts = contracts[contracts['end'] > contracts['update']]

        for contractid, update in zip(contracts.index, contracts['update']):
            log.info("======= get %s %s hq =======" % (contractid, self.period))
            file_string = os.path.join(future_hq_dir, contractid + '.h5')

            # if os.path.exists(file_string):
            #     pass
            # else:
            df = tdx_future_hq_func(contractid, update)
            if not isinstance(df, pd.DataFrame) or len(df) == 0:
                log.info("======= There is no %s %s hq =======" % (contractid, self.period))
                continue
            df.to_hdf(file_string, 'table', format='table', append=True, complevel=5, complib='blosc')
            contracts.loc[contractid, 'update'] = df.index.max()

        contracts.to_hdf(file_name, 'table', format='table', data_columns=True, complevel=5, complib='blosc')


if __name__ == '__main__':

    dce_tdx_hq = TdxQuotes()

    to_do = 1
    if to_do:
        dce_tdx_hq.save_future_hq()

    df = dce_tdx_hq.tdx_future_day_hq('il8',)
    file_string = r'J:\h5\future\dce\day\JL8.h5'
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
