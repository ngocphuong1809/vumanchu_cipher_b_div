from typing import Union

import numpy as np
import talib

from jesse.helpers import slice_candles

# f_rsimfi(_period, _multiplier, _tf) => security(syminfo.tickerid, _tf, sma(((close - open) / (high - low)) * _multiplier, _period) - rsiMFIPosY)

def rsimfi(candles: np.ndarray, period: int = 60, multiplier: float = 250, sequential: bool = False) -> Union[float, np.ndarray]:
    """
    MFI - Money Flow Index

    :param candles: np.ndarray
    :param period: int - default: 14
    :param sequential: bool - default: False

    :return: float | np.ndarray
    """
    candles = slice_candles(candles, sequential)
    rf = talib.SMA((((candles[:, 2] - candles[:, 1])/(candles[:, 3] - candles[:, 4]))* multiplier), period)

    return rf if sequential else rf[-1]
