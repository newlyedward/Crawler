import numpy as np
import pandas as pd

from Quant.instrument import Instrument
from utils import LogHandler

log = LogHandler('ts_czsz')


class KsCzsz:
    def __init__(self, ks):
        self.ks = ks
        self.gdfx = pd.DataFrame()
        self.bi = pd.DataFrame()
        self.segments = []

    @staticmethod
    def removed_continue_peak(gdfx):
        flag = pd.Series([False] * 3)
        while not flag.all():
            yflag = abs((gdfx.peak / gdfx.peak.shift(1)) ** (gdfx.peak / abs(gdfx.peak))) > 1
            tflag = abs((gdfx.peak / gdfx.peak.shift(-1)) ** (gdfx.peak / abs(gdfx.peak))) > 1
            flag = np.logical_and(yflag, tflag)
            flag.iloc[[0, -1]] = True
            gdfx = gdfx[flag]
        return gdfx

    @staticmethod
    def removed_near_peak(gdfx, num):
        yflag = abs((gdfx.peak / gdfx.peak.shift(2)) ** (gdfx.peak / abs(gdfx.peak))) > 1
        tflag = abs((gdfx.peak / gdfx.peak.shift(-2)) ** (gdfx.peak / abs(gdfx.peak))) > 1
        nflag = gdfx.kindex - gdfx.kindex.shift(1) > num
        flag = np.logical_or(np.logical_and(yflag, tflag), nflag)
        flag.iloc[[0, -1]] = True
        return gdfx[flag]

    def calculate_gdfx(self):
        hl_df = self.ks
        if len(hl_df) < 3:
            log.info('length of quotes is not enough!')
            return self.gdfx

        # 寻找k线高点
        HH = pd.DataFrame()
        HH['-2'] = hl_df.high.shift(2)
        HH['-1'] = hl_df.high.shift(1)
        HH['0'] = hl_df.high
        HH['1'] = hl_df.high.shift(-1)
        HH['2'] = hl_df.high.shift(-2)
        HH = hl_df.loc[:, ['high', 'kindex']].loc[HH.idxmax(axis=1) == '0']
        HH.columns = ['peak', 'kindex']

        # 寻找k线低点
        LL = pd.DataFrame()
        LL['-2'] = hl_df.low.shift(2)
        LL['-1'] = hl_df.low.shift(1)
        LL['0'] = hl_df.low
        LL['1'] = hl_df.low.shift(-1)
        LL['2'] = hl_df.low.shift(-2)
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

    def calculate_bi(self):
        if len(self.gdfx) < 2:
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
