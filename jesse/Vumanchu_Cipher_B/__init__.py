from cmath import nan
from operator import truediv
from time import gmtime
from jesse.strategies import Strategy, cached
import jesse.indicators as ta
from jesse import utils
import lib 
import numpy as np
from jesse.helpers import get_candle_source, slice_candles
import tulipy as ti
import math

 
class Vumanchu_Ciper_B(Strategy):

    def __init__(self):
        super().__init__()
        self.vars["wtShow"]                 = True          #Show WaveTrend
        self.vars["wtBuyShow"]              = True          #Show Buy dots
        self.vars["wtGoldShow"]             = False         #Showd Gold dots
        self.vars["wtSellShow"]             = True          #Show Sell dots
        self.vars["wtDivShow"]              = False         #Show Div dots
        self.vars["vwapShow"]               = False         #Show  Fast WT
        self.vars["wtChannelLen"]           = 9             #WT Channel Length
        self.vars["wtAverageLen"]           = 12            #WT Average Length
        self.vars["wtMASource"]             = "hlc3"        #WT MA Source  
        self.vars["wtMALen"]                = 3             #WT MA Length
        self.vars["obLevel"]                = 53            #WT OverBought Level 1
        self.vars["obLevel2"]               = 60            #WT OverBought Level 2
        self.vars["obLevel3"]               = 100           #WT OverBought Level 3
        self.vars["osLevel"]                = -53           #WT OverSold Level 1
        self.vars["osLevel2"]               = -60           #WT OverSold Level 1      
        self.vars["osLevel3"]               = -75           #WT OverSold Level 1      
        self.vars["wtShowDiv"]              = False         #Show WT Regular Divergences
        self.vars["wtShowHiddenDiv"]        = False         #Show WT Hidden Divergences
        self.vars["showHiddenDiv_nl"]       = True          #Not apply OB/OS Limits on Hidden Divergences
        self.vars["wtDivOBLevel"]           = 45            #WT Bearish Divergences min
        self.vars["wtDivOSLevel"]           = -65           #WT Bullish Divergences min
        self.vars["wtDivOBLevel_addshow"]   = False         #Show 2nd WT Regular Divergences
        self.vars["wtDivOBLevel_add"]       = 15            #WT 2nd Bearish Divergence
        self.vars["wtDivOSLevel_add"]       = -40           #WT 2nd Bullish Divergence 15 min
        self.vars["rsiMFIShow"]             = True          #Show MFI
        self.vars["rsiMFIperiod"]           = 60            #MFI period
        self.vars["rsiMFIMultiplier"]       = 250           #MFI Area multiplier
        self.vars["rsiMFIPosY"]             = 2.5           #MFI Area Y Pos
        self.vars["rsiShow"]                = False         #Show RSI
        self.vars["rsiSRC"]                 = 'close'       #RSI Source
        self.vars["rsiLen"]                 = 14            #RSI Length
        self.vars["rsiShowDiv"]             = False         #Show RSI Regular Divergences
        self.vars["rsiShowHiddenDiv"]       = False         #Show RSI Hidden Divergences
        self.vars["rsiDivOBLevel"]          = 60            #RSI Bearish Divergence min
        self.vars["rsiDivOSLevel"]          = 30            #RSI Bullish Divergence mmin
        self.vars["stochShow"]              = False         #Show Stochastic RSI
        self.vars["stochUseLog"]            = True          #Use Log?
        self.vars["stochAvg"]               = False         #Use Average of both K & D
        self.vars["stochSRC"]               = 'close'       #Stochastic RSi Source
        self.vars["stochLen"]               = 14            #Stochastic RSI Length
        self.vars["stochRsiLen"]            = 14            #RSI Length
        self.vars["stochKSmooth"]           = 3             #Stochastic RSI K Smooth
        self.vars["stochDSmooth"]           = 3             #Stochastic RSI D Smooth
        self.vars["stochShowDiv"]           = False         #Show Stoch Regular Divergences
        self.vars["stochShowHiddenDiv"]     = False         #Show Stoch Hidden Divergences
        self.vars["tcLine"]                 = False         #Show Schaff TC Line
        self.vars["tcSRC"]                  = 'close'       #Schaff TC Source
        self.vars["tclength"]               = 10            #Schaff TC
        self.vars["tcfastlength"]           = 23            #Schaff TC Fast Length
        self.vars["tcslowlength"]           = 50            #Schaff TC Slow Length
        self.vars["tcfactor"]               = 0.5           #Schaff TC Factor
        self.vars["sommiFlagShow"]          = False         #Show Sommi Flag
        self.vars["sommiShowVwap"]          = False         #Show Sommi F. Wave
        self.vars["sommiVwapTF"]            = "720"         #Sommi F. Wave timeframe    
        self.vars["sommiVwapBearLevel"]     = 0             #F. Wave Bear Level (less than)
        self.vars["sommiVwapBullLevel"]     = 0             #F. Wave Bull Level (more than)
        self.vars["soomiFlagWTBearLevel"]   = 0             #WT Bear Level (less than)
        self.vars["soomiFlagWTBullLevel"]   = 0             #WT Bull Level (more than)
        self.vars["soomiRSIMFIBearLevel"]   = 0             #Money Flow Bear Level (less than)
        self.vars["soomiRSIMFIBullLevel"]   = 0             #Money Flow Bull Level (more than)
        self.vars["sommiDiamondShow"]       = False         #Show Sommi Diamond
        self.vars["sommiHTCRes"]            = '60'          #HTF Candle Res. 1
        self.vars["sommiHTCRes2"]           = '240'         #HTF Candle Res. 2
        self.vars["sommiHTCRes"]            = '60'          #HTF Candle Res. 1
        self.vars["soomiDiamondWTBearLevel"]= 0             #WT Bear Level (more than)
        self.vars["soomiDiamondWTBullLevel"]= 0             #WT Bull Level (less than)
        self.vars["macdWTColorsShow"]       = False         #Show MACD Colors
        self.vars["macdWTColorsTF"]         = '240'         #MACD Colors MACD TF
        self.vars["darkMode"]               = False         #Dark mode

     

    def hyperparameters():
        return [ 
            {'name': 'rsiOversold', 'title': 'RSI OVerSold', 'type': int, 'min': 50, 'max': 100, 'default': 30},
            {'name': 'rsiOverbought', 'title': 'RSI OverBought', 'type': int, 'min': 0, 'max':50,'default':60},
            {'name': 'ema50', 'title': 'EMA 50', 'type': int, 'default': 50},
            {'name': 'ema200', 'title': 'EMA 200', 'type': int, 'default': 200},
            {'name': 'usr_risk', 'title':  'Equity Risk (%)', 'type': int, 'min': 1, 'max': 100, 'default': 5},
            {'name': 'slMult', 'title': 'Stop Loss Mult', 'type': float, 'min': 0.1, 'max': 100, 'default': 1.5},
            {'name': 'tpMult', 'title': 'Stop Loss Mult', 'type': float, 'min': 0.1, 'max': 100, 'default': 2.9},
            {'name': 'atr_valu', 'title': 'ATR (Period)', 'type': int, 'min': 1, 'max': 500, 'default': 14},
slMult = input(1.5,title = ' Stop Loss Multiplier')
tpMult = input(2.9, title = ' Take Profit Multiplier')


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
    
    # f_top_fractal(src) => src[4] < src[2] and src[3] < src[2] and src[2] > src[1] and src[2] > src[0]
    def f_top_fractal(self, src) -> bool:
        return src[4] < src[2] and src[3] < src[2] and src[2] > src[1] and src[2] > src[0]

    # f_bot_fractal(src) => src[4] > src[2] and src[3] > src[2] and src[2] < src[1] and src[2] < src[0]
    def f_bot_fractal(self, src) -> bool:
        return src[4] > src[2] and src[3] > src[2] and src[2] < src[1] and src[2] < src[0]

    # f_fractalize(src) => f_top_fractal(src) ? 1 : f_bot_fractal(src) ? -1 : 0
    def f_fractalize(self, src):
        if self.f_top_fractal(src):
            return 1
        else:
            if self.f_bot_fractal(src):
                return -1
            else:
                return 0
    
    # f_findDivs(src, topLimit, botLimit, useLimits) =>
    #     fractalTop = f_fractalize(src) > 0 and (useLimits ? src[2] >= topLimit : true) ? src[2] : na
    #     fractalBot = f_fractalize(src) < 0 and (useLimits ? src[2] <= botLimit : true) ? src[2] : na
    #     highPrev = valuewhen(fractalTop, src[2], 0)[2]
    #     highPrice = valuewhen(fractalTop, high[2], 0)[2]
    #     lowPrev = valuewhen(fractalBot, src[2], 0)[2]
    #     lowPrice = valuewhen(fractalBot, low[2], 0)[2]
    #     bearSignal = fractalTop and high[2] > highPrice and src[2] < highPrev
    #     bullSignal = fractalBot and low[2] < lowPrice and src[2] > lowPrev
    #     bearDivHidden = fractalTop and high[2] < highPrice and src[2] > highPrev
    #     bullDivHidden = fractalBot and low[2] > lowPrice and src[2] < lowPrev
    #     [fractalTop, fractalBot, lowPrev, bearSignal, bullSignal, bearDivHidden, bullDivHidden]
    def f_findDivs(self, src, topLimit, botLimit, useLimits) -> bool:
        #     fractalTop = f_fractalize(src) > 0 and (useLimits ? src[2] >= topLimit : true) ? src[2] : na
        if useLimits:
            ft_ul = src[2] >= topLimit
        else: 
            ft_ul = True
        
        if ft_ul:
            ft = src[2]
        else:
            ft = nan
        fractalTop = self.f_fractalize(src) > 0 and ft

        #     fractalBot = f_fractalize(src) < 0 and (useLimits ? src[2] <= botLimit : true) ? src[2] : na
        if useLimits:
            ft_ul = src[2] <= botLimit
        else: 
            ft_ul = True
        
        if ft_ul:
            ft = src[2]
        else:
            ft = nan
        fractalBot = self.f_fractalize(src) < 0 and ft
        
        #     highPrev = valuewhen(fractalTop, src[2], 0)[2]
        highPrev = lib.valuewhen(fractalTop, src[2], 0)[2]

        #     highPrice = valuewhen(fractalTop, high[2], 0)[2]
        highPrice = lib.valuewhen(fractalTop, self.high[2], 0)[2]

        
        #     lowPrev = valuewhen(fractalBot, src[2], 0)[2]
        lowPrev = lib.valuewhen(fractalBot, src[2], 0)[2]

        #     lowPrice = valuewhen(fractalBot, low[2], 0)[2]
        lowPrice = lib.valuewhen(fractalBot, self.low[2], 0)[2]

        #     bearSignal = fractalTop and high[2] > highPrice and src[2] < highPrev
        bearSignal = fractalTop and self.high[2] > highPrice and src[2] < highPrev

        #     bullSignal = fractalBot and low[2] < lowPrice and src[2] > lowPrev
        bullSignal = fractalBot and self.low[2] < lowPrice and src[2] > lowPrev

        #     bearDivHidden = fractalTop and high[2] < highPrice and src[2] > highPrev
        bearDivHidden = fractalTop and self.high[2] < highPrice and src[2] > highPrev

        #     bullDivHidden = fractalBot and low[2] > lowPrice and src[2] < lowPrev
        bullDivHidden = fractalBot and self.low[2] < highPrice and src[2] < lowPrev

        #     [fractalTop, fractalBot, lowPrev, bearSignal, bullSignal, bearDivHidden, bullDivHidden]
        return (fractalTop, fractalBot, lowPrev, bearSignal, bullSignal, bearDivHidden, bullDivHidden)

    # f_rsimfi(_period, _multiplier, _tf) => security(syminfo.tickerid, _tf, sma(((close - open) / (high - low)) * _multiplier, _period) - rsiMFIPosY)
    def f_rsimfi(self, _period, _multiplier, _tf):
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

    def f_wavetrend(self, src, chlen, avg, malen, tf):
        #     tfsrc = security(syminfo.tickerid, tf, src)
        #     esa = ema(tfsrc, chlen)
        esa = ti.ema(src, chlen)
        np.nan_to_num(esa, copy=False)
        #     de = ema(abs(tfsrc - esa), chlen)
        de  = ti.ema(abs(src - esa), chlen)
        np.nan_to_num(de, copy=False)
        #     ci = (tfsrc - esa) / (0.015 * de)
        ci  = (src - esa) / (0.015 * de)
        np.nan_to_num(ci, copy=False)
        #     wt1 = security(syminfo.tickerid, tf, ema(ci, avg))
        wt1 = ti.ema(ci, avg)
        np.nan_to_num(wt1, copy=False)
        #     wt2 = security(syminfo.tickerid, tf, sma(wt1, malen))
        wt2 = ti.sma(wt1, malen)
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
        return (wt1[-1], wt2[-1], wtOversold, wtOverbought, wtCross, wtCrossUp, wtCrossDown, wtCrosslast, wtCrossUplast, wtCrossDownlast, wtVwap)

    # // Schaff Trend Cycle
    # f_tc(src, length, fastLength, slowLength) =>
    #     ema1 = ema(src, fastLength)
    #     ema2 = ema(src, slowLength)
    #     macdVal = ema1 - ema2	
    #     alpha = lowest(macdVal, length)
    #     beta = highest(macdVal, length) - alpha
    #     gamma = (macdVal - alpha) / beta * 100
    #     gamma := beta > 0 ? gamma : nz(gamma[1])
    #     delta = gamma
    #     delta := na(delta[1]) ? delta : delta[1] + tcfactor * (gamma - delta[1])
    #     epsilon = lowest(delta, length)
    #     zeta = highest(delta, length) - epsilon
    #     eta = (delta - epsilon) / zeta * 100
    #     eta := zeta > 0 ? eta : nz(eta[1])
    #     stcReturn = eta
    #     stcReturn := na(stcReturn[1]) ? stcReturn : stcReturn[1] + tcfactor * (eta - stcReturn[1])
    #     stcReturn
    def f_tc(self, src, length, fastLength, slowLength):
        #     ema1 = ema(src, fastLength)
        ema1 = ta.ema(src, fastLength)
        #     ema2 = ema(src, slowLength)
        ema2 = ta.ema(src, slowLength)
        #     macdVal = ema1 - ema2	
        macdVal = ema1 - ema2
        #     alpha = lowest(macdVal, length)
        alpha = min(macdVal, length)
        #     beta = highest(macdVal, length) - alpha
        beta = max(macdVal, length) - alpha
        #     gamma = (macdVal - alpha) / beta * 100
        gamma = (macdVal - alpha) / beta * 100
        #     gamma := beta > 0 ? gamma : nz(gamma[1])
        if beta > 0:
            gamma = gamma
        else:
            gamma = lib.nz(gamma[1])
        #     delta = gamma
        delta = gamma
        #     delta := na(delta[1]) ? delta : delta[1] + tcfactor * (gamma - delta[1])
        if lib.na(delta[1]):
            delta = delta
        else:
            delta = delta[1] + self.vars["tcfactor"] * (gamma - delta[1]) 
        #     epsilon = lowest(delta, length)
        epsilon = min(delta, length)
        #     zeta = highest(delta, length) - epsilon
        zeta = max(delta, length) - epsilon
        #     eta = (delta - epsilon) / zeta * 100
        eta = (delta - epsilon) / zeta * 100
        #     eta := zeta > 0 ? eta : nz(eta[1])
        if zeta > 0:
            ete = eta
        else:
            eta = lib.nz(eta[1])
        #     stcReturn = eta
        stcReturn = eta
        #     stcReturn := na(stcReturn[1]) ? stcReturn : stcReturn[1] + tcfactor * (eta - stcReturn[1])
        if lib.na(stcReturn[1]):
            stcReturn = stcReturn
        else:
            stcReturn = stcReturn[1] + self.vars["tcfactor"] * (eta - stcReturn[1])
        #     stcReturn
        return stcReturn

    # // Stochastic RSI
    # f_stochrsi(_src, _stochlen, _rsilen, _smoothk, _smoothd, _log, _avg) =>
    #     src = _log ? log(_src) : _src
    #     rsi = rsi(src, _rsilen)
    #     kk = sma(stoch(rsi, rsi, rsi, _stochlen), _smoothk)
    #     d1 = sma(kk, _smoothd)
    #     avg_1 = avg(kk, d1)
    #     k = _avg ? avg_1 : kk
    #     [k, d1]
    def f_stochrsi(self,_src, _stochlen, _rsilen, _smoothk, _smoothd, _log, _avg):
        #     src = _log ? log(_src) : _src
        if _log:
            src = math.log(_src)
        else:
            src = _src
        #     rsi = rsi(src, _rsilen)
        rsi = ta.rsi(src, _rsilen)
        #     kk = sma(stoch(rsi, rsi, rsi, _stochlen), _smoothk)
        kk = ta.sma(ta.stoch(rsi, rsi, rsi, _stochlen), _smoothk)
        #     d1 = sma(kk, _smoothd)
        #     avg_1 = avg(kk, d1)
        #     k = _avg ? avg_1 : kk
        #     [k, d1]

    # // MACD
    # f_macd(src, fastlen, slowlen, sigsmooth, tf) =>
    #     fast_ma = security(syminfo.tickerid, tf, ema(src, fastlen))
    #     slow_ma = security(syminfo.tickerid, tf, ema(src, slowlen))
    #     macd = fast_ma - slow_ma,
    #     signal = security(syminfo.tickerid, tf, sma(macd, sigsmooth))
    #     hist = macd - signal
    #     [macd, signal, hist]


    def should_long(self) -> bool:
        return False

    def should_short(self) -> bool:
        return False

    def should_cancel(self) -> bool:
        return True

    def go_long(self):
        pass

    def go_short(self):
        pass
