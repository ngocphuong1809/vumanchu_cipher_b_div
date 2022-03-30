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
        self.debug_log              = 1          ## Turn on for debug logging to CSV, 
        self.price_precision        = 2 		#self._price_precision()
        # self.vars["wtShow"]                         = True          #Show WaveTrend
        # self.vars["wtBuyShow"]                      = True          #Show Buy dots
        # self.vars["wtGoldShow"]                     = False         #Showd Gold dots
        # self.vars["wtSellShow"]                     = True          #Show Sell dots
        # self.vars["wtDivShow"]                      = False         #Show Div dots
        # self.vars["vwapShow"]                       = False         #Show  Fast WT
        self.vars["wtChannelLen"]                   = 9             #WT Channel Length
        self.vars["wtAverageLen"]                   = 12            #WT Average Length
        self.vars["wtMASource"]                     = "hlc3"        #WT MA Source  
        self.vars["wtMALen"]                        = 3             #WT MA Length
        self.vars["obLevel"]                        = 53            #WT OverBought Level 1
        # self.vars["obLevel2"]                       = 60            #WT OverBought Level 2
        # self.vars["obLevel3"]                       = 100           #WT OverBought Level 3
        self.vars["osLevel"]                        = -53           #WT OverSold Level 1
        # self.vars["osLevel2"]                       = -60           #WT OverSold Level 1      
        # self.vars["osLevel3"]                       = -75           #WT OverSold Level 1      
        # self.vars["wtShowDiv"]                      = False         #Show WT Regular Divergences
        # self.vars["wtShowHiddenDiv"]                = False         #Show WT Hidden Divergences
        # self.vars["showHiddenDiv_nl"]               = True          #Not apply OB/OS Limits on Hidden Divergences
        # self.vars["wtDivOBLevel"]                   = 45            #WT Bearish Divergences min
        # self.vars["wtDivOSLevel"]                   = -65           #WT Bullish Divergences min
        # self.vars["wtDivOBLevel_addshow"]           = False         #Show 2nd WT Regular Divergences
        # self.vars["wtDivOBLevel_add"]               = 15            #WT 2nd Bearish Divergence
        # self.vars["wtDivOSLevel_add"]               = -40           #WT 2nd Bullish Divergence 15 min
        # self.vars["rsiMFIShow"]                     = True          #Show MFI
        self.vars["rsiMFIperiod"]                   = 60            #MFI period
        self.vars["rsiMFIMultiplier"]               = 250           #MFI Area multiplier
        self.vars["rsiMFIPosY"]                     = 2.5           #MFI Area Y Pos
        # self.vars["rsiShow"]                        = False         #Show RSI
        # self.vars["rsiSRC"]                         = 'close'       #RSI Source
        # self.vars["rsiLen"]                         = 14            #RSI Length
        # self.vars["rsiShowDiv"]                     = False         #Show RSI Regular Divergences
        # self.vars["rsiShowHiddenDiv"]               = False         #Show RSI Hidden Divergences
        # self.vars["rsiDivOBLevel"]                  = 60            #RSI Bearish Divergence min
        # self.vars["rsiDivOSLevel"]                  = 30            #RSI Bullish Divergence mmin
        # self.vars["stochShow"]                      = False         #Show Stochastic RSI
        # self.vars["stochUseLog"]                    = True          #Use Log?
        # self.vars["stochAvg"]                       = False         #Use Average of both K & D
        # self.vars["stochSRC"]                       = 'close'       #Stochastic RSi Source
        # self.vars["stochLen"]                       = 14            #Stochastic RSI Length
        # self.vars["stochRsiLen"]                    = 14            #RSI Length
        # self.vars["stochKSmooth"]                   = 3             #Stochastic RSI K Smooth
        # self.vars["stochDSmooth"]                   = 3             #Stochastic RSI D Smooth
        # self.vars["stochShowDiv"]                   = False         #Show Stoch Regular Divergences
        # self.vars["stochShowHiddenDiv"]             = False         #Show Stoch Hidden Divergences
        # self.vars["tcLine"]                         = False         #Show Schaff TC Line
        # self.vars["tcSRC"]                          = 'close'       #Schaff TC Source
        # self.vars["tclength"]                       = 10            #Schaff TC
        # self.vars["tcfastlength"]                   = 23            #Schaff TC Fast Length
        # self.vars["tcslowlength"]                   = 50            #Schaff TC Slow Length
        # self.vars["tcfactor"]                       = 0.5           #Schaff TC Factor
        # self.vars["sommiFlagShow"]                  = False         #Show Sommi Flag
        # self.vars["sommiShowVwap"]                  = False         #Show Sommi F. Wave
        # self.vars["sommiVwapTF"]                    = "720"         #Sommi F. Wave timeframe    
        # self.vars["sommiVwapBearLevel"]             = 0             #F. Wave Bear Level (less than)
        # self.vars["sommiVwapBullLevel"]             = 0             #F. Wave Bull Level (more than)
        # self.vars["soomiFlagWTBearLevel"]           = 0             #WT Bear Level (less than)
        # self.vars["soomiFlagWTBullLevel"]           = 0             #WT Bull Level (more than)
        # self.vars["soomiRSIMFIBearLevel"]           = 0             #Money Flow Bear Level (less than)
        # self.vars["soomiRSIMFIBullLevel"]           = 0             #Money Flow Bull Level (more than)
        # self.vars["sommiDiamondShow"]               = False         #Show Sommi Diamond
        # self.vars["sommiHTCRes"]                    = '60'          #HTF Candle Res. 1
        # self.vars["sommiHTCRes2"]                   = '240'         #HTF Candle Res. 2
        # self.vars["sommiHTCRes"]                    = '60'          #HTF Candle Res. 1
        # self.vars["soomiDiamondWTBearLevel"]        = 0             #WT Bear Level (more than)
        # self.vars["soomiDiamondWTBullLevel"]        = 0             #WT Bull Level (less than)
        # self.vars["macdWTColorsShow"]               = False         #Show MACD Colors
        # self.vars["macdWTColorsTF"]                 = '240'         #MACD Colors MACD TF
        # self.vars["darkMode"]                       = False         #Dark mode

        self.vars["atr_valu"]                       = 14            #ATR (Period)
        self.vars["rsiOversold"]                    = 30            #RSI OverSold
        self.vars["rsiOverbought"]                  = 60            #RSI OverBought

        self.vars["longTradesEnabled"]              = True          # Long Trades (Filter)
        self.vars["shortTradesEnabled"]             = True          # Short Trades (Filter)
        self.vars["longTrailingTakeProfitExecuted"] = False
        self.vars["shortTrailingTakeProfitExecuted"]= False
        self.vars["enableEntryTrailing"]            = False         # Enable/ Disable the trailing for entry position
        self.vars["devEntryPerc"]                   = 3.0           #Deviation % The step to follow the price when the open position condition is met
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
    def rsi(self):
        return ta.rsi(self.candles, self.vars["rsiLen"])
    
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

    def openLongPosition(self) -> bool:
        if self.vars["longTradesEnabled"] and self.signal == "buySignal":
            return True
        return False

    def openShortPosition(self) -> bool:
        if self.vars["shortTradesEnabled"] and self.signal == "sellSignal":
            return True
        return False

    def closeLongPosition(self) -> bool:
        if self.vars["longTradesEnabled"] and self.signal == "sellSignal":
            return True
        return False

    def closeShortPosition(self) -> bool:
        if self.vars["shortTradesEnabled"] and self.signal == "buySignal":
            return True
        return False
    
    def validOpenLongPosition(self) -> bool:
        if self.openLongPosition and self.position.is_long:
             return True
        return False

    def validOpenShortPosition(self) -> bool:
        if self.openShortPosition and self.position.is_short:
            return True
        return False

    def validCloseLongPosition(self) -> bool:
        if self.closeLongPosition and self.position.is_long:
            return True
        return False
    
    def validCloseShortPosition(self) -> bool:
        if self.closeShortPosition and self.position.is_short:
            return True
        return False

    def barsSinceValidOpenLong(self) -> int:
        return lib.nz(lib.barssince(self.validOpenLongPosition), 999999)

    def barsSinceValidOpenShort(self) -> int:
        return lib.nz(lib.barssince(self.validOpenShortPosition), 999999)

    def barsSinceCloseLong(self) -> int:
        return lib.nz(lib.barssince(self.closeLongPosition), 999999)
    
    def barsSinceCloseShort(self) -> int:
        return lib.nz(lib.barssince(self.closeShortPosition), 999999)
    
    def openPrice(self) -> float:
        return lib.valuewhen(self.validOpenLongPosition or self.validOpenShortPosition, self.close, 0)

    def openAtr(self) -> float:
        return lib.valuewhen(self.validOpenLongPosition or self.validOpenShortPosition, self.openAtr, 0)

    def barsSinceEnterLong(self) -> int:
        return lib.nz(lib.barssince(self.vars["enterLongPosition"]), 999999)

    def openLongIsActive(self) -> bool:
        return self.barsSinceCloseLong >= self.barsSinceValidOpenLong

    def enterLongIsPending(self) -> bool:
        return self.barsSinceEnterLong >= self.barsSinceValidOpenLong

    def tryEnterLongPosition(self) -> bool:
        return self.vars["longTradesEnabled"] and self.openLongIsActive and self.enterLongIsPending
    
    def getLongEntryPrice(self, baseSrc):
        return baseSrc + self.vars["devEntryAtrMult"]  * self.openAtr

    def longEntryPrice(self) -> float:
        longEntryPrice = nan
        if self.validOpenLongPosition:
            longEntryPrice = self.getLongEntryPrice(self.close)
        else:
            if self.tryEnterLongPosition:
                longEntryPrice = min(self.getLongEntryPrice(self.low), lib.nz(longEntryPrice[1], 999999))
            else: longEntryPrice = nan
    
    def enterLongPosition(self):
        if self.vars["enableEntryTrailing"]:
            temp = nan
            if self.openLongPosition:
                temp = self.close
            else:
                temp = self.high
            return self.vars["longTradesEnabled"] and utils.crossed(temp, self.longEntryPrice, "above")
        else:
            return self.openLongPosition 

    def validEnterLongPosition(self) -> bool:
        return self.enterLongPosition and not self.position.is_long

    def barsSinceEnterShort(self) -> int:
        return lib.nz(lib.barssince(self.vars["enterShortPosition"]), 999999)

    def openShortIsActive(self) -> bool:
        return self.barsSinceCloseShort >= self.barsSinceValidOpenShort

    def enterShortIsPending(self) -> bool:
        return self.barsSinceEnterShort >= self.barsSinceValidOpenShort

    def tryEnterShortPosition(self) -> bool:
        return self.vars["shortTradesEnabled"] and self.openShortIsActive and self.enterShortIsPending

    def getShortEntryPrice(self, baseSrc):
        return baseSrc - self.vars["devEntryAtrMult"]  * self.openAtr

    def shortEntryPrice(self) -> float:
        shortEntryPrice = nan
        if self.validOpenShortPosition:
            shortEntryPrice = self.getShortEntryPrice(self.close)
        else:
            if self.tryEnterShortPosition:
                shortEntryPrice = min(self.getShortEntryPrice(self.low), lib.nz(shortEntryPrice[1], 999999))
            else: shortEntryPrice = nan
    
    def enterShortPosition(self):
        if self.vars["enableEntryTrailing"]:
            temp = nan
            if self.openShortPosition:
                temp = self.close
            else:
                temp = self.high
            return self.vars["shortTradesEnabled"] and utils.crossed(temp, self.shortEntryPrice, "below")
        else:
            return self.openShortPosition 

    def validEnterShortPosition(self) -> bool:
        return self.enterShortPosition and not self.position.is_long

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
        # if self.debug_log >= 5:    
        #     self.data_log.append([self.index, self.ts, self.open, self.high, self.low, self.close, self.current_candle[5]])
        return 

    def before(self):
        # Call on first candle
        
        if self.index == 0:
            self.on_first_candle()
        self.sliced_candles = np.nan_to_num(jh.slice_candles(self.candles, sequential=True))

        # Call on new candle
        self.on_new_candle()


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

    

