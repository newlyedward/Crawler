import numpy as np
import pandas as pd

from Quant.instrument import Instrument
from utils import LogHandler

log = LogHandler('ts_czsz')


def segment_verify(segment, upsegment):
    x = segment.join(upsegment,lsuffix='_x', rsuffix='_y')
    x.fillna(method='bfill', inplace=True)
    x['diff'] = abs((x['peak_y'] / x['peak_x']) ** (x['peak_y'] / abs(x['peak_y']))) < 1
    return x['diff']


def segment_revised(segment, upsegment):
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
    flag = pd.Series([False] * 3)
    while not flag.all():
        t_peak = segment.peak
        t_peak_m1 = segment.peak.shift(1)
        t_peak_p1 = segment.peak.shift(-1)
        t_sign = t_peak / abs(t_peak)
        t_peak_m1.iat[0] = t_peak.iat[0] - 1
        t_peak_p1.iat[-1] = t_peak.iat[-1] - 1

        yflag = abs((t_peak / t_peak_m1) ** t_sign) > 1       # 低于或高于前面的低点或高点
        tflag = abs((t_peak / t_peak_p1) ** t_sign) >= 1      # 可以等于后面的点

        flag = np.logical_and(yflag, tflag)
        segment = segment[flag]
    return segment


def removed_near_peak(segment, num):
    t_index = segment.kindex
    t_index_m1 = segment.kindex.shift(1)
    t_index_m1.iat[0] = t_index.iat[0] - num - 1
    nflag = t_index - t_index_m1 > num

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

    flag = np.logical_or(nflag, np.logical_and(yflag, tflag))

    upsegment = segment[flag]
    upsegment.drop_duplicates('kindex', inplace=True)  # 删除同一根k线上的高低点
    upsegment = removed_continue_peak(upsegment)
    return upsegment

def upgrade_segment(segment):
    upsegment = pd.DataFrame()
    if len(segment) < 7:
        return segment
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


class KsCzsz:
    def __init__(self, ks):
        self.ks = ks
        self.gdfx = pd.DataFrame()
        self.bi = pd.DataFrame()
        self.segments = []

    @staticmethod
    def segment_verify(segment, upsegment):
        x = pd.merge(segment, upsegment, how='left', left_index=True, right_index=True)
        x.fillna(method='bfill', inplace=True)
        x['diff'] = abs((x['peak_y'] / x['peak_x']) ** (x['peak_y'] / abs(x['peak_y']))) < 1
        return x[x['diff']]

    @staticmethod
    def removed_continue_peak(segment):
        flag = pd.Series([False] * 3)
        while not flag.all():
            yflag = abs((segment.peak / segment.peak.shift(1)) ** (segment.peak / abs(segment.peak))) >= 1
            tflag = abs((segment.peak / segment.peak.shift(-1)) ** (segment.peak / abs(segment.peak))) >= 1
            flag = np.logical_and(yflag, tflag)
            flag.iloc[[0, -1]] = True
            segment = segment[flag]
        if segment.iat[-2, 1] != segment.iat[-1, 1] and segment.iat[-2, 0] * segment.iat[-1, 0] < 0:  flag.iloc[
            -1] = True
        return segment[flag]

    @staticmethod
    def removed_near_peak(gdfx, num):
        yflag = abs((gdfx.peak / gdfx.peak.shift(2)) ** (gdfx.peak / abs(gdfx.peak))) > 1
        tflag = abs((gdfx.peak / gdfx.peak.shift(-2)) ** (gdfx.peak / abs(gdfx.peak))) > 1
        nflag = gdfx.kindex - gdfx.kindex.shift(1) > num
        Nflag = -(gdfx.peak.shift(1) / gdfx.peak.shift(-1)) ** (gdfx.peak / abs(gdfx.peak)) > 1  # 删除点后，前面的点要比后面的点高或者低
        flag = np.logical_or(nflag, np.logical_and(yflag, tflag))
        flag = np.logical_or(Nflag, flag)
        flag.iloc[0] = True
        if gdfx.iat[-2, 1] != gdfx.iat[-1, 1] and gdfx.iat[-2, 0] * gdfx.iat[-1, 0] < 0:  flag.iloc[-1] = True
        return gdfx[flag]

    def calculate_gdfx(self):
        hl_df = self.ks
        if len(hl_df) < 3:
            log.info('length of quotes is not enough!')
            return self.gdfx

        # 寻找k线高点
        HH = pd.DataFrame()
        # HH['-2'] = hl_df.high.shift(2)
        HH['-1'] = hl_df.high.shift(1)
        HH['0'] = hl_df.high
        HH['1'] = hl_df.high.shift(-1)
        # HH['2'] = hl_df.high.shift(-2)
        HH = hl_df.loc[:, ['high', 'kindex']].loc[HH.idxmax(axis=1) == '0']
        HH.columns = ['peak', 'kindex']

        # 寻找k线低点
        LL = pd.DataFrame()
        # LL['-2'] = hl_df.low.shift(2)
        LL['-1'] = hl_df.low.shift(1)
        LL['0'] = hl_df.low
        LL['1'] = hl_df.low.shift(-1)
        # LL['2'] = hl_df.low.shift(-2)
        LL = hl_df.loc[:, ['low', 'kindex']].loc[LL.idxmin(axis=1) == '0']
        LL.columns = ['peak', 'kindex']
        LL.peak = -LL.peak

        # 连接顶底分形
        gdfx = pd.concat([HH, LL])
        gdfx = gdfx.sort_index()

        # 去除连续的顶分形中较低点，连续底分型中的较高点
        gdfx = self.removed_continue_peak(gdfx)
        gdfx = self.removed_near_peak(gdfx, 0)
        gdfx = self.removed_continue_peak(gdfx)

        self.gdfx = gdfx

        return gdfx

    def upgrade(self):
        if len(self.gdfx) < 6:
            log.info('length of gdfx is not enough!')
            return self.bi


if __name__ == '__main__':
    instrument = Instrument()
    code = 'il8'
    df = instrument.bar(code, asset='future')
    hl_df = df.loc[:, ['high', 'low']]
    hl_df['kindex'] = np.arange(len(hl_df))

    ks_czsz = KsCzsz(hl_df)
    ks_czsz.calculate_gdfx()
    print(ks_czsz.gdfx.head(20))
    print(ks_czsz.gdfx.tail(20))
