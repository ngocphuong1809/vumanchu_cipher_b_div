from cmath import nan
from typing import Union

from jesse.strategies import Strategy, cached
import jesse.indicators as ta
from jesse import utils
import custom_indicators as cta
import lib
import numpy as np
from jesse.helpers import get_candle_source, slice_candles
import jesse.helpers as jh

import tulipy as ti
import math
from wt import wt
from rsimfi import rsimfi
import utils as tu

 
class Vumanchu(Strategy):

    def __init__(self):
        super().__init__()
        self.debug_log                              = 1          ## Turn on for debug logging to CSV, 
        self.price_precision                        = 2 		#self._price_precision()
       
        self.vars["wtChannelLen"]                   = 9             #WT Channel Length
        self.vars["wtAverageLen"]                   = 12            #WT Average Length
        self.vars["wtMASource"]                     = "hlc3"        #WT MA Source  
        self.vars["wtMALen"]                        = 3             #WT MA Length
        self.vars["obLevel"]                        = 53            #WT OverBought Level 1
        self.vars["osLevel"]                        = -53           #WT OverSold Level 1
  
        self.vars["rsiMFIperiod"]                   = 60            #MFI period
        self.vars["rsiMFIMultiplier"]               = 250           #MFI Area multiplier
        self.vars["rsiMFIPosY"]                     = 2.5           #MFI Area Y Pos

        self.vars["atr_valu"]                       = 14            #ATR (Period)
        self.vars["rsiOversold"]                    = 30            #RSI OverSold
        self.vars["rsiOverbought"]                  = 60            #RSI OverBought

        self.vars["longTradesEnabled"]              = True          # Long Trades (Filter)
        self.vars["shortTradesEnabled"]             = True          # Short Trades (Filter)
        self.vars["enableEntryTrailing"]            = False         # Enable/ Disable the trailing for entry position
       
        self.vars["devEntryAtrMult"]                = 0.5           # Deviation ATR Mul  Multiplier to be used on the initial entrys` ATR to calculate the step for following the price, when the entry target is reached
        self.vars["enterLongPosition"]              = False
        self.vars["enterShortPosition"]             = False

        self.vars["botRisk"]                        = 3.0           #Bot risk % each entry
        self.vars["botLeverage"]                    = 10.0          # Bot Leverage
        self.vars["botPricepPrecision"]             = 4             #Bot Order Price Precision
        self.vars["botBasePrecision"]               = 1             #Bot Order Coin Precision
 

    def hyperparameters(self):
        return [ 
            {'name': 'ema50', 'title': 'EMA 50', 'type': int, 'min': 30, 'max': 100, 'default': 50},
            {'name': 'ema200', 'title': 'EMA 200', 'type': int, 'min': 150, 'max': 400, 'default': 200},

            {'name': 'long_slMult', 'title': 'Long Stop Loss Mult', 'type': float, 'min': 1.0, 'max': 3.0, 'default': 1.5},
            {'name': 'long_tpMult', 'title': 'Long Take Profit Mult', 'type': float, 'min': 2.0, 'max': 6.0, 'default': 2.9},

            {'name': 'short_slMult', 'title': 'Short Stop Loss Mult', 'type': float, 'min': 1.0, 'max': 3.0, 'default': 1.5},
            {'name': 'short_tpMult', 'title': 'Short Take Profit Mult', 'type': float, 'min': 2.0, 'max': 6.0, 'default': 2.9},     
        ]

    @property
    def ema50(self):
        return ta.ema(self.candles, self.hp["ema50"])

    @property
    def ema200(self):
        return ta.ema(self.candles, self.hp["ema200"])

    @property
    def ema50pullback(self) -> bool:
        return self.close > self.ema50 - (self.ema50*0.05) and self.close < self.ema50 + (self.ema50*0.05)
    @property
    def emaLong(self) -> bool:
        return self.close > self.ema200 and self.ema50pullback

    @property
    def emaShort(self) -> bool:
        return self.close < self.ema200 and self.ema50pullback
    
    @property
    def atr(self):
        return ta.atr(self.candles, self.vars["atr_valu"])

    @property
    def rsiMFI(self):
        rf = rsimfi(self.candles, self.vars["rsiMFIperiod"],self.vars["rsiMFIMultiplier"])
        rmfi = rf - self.vars["rsiMFIPosY"] 
        return rmfi

    def unit_qty_long(self):
        risk_loss = self.capital * self.vars["botRisk"]  / (self.atr * self.hp["long_slMult"] * 100 / self.price) 
        return max(0, min(self.capital, risk_loss))

    def unit_qty_short(self):
        risk_loss = self.capital * self.vars["botRisk"]  / (self.atr * self.hp["short_slMult"]  * 100  / self.price) 
        return max(0, min(self.capital, risk_loss))

    def risk_qty_long(self):
        risk_loss = self.capital * self.vars["botRisk"]  / (self.atr * self.hp["long_slMult"] * 100) 
        return risk_loss

    def risk_qty_short(self):
        risk_loss = self.capital * self.vars["botRisk"]  / (self.atr * self.hp["long_slMult"] * 100) 
        return risk_loss

    @property
    def signal(self):
        signal = None
        # // Calculates WaveTrend
    
        [wt1, wt2, wtCross, wtCrossUp, wtCrossDown, wtOversold, wtOverbought] = wt(self.candles, self.vars["wtChannelLen"], self.vars["wtAverageLen"], self.vars["wtMALen"], self.vars["obLevel"], self.vars["osLevel"], self.vars["wtMASource"])
        
        # buySignal = wtCross and wtCrossUp and wtOversold and wtBuy
        if wtCross:
            if wtCrossUp:
                if wtOversold:
                    if wt2[-1] >= 0:
                        if wt1[-1] <= 0:
                            if self.rsiMFI > 0:
                                if self.emaLong:
                                    signal = "buySignal"
        
        # sellSignal = wtCross and wtCrossDown and wtOverbought and wtSell
        if wtCross:
            if wtCrossDown:
                if wtOverbought:
                    if wt2[-1] >= 0:
                        if wt1[-1] >= 0:
                            if self.rsiMFI > 0:
                                if self.emaShort:
                                    signal = "sellSignal"

        return signal

    def on_first_candle(self):
        # print("On First Candle")
        if jh.is_live():
            self.price_precision = self._price_precision()
            self.qty_precision = self._qty_precision()
        else:
            self.price_precision = 2
            self.qty_precision = 2

    def on_new_candle(self):
        if self.debug_log > 0:  
            self.ts = tu.timestamp_to_gmt7(self.current_candle[0] / 1000)
        return 

    def before(self):
        # Call on first candle
        if self.index == 0:
            self.on_first_candle()
        self.sliced_candles = np.nan_to_num(jh.slice_candles(self.candles, sequential=True))

        # Call on new candle
        self.on_new_candle()

    def should_long(self) -> bool:
        qty = max(min(round(self.risk_qty_long(), self.qty_precision), (self.available_margin - 1)/ self.price), 0)
        if qty != 0:
            if self.vars["longTradesEnabled"]:
                if self.signal == "buySignal":
                    return True

    def should_short(self) -> bool:
        qty = max(min(round(self.risk_qty_short(), self.qty_precision), (self.available_margin - 1)/ self.price), 0)
        if qty != 0:
            if self.vars["shortTradesEnabled"]:
                if self.signal == "sellSignal":
                    return True

    def should_cancel(self) -> bool:
        return True

    def go_long(self):

        qty = max(min(round(self.risk_qty_long(), self.qty_precision), (self.available_margin - 1)/ self.price), 0)
        
        self.buy = qty, self.price

        stop_loss = self.price - self.atr * self.hp["long_slMult"]
        take_profit = self.price + self.atr * self.hp["long_tpMult"]
        self.stop_loss = qty, stop_loss
        self.take_profit = qty, take_profit
        

    def go_short(self):

        qty = max(min(round(self.risk_qty_short(), self.qty_precision), (self.available_margin - 1)/ self.price), 0)

        self.sell = qty, self.price

        stop_loss = self.price + self.atr * self.hp["short_slMult"]
        take_profit = self.price - self.atr * self.hp["short_tpMult"]
        self.stop_loss = qty, stop_loss
        self.take_profit = qty, take_profit

    

