
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
        # self.vars["rsiOversold"]                    = 30            #RSI OverSold
        # self.vars["rsiOverbought"]                  = 60            #RSI OverBought

        self.vars["longTradesEnabled"]              = True          # Long Trades (Filter)
        self.vars["shortTradesEnabled"]             = True          # Short Trades (Filter)
        # self.vars["enableEntryTrailing"]            = False         # Enable/ Disable the trailing for entry position
       
        # self.vars["devEntryAtrMult"]                = 0.5           # Deviation ATR Mul  Multiplier to be used on the initial entrys` ATR to calculate the step for following the price, when the entry target is reached
        # self.vars["enterLongPosition"]              = False
        # self.vars["enterShortPosition"]             = False

        self.vars["botRisk"]                        = 3.0           #Bot risk % each entry
        # self.vars["botLeverage"]                    = 10.0          # Bot Leverage
        # self.vars["botPricepPrecision"]             = 4             #Bot Order Price Precision
        # self.vars["botBasePrecision"]               = 1             #Bot Order Coin Precision
 
        self.svars["slMult"]                        = 1.6
        self.svars["tpMult"]                        = 2.9
        self.svars["fast_ema"]                      = 50
        self.svars["slow_ema"]                      = 200

        self.lvars["slMult"]                        = 1.6
        self.lvars["tpMult"]                        = 2.9
        self.lvars["fast_ema"]                      = 50
        self.lvars["slow_ema"]                      = 200



    def hyperparameters(self):
        return [ 
            {'name': 'fast_ema', 'title': 'Fast EMA (EMA 50)', 'type': int, 'min': 30, 'max': 100, 'default': 50},
            {'name': 'slow_ema', 'title': 'Slow EMA (EMA 200)', 'type': int, 'min': 150, 'max': 400, 'default': 200},

            {'name': 'slMult', 'title': 'Long Stop Loss Mult', 'type': float, 'min': 1.0, 'max': 3.0, 'default': 1.6},
            {'name': 'tpMult', 'title': 'Long Take Profit Mult', 'type': float, 'min': 2.0, 'max': 6.0, 'default': 2.9},

            # {'name': 'short_slMult', 'title': 'Short Stop Loss Mult', 'type': float, 'min': 1.0, 'max': 3.0, 'default': 1.6},
            # {'name': 'short_tpMult', 'title': 'Short Take Profit Mult', 'type': float, 'min': 2.0, 'max': 6.0, 'default': 2.9},     
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
        # self.price_precision = self._price_precision()
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

            # print("Write params to file: " + file_name)
            # print("Common Vars: ", vars['common_vars'])
            # print("Long Vars: ", vars['long_vars'])
            # print("Short Vars: ", vars['short_vars'])

        if jh.is_optimizing():
            self.svars["fast_ema"]                  = self.hp["fast_ema"]
            self.svars["slow_ema"]                  = self.hp["slow_ema"]
            self.svars["slMult"]                    = self.hp["slMult"]
            self.svars["tpMult"]                    = self.hp["tpMult"]

            self.lvars["fast_ema"]                  = self.hp["fast_ema"]
            self.lvars["slow_ema"]                  = self.hp["slow_ema"]
            self.lvars["slMult"]                    = self.hp["slMult"]
            self.lvars["tpMult"]                    = self.hp["tpMult"]
        
          

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

    @property
    @cached
    def fast_ema(self):
        return ta.ema(self.candles, self.hp["fast_ema"])

    @property
    @cached
    def slow_ema(self):
        return ta.ema(self.candles, self.hp["slow_ema"])

    @property
    @cached
    def emapullback(self) -> bool:
        return self.close > self.fast_ema - (self.fast_ema*0.05) and self.close < self.fast_ema + (self.fast_ema*0.05)
    @property
    @cached
    def emaLong(self) -> bool:
        return self.close > self.slow_ema and self.emapullback

    @property
    def emaShort(self) -> bool:
        return self.close < self.slow_ema and self.emapullback
    
    @property    
    @cached
    def atr(self):
        return ta.atr(self.candles, self.vars["atr_valu"])

# f_rsimfi(_period, _multiplier, _tf) => security(syminfo.tickerid, _tf, sma(((close - open) / (high - low)) * _multiplier, _period) - rsiMFIPosY)
    @property
    @cached
    def rsiMFI(self):
        rf = rsimfi(self.candles, self.vars["rsiMFIperiod"],self.vars["rsiMFIMultiplier"])
        print(rf)
        rmfi = rf - self.vars["rsiMFIPosY"] 
        return rmfi

    def unit_qty_long(self):
        risk_loss = self.capital * self.vars["botRisk"]  / (self.atr * self.lvars["slMult"] * 100 / self.price) 
        return max(0, min(self.capital, risk_loss))

    def unit_qty_short(self):
        risk_loss = self.capital * self.vars["botRisk"]  / (self.atr * self.svars["slMult"]  * 100  / self.price) 
        return max(0, min(self.capital, risk_loss))

    def risk_qty_long(self):
        risk_loss = self.capital * self.vars["botRisk"]  / (self.atr * self.lvars["slMult"] * 100) 
        return risk_loss

    def risk_qty_short(self):
        risk_loss = self.capital * self.vars["botRisk"]  / (self.atr * self.svars["slMult"] * 100) 
        return risk_loss

    @property
    def signal(self):
        signal = None
        # // Calculates WaveTrend
        cmt = ''
    
        [wt1, wt2, wtCross, wtCrossUp, wtCrossDown, wtOversold, wtOverbought] = wt(self.candles, self.vars["wtChannelLen"], self.vars["wtAverageLen"], self.vars["wtMALen"], self.vars["obLevel"], self.vars["osLevel"], self.vars["wtMASource"])
        
        
        # //LA WT BUY/SELL
        # wtBuy = wt2 <=0 and wt1 <=0 and rsiMFI >0 and emaLong
        # wtSell = wt2 >=0 and wt1 >=0 and rsiMFI <0 and emaShort

        # buySignal = wtCross and wtCrossUp and wtOversold and wtBuy
        if wtCross and wtCrossUp and wtOversold and wt2[-1] <= 0 and wt1[-1] <= 0 and self.rsiMFI > 0 and self.emaLong:
            signal = "buySignal"
            cmt = 'LongCond'

        
    
        # sellSignal = wtCross and wtCrossDown and wtOverbought and wtSell
        if wtCross and wtCrossDown and wtOverbought and wt2[-1] >= 0 and wt1[-1] >= 0 and self.rsiMFI < 0 and self.emaShort:
            signal = "sellSignal"
            cmt = 'ShortCond'


        # Debuging
        # if (self.debug_log == 2 and signal == "sellSignal") or self.debug_log > 2:
        #     cmt = 'ShortCond'
        
        # self.data_log.append([self.index, self.ts, self.open, self.high, self.low, self.close, self.current_candle[5], \
        #         cmt, wt1, wt2, wtCross, wtCrossUp, wtCrossDown, wtOversold, wtOverbought, self.rsiMFI])
        
        if self.debug_log >= 1 and (cmt == 'LongCond' or cmt == 'ShortCond'):
            if self.pre_index != self.index:
                self.indicator_log.append([self.index, self.ts, cmt, wt1[-1], wt2[-1], self.rsiMFI])
                self.pre_index = self.index

        return signal

    

    def should_long(self) -> bool:
        qty = max(min(round(self.risk_qty_long(), self.qty_precision), (self.available_margin - 1)/ self.price), 0)
        if qty != 0 and self.vars["longTradesEnabled"] and self.signal == "buySignal":
            return True

    def should_short(self) -> bool:
        qty = max(min(round(self.risk_qty_short(), self.qty_precision), (self.available_margin - 1)/ self.price), 0)
        if qty != 0 and self.vars["shortTradesEnabled"] and self.signal == "sellSignal":
            return True

    def should_cancel(self) -> bool:
        return True

    def go_long(self):

        qty = max(min(round(self.risk_qty_long(), self.qty_precision), (self.available_margin - 1)/ self.price), 0)
        self.qty = qty

        self.starting_balance = self.capital
        
        self.buy = qty, self.price
        self.initial_entry = self.price
        self.long_sl = self.price - self.atr * self.lvars["slMult"]
        self.long_tp = self.price + self.atr * self.lvars["tpMult"]
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
        self.short_sl = self.price + self.atr * self.svars["slMult"]
        self.short_tp = self.price - self.atr * self.svars["tpMult"]
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
        # self.last_was_profitable = True
        # print(f"Close Position {self.price} {self.short_sl} {self.long_sl}")

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
    
    # def on_cancel(self):
        # self.pyramiding_levels = 0 

    def watch_list(self):
        return [
            
        ]
    def terminate(self):
        print(f'Backtest is done, Total Capital : {self.capital}')
        if self.debug_log >= 1:
            print(self.indicator_log)
            tu.write_csv(type(self).__name__ +'-' + self.symbol +'-' + self.timeframe, self.data_header, self.data_log)
            tu.write_csv(type(self).__name__ +'-' + self.symbol +'-' + self.timeframe + '-indicator', self.indicator_header, self.indicator_log)
            tu.write_pine(type(self).__name__ +'-' + self.symbol +'-' + self.timeframe, self.pine_log)

    def pine_long(self, comment, ts, qty, ts_out, sl, tp):
        self.pine_orderid += 1
        ts = int(ts) + jh.timeframe_to_one_minutes(self.timeframe) * 60 * 1000
        # if self.pine_reduced_ts > 0:
        #     self.pine_orderid += 1
        #     self.pine_log += f'strategy.entry("{self.pine_orderid - 1}", strategy.long, {qty}, {tp:.2f}, when = time_close == {ts:.0f}, comment="{comment}")\n'
        #     self.pine_log += f'strategy.entry("{self.pine_orderid}", strategy.long, {qty}, {tp:.2f}, when = time_close == {ts:.0f}, comment="{comment}")\n'
        #     self.pine_log += f'strategy.exit("{self.pine_orderid - 1}","{self.pine_orderid - 1}", limit = {self.pine_reduced_price:.2f}, when = time_close >= {self.pine_reduced_ts:.0f})\n'
        #     self.pine_log += f'strategy.exit("{self.pine_orderid}","{self.pine_orderid}", stop = {sl:.2f}, limit = {tp:.2f}, when = time_close >= {ts_out:.0f})\n'
        # else:
        self.pine_log += f'strategy.entry("{self.pine_orderid}", strategy.long, {qty}, {tp:.2f}, when = time_close == {ts:.0f}, comment="{comment}")\n'
        self.pine_log += f'strategy.exit("{self.pine_orderid}","{self.pine_orderid}", stop = {sl:.2f}, limit = {tp:.2f}, when = time_close >= {ts_out:.0f})\n'

    def pine_short(self, comment, ts, qty, ts_out, sl, tp):
        self.pine_orderid += 1
        ts = int(ts) + jh.timeframe_to_one_minutes(self.timeframe) * 60 * 1000
        # if self.pine_reduced_ts > 0:
        #     self.pine_orderid += 1
        #     self.pine_log += f'strategy.entry("{self.pine_orderid - 1}", strategy.short, {qty/2}, {tp:.2f}, when = time_close == {ts:.0f}, comment="{comment}")\n'
        #     self.pine_log += f'strategy.entry("{self.pine_orderid}", strategy.short, {qty/2}, {tp:.2f}, when = time_close == {ts:.0f}, comment="{comment}")\n'
        #     self.pine_log += f'strategy.exit("{self.pine_orderid - 1}","{self.pine_orderid - 1}", limit = {self.pine_reduced_price:.2f}, when = time_close >= {self.pine_reduced_ts:.0f})\n'
        #     self.pine_log += f'strategy.exit("{self.pine_orderid}","{self.pine_orderid}", stop = {sl:.2f}, limit = {tp:.2f}, when = time_close >= {ts_out:.0f})\n'
        # else:
        self.pine_log += f'strategy.entry("{self.pine_orderid}", strategy.short, {qty}, {tp:.2f}, when = time_close == {ts:.0f}, comment="{comment}")\n'
        self.pine_log += f'strategy.exit("{self.pine_orderid}","{self.pine_orderid}", stop = {sl:.2f}, limit = {tp:.2f}, when = time_close >= {ts_out:.0f})\n'

    

