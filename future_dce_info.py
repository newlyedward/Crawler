# -*- coding: utf-8 -*-
import os
import redis
import pandas as pd
import datetime as dt
from utils import get_html_tree, get_congfig_handle
from settings import *



def dce_contract_info(url, ua):
    resp = get_html_tree(url, ua)

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

    return df


if __name__ == '__main__':
    config = get_congfig_handle()
    base_dir = config.get('FinData', 'base_dir')

    future_dir = os.path.join(base_dir, 'future')
    if not os.path.exists(future_dir):
        os.makedirs(future_dir)

    redis_host = config.get('Redis', 'host')
    redis_port = config.getint('Redis', 'port')

    conn = redis.Redis(redis_host, redis_port, decode_responses=True)
    ua = conn.srandmember('user_agent')

    # 获取大连交易所合约信息
    to_do = 1
    if to_do:
        url = CONTRACTS_URL

        df = dce_contract_info(url, ua)

        file_name = os.path.join(future_dir, CONTRACTS_FILE)
        df_future = df[~df['delivery'].isnull()]
        if os.path.exists(file_name):
            df = pd.read_hdf(file_name, 'table', columns=['update'])
            df_future['update'] = df['update']
        else:
            df_future.loc[:, 'update'] = dt.datetime(1970, 1, 1)
        df_future.to_hdf(file_name, 'table', format='table', data_columns=True, complevel=5, complib='blosc')
