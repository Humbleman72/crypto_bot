#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        cryptocurrency/crypto_logger_input.py
# By:          Samuel Duclos
# For          Myself
# Description: Simple Binance logger circular buffered for N time precision.

# Library imports.
from cryptocurrency.crypto_logger_base import Crypto_logger_base
from cryptocurrency.authentication import Cryptocurrency_authenticator
from cryptocurrency.exchange import Cryptocurrency_exchange
from cryptocurrency.conversion_table import get_conversion_table, get_tradable_tickers_info
from os import mkdir
from os.path import exists, join

import datetime
import pandas as pd
pd.options.mode.chained_assignment = None

class Crypto_logger_input(Crypto_logger_base):
    def __init__(self, delay=4.7, interval='15s', buffer_size=3000, 
                 price_percent=5.0, volume_percent=0.0, as_pair=False):
        """
        :param interval: OHLCV interval to log. Default is 15 seconds.
        :param delay: delay between Binance API requests. Minimum calculated was 4.7 seconds.
        :param buffer_size: buffer size to avoid crashing on memory accesses.
        :param price_percent: price move percent.
        :param volume_percent: volume move percent.
        """
        self.resample = None
        self.price_percent = price_percent
        self.volume_percent = volume_percent
        self.as_pair = as_pair
        super().__init__(interval=interval, delay=delay, buffer_size=buffer_size, 
                         directory='crypto_logs', log_name='crypto_input_log_' + interval, 
                         raw=True)

        authenticator = Cryptocurrency_authenticator(use_keys=False, testnet=False)
        self.client = authenticator.spot_client

        exchange = Cryptocurrency_exchange(client=self.client, directory=self.directory)
        self.exchange_info = exchange.info

    def filter_movers(self, dataset, count=1000, price_percent=5.0, volume_percent=0.0):
        dataset = dataset.reset_index()
        dataset[['price_change_percent', 'rolling_quote_volume']] = \
            dataset[['price_change_percent', 'rolling_quote_volume']].astype(float)
        dataset['last_price_move'] = dataset['price_change_percent'].copy()
        dataset['last_volume_move'] = dataset['rolling_quote_volume'].copy()
        movers = dataset.groupby(['symbol'])
        dataset = dataset.drop(columns=['last_price_move', 'last_volume_move'])
        price_movers = movers['last_price_move']
        volume_movers = movers['last_volume_move']
        price_movers = price_movers.agg(lambda x: x.diff(1).abs().iloc[-1])
        volume_movers = volume_movers.agg(lambda x: (100 * x.pct_change(1)).iloc[-1])
        price_movers = price_movers.sort_values(ascending=False)
        volume_movers = volume_movers.sort_values(ascending=False)
        price_movers = price_movers[price_movers > 0.0]
        price_movers = price_movers.to_frame(name='last_price_move')
        volume_movers = volume_movers.to_frame(name='last_volume_move')
        movers = pd.concat([price_movers, volume_movers], axis='columns')
        movers = movers.reset_index()
        price_movers_mask = movers['last_price_move'] > price_percent
        volume_movers_mask = movers['last_volume_move'] > volume_percent
        movers = movers[price_movers_mask & volume_movers_mask]
        movers = movers.sort_values(by=['last_volume_move', 'last_price_move'], ascending=False)
        movers = movers.tail(count).reset_index(drop=True)
        return dataset.merge(right=movers, how='right', on=['symbol']).set_index('date')

    def screen(self, dataset):
        dataset = get_tradable_tickers_info(dataset, as_pair=self.as_pair)
        dataset = self.filter_movers(dataset, count=1000, 
                                     price_percent=self.price_percent, 
                                     volume_percent=self.volume_percent)
        return dataset.drop_duplicates(subset=['symbol', 'count'], keep='last')

    def prepare_downsampling(self, dataset):
        dataset['close_time'] /= 1000
        dataset['close_time'] = \
            dataset['close_time'].apply(datetime.datetime.fromtimestamp)
        dataset['date'] = pd.DatetimeIndex(dataset['close_time']).round(self.interval)
        return dataset.set_index('date').sort_index()

    def get(self):
        """Get all pairs data from Binance API."""
        dataset = get_conversion_table(self.client, self.exchange_info)
        self.conversion_table = dataset.copy()
        self.conversion_table.to_csv(self.log_name.replace('.txt', '') + '_conversion_table.txt')
        return self.prepare_downsampling(self.conversion_table)
