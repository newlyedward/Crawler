# -*- coding: utf-8 -*-
"""
get future info from file or database
"""
import os
import pandas as pd

from Quant.instrument import Instrument
from utils import LogHandler

log = LogHandler('future')


class Future(Instrument):
    future_dir = os.path.join(Instrument.base_dir, 'future')
    if not os.path.exists(future_dir):
        os.makedirs(future_dir)

    def __init__(self, market='dce', period='day'):
        super(Future, self).__init__(market, period)
        self.db = self.mongo['futures']

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
            filter_dict['end'] = {'$gt': update}

        return self.find(self.db['contract'], filter_dict)

    def option(self, market='', varietyid='', contractid='', update=''):
        filter_dict = {}

        if market:
            filter_dict['market'] = market
        if contractid:
            filter_dict = {'contractid': contractid.lower()}
        if varietyid:
            filter_dict['varietyid'] = varietyid.upper()
        if update:
            update = int(update.strftime('%Y%m%d'))
            filter_dict['end'] = {'$gt': update}

        return self.find(self.db['option'], filter_dict)


if __name__ == '__main__':
    future = Future()
    print(future.contract().tail())
    print('====================================================')
    print(future.contract(contractid='i1801').tail())
    print('====================================================')
    print(future.contract(varietyid='i').tail())
    print('====================================================')
    print(future.contract(varietyid='ii'))
    print('====================================================')
    import datetime as dt

    print('====================================================')
    print(future.contract(varietyid='i', update=dt.datetime.now()).tail())
    print('====================================================')
    print(future.contract(update=dt.datetime.now()).tail())
    print(future.contract(market='DCE', update=dt.datetime.now()).tail())
    print('====================================================')
    # print(future.variety())
    # print(future.variety(market='大连交易所'))
    # print('====================================================')
    # print(future.variety(market='大连商品交易所'))
    # print('====================================================')
    # print(future.variety(market='大连商品交易所', varietyid='i'))
    # print(future.variety(varietyid='i'))
    # print(future.variety(varietyid='ii'))
