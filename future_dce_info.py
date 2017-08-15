# -*- coding: utf-8 -*-
import os
import redis
import pandas as pd
from settings import *
from utils import get_html_tree

if __name__ == '__main__':
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    future_dir = os.path.join(base_dir, 'future')
    if not os.path.exists(future_dir):
        os.mkdir(future_dir)

    conn = redis.Redis('192.168.2.88', 6379, decode_responses=True)
    ua = conn.srandmember('user_agent')
    url = 'http://www.dce.com.cn/publicweb/businessguidelines/queryContractInfo.html'
    resp = get_html_tree(url, ua)

    cols = resp.xpath('//div[@class="dataArea"]/table[@cellpadding="0"]/tr/th/text()')
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

    file_name = os.path.join(future_dir, 'dlse_contracts.h5')
    df.to_hdf(file_name, 'table', complevel=5, complib='blosc')