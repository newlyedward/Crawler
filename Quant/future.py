# -*- coding: utf-8 -*-
"""
get future info from file or database
"""
import os
import pandas as pd

from .instrument import Instrument
from utils import LogHandler

log = LogHandler('future')


class Future(Instrument):
    future_dir = os.path.join(Instrument.base_dir, 'future')
    if not os.path.exists(future_dir):
        os.makedirs(future_dir)

    def __init__(self, market='dce', period='day'):
        super(Future, self).__init__(market, period)
        self.db = self.mongo['futures']

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

    def variety(self, market='', varietyid=''):
        filter_dict = {}
        if market:
            filter_dict['market'] = market

        if varietyid:
            filter_dict['varietyid'] = varietyid.upper()

        return self.find(self.db['variety'], filter_dict)

    def contract(self, market='', varietyid='', contractid='', update=''):
        filter_dict = {}

        if market:
            filter_dict['market'] = market
        if contractid:
            filter_dict = {'contractid': contractid.lower()}
        if varietyid:
            filter_dict['varietyid'] = varietyid.upper()
        if update:
            update = int(update.strftime('%Y%m%d'))
            filter_dict = {'end': {'$gt': update}}

        return self.find(self.db['contract'], filter_dict)


if __name__ == '__main__':
    future = Future()
    # print(future.contract().tail())
    # print(future.contract(contractid='i1801').tail())
    # print(future.contract(varietyid='i').tail())
    # print(future.contract(varietyid='ii'))
    import datetime as dt

    # print(future.contract(varietyid='i', update=dt.datetime.now()))
    # print(future.contract(update=dt.datetime.now()))
    # print(future.variety())
    print(future.variety(market='大连交易所'))
    print('====================================================')
    print(future.variety(market='大连商品交易所'))
    print('====================================================')
    print(future.variety(market='大连商品交易所', varietyid='i'))
    # print(future.variety(varietyid='i'))
    # print(future.variety(varietyid='ii'))
