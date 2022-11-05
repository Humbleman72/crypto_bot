#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        cryptocurrency/ohlcv.py
# By:          Samuel Duclos
# For          Myself
# Description: Download OHLCV precomputed DataFrame from the Binance API.

# Library imports.
from datetime import datetime
import pandas as pd

def download_pair(client, symbol, interval='1m', period=60, offset_s=0):
    def get_n_periods_from_time(period=60):
        interval_digits = int(''.join(filter(str.isdigit, interval)))
        interval_string = str(''.join(filter(str.isalpha, interval)))
        return str(interval_digits * period) + interval_string

    start_str = get_n_periods_from_time(period=period)
    data = client.get_historical_klines(symbol=symbol, interval=interval, start_str=start_str)
    data = pd.DataFrame(data, columns=['date', 'open', 'high', 'low', 'close', 
                                       'base_volume', 'close_time', 'quote_volume', 
                                       'n_trades', 'taker_buy_base_volume', 
                                       'taker_buy_quote_volume', 'ignore'])
    data['date'] = data['date'].apply(lambda timestamp: \
                                      datetime.fromtimestamp((timestamp / 1000) + int(offset_s)))

    data = data.drop(columns=['close_time', 'ignore']).set_index('date')
    data[['open', 'high', 'low', 'close', 'base_volume', 'quote_volume', 
          'taker_buy_base_volume', 'taker_buy_quote_volume']] = \
        data[['open', 'high', 'low', 'close', 'base_volume', 'quote_volume', 
              'taker_buy_base_volume', 'taker_buy_quote_volume']].applymap(
            lambda entry: entry.rstrip('0').rstrip('.'))
    data = data.astype(float)
    data['n_trades'] = data['n_trades'].astype(int)
    return data

