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
    def find(collection, item_id, id_text):
        if item_id:
            records = collection.find({id_text: item_id})
        else:
            records = collection.find()

        df = pd.DataFrame(list(records))

        if df.empty:
            return None
        else:
            del df['_id']
            return df

    def variety(self, varietyid=''):
        return self.find(self.db['variety'], varietyid.upper(), 'varietyid')

    def contract(self, varietyid='', contractid=''):
        if varietyid:
            return self.find(self.db['contract'], varietyid.upper(), 'varietyid')
            # 需要返回多个
        else:
            return self.find(self.db['contract'], contractid.lower(), 'contractid')


if __name__ == '__main__':
    future = Future()
    # print(future.contract().tail())
    # print(future.contract(contractid='i1801').tail())
    # print(future.contract(varietyid='i').tail())
    # print(future.contract(varietyid='ii'))

    print(future.variety())
    print(future.variety('i'))
    print(future.variety('ii'))
