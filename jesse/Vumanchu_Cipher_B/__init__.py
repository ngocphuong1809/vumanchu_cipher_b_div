
from selectors import EpollSelector
import string
from jesse.strategies import Strategy, cached
import jesse.indicators as ta
from jesse import utils
import numpy as np
import jesse.helpers as jh
from wt import wt
from rsimfi import rsimfi
import utils as tu

 
class Vumanchu(Strategy):

    def __init__(self):
        super().__init__()
        self.debug_log                              = 1          ## Turn on for debug logging to CSV, 
        self.price_precision                        = 2 		#self._price_precision()
        self.hps                                    = []
        self.svars                                  = {}
        self.lvars                                  = {}
        self.data_header                            = ['Index', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Action', 'Cmt', 'Starting Balance', 'Finishing Balance', 'Profit', 'Qty','SL','TP']
        self.data_log                               = []
        self.indicator_header                       = ['Index', 'Time', 'Cmt', 'wt1', 'wt2', 'rsiMFI']
        self.indicator_log                          = []

        self.pine_log                               = ''
        self.pine_orderid                           = 0
        self.l_wt1                                  = 0
        self.l_wt2                                  = 0
        self.s_wt1                                  = 0
        self.s_wt2                                  = 0
        self.sliced_candles                         = {}
        self.is_optimising                          = False
        self.params_overdrive                       = True          ## Overwrite params to file, turn off for production, turn on for testing / optimizing

        self.pre_index                              = 0
        self.qty                                    = 0

        self.long_sl                                = 0
        self.long_tp                                = 0
        self.short_sl                               = 0
        self.short_tp                               = 0

        self.initial_entry                          = 0
        self.starting_capital                       = 0

        self.onlyLong                               = False          #True: Only Long Position
        self.onlyShort                              = False         #True: Only Short Position
        self.LS                                     = True         #True: Long and Short Position

        # self.vars["wtChannelLen"]                   = 9             #WT Channel Length
        # self.vars["wtAverageLen"]                   = 12            #WT Average Length
        # self.vars["wtMASource"]                     = "hlc3"        #WT MA Source  
        # self.vars["wtMALen"]                        = 3             #WT MA Length
        # self.vars["obLevel"]                        = 53            #WT OverBought Level 1
        # self.vars["osLevel"]                        = -53           #WT OverSold Level 1
  
        self.vars["rsiMFIperiod"]                   = 60            #MFI period
        self.vars["rsiMFIMultiplier"]               = 250           #MFI Area multiplier
        self.vars["rsiMFIPosY"]                     = 2.5           #MFI Area Y Pos

        self.vars["atr_valu"]                       = 14            #ATR (Period)

        self.vars["longTradesEnabled"]              = True          # Long Trades (Filter)
        self.vars["shortTradesEnabled"]             = True          # Short Trades (Filter)

        self.vars["botRisk"]                        = 3.0           #Bot risk % each entry
 
        self.svars["slMult"]                        = 1.6
        self.svars["tpMult"]                        = 2.9
        self.svars["fast_ema"]                      = 50
        self.svars["slow_ema"]                      = 200
        self.svars["wtChannelLen"]                  = 9
        self.svars["wtAverageLen"]                  = 12
        self.svars["wtMASource"]                    = 3
        self.svars["wtMALen"]                       = 3
        self.svars["obLevel"]                       = 53
        self.svars["osLevel"]                       = -53

        self.lvars["slMult"]                        = 1.6
        self.lvars["tpMult"]                        = 2.9
        self.lvars["fast_ema"]                      = 50
        self.lvars["slow_ema"]                      = 200
        self.lvars["wtChannelLen"]                  = 9
        self.lvars["wtAverageLen"]                  = 12
        self.lvars["wtMASource"]                    = 3
        self.lvars["wtMALen"]                       = 3
        self.lvars["obLevel"]                       = 53
        self.lvars["osLevel"]                       = -53
        


    def hyperparameters(self):
        return [ 
            {'name': 'long_fast_ema', 'title': 'Fast EMA (EMA 50)', 'type': int, 'min': 30, 'max': 100, 'default': 50},
            {'name': 'long_slow_ema', 'title': 'Slow EMA (EMA 200)', 'type': int, 'min': 150, 'max': 400, 'default': 200},
            {'name': 'long_slMult', 'title': 'Long Stop Loss Mult', 'type': float, 'min': 1.0, 'max': 3.0, 'default': 1.6},
            {'name': 'long_tpMult', 'title': 'Long Take Profit Mult', 'type': float, 'min': 2.0, 'max': 6.0, 'default': 2.9},    
            {'name': 'long_wtChannelLen', 'title': 'WT Channel Length', 'type': int, 'min': 7, 'max': 11, 'default': 9},
            {'name': 'long_wtAverageLen', 'title': 'WT Average Length', 'type': int, 'min': 10, 'max': 14, 'default': 12},
            {'name': 'long_wtMASource', 'title': 'WT MA Source', 'type': int, 'min': 2, 'max': 4, 'default': 3},
            {'name': 'long_wtMALen', 'title': 'WT MA Length', 'type': int, 'min': 2, 'max': 4, 'default': 3},
            {'name': 'long_obLevel', 'title': 'WT Overbought Level 1', 'type': int, 'min': 50, 'max': 56, 'default': 53},
            {'name': 'long_osLevel', 'title': 'WT Oversold Level 1', 'type': int, 'min': -56, 'max': -50, 'default': -53},

            {'name': 'short_fast_ema', 'title': 'Fast EMA (EMA 50)', 'type': int, 'min': 30, 'max': 100, 'default': 50},
            {'name': 'short_slow_ema', 'title': 'Slow EMA (EMA 200)', 'type': int, 'min': 150, 'max': 400, 'default': 200},
            {'name': 'short_slMult', 'title': 'Long Stop Loss Mult', 'type': float, 'min': 1.0, 'max': 3.0, 'default': 1.6},
            {'name': 'short_tpMult', 'title': 'Long Take Profit Mult', 'type': float, 'min': 2.0, 'max': 6.0, 'default': 2.9},    
            {'name': 'short_wtChannelLen', 'title': 'WT Channel Length', 'type': int, 'min': 7, 'max': 11, 'default': 9},
            {'name': 'short_wtAverageLen', 'title': 'WT Average Length', 'type': int, 'min': 10, 'max': 14, 'default': 12},
            {'name': 'short_wtMASource', 'title': 'WT MA Source', 'type': int, 'min': 2, 'max': 4, 'default': 3},
            {'name': 'short_wtMALen', 'title': 'WT MA Length', 'type': int, 'min': 2, 'max': 4, 'default': 3},
            {'name': 'short_obLevel', 'title': 'WT Overbought Level 1', 'type': int, 'min': 50, 'max': 56, 'default': 53},
            {'name': 'short_osLevel', 'title': 'WT Oversold Level 1', 'type': int, 'min': -56, 'max': -50, 'default': -53}
        ]


    def on_first_candle(self):
        # print("On First Candle")
        if jh.is_live():
            self.price_precision = self._price_precision()
            self.qty_precision = self._qty_precision()
        else:
            self.price_precision = 2
            self.qty_precision = 2

        # Load params from file if not loaded
        file_name = "params/" + type(self).__name__ + '_' + self.symbol + '_' + self.timeframe +'.json'
        vars = {}
        file_exists = jh.file_exists(file_name)
        if file_exists:
            fvars = tu.load_params(file_name)
            param_update = False
            if len(self.vars) + len(self.lvars) + len(self.svars) != len(fvars['common_vars']) + len(fvars['long_vars']) + len(fvars['short_vars']):
                # print("Params file is updated")
                param_update = True
            if not self.params_overdrive:
                self.vars  = fvars['common_vars']
                self.lvars = fvars['long_vars']
                self.svars = fvars['short_vars']
            if param_update:
                vars['common_vars'] = self.vars
                vars['long_vars']   = self.lvars
                vars['short_vars']  = self.svars
                tu.save_params(file_name, vars)
               
        else:
            # Write default params
            vars['common_vars'] = self.vars
            vars['long_vars']   = self.lvars
            vars['short_vars']  = self.svars
            tu.save_params(file_name, vars)

        if jh.is_optimizing():
            self.svars["fast_ema"]                  = self.hp["long_fast_ema"]
            self.svars["slow_ema"]                  = self.hp["long_slow_ema"]
            self.svars["slMult"]                    = self.hp["long_slMult"]
            self.svars["tpMult"]                    = self.hp["long_tpMult"]
            self.svars["wtChannelLen"]              = self.hp["long_wtChannelLen"]
            self.svars["wtAverageLen"]              = self.hp["long_wtAverageLen"]
            self.svars["wtMASource"]                = self.hp["long_wtMASource"]
            self.svars["wtMALen"]                   = self.hp["long_wtMALen"]
            self.svars["obLevel"]                   = self.hp["long_obLevel"]
            self.svars["osLevel"]                   = self.hp["long_osLevel"]

            self.lvars["fast_ema"]                  = self.hp["short_fast_ema"]
            self.lvars["slow_ema"]                  = self.hp["short_slow_ema"]
            self.lvars["slMult"]                    = self.hp["short_slMult"]
            self.lvars["tpMult"]                    = self.hp["short_tpMult"]
            self.lvars["wtChannelLen"]              = self.hp["short_wtChannelLen"]
            self.lvars["wtAverageLen"]              = self.hp["short_wtAverageLen"]
            self.lvars["wtMASource"]                = self.hp["short_wtMASource"]
            self.lvars["wtMALen"]                   = self.hp["short_wtMALen"]
            self.lvars["obLevel"]                   = self.hp["short_obLevel"]
            self.lvars["osLevel"]                   = self.hp["short_osLevel"]

        
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

    #for long
    @property
    @cached
    def long_fast_ema(self):
        return ta.ema(self.candles, self.hp["long_fast_ema"])

    @property
    @cached
    def long_slow_ema(self):
        return ta.ema(self.candles, self.hp["long_slow_ema"])

    @property
    @cached
    def long_emapullback(self) -> bool:
        return self.close > self.long_fast_ema - (self.long_fast_ema*0.05) and self.close < self.long_fast_ema + (self.long_fast_ema*0.05)
    @property
    @cached
    def emaLong(self) -> bool:
        return self.close > self.long_slow_ema and self.long_emapullback

    #for short
    @property
    @cached
    def short_fast_ema(self):
        return ta.ema(self.candles, self.hp["short_fast_ema"])

    @property
    @cached
    def short_slow_ema(self):
        return ta.ema(self.candles, self.hp["short_slow_ema"])

    @property
    @cached
    def short_emapullback(self) -> bool:
        return self.close > self.short_fast_ema - (self.short_fast_ema*0.05) and self.close < self.short_fast_ema + (self.short_fast_ema*0.05)
    
    @property
    def emaShort(self) -> bool:
        return self.close < self.short_slow_ema and self.short_emapullback
    
    @property    
    @cached
    def atr(self):
        return ta.atr(self.candles, self.vars["atr_valu"])

# f_rsimfi(_period, _multiplier, _tf) => security(syminfo.tickerid, _tf, sma(((close - open) / (high - low)) * _multiplier, _period) - rsiMFIPosY)
    @property
    @cached
    def rsiMFI(self):
        rf = rsimfi(self.candles, self.vars["rsiMFIperiod"],self.vars["rsiMFIMultiplier"])
        rmfi = rf - self.vars["rsiMFIPosY"] 
        return rmfi

    def risk_qty_long(self):
        risk_loss = self.capital * self.vars["botRisk"]  / (self.atr * self.hp["long_slMult"] * 100) 
        return risk_loss

    def risk_qty_short(self):
        risk_loss = self.capital * self.vars["botRisk"]  / (self.atr * self.hp["short_slMult"] * 100) 
        return risk_loss

    @property
    def signal(self):
        signal = None
        # // Calculates WaveTrend
        cmt = ''
        if self.hp["long_wtMASource"] == 2:
            self.hp["long_wtMASource"] = 'hl2'
        elif self.hp["long_wtMASource"] == 3:
            self.hp["long_wtMASource"] = 'hlc3'
        elif self.hp["long_wtMASource"] == 4:
            self.hp["long_wtMASource"] = 'ohlc4'
        [long_wt1, long_wt2, long_wtCross, long_wtCrossUp, long_wtCrossDown, long_wtOversold, long_wtOverbought] = wt(self.candles, self.hp["long_wtChannelLen"], self.hp["long_wtAverageLen"], self.hp["long_wtMALen"], self.hp["long_obLevel"], self.hp["long_osLevel"], self.hp["long_wtMASource"])
        
        if self.hp["short_wtMASource"] == 2:
            self.hp["short_wtMASource"] = 'hl2'
        elif self.hp["short_wtMASource"] == 3:
            self.hp["short_wtMASource"] = 'hlc3'
        elif self.hp["short_wtMASource"] == 4:
            self.hp["short_wtMASource"] = 'ohlc4'
        [short_wt1, short_wt2, short_wtCross, short_wtCrossUp, short_wtCrossDown, short_wtOversold, short_wtOverbought] = wt(self.candles, self.hp["short_wtChannelLen"], self.hp["short_wtAverageLen"], self.hp["short_wtMALen"], self.hp["short_obLevel"], self.hp["short_osLevel"], self.hp["short_wtMASource"])
        
        # //LA WT BUY/SELL
        # wtBuy = wt2 <=0 and wt1 <=0 and rsiMFI >0 and emaLong
        # wtSell = wt2 >=0 and wt1 >=0 and rsiMFI <0 and emaShort

        # buySignal = wtCross and wtCrossUp and wtOversold and wtBuy
        if long_wtCross and long_wtCrossUp and long_wtOversold and long_wt2[-1] <= 0 and long_wt1[-1] <= 0 and self.rsiMFI > 0 and self.emaLong:
            signal = "buySignal"
            cmt = 'LongCond'

        # sellSignal = wtCross and wtCrossDown and wtOverbought and wtSell
        if short_wtCross and short_wtCrossDown and short_wtOverbought and short_wt2[-1] >= 0 and short_wt1[-1] >= 0 and self.rsiMFI < 0 and self.emaShort:
            signal = "sellSignal"
            cmt = 'ShortCond'

        if self.debug_log >= 1 and self.pre_index != self.index:
            if cmt == 'LongCond':
                self.indicator_log.append([self.index, self.ts, cmt, long_wt1[-1], long_wt2[-1], self.rsiMFI])
                self.pre_index = self.index
            elif cmt == 'ShortCond':
                self.indicator_log.append([self.index, self.ts, cmt, short_wt1[-1], short_wt2[-1], self.rsiMFI])
                self.pre_index = self.index


        return signal

    def should_long(self) -> bool:
        if self.onlyLong or self.LS:
            qty = max(min(round(self.risk_qty_long(), self.qty_precision), (self.available_margin - 1)/ self.price), 0)
            if qty != 0 and self.vars["longTradesEnabled"] and self.signal == "buySignal":
                return True
        else:
            return False

    def should_short(self) -> bool:
        if self.onlyShort or self.LS:
            qty = max(min(round(self.risk_qty_short(), self.qty_precision), (self.available_margin - 1)/ self.price), 0)
            if qty != 0 and self.vars["shortTradesEnabled"] and self.signal == "sellSignal":
                return True
        else:
            return False

    def should_cancel(self) -> bool:
        return True

    def go_long(self):

        qty = max(min(round(self.risk_qty_long(), self.qty_precision), (self.available_margin - 1)/ self.price), 0)
        self.qty = qty

        self.starting_balance = self.capital
        
        self.buy = qty, self.price
        self.initial_entry = self.price
        self.long_sl = self.price - self.atr * self.hp["long_slMult"]
        self.long_tp = self.price + self.atr * self.hp["long_tpMult"]
        self.stop_loss = qty, self.long_sl
        self.take_profit = qty, self.long_tp

        if self.debug_log >= 1:    
         
            self.pine_entryts = self.current_candle[0]
            self.pine_cmt = 'L[' #cmt
            self.data_log.append([self.index, self.ts, self.open, self.close, self.high, self.low, self.current_candle[5], "Entry Long", '',
                self.starting_balance, self.capital, self.capital - self.starting_balance , qty, self.long_sl, self.long_tp])
        
    def go_short(self):

        qty = max(min(round(self.risk_qty_short(), self.qty_precision), (self.available_margin - 1)/ self.price), 0)

        self.qty = qty
        
        self.starting_balance = self.capital
        
        self.sell = qty, self.price
        self.initial_entry = self.price
        self.short_sl = self.price + self.atr * self.hp["short_slMult"]
        self.short_tp = self.price - self.atr * self.hp["short_tpMult"]
        self.stop_loss = qty, self.short_sl
        self.take_profit = qty, self.short_tp

        if self.debug_log >= 1:   
        
            self.pine_entryts = self.current_candle[0]
            self.pine_cmt = 'L[' #cmt
            self.data_log.append([self.index, self.ts, self.open, self.close, self.high, self.low, self.current_candle[5], "Entry Short", '', self.starting_balance,
                self.capital, self.capital - self.starting_balance , qty, self.short_sl, self.short_tp])

    def view_orders(self,orders):
        for order in orders:
            print(f"Type {order.type} active {order.is_active} price ={order.price}")

    def cancel_stop_orders(self,orders):
        for order in orders:
            if order.type == "STOP":
                order.cancel()
 
    def on_close_position(self, order):
        cmt = ''

        if self.debug_log >= 1 and self.short_sl > 0:
            self.pine_short(self.pine_cmt + "]", self.pine_entryts, self.qty, self.current_candle[0], self.short_sl, self.short_tp)
   
        if self.debug_log >= 1 and self.long_sl > 0:
            self.pine_long(self.pine_cmt + "]", self.pine_entryts, self.qty, self.current_candle[0], self.long_sl, self.long_tp)

        price = order.price
        if self.debug_log >= 1:
            if (self.short_sl > 0 and price < self.initial_entry) or (self.long_sl and price > self.initial_entry):
                wl = 'Win'
            else:
                wl = 'Lose'
            if price == self.short_sl or self.price == self.long_sl:
                cmt = f"Exit: {wl} Stop Loss"
            elif price == self.short_tp or self.price == self.long_tp:
                cmt = f"Exit: {wl} Take Profit"
            
            self.data_log.append([self.index, self.ts, self.open, self.close, self.high, self.low, self.current_candle[5], cmt, wl, self.starting_balance, self.capital, self.capital - self.starting_balance , self.position.qty])

        self.short_sl = 0
        self.short_tp = 0
    
        self.long_sl = 0
        self.long_tp = 0

        self.initial_entry = 0  
    
    def watch_list(self):
        return [
            
        ]
    def terminate(self):
        print(f'Backtest is done, Total Capital : {self.capital}')
        if self.debug_log >= 1:
            print(self.indicator_log)
            tu.write_csv(type(self).__name__ +'-' + self.symbol +'-' + self.timeframe, self.data_header, self.data_log)
            tu.write_csv(type(self).__name__ +'-' + self.symbol +'-' + self.timeframe + '-indicator', self.indicator_header, self.indicator_log)
            tu.write_pine(type(self).__name__ +'-' + self.symbol +'-' + self.timeframe, self.metrics['starting_balance'], self.pine_log)

    def pine_long(self, comment, ts, qty, ts_out, sl, tp):
        self.pine_orderid += 1
        ts = int(ts) + jh.timeframe_to_one_minutes(self.timeframe) * 60 * 1000
        
        self.pine_log += f'strategy.entry("{self.pine_orderid}", strategy.long, {qty}, {tp:.2f}, when = time_close == {ts:.0f}, comment="{comment}")\n'
        self.pine_log += f'strategy.exit("{self.pine_orderid}","{self.pine_orderid}", stop = {sl:.2f}, limit = {tp:.2f}, when = time_close >= {ts_out:.0f})\n'

    def pine_short(self, comment, ts, qty, ts_out, sl, tp):
        self.pine_orderid += 1
        ts = int(ts) + jh.timeframe_to_one_minutes(self.timeframe) * 60 * 1000
        
        self.pine_log += f'strategy.entry("{self.pine_orderid}", strategy.short, {qty}, {tp:.2f}, when = time_close == {ts:.0f}, comment="{comment}")\n'
        self.pine_log += f'strategy.exit("{self.pine_orderid}","{self.pine_orderid}", stop = {sl:.2f}, limit = {tp:.2f}, when = time_close >= {ts_out:.0f})\n'


