from typing import Union

import numpy as np
import talib
import jesse.indicators as ta


from jesse.helpers import slice_candles

def rsimfi(candles: np.ndarray, period: int = 60, multiplier: float = 250.0, sequential: bool = False) -> Union[float, np.ndarray]:
    """
    MFI - Money Flow Index

    :param candles: np.ndarray
    :param period: int - default: 14
    :param sequential: bool - default: False

    :return: float | np.ndarray
    """
    candles = slice_candles(candles, sequential)
    rf = ta.sma(((candles[:, 2] - candles[:, 1])/(candles[:, 3] - candles[:, 4]))* multiplier, period)

    return rf

  
