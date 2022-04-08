from collections import namedtuple

import numpy as np
import talib as ta

from jesse.helpers import get_candle_source, slice_candles

Wavetrend = namedtuple('Wavetrend', ['wt1', 'wt2', 'wtCross', 'wtCrossUp', 'wtCrossDown', 'wtOversold', 'wtOverbought'])

def wt(candles: np.ndarray,
       wtchannellen: int = 9,
       wtaveragelen: int = 12,
       wtmalen: int = 3,
       oblevel: int = 53,
       oslevel: int = -53,
       source_type: str = "hlc3",
       sequential: bool = False) -> Wavetrend:
    """
    Wavetrend indicator

    :param candles: np.ndarray
    :param wtchannellen:  int - default: 9
    :param wtaveragelen: int - default: 12
    :param wtmalen: int - default: 3
    :param oblevel: int - default: 53
    :param oslevel: int - default: -53
    :param source_type: str - default: "hlc3"
    :param sequential: bool - default: False

    :return: Wavetrend
    """
    candles = slice_candles(candles, sequential)

    src = get_candle_source(candles, source_type=source_type)

    # wt
#     esa = ema(tfsrc, chlen)
    esa = ta.EMA(src, wtchannellen)    

#     de = ema(abs(tfsrc - esa), chlen)
    de = ta.EMA(abs(src - esa), wtchannellen)

#     ci = (tfsrc - esa) / (0.015 * de)
    ci = (src - esa) / (0.015 * de)

#     wt1 = security(syminfo.tickerid, tf, ema(ci, avg))
    wt1 = ta.EMA(ci, wtaveragelen)

#     wt2 = security(syminfo.tickerid, tf, sma(wt1, malen))
    wt2 = ta.SMA(wt1, wtmalen)

#     wtVwap = wt1 - wt2
    # wtVwap = wt1 - wt2

#     wtOversold = wt2 <= osLevel
    wtOversold = wt2[-1] <= oslevel

#     wtOverbought = wt2 >= obLevel
    wtOverbought = wt2[-2] >= oblevel

#     wtCross = cross(wt1, wt2)
    wtCross =  (wt1[-2] <= wt2[-2] and wt1[-1] > wt2[-1]) or (wt1[-2] >= wt2[-2] and wt1[-1] < wt2[-1])

#     wtCrossUp = wt2 - wt1 <= 0
    wtCrossUp = wt2[-1] - wt1[-1] <= 0

#     wtCrossDown = wt2 - wt1 >= 0
    wtCrossDown = wt2[-1] - wt1[-1] >= 0

    return Wavetrend(wt1, wt2, wtCross, wtCrossUp, wtCrossDown, wtOversold, wtOverbought)
   
