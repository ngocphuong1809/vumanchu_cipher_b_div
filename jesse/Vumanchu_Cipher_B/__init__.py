from cmath import nan
from jesse.strategies import Strategy, cached
import jesse.indicators as ta
from jesse import utils
import custom_indicators as cta
from custom_indicators import lib
import numpy as np
from jesse.helpers import get_candle_source, slice_candles
import tulipy as ti
import math

 
class Vumanchu_Ciper_B(Strategy):

    def __init__(self):
        super().__init__()
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

            # {'name': 'usr_risk', 'title':  'Equity Risk (%)', 'type': int, 'min': 1, 'max': 100, 'default': 5},

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
        return ta.atr(self.candles, self.hp["atr_valu"])
    
    # # f_top_fractal(src) => src[4] < src[2] and src[3] < src[2] and src[2] > src[1] and src[2] > src[0]
    # def f_top_fractal(self, src) -> bool:
    #     return src[4] < src[2] and src[3] < src[2] and src[2] > src[1] and src[2] > src[0]

    # # f_bot_fractal(src) => src[4] > src[2] and src[3] > src[2] and src[2] < src[1] and src[2] < src[0]
    # def f_bot_fractal(self, src) -> bool:
    #     return src[4] > src[2] and src[3] > src[2] and src[2] < src[1] and src[2] < src[0]

    # # f_fractalize(src) => f_top_fractal(src) ? 1 : f_bot_fractal(src) ? -1 : 0
    # def f_fractalize(self, src):
    #     if self.f_top_fractal(src):
    #         return 1
    #     else:
    #         if self.f_bot_fractal(src):
    #             return -1
    #         else:
    #             return 0
    
    # # f_findDivs(src, topLimit, botLimit, useLimits) =>
    # #     fractalTop = f_fractalize(src) > 0 and (useLimits ? src[2] >= topLimit : true) ? src[2] : na
    # #     fractalBot = f_fractalize(src) < 0 and (useLimits ? src[2] <= botLimit : true) ? src[2] : na
    # #     highPrev = valuewhen(fractalTop, src[2], 0)[2]
    # #     highPrice = valuewhen(fractalTop, high[2], 0)[2]
    # #     lowPrev = valuewhen(fractalBot, src[2], 0)[2]
    # #     lowPrice = valuewhen(fractalBot, low[2], 0)[2]
    # #     bearSignal = fractalTop and high[2] > highPrice and src[2] < highPrev
    # #     bullSignal = fractalBot and low[2] < lowPrice and src[2] > lowPrev
    # #     bearDivHidden = fractalTop and high[2] < highPrice and src[2] > highPrev
    # #     bullDivHidden = fractalBot and low[2] > lowPrice and src[2] < lowPrev
    # #     [fractalTop, fractalBot, lowPrev, bearSignal, bullSignal, bearDivHidden, bullDivHidden]
    # def f_findDivs(self, src, topLimit, botLimit, useLimits):
    #     #     fractalTop = f_fractalize(src) > 0 and (useLimits ? src[2] >= topLimit : true) ? src[2] : na
    #     if useLimits:
    #         ft_ul = src[2] >= topLimit
    #     else: 
    #         ft_ul = True
        
    #     if ft_ul:
    #         ft = src[2]
    #     else:
    #         ft = math.nan
    #     fractalTop = self.f_fractalize(src) > 0 and ft

    #     #     fractalBot = f_fractalize(src) < 0 and (useLimits ? src[2] <= botLimit : true) ? src[2] : na
    #     if useLimits:
    #         ft_ul = src[2] <= botLimit
    #     else: 
    #         ft_ul = True
        
    #     if ft_ul:
    #         ft = src[2]
    #     else:
    #         ft = math.nan
    #     fractalBot = self.f_fractalize(src) < 0 and ft
        
    #     #     highPrev = valuewhen(fractalTop, src[2], 0)[2]
    #     highPrev = lib.valuewhen(fractalTop, src[2], 0)[2]

    #     #     highPrice = valuewhen(fractalTop, high[2], 0)[2]
    #     highPrice = lib.valuewhen(fractalTop, self.high[2], 0)[2]

        
    #     #     lowPrev = valuewhen(fractalBot, src[2], 0)[2]
    #     lowPrev = lib.valuewhen(fractalBot, src[2], 0)[2]

    #     #     lowPrice = valuewhen(fractalBot, low[2], 0)[2]
    #     lowPrice = lib.valuewhen(fractalBot, self.low[2], 0)[2]

    #     #     bearSignal = fractalTop and high[2] > highPrice and src[2] < highPrev
    #     bearSignal = fractalTop and self.high[2] > highPrice and src[2] < highPrev

    #     #     bullSignal = fractalBot and low[2] < lowPrice and src[2] > lowPrev
    #     bullSignal = fractalBot and self.low[2] < lowPrice and src[2] > lowPrev

    #     #     bearDivHidden = fractalTop and high[2] < highPrice and src[2] > highPrev
    #     bearDivHidden = fractalTop and self.high[2] < highPrice and src[2] > highPrev

    #     #     bullDivHidden = fractalBot and low[2] > lowPrice and src[2] < lowPrev
    #     bullDivHidden = fractalBot and self.low[2] < highPrice and src[2] < lowPrev

    #     #     [fractalTop, fractalBot, lowPrev, bearSignal, bullSignal, bearDivHidden, bullDivHidden]
    #     return [fractalTop, fractalBot, lowPrev, bearSignal, bullSignal, bearDivHidden, bullDivHidden]

    # f_rsimfi(_period, _multiplier, _tf) => security(syminfo.tickerid, _tf, sma(((close - open) / (high - low)) * _multiplier, _period) - rsiMFIPosY)
    def f_rsimfi(self, _period, _multiplier):
        return ti.sma(((self.close - self.open)/ (self.high - self.low)) * _multiplier, _period) - self.vars["rsiMFIPosY"] 

    #     // WaveTrend
    # f_wavetrend(src, chlen, avg, malen, tf) =>
    #     tfsrc = security(syminfo.tickerid, tf, src)
    #     esa = ema(tfsrc, chlen)
    #     de = ema(abs(tfsrc - esa), chlen)
    #     ci = (tfsrc - esa) / (0.015 * de)
    #     wt1 = security(syminfo.tickerid, tf, ema(ci, avg))
    #     wt2 = security(syminfo.tickerid, tf, sma(wt1, malen))
    #     wtVwap = wt1 - wt2
    #     wtOversold = wt2 <= osLevel
    #     wtOverbought = wt2 >= obLevel
    #     wtCross = cross(wt1, wt2)
    #     wtCrossUp = wt2 - wt1 <= 0
    #     wtCrossDown = wt2 - wt1 >= 0
    #     wtCrosslast = cross(wt1[2], wt2[2])
    #     wtCrossUplast = wt2[2] - wt1[2] <= 0
    #     wtCrossDownlast = wt2[2] - wt1[2] >= 0
    #     [wt1, wt2, wtOversold, wtOverbought, wtCross, wtCrossUp, wtCrossDown, wtCrosslast, wtCrossUplast, wtCrossDownlast, wtVwap]

    def f_wavetrend(self, src, chlen, avg, malen):
        #     tfsrc = security(syminfo.tickerid, tf, src)
        #     esa = ema(tfsrc, chlen)
        esa = ta.ema(src, chlen)
        np.nan_to_num(esa, copy=False)
        #     de = ema(abs(tfsrc - esa), chlen)
        de  = ta.ema(abs(src - esa), chlen)
        np.nan_to_num(de, copy=False)
        #     ci = (tfsrc - esa) / (0.015 * de)
        ci  = (src - esa) / (0.015 * de)
        np.nan_to_num(ci, copy=False)
        #     wt1 = security(syminfo.tickerid, tf, ema(ci, avg))
        wt1 = ta.ema(ci, avg)
        np.nan_to_num(wt1, copy=False)
        #     wt2 = security(syminfo.tickerid, tf, sma(wt1, malen))
        wt2 = ta.sma(wt1, malen)
        np.nan_to_num(wt2, copy=False)
        #     wtVwap = wt1 - wt2
        wtVwap = wt1[-1] - wt2[-1]
        #     wtOversold = wt2 <= osLevel
        wtOversold = wt2[-1] <= self.vars["osLevel"]
        #     wtOverbought = wt2 >= obLevel
        wtOverbought = wt2[-1] >= self.vars["obLevel"]
        #     wtCross = cross(wt1, wt2)
        wtCross =  (wt1[-2] <= wt2[-2] and wt1[-1] > wt2[-1]) or (wt1[-2] >= wt2[-2] and wt1[-1] < wt2[-1])
        #     wtCrossUp = wt2 - wt1 <= 0
        wtCrossUp = wt2[-1] - wt1[-1] <= 0
        #     wtCrossDown = wt2 - wt1 >= 0
        wtCrossDown = wt2[-1] - wt1[-1] >= 0
        #     wtCrosslast = cross(wt1[2], wt2[2])
        wtCrosslast = (wt1[-2][2] <= wt2[-2][2] and wt1[-1][2] > wt2[-1][2]) or (wt1[-2][2] >= wt2[-2][2] and wt1[-1][2] < wt2[-1][2])
        #     wtCrossUplast = wt2[2] - wt1[2] <= 0
        wtCrossUplast = wt2[-2][2] - wt1[-2][2] <=0
        #     wtCrossDownlast = wt2[2] - wt1[2] >= 0
        wtCrossDownlast = wt2[-2][2] - wt1[-2][2] >=0
        #     [wt1, wt2, wtOversold, wtOverbought, wtCross, wtCrossUp, wtCrossDown, wtCrosslast, wtCrossUplast, wtCrossDownlast, wtVwap]
        return [wt1[-1], wt2[-1], wtOversold, wtOverbought, wtCross, wtCrossUp, wtCrossDown, wtCrosslast, wtCrossUplast, wtCrossDownlast, wtVwap]

    # # // Schaff Trend Cycle
    # # f_tc(src, length, fastLength, slowLength) =>
    # #     ema1 = ema(src, fastLength)
    # #     ema2 = ema(src, slowLength)
    # #     macdVal = ema1 - ema2	
    # #     alpha = lowest(macdVal, length)
    # #     beta = highest(macdVal, length) - alpha
    # #     gamma = (macdVal - alpha) / beta * 100
    # #     gamma := beta > 0 ? gamma : nz(gamma[1])
    # #     delta = gamma
    # #     delta := na(delta[1]) ? delta : delta[1] + tcfactor * (gamma - delta[1])
    # #     epsilon = lowest(delta, length)
    # #     zeta = highest(delta, length) - epsilon
    # #     eta = (delta - epsilon) / zeta * 100
    # #     eta := zeta > 0 ? eta : nz(eta[1])
    # #     stcReturn = eta
    # #     stcReturn := na(stcReturn[1]) ? stcReturn : stcReturn[1] + tcfactor * (eta - stcReturn[1])
    # #     stcReturn
    # def f_tc(self, src, length, fastLength, slowLength):
    #     #     ema1 = ema(src, fastLength)
    #     ema1 = ta.ema(src, fastLength)
    #     #     ema2 = ema(src, slowLength)
    #     ema2 = ta.ema(src, slowLength)
    #     #     macdVal = ema1 - ema2	
    #     macdVal = ema1 - ema2
    #     #     alpha = lowest(macdVal, length)
    #     alpha = min(macdVal, length)
    #     #     beta = highest(macdVal, length) - alpha
    #     beta = max(macdVal, length) - alpha
    #     #     gamma = (macdVal - alpha) / beta * 100
    #     gamma = (macdVal - alpha) / beta * 100
    #     #     gamma := beta > 0 ? gamma : nz(gamma[1])
    #     if beta > 0:
    #         gamma = gamma
    #     else:
    #         gamma = lib.nz(gamma[1])
    #     #     delta = gamma
    #     delta = gamma
    #     #     delta := na(delta[1]) ? delta : delta[1] + tcfactor * (gamma - delta[1])
    #     if lib.na(delta[1]):
    #         delta = delta
    #     else:
    #         delta = delta[1] + self.vars["tcfactor"] * (gamma - delta[1]) 
    #     #     epsilon = lowest(delta, length)
    #     epsilon = min(delta, length)
    #     #     zeta = highest(delta, length) - epsilon
    #     zeta = max(delta, length) - epsilon
    #     #     eta = (delta - epsilon) / zeta * 100
    #     eta = (delta - epsilon) / zeta * 100
    #     #     eta := zeta > 0 ? eta : nz(eta[1])
    #     if zeta > 0:
    #         eta = eta
    #     else:
    #         eta = lib.nz(eta[1])
    #     #     stcReturn = eta
    #     stcReturn = eta
    #     #     stcReturn := na(stcReturn[1]) ? stcReturn : stcReturn[1] + tcfactor * (eta - stcReturn[1])
    #     if lib.na(stcReturn[1]):
    #         stcReturn = stcReturn
    #     else:
    #         stcReturn = stcReturn[1] + self.vars["tcfactor"] * (eta - stcReturn[1])
    #     #     stcReturn
    #     return stcReturn

    # def f_stochrsi(self,_src, _stochlen, _rsilen, _smoothk, _smoothd, _log, _avg):
    #     #     src = _log ? log(_src) : _src
    #     if _log:
    #         src = math.log(_src)
    #     else:
    #         src = _src
    #     #     rsi = rsi(src, _rsilen)
    #     rsi = ta.rsi(src, _rsilen)
    #     #     kk = sma(stoch(rsi, rsi, rsi, _stochlen), _smoothk)
    #     kk = ta.sma(ta.stoch(rsi, rsi, rsi, _stochlen), _smoothk)
    #     #     d1 = sma(kk, _smoothd)
    #     #     avg_1 = avg(kk, d1)
    #     #     k = _avg ? avg_1 : kk
    #     #     [k, d1]

    # # // MACD
    # # f_macd(src, fastlen, slowlen, sigsmooth, tf) =>
    # #     fast_ma = security(syminfo.tickerid, tf, ema(src, fastlen))
    # #     slow_ma = security(syminfo.tickerid, tf, ema(src, slowlen))
    # #     macd = fast_ma - slow_ma,
    # #     signal = security(syminfo.tickerid, tf, sma(macd, sigsmooth))
    # #     hist = macd - signal
    # #     [macd, signal, hist]
    # def f_macd(self, src, fastlen, slowlen, sigsmooth):
    #     fast_ma = ta.ema(src, fastlen)
    #     slow_ma = ta.ema(src, slowlen)
    #     macd = fast_ma - slow_ma
    #     signal = ta.sma(macd, sigsmooth)
    #     hist = macd - signal
    #     return [macd, signal,hist]

    # # // Get higher timeframe candle
    # # f_getTFCandle(_tf) => 
    # #     _open  = security(heikinashi(syminfo.tickerid), _tf, open, barmerge.gaps_off, barmerge.lookahead_on)
    # #     _close = security(heikinashi(syminfo.tickerid), _tf, close, barmerge.gaps_off, barmerge.lookahead_on)
    # #     _high  = security(heikinashi(syminfo.tickerid), _tf, high, barmerge.gaps_off, barmerge.lookahead_on)
    # #     _low   = security(heikinashi(syminfo.tickerid), _tf, low, barmerge.gaps_off, barmerge.lookahead_on)
    # #     hl2   = (_high + _low) / 2.0
    # #     newBar = change(_open)
    # #     candleBodyDir = _close > _open
    # #     [candleBodyDir, newBar]
    # def f_getTFCandle(self):
    #     _open = self.open
    #     _close = self.close
    #     _high = self.high
    #     _low = self.low
    #     _hl2 = (_high + _low) / 2.0
    #     newBar = _open - _open[-1]
    #     candleBodyDir = _close > _open
    #     return [candleBodyDir, newBar]

    # # // Sommi flag
    # # f_findSommiFlag(tf, wt1, wt2, rsimfi, wtCross, wtCrossUp, wtCrossDown) =>    
    # #     [hwt1, hwt2, hwtOversold, hwtOverbought, hwtCross, hwtCrossUp, hwtCrossDown, hwtCrosslast, hwtCrossUplast, hwtCrossDownlast, hwtVwap] = f_wavetrend(wtMASource, wtChannelLen, wtAverageLen, wtMALen, tf)      
        
    # #     bearPattern = rsimfi < soomiRSIMFIBearLevel and
    # #                 wt2 > soomiFlagWTBearLevel and 
    # #                 wtCross and 
    # #                 wtCrossDown and 
    # #                 hwtVwap < sommiVwapBearLevel
                    
    # #     bullPattern = rsimfi > soomiRSIMFIBullLevel and 
    # #                 wt2 < soomiFlagWTBullLevel and 
    # #                 wtCross and 
    # #                 wtCrossUp and 
    # #                 hwtVwap > sommiVwapBullLevel
        
    # #     [bearPattern, bullPattern, hwtVwap]
    # def f_findSommiFlag(self, wt1, wt2, rsimfi, wtCross, wtCrossUp, wtCrossDown):
    #     #     [hwt1, hwt2, hwtOversold, hwtOverbought, hwtCross, hwtCrossUp, hwtCrossDown, hwtCrosslast, hwtCrossUplast, hwtCrossDownlast, hwtVwap] = f_wavetrend(wtMASource, wtChannelLen, wtAverageLen, wtMALen, tf)      
    #     [hwt1, hwt2, hwtOversold, hwtOverbought, hwtCross, hwtCrossUp, hwtCrossDown, hwtCrosslast, hwtCrossUplast, hwtCrossDownlast, hwtVwap] = self.f_wavetrend(self.vars["wtMASource"], self.vars["wtChannelLen"], self.vars["wtAverageLen"], self.vars["wtMALen"]) 

    #     bearPattern = rsimfi < self.vars["soomiRSIMFIBearLevel"] and wt2 > self.vars["soomiFlagWTBearLevel"] and wtCross and wtCrossDown and hwtVwap < self.vars["sommiVwapBearLevel"]

                    
    #     bullPattern = rsimfi > self.vars["soomiRSIMFIBullLevel"] and wt2 < self.vars["soomiFlagWTBullLevel"] and wtCross and wtCrossUp and hwtVwap > self.vars["sommiVwapBullLevel"]
        
    #     return [bearPattern, bullPattern, hwtVwap]

    # # f_findSommiDiamond(tf, tf2, wt1, wt2, wtCross, wtCrossUp, wtCrossDown) =>
    # #     [candleBodyDir, newBar] = f_getTFCandle(tf)
    # #     [candleBodyDir2, newBar2] = f_getTFCandle(tf2)
    # #     bearPattern = wt2 >= soomiDiamondWTBearLevel and
    # #                 wtCross and
    # #                 wtCrossDown and
    # #                 not candleBodyDir and
    # #                 not candleBodyDir2                   
    # #     bullPattern = wt2 <= soomiDiamondWTBullLevel and
    # #                 wtCross and
    # #                 wtCrossUp and
    # #                 candleBodyDir and
    # #                 candleBodyDir2 
    # #     [bearPattern, bullPattern]    
    # def f_findSommiDiamond(self, wt1, wt2, wtCross, wtCrossUp, wtCrossDown):
    #     [candleBodyDir, newBar] = self.f_getTFCandle()
    #     [candleBodyDir2, newBar2] = self.f_getTFCandle()

    #     bearPattern = wt2 >= self.vars["soomiDiamondWTBearLevel"] and wtCross and wtCrossDown and not candleBodyDir and not candleBodyDir2  

    #     bullPattern = wt2 <= self.vars["soomiDiamondWTBullLevel"] and wtCross and wtCrossUp and candleBodyDir and candleBodyDir2 
    #     return [bearPattern, bullPattern]
    
    # // RSI + MFI Area
    # rsiMFI = f_rsimfi(rsiMFIperiod, rsiMFIMultiplier, timeframe.period)
    @property
    def rsiMFI(self):
        return self.f_rsimfi(self.vars["rsiMFIperiod"],self.vars["rsiMFIMultiplier"])

    def unit_qty_long(self):
        risk_loss = self.capital * self.vars["bot_risk"]  / (self.atr * self.hp["long_slMult"] * 100 / self.price) 
        return max(0, min(self.capital, risk_loss))

    def unit_qty_short(self):
        risk_loss = self.capital * self.vars["bot_risk"]  / (self.atr * self.hp["short_slMult"]  * 100  / self.price) 
        return max(0, min(self.capital, risk_loss))

    def risk_qty_long(self):
        risk_loss = self.capital * self.vars["bot_risk"]  / (self.atr * self.hp["long_slMult"] * 100) 
        return risk_loss

    def risk_qty_short(self):
        risk_loss = self.capital * self.vars["bot_risk"]  / (self.atr * self.hp["long_slMult"] * 100) 
        return risk_loss


    @property
    def signal(self):
        signal = None
        # // Calculates WaveTrend
        [wt1, wt2, wtOversold, wtOverbought, wtCross, wtCrossUp, wtCrossDown, wtVwap] = cta.wavetrend(self.candles, self.vars["wtChannelLen"], self.vars["wtAverageLen"], self.vars["wtMALen"], self.vars["wtMASource"])
        
        # [wt1, wt2, wtOversold, wtOverbought, wtCross, wtCrossUp, wtCrossDown, wtCross_last, wtCrossUp_last, wtCrossDown_last, wtVwap] = self.f_wavetrend(self.vars["wtMASource"], self.vars["wtChannelLen"], self.vars["wtAverageLen"], self.vars["wtMALen"])
        # wtBuy = wt2 <=0 and wt1 <=0 and rsiMFI >0 and emaLong
        wtBuy = wt2 <= 0 and wt1 <= 0 and self.rsiMFI > 0 and self.emaLong
        
        # wtSell = wt2 >=0 and wt1 >=0 and rsiMFI <0 and emaShort
        wtSell = wt2 >= 0 and wt1 >= 0 and self.rsiMFI < 0 and self.emaShort
        
        # buySignal = wtCross and wtCrossUp and wtOversold and wtBuy
        buySignal = wtCross and wtCrossUp and wtOversold and wtBuy
        
        # sellSignal = wtCross and wtCrossDown and wtOverbought and wtSell
        sellSignal = wtCross and wtCrossDown and wtOverbought and wtSell

        if buySignal:
            signal = 'buySinal'
        elif sellSignal:
            signal = 'sellSignal'
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
        return self.vars["longTradesEnabled"] and self.signal == "buySignal"

    def should_short(self) -> bool:
        return self.vars["shortTradesEnabled"] and self.signal == "sellSignal"

    def should_cancel(self) -> bool:
        return True

    def go_long(self):
        qty = max(min(round(self.risk_qty_long(), self.qty_precision), (self.available_margin - 1)/ self.price), 0)
        
        if qty == 0:
            return

        self.buy = qty, self.price

        stop_loss = self.price - self.atr * self.hp["long_slMult"]
        take_profit = self.price + self.atr * self.hp["long_tpMult"]
        self.stop_loss = qty, stop_loss
        self.take_profit = qty, take_profit
        

    def go_short(self):
        qty = max(min(round(self.risk_qty_short(), self.qty_precision), (self.available_margin - 1)/ self.price), 0)

        if qty == 0:
            return

        self.sell = qty, self.price

        stop_loss = self.price + self.atr * self.hp["short_slMult"]
        take_profit = self.price - self.atr * self.hp["short_tpMult"]
        self.stop_loss = qty, stop_loss
        self.take_profit = qty, take_profit

    

