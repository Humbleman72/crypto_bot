#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        get_historical_data.py
# By:          Jonathan Fournier
# For:         Myself
# Description: This file implements OHLCV retrieval through Binance API REST calls.

# Library imports.
import requests
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta

base_url = "https://api.binance.com/api/v3"

df_columns = ['open_time', 'close_time', 'open', 'high', 'low', 'close',
              'volume', 'quote_asset_volume', 'num_trades', 'taker_buy_base_asset_volume',
              'taker_buy_quote_asset_volume', 'ignore', 'open_timestamp', 'close_timestamp']


def get_historical_price(symbol: str, currency: str, start_dt: datetime, end_dt: datetime, interval: str):
    start_timestamp = round(start_dt.timestamp()) * 1000
    end_timestamp = round(end_dt.timestamp()) * 1000 - 1

    r = requests.get(
        f'{base_url}/klines?symbol={symbol}{currency}&interval={interval}&startTime={start_timestamp}&endTime={end_timestamp}&limit=1000')
    content = json.loads(r.content)

    if (len(content) > 0):
        df = pd.DataFrame.from_records(content, columns=['open_timestamp', 'open', 'high', 'low', 'close', 'volume',
                                                         'close_timestamp', 'quote_asset_volume', 'num_trades',
                                                         'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume',
                                                         'ignore'])
        df['open_time'] = df.open_timestamp.apply(lambda ts: datetime.fromtimestamp(ts / 1000))
        df['close_time'] = df.close_timestamp.apply(lambda ts: datetime.fromtimestamp(ts / 1000))
        return df[df_columns].sort_values('open_time', ascending=False)
    else:
        print('NO DATA RETRIEVED')
        print(f'RESPONSE: {content}')
        return None

if __name__ == '__main__':
    SYMBOL = 'BNB'
    CURRENCY = 'USDT'  # Fix to USDT - can change as needed
    print(f'[START] {SYMBOL}/{CURRENCY}')

    # Start with past midnight today (1st Iteration)
    end_dt = datetime.now()
    # end_dt_midnight = end_dt.replace(hour=0, minute=0, second=0, microsecond=0)  # End: Midnight yesterday D-0 00:00
    # end_dt_checkpoint = end_dt_midnight
    start_dt = end_dt - timedelta(hours=1)  # Start: Get 16 hours ago yesterday from midnight D-1 08:00

    print(f'{SYMBOL} 1ST ITERATION - Start Datetime: {start_dt} | End Datetime: {end_dt}')
    df = get_historical_price(SYMBOL, CURRENCY, start_dt, end_dt, "1m")

    print(df.iloc[0])
