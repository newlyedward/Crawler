# -*- coding: utf-8 -*-
"""
get info from web
"""
import redis
import requests
import pandas as pd
import datetime as dt
from pymongo import MongoClient
from utils import get_congfig_handle, LogHandler
from settings import *

log = LogHandler('future_dce_info')


class FutureInfo(object):
    def __init__(self, market):
        self.market = market
        config = get_congfig_handle()

        mongo_host = config.get('Mongo', 'host')
        mongo_port = config.getint('Mongo', 'port')
        self.mongo = MongoClient(mongo_host, mongo_port)

        redis_host = config.get('Redis', 'host')
        redis_port = config.getint('Redis', 'port')

        self.ua_key = config.get('Redis', 'ua_key')
        self.conn = redis.Redis(redis_host, redis_port, decode_responses=True)

    def __del__(self):
        self.mongo.close()

    def member_position_batch(self, ):
        pass

    def save_contracts(self):
        pass

    def contracts(self, varietyid):
        pass

    def varieties(self):
        pass


class FutureDceInfo(FutureInfo):
    def __init__(self):
        super(FutureDceInfo, self).__init__('dce')

    def member_position_batch(self):
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

    def save_contracts(self):
        # get varietyid from database
        db = self.mongo['futures']
        records = db['variety'].find(projection=['varietyid', 'delivery_months'])

        if records.count() < 1:
            log.info('There is no varieties in database')
            return

        for record in records:
            varietyid = record['varietyid']

            months_num = len(record['delivery_months'])
            today = int(dt.datetime.now().strftime('%Y%m%d'))
            contracts_num = db['contract'].find({'varietyid': varietyid, 'end': {'$gt': today}}).count()

            # 如果合约存在，不更新合约， 不对当月是否有合约交割进行判断
            if months_num <= contracts_num:
                log.info('%s contracts all are existed' % varietyid)
                continue

            df = self.contracts(varietyid.lower())

            try:
                last = list(
                    db['contract'].find({'varietyid': varietyid}, projection={'_id': 0, 'begin': 1})
                        .sort('begin', -1).limit(1))[0]['begin']
            except:
                update_df = df
            else:
                update_df = df[df['begin'] > last]

            if update_df.empty:
                continue

            contracts = update_df[update_df['contractid'].str.match('\w{1,2}\d{4}$')].to_dict('records')
            if not contracts:
                log.info('Don not get new records of variety %s' % varietyid)
                continue

            result = db['contract'].insert_many(contracts)
            log.info('Insert %d records of variety %s' % (len(result.inserted_ids), varietyid))

            # 期权暂时不处理
            # options = update_df[update_df['contractid'].str.match('\w{1,2}\d{4}-\w-\d+')].to_dict('records')
            # if not options:
            #     continue
            #
            # result = db['option'].insert_many(options)
            # log.info('Insert %d records of variety %s' % (len(result.inserted_ids), varietyid))

    def contracts(self, varietyid):
        # 提取数据
        dfs = pd.read_html(CONTRACTS_DCE_URL + varietyid, header=0, skiprows=0)
        # {'交易单位': 10,                    # int
        #  '合约代码': 'a0311',
        #  '品种': '豆一',
        #  '开始交易日': 20020522,             # int
        #  '最后交割日': '20031121',           # str 期权没有交割日
        #  '最后交易日': 20031114,             # int
        #  '最小变动价位': 1.0}                # int
        dfs[0].columns = ['varietyid', 'contractid', 'unit', 'change', 'begin', 'end', 'delivery']
        dfs[0].varietyid = varietyid.upper()
        return dfs[0]


if __name__ == '__main__':

    # 获取大连交易所合约信息
    future_dce_info = FutureDceInfo()
    to_do = 0
    if to_do:
        df = future_dce_info.contracts('i')
        print(df.head())

    to_do = 0
    if to_do:
        future_dce_info.save_contracts()
