# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd
import datetime as dt
from pymongo import MongoClient

from utils import LogHandler
from settings import *
from Quant.future import Future

log = LogHandler('tdx_hq')


class TdxFutureQuotes(Future):
    def __init__(self, market='dce', period='day'):
        super(TdxFutureQuotes, self).__init__(market, period)
        self.tdx_hq_dir = ''
        self.tdx_dir = super(TdxFutureQuotes, self).config.get('TDX', 'tdx_dir')
        self.set_period(period)

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

    @staticmethod
    def _tdx_future_day_hq(file_handler):
        names = 'datetime', 'open', 'high', 'low', 'close', 'openInt', 'volume', 'comment'
        offsets = tuple(range(0, 31, 4))
        formats = 'i4', 'f4', 'f4', 'f4', 'f4', 'i4', 'i4', 'i4'

        dt_types = np.dtype({'names': names, 'offsets': offsets, 'formats': formats}, align=True)
        hq_day_df = pd.DataFrame(np.fromfile(file_handler, dt_types))
        hq_day_df.index = pd.to_datetime(hq_day_df['datetime'].astype('str'), errors='coerce')
        hq_day_df.pop('datetime')
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

        delta = (end - update)
        factor = delta.days
        try:
            f.seek(-32 * factor, 2)
        except OSError:
            f.seek(0, 0)
            log.warning('%s trade recoders are few and factor = %d is too big.', contractid, factor)
        hq_day_df = self._tdx_future_day_hq(f)
        return hq_day_df[hq_day_df.index > update]

    def _tdx_future_min_hq(self, file_handler):
        names = 'date', 'time', 'open', 'high', 'low', 'close', 'openInt', 'volume', 'comment'
        formats = 'u2', 'u2', 'f4', 'f4', 'f4', 'f4', 'i4', 'i4', 'i4'
        offsets = (0, 2) + tuple(range(4, 31, 4))

        dt_types = np.dtype({'names': names, 'offsets': offsets, 'formats': formats}, align=True)
        hq_min_df = pd.DataFrame(np.fromfile(file_handler, dt_types))

        hq_min_df.index = hq_min_df.date.transform(self._int2date) + pd.to_timedelta(hq_min_df.time,
                                                                                     unit='m')
        hq_min_df.pop('date')
        hq_min_df.pop('time')
        return hq_min_df

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

        f = open(hq_path, "rb")

        f.seek(0, 0)
        begin = np.fromfile(f, dtype=np.int16, count=1)
        begin = self._int2date(begin)

        f.seek(-32, 2)
        end = np.fromfile(f, dtype=np.int16, count=1)
        end = self._int2date(end)

        if update < begin:
            f.seek(0, 0)
            return self._tdx_future_min_hq(f)
        elif update > end:
            return None

        k_num = 240
        if self.period == '5min':
            k_num = k_num / 5

        delta = (end - update)
        factor = delta.days * k_num

        while update < end:
            try:
                f.seek(-32 * factor, 2)
                end = np.fromfile(f, dtype=np.int16, count=1)
                f.seek(-32 * factor, 2)  # 数据读取后移位，文件指针要回到原来位置
                end = self._int2date(end)
                factor = factor * 2
            except OSError:
                f.seek(0, 0)
                log.warning('%s trade recoders are few and factor = %d is too big.', contractid, factor)
                break
            except TypeError:
                log.error('{} end date is null!'.format(contractid))
                return None

        hq_min_df = self._tdx_future_min_hq(f)
        return hq_min_df[hq_min_df.index > update]

    def to_mongodb(self):
        contract_df = self.variety()

        if not isinstance(contract_df, pd.DataFrame) or contract_df.empty:
            log.info('Data variety is empty')
            return

        if self.period == 'day':
            tdx_future_hq_func = self.tdx_future_day_hq
        elif self.period in ['1min', '5min']:
            tdx_future_hq_func = self.tdx_future_min_hq
        else:
            log.info('Wrong period -- %', self.period)
            return None

        collection = self.db['quote']

        # 存储指数和主力合约
        for varietyid in contract_df['varietyid']:
            contractid = varietyid + 'L8'  # 主力合约
            try:
                last = list(
                    collection.find({'contractid': contractid}, projection={'_id': 0, 'datetime': 1})
                        .sort('datetime', -1).limit(1))[0]['datetime']
            except:
                quote_df = tdx_future_hq_func(contractid)
            else:
                quote_df = tdx_future_hq_func(contractid, last)

            quote_df['contractid'] = contractid

            quote = quote_df.to_dict('records')
            if not quote:
                log.info('Don not get new quotes of %s' % contractid)
                continue

            result = collection.insert_many(quote)
            log.debug('Insert %d quotes of variety %s' % (len(result.inserted_ids), contractid))

    def _to_hdf(self, contractid, future_hq_dir, tdx_future_hq_func):
        file_string = os.path.join(future_hq_dir, contractid.lower() + '.' + self.period)
        try:
            last = pd.read_hdf(file_string, 'table', start=-1)
            update = list(last.index)[0]
        except:
            quote_df = tdx_future_hq_func(contractid)
        else:
            quote_df = tdx_future_hq_func(contractid, update)

        if isinstance(quote_df, pd.DataFrame) and not quote_df.empty:
            quote_df.to_hdf(file_string, 'table', format='table', append=True, complevel=5, complib='blosc')

    def to_hdf(self, update=''):
        contract_df = self.variety()

        if not isinstance(contract_df, pd.DataFrame) or contract_df.empty:
            log.info('Data variety is empty')
            return

        future_hq_dir = os.path.join(self.future_dir, 'hq', self.period)
        if not os.path.exists(future_hq_dir):
            os.makedirs(future_hq_dir)

        if self.period == 'day':
            tdx_future_hq_func = self.tdx_future_day_hq
        elif self.period in ['1min', '5min']:
            tdx_future_hq_func = self.tdx_future_min_hq
        else:
            log.info('Wrong period -- %', self.period)
            return None

        # get varietyid list from mongodb and construct index an continue contacts
        # 存储指数和主力合约
        for varietyid in contract_df['varietyid']:
            contractid = varietyid + 'l8'  # 主力合约
            self._to_hdf(contractid, future_hq_dir, tdx_future_hq_func)

            contractid = varietyid + 'l9'  # 主力合约
            self._to_hdf(contractid, future_hq_dir, tdx_future_hq_func)

        if update:
            contract_df = self.contract(update=update)
        else:
            contract_df = self.contract()

        if contract_df.empty:
            log.info('Data variety is empty')
            return

        for contractid in contract_df['contractid']:
            self._to_hdf(contractid, future_hq_dir, tdx_future_hq_func)

    @staticmethod
    def _int2date(x):
        year = int(x / 2048) + 2004
        month = int(x % 2048 / 100)
        day = x % 2048 % 100
        return dt.datetime(year, month, day)


if __name__ == '__main__':
    dce_tdx_hq = TdxFutureQuotes()

    # to_do = 1
    # if to_do:
    #     dce_tdx_hq.save_future_hq()

    # df = dce_tdx_hq.tdx_future_day_hq('il8')
    # file_string = r'J:\h5\future\dce\day\JL8.h5'
    # df.to_hdf(file_string, 'table', format='table', append=True, complevel=5, complib='blosc')
    # print(df.head())
    # print(df.tail())

    # 存储dce day和1min数据
    # dce_tdx_hq.to_hdf(update=dt.datetime.now())
    dce_tdx_hq.set_period('1min')
    # dce_tdx_hq.to_hdf()
    dce_tdx_hq.to_hdf(update=dt.datetime.now())
