# -*- coding: utf-8 -*-
import os
import redis
import requests
import pandas as pd
import datetime as dt
from utils import get_html_tree, get_congfig_handle
from settings import *


class FutureInfo(object):
    def __init__(self, market):
        self.market = market
        config = get_congfig_handle()
        base_dir = config.get('FinData', 'base_dir')

        future_dir = os.path.join(base_dir, 'future')
        if not os.path.exists(future_dir):
            os.makedirs(future_dir)
        self.future_dir = future_dir

        redis_host = config.get('Redis', 'host')
        redis_port = config.getint('Redis', 'port')

        self.ua_key = config.get('Redis', 'ua_key')
        self.conn = redis.Redis(redis_host, redis_port, decode_responses=True)

    def member_position_batch(self, ):
        pass

    def contracts_info(self, ):
        pass


class FutureDceInfo(FutureInfo):
    def __init__(self):
        super(FutureDceInfo, self).__init__('dce')

    def member_position_batch(self, ):
        params = {'memberDealPosiQuotes.variety': 'a',  # 不起作用
                  'memberDealPosiQuotes.trade_type': '0',
                  'contract.contract_id': 'all',
                  'contract.variety_id': 'a',  # 不起作用
                  'year': '2017',  # 缺省是当天
                  'month': '8',  # 起始月份为0
                  'day': '04',
                  'batchExportFlag': 'batch'}

        r = requests.post(MEMBER_POS_BATCH_DCE_URL, data=params, stream=True)
        f = open("file_path", "wb")
        for chunk in r.iter_content(chunk_size=512):
            if chunk:
                f.write(chunk)
        f.close()

    def contracts_info(self, ):
        ua = self.conn.srandmember('self.ua_key')
        resp = get_html_tree(CONTRACTS_DCE_URL, ua)

        # cols = resp.xpath('//div[@class="dataArea"]/table[@cellpadding="0"]/tr/th/text()')
        cols = ['variety', 'code', 'unit', 'change', 'begin', 'end', 'delivery']
        content = resp.xpath('//div[@class="dataArea"]/table[@cellpadding="0"]/tr/td/text()')
        contract_info = {cols[0]: content[::7],
                         cols[1]: content[1::7],
                         cols[2]: content[2::7],
                         cols[3]: content[3::7],
                         cols[4]: content[4::7],
                         cols[5]: content[5::7],
                         cols[6]: content[6::7],
                         }
        df = pd.DataFrame(contract_info)
        df.index = df[cols[1]]
        df.pop(cols[1])
        df[cols[2]] = df[cols[2]].astype('int')
        df[cols[3]] = df[cols[3]].str.strip().astype('float')
        df[cols[4]] = pd.to_datetime(df[cols[4]], errors='coerce')
        df[cols[5]] = pd.to_datetime(df[cols[5]], errors='coerce')
        df[cols[6]] = pd.to_datetime(df[cols[6]], errors='coerce')

        file_name = os.path.join(self.future_dir, self.market + CONTRACTS_FILE)
        df_future = df[~df['delivery'].isnull()]
        if os.path.exists(file_name):
            df = pd.read_hdf(file_name, 'table', columns=['update'])
            df_future['update'] = df['update']
        else:
            df_future.loc[:, 'update'] = dt.datetime(1970, 1, 1)
        df_future.to_hdf(file_name, 'table', format='table', data_columns=True, complevel=5, complib='blosc')


if __name__ == '__main__':

    # 获取大连交易所合约信息
    future_dce_info = FutureDceInfo()
    to_do = 1
    if to_do:
        future_dce_info.contracts_info()
