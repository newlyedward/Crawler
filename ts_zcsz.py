import numpy as np
import pandas as pd

from Quant.instrument import Instrument
from utils import LogHandler

log = LogHandler('ts_czsz')


def segment_verify(segment, upsegment):
    x = segment.join(upsegment, lsuffix='_x', rsuffix='_y')
    x.fillna(method='bfill', inplace=True)
    x['diff'] = abs((x['peak_y'] / x['peak_x']) ** (x['peak_y'] / abs(x['peak_y']))) < 1
    return x['diff']


def segment_revised(segment, upsegment):
    """
        修正端点不是区间内最高最低点的高级别线段
    :param segment: 低级别线段
    :param upsegment: 高级别线段
    :return: 修正后的高级别线段
    """
    x = segment.join(upsegment, lsuffix='_x', rsuffix='_y')
    x.fillna(method='bfill', inplace=True)
    x['diff'] = abs((x['peak_y'] / x['peak_x']) ** (x['peak_y'] / abs(x['peak_y']))) <= 1
    up_segment = segment[x['diff']]

    up_segment = removed_continue_peak(up_segment)

    x = segment.join(up_segment, lsuffix='_x', rsuffix='_y')
    x.fillna(method='ffill', inplace=True)
    x['diff'] = abs((x['peak_y'] / x['peak_x']) ** (x['peak_y'] / abs(x['peak_y']))) <= 1
    up_segment = segment[x['diff']]

    up_segment = removed_continue_peak(up_segment)
    return up_segment


def removed_continue_peak(segment):
    """

    :param segment:
    :return:
    """
    flag = pd.Series([False] * 3)
    while not flag.all():
        t_peak = segment.peak
        t_peak_m1 = segment.peak.shift(1)
        t_peak_p1 = segment.peak.shift(-1)
        t_sign = t_peak / abs(t_peak)
        t_peak_m1.iat[0] = t_peak.iat[0] - 1
        t_peak_p1.iat[-1] = t_peak.iat[-1] - 1

        yflag = abs((t_peak / t_peak_m1) ** t_sign) > 1  # 低于或高于前面的低点或高点
        tflag = abs((t_peak / t_peak_p1) ** t_sign) >= 1  # 可以等于后面的点

        flag = np.logical_and(yflag, tflag)
        segment = segment[flag]
    return segment


def removed_near_peak(gdfx, num):
    """

    :param gdfx:
    :param num:
    :return:
    """
    t_index = gdfx.kindex
    t_index_m1 = gdfx.kindex.shift(1)
    t_index_m1.iat[0] = t_index.iat[0] - num - 1
    nflag = t_index - t_index_m1 > num

    t_peak = gdfx.peak
    t_peak_m2 = gdfx.peak.shift(2)
    t_peak_p2 = gdfx.peak.shift(-2)
    t_sign = t_peak / abs(t_peak)
    t_peak_m2.iat[0] = t_peak.iat[0] - 1
    t_peak_m2.iat[1] = t_peak.iat[1] - 1
    t_peak_p2.iat[-1] = t_peak.iat[-1] - 1
    t_peak_p2.iat[-2] = t_peak.iat[-2] - 1
    yflag = abs((t_peak / t_peak_m2) ** t_sign) > 1
    tflag = abs((t_peak / t_peak_p2) ** t_sign) >= 1

    flag = np.logical_or(nflag, np.logical_and(yflag, tflag))

    upsegment = gdfx[flag]
    upsegment = upsegment.drop_duplicates('kindex')  # 删除同一根k线上的高低点
    upsegment = removed_continue_peak(upsegment)
    return upsegment


def calculate_gdfx(ohlc_df):
    """

    :param ohlc_df: 带high,low有时间序列的DataFrame
    :return: 高低分形的时间序列
    """
    gdfx = pd.DataFrame()
    if len(ohlc_df) < 3:
        log.info('length of quotes is not enough!')
        return gdfx

    hl_df = ohlc_df.loc[:, ['high', 'low']]
    hl_df['kindex'] = np.arange(len(hl_df))

    # 寻找k线高点
    HH = pd.DataFrame()
    HH['-1'] = hl_df.high.shift(1)
    HH['0'] = hl_df.high
    HH['1'] = hl_df.high.shift(-1)
    HH = hl_df.loc[:, ['high', 'kindex']].loc[HH.idxmax(axis=1) == '0']
    HH.columns = ['peak', 'kindex']

    # 寻找k线低点
    LL = pd.DataFrame()
    LL['-1'] = hl_df.low.shift(1)
    LL['0'] = hl_df.low
    LL['1'] = hl_df.low.shift(-1)
    LL = hl_df.loc[:, ['low', 'kindex']].loc[LL.idxmin(axis=1) == '0']
    LL.columns = ['peak', 'kindex']
    LL.peak = -LL.peak

    # 连接顶底分形
    gdfx = pd.concat([HH, LL])
    gdfx = gdfx.sort_index()

    return gdfx


def calculate_segment(gdfx):
    """

    :param gdfx:
    :return:
    """
    segment = pd.DataFrame()

    if len(gdfx) < 3:
        return segment
    bi = removed_continue_peak(gdfx)
    segment = removed_near_peak(bi, 0)
    segment = segment_revised(bi, segment)

    return segment


def upgrade_segment(segment):
    """

    :param segment:
    :return:
    """
    upsegment = pd.DataFrame()
    if len(segment) < 7:
        return upsegment

    t_peak = segment.peak
    t_peak_m2 = segment.peak.shift(2)
    t_peak_p2 = segment.peak.shift(-2)
    t_sign = t_peak / abs(t_peak)
    t_peak_m2.iat[0] = t_peak.iat[0] - 1
    t_peak_m2.iat[1] = t_peak.iat[1] - 1
    t_peak_p2.iat[-1] = t_peak.iat[-1] - 1
    t_peak_p2.iat[-2] = t_peak.iat[-2] - 1

    yflag = abs((t_peak / t_peak_m2) ** t_sign) > 1
    tflag = abs((t_peak / t_peak_p2) ** t_sign) >= 1
    flag = np.logical_and(yflag, tflag)

    upsegment = segment[flag]
    upsegment = removed_continue_peak(upsegment)
    upsegment = segment_revised(segment, upsegment)

    return upsegment


if __name__ == '__main__':
    instrument = Instrument()
    code = 'il8'
    df = instrument.bar(code, asset='future')
    gdfx = calculate_gdfx(df)
    segment = calculate_segment(gdfx)
    upsegment = upgrade_segment(segment)
    print('---------------------------gdfx------------------------')
    print(gdfx.head(20))
    print(gdfx.tail(20))
    print('---------------------------segment------------------------')
    print(segment.head(20))
    print(segment.tail(20))
    print('---------------------------upsegment------------------------')
    print(upsegment.head(20))
    print(upsegment.tail(20))
