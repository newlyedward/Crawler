# -*- coding: utf-8 -*-
"""
get financial instrument info from file or database
"""
import os
import numpy as np
import pandas as pd
import datetime as dt
from pymongo import MongoClient

from utils import get_congfig_handle, LogHandler
from settings import *


# log = LogHandler('instrument')


class Instrument(object):
    config = get_congfig_handle()
    mongo_host = config.get('Mongo', 'host')
    mongo_port = config.getint('Mongo', 'port')
    mongo = MongoClient(mongo_host, mongo_port)

    base_dir = config.get('FinData', 'base_dir')
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    def __init__(self, market, period='day'):
        self.period = period.lower()
        self.market = market.lower()

    @staticmethod
    def find(collection, filter_dict):
        if filter_dict:
            records = collection.find(filter_dict)
        else:
            records = collection.find()

        df = pd.DataFrame(list(records))

        if df.empty:
            return None
        else:
            del df['_id']
            return df

    def bar(self, code, asset, start_date='', end_date='', ktype='day', adj=None):
        """
        :param code: 证券代码，股票ETF，期货，期权，港股
        :param start_date: 开始日期
        :param end_date: 结束日期
        :param ktype: 周期，支持1分钟:1min，日:day
        :param asset: 资产类型，B:债券, E:股票, F:期货, O:期权
        :param adj: 复权类型, None:不复权, qfq:前复权, hfq:后复权
        :return: DataFrame
        """
        df = pd.DataFrame()
        # filterstring = ''
        filestring = os.path.join(self.base_dir, asset.lower(), 'hq', ktype.lower(), code.lower() + '.' + ktype.lower())

        if not os.path.exists(filestring):
            return df

        if start_date and end_date:
            filterstring = "index>=Timestamp('{}') & index<=Timestamp('{}')".format(start_date, end_date)
        elif start_date:
            filterstring = "index>=Timestamp('{}')".format(start_date)
        elif end_date:
            filterstring = "index<=Timestamp('{}')".format(end_date)
        else:
            filterstring = ''

        if filterstring:
            df = pd.read_hdf(filestring, 'table', where=filterstring)
        else:
            df = pd.read_hdf(filestring, 'table')
        return df

    def __del__(self):
        self.mongo.close()


if __name__ == '__main__':
    instrument = Instrument(market='')
    df = instrument.bar('ml8', asset='future')
    print('==================full data================')
    print(df.head())
    print('==================start_date================')
    df = instrument.bar('ml8', asset='future', start_date='20170915')
    print(df.head())
    print('==================end_date================')
    df = instrument.bar('ml8', asset='future', end_date='20170915')
    print(df.tail())
    print('==================start and end================')
    df = instrument.bar('ml8', asset='future', start_date='20170915', end_date='20170922')
    print(df)
