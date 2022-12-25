#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        crypto_monitor.py
# By:          Jonathan Fournier
# For:         Myself
# Description: This file implements a monitor for take profit and stop loss.

# Library imports.
from enum import Enum
from datetime import datetime

import time
import numpy as np
import pandas as pd

MIN_PERCENT_LIMIT = -0.05
MAX_PERCENT_LIMIT = 0.10

NO_GOOD = 1
GOOD = 2
NEUTRAL = 3

def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    new_time = utc_datetime + offset
    return new_time

def get_date_delta_str(date1, date2):
    delta = date2 - date1
    total_seconds = delta.total_seconds()

    hours = int(total_seconds // 3600)
    minutes = int(total_seconds % 3600 // 60)
    seconds = int(total_seconds % 60)

    date_delta_str = f'{seconds}s'
    if minutes != 0:
        date_delta_str = f'{minutes}m ' + date_delta_str
    if hours != 0:
        date_delta_str = f'{hours}h ' + date_delta_str

    return date_delta_str

class CryptoSymbol:
    def __init__(self, symbol, price, date):
        date_now = datetime.now()

        self.symbol = symbol
        self.price = 0.0
        self.buy_price = price
        self.buy_date = date_now
        self.buy_date_str = '0s'
        self.percent_change = 0.0
        self.min_percent = 10.0
        self.min_percent_date = None
        self.min_percent_date_str = ''
        self.max_percent = -10.0
        self.max_percent_date = None
        self.max_percent_date_str = ''
        self.date_added = datetime_from_utc_to_local(date)
        self.date_added_str = None
        self.status = NEUTRAL
        self.status_update_date = None
        self.status_update_date_str = ''

        time_str = self.buy_date.strftime("[%Y-%m-%d %H:%M:%S]")
        print(f'{time_str} Purchased {self.symbol} at {self.buy_price}')

    def update(self, price, date, utc=True):
        print(f'Updating {self.symbol} with {price}')
        date_local = date
        if utc:
            date_local = datetime_from_utc_to_local(date_local)
        date_now = datetime.now()

        self.date_added_str = get_date_delta_str(self.date_added, date_now)
        self.buy_date_str = get_date_delta_str(self.buy_date, date_now)

        percent_change = (price - self.buy_price) / self.buy_price
        if percent_change > self.max_percent:
            self.max_percent = percent_change
            self.max_percent_date = date_now
        if percent_change < self.min_percent:
            self.min_percent = percent_change
            self.min_percent_date = date_now
        self.percent_change = percent_change
        self.price = price

        self.min_percent_date_str = get_date_delta_str(self.buy_date, self.min_percent_date)
        self.max_percent_date_str = get_date_delta_str(self.buy_date, self.max_percent_date)

        if self.status == NEUTRAL:
            if self.min_percent <= MIN_PERCENT_LIMIT and not self.max_percent >= MAX_PERCENT_LIMIT:
                self.status = NO_GOOD
                self.status_update_date_str = get_date_delta_str(self.buy_date, date_now)

            if self.max_percent >= MAX_PERCENT_LIMIT and not self.min_percent <= MIN_PERCENT_LIMIT:
                self.status = GOOD
                self.status_update_date_str = get_date_delta_str(self.buy_date, date_now)

        # if self.min_percent_date is not None:
        #     self.min_percent_date_str = get_date_delta_str(date_now, self.min_percent_date)
        # else:
        #     self.min_percent_date_str = ''
        #
        # if self.max_percent_date is not None:
        #     self.max_percent_date_str = get_date_delta_str(date_now, self.max_percent_date)
        # else:
        #     self.max_percent_date_str = ''


class CryptoMonitor:
    def __init__(self):
        self.crypto_list = []

    def add_crypto(self, symbol, price, date):
        if symbol not in [cs.symbol for cs in self.crypto_list]:
            self.crypto_list.append(CryptoSymbol(symbol, price, date))

    def process(self, dataset):
        df = pd.DataFrame(columns=['symbol', 'price', 'buy_price', 'buy_time', 'percent_change', 'min_percent', 'min_percent_time',
                                   'max_percent', 'max_percent_time', 'date_added', 'status', 'status_update_time'])

        if len(self.crypto_list) == 0:
            print('List of monitored assets is empty.')
            return df

        for crypto_symbol in self.crypto_list:
            symbol = crypto_symbol.symbol
            data = dataset.loc[dataset['symbol'] == symbol]
            date = data.index.to_pydatetime()
            if type(date) is np.ndarray:
                date = date[0]
            price = float(data['close'])

            crypto_symbol.update(price, date)

            df = df.append({'symbol': symbol,
                            'price': price,
                            'buy_price': crypto_symbol.buy_price,
                            'buy_time': crypto_symbol.buy_date_str,
                            'percent_change': crypto_symbol.percent_change,
                            'min_percent': crypto_symbol.min_percent,
                            'min_percent_time': crypto_symbol.min_percent_date_str,
                            'max_percent': crypto_symbol.max_percent,
                            'max_percent_time': crypto_symbol.max_percent_date_str,
                            'date_added': crypto_symbol.date_added_str,
                            'status': crypto_symbol.status,
                            'status_update_time': crypto_symbol.status_update_date_str},
                           ignore_index=True)

        # print('len', len(df))
        # print(df)
        return df
