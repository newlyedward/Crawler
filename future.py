# -*- coding: utf-8 -*-
"""
get future info from file or database
"""
import os
import pandas as pd

from instrument import Instrument
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

    def variety(self, varietyid=''):
        if varietyid:
            return self.find(self.db['variety'], {'varietyid': varietyid.upper()})
        else:
            return self.find(self.db['variety'], {})

    def contract(self, varietyid='', contractid='', update=''):
        filter_dict = {}
        update = int(update.strftime('%Y%m%d'))
        if varietyid:
            filter_dict = {'varietyid': varietyid.upper()}
            if update:
                filter_dict['end'] = {'$gt': update}
            return self.find(self.db['contract'], filter_dict)
        elif update:
            filter_dict = {'end': {'$gt': update}}
        elif contractid:
            filter_dict = {'contractid': contractid.lower()}

        return self.find(self.db['contract'], filter_dict)


if __name__ == '__main__':
    future = Future()
    # print(future.contract().tail())
    # print(future.contract(contractid='i1801').tail())
    # print(future.contract(varietyid='i').tail())
    # print(future.contract(varietyid='ii'))
    import datetime as dt

    print(future.contract(varietyid='i', update=dt.datetime.now()))
    print(future.contract(update=dt.datetime.now()))
    # print(future.variety())
    # print(future.variety('i'))
    # print(future.variety('ii'))
