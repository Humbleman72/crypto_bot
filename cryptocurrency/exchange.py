#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File:        cryptocurrency/exchange.py
# By:          Samuel Duclos
# For:         Myself
# Description: This file handles python-binance global exchange info.
from os import mkdir
from os.path import exists, join
import pandas as pd
class Cryptocurrency_exchange:
    def __init__(self, client=None, directory='crypto_logs'):
        self.client, self.info_path = client, join('crypto_logs', 'crypto_exchange_info.txt')
        if not exists(directory):
            mkdir(directory)
        if exists(self.info_path):
            self.info = pd.read_csv(self.info_path, index_col=0)
        else:
            self.get_exchange_info()
            self.info.to_csv(self.info_path)
    def get_exchange_info(self):
        def build_filters(symbols_info, index):
            try:
                symbol = symbols_info['symbol'].iat[index]
                df = pd.DataFrame(symbols_info['filters'].iat[index])
                min_price = df[df['filterType'] == 'PRICE_FILTER']['minPrice'].iat[0]
                max_price = df[df['filterType'] == 'PRICE_FILTER']['maxPrice'].iat[0]
                tick_size = df[df['filterType'] == 'PRICE_FILTER']['tickSize'].iat[0]
                step_size = df[df['filterType'] == 'LOT_SIZE']['stepSize'].iat[0]
                multiplier_up = df[df['filterType'] == 'PERCENT_PRICE']['multiplierUp'].iat[0]
                multiplier_down = df[df['filterType'] == 'PERCENT_PRICE']['multiplierDown'].iat[0]
                df = pd.DataFrame([[symbol, min_price, max_price, tick_size, step_size, multiplier_up, multiplier_down]], 
                                  columns=['symbol', 'min_price', 'max_price', 'tick_size', 'step_size', 'multiplier_up', 'multiplier_down'])
            except Exception as e:
                df = None
            return df
        symbols_info = self.client.get_exchange_info()
        symbols_info = pd.DataFrame(pd.DataFrame([symbols_info])['symbols'].iat[0])
        symbols_info = symbols_info[symbols_info['status'] == 'TRADING']
        symbols_info = symbols_info[symbols_info['isSpotTradingAllowed']]
        symbols_info = symbols_info[symbols_info['quoteOrderQtyMarketAllowed']]
        symbols_info = symbols_info.drop(columns=['status', 'isSpotTradingAllowed', 'isMarginTradingAllowed', 'permissions', 'icebergAllowed', 
                                                  'ocoAllowed', 'quoteOrderQtyMarketAllowed', 'orderTypes']).set_index('symbol', drop=False)
        filters = [build_filters(symbols_info, i) for i in range(symbols_info.shape[0])]
        filters = [x for x in filters if x is not None]
        df = pd.DataFrame()
        for x in filters:
            df = pd.concat([df, x], axis='index')
        df = df.set_index('symbol')
        symbols_info = pd.concat([symbols_info, df], axis='columns')
        self.info = symbols_info.drop(columns=['symbol', 'filters']).reset_index('symbol')
