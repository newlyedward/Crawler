# import redis
# import requests
import pandas as pd
from io import StringIO
# import datetime as dt
# from pymongo import MongoClient
from utils import get_html_text, LogHandler
from settings import *

log = LogHandler('stock_sina_info')


def financial_statement(code, st_type='BalanceSheet'):
    """
    :param code:    A stock code, 6 digits
    :param st_type: BalanceSheet
                    ProfitStatement
                    CashFlow
    :return: pd.DateFrame
    """
    if st_type not in ['BalanceSheet', 'ProfitStatement', 'CashFlow']:
        log.info('Wrong types of financial statement')
        return

    url = FST_SINA_URL_FORMAT.format(st_type, code)
    html = get_html_text(url)
    origin_df = pd.read_table(StringIO(html))

    df = origin_df.T
    df.columns = df.iloc[0]
    df.drop(list(df.index[[0, -2, -1]]), axis=0, inplace=True)
    df.drop('单位', axis=1, inplace=True)

    df = df.astype('float64')
    df.index = pd.to_datetime(df.index)

    return df.fillna(0)


if __name__ == '__main__':
    print('====================BalanceSheet====================')
    print(financial_statement('002475').head())
    print('====================ProfitStatement====================')
    print(financial_statement('002475', 'ProfitStatement').tail())
    print('====================CashFlow====================')
    print(financial_statement('002475', 'CashFlow').tail())
