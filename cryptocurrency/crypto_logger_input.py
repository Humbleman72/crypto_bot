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
from cryptocurrency.conversion import get_timezone_offset_in_seconds
from cryptocurrency.conversion_table import get_conversion_table, get_tradable_tickers_info

import pandas as pd
pd.options.mode.chained_assignment = None

# Class definition.
class Crypto_logger_input(Crypto_logger_base):
    def __init__(self, delay=4.7, interval='15s', buffer_size=3000, 
                 price_percent=5.0, volume_percent=0.0, as_pair=False, 
                 append=False, roll=1000, log=True):
        """
        :param interval: OHLCV interval to log. Default is 15 seconds.
        :param delay: delay between Binance API requests. Minimum calculated was 4.7 seconds.
        :param buffer_size: buffer size to avoid crashing on memory accesses.
        :param price_percent: price move percent.
        :param volume_percent: volume move percent.
        """
        self.price_percent = price_percent
        self.volume_percent = volume_percent
        self.as_pair = as_pair
        super().__init__(delay=delay, interval=interval, interval_input='', 
                         buffer_size=buffer_size, directory='crypto_logs', 
                         log_name='crypto_input_log_' + interval, input_log_name='', 
                         raw=True, append=append, roll=roll, log=log)

        authenticator = Cryptocurrency_authenticator(use_keys=False, testnet=False)
        self.client = authenticator.spot_client

        exchange = Cryptocurrency_exchange(client=self.client, directory=self.directory)
        self.exchange_info = exchange.info

        self.offset_s = get_timezone_offset_in_seconds()

    def filter_movers(self, dataset, count=1000, price_percent=5.0, volume_percent=0.0):
        dataset = dataset.reset_index()
        dataset[['price_change_percent', 'rolling_base_volume']] = \
            dataset[['price_change_percent', 'rolling_base_volume']].astype(float)
        dataset['last_price_move'] = dataset['price_change_percent'].copy()
        dataset['last_volume_move'] = dataset['rolling_base_volume'].copy()
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
        movers = movers.tail(count)
        movers = movers.reset_index(drop=True)
        #dataset = dataset.set_index('symbol')
        #movers = movers.set_index('symbol')
        #dataset = dataset.merge(right=movers, how='right', left_index=True, right_index=True)
        dataset = dataset.merge(right=movers, how='right', on=['symbol'])
        dataset = dataset.set_index('date')
        return dataset.drop_duplicates(subset=['symbol', 'count'], keep='last')

    def screen(self, dataset, dataset_screened=None):
        if dataset is not None:
            dataset = get_tradable_tickers_info(dataset, as_pair=self.as_pair)
            dataset_screened = self.filter_movers(dataset, count=1000, 
                                                  price_percent=self.price_percent, 
                                                  volume_percent=self.volume_percent)
        return dataset_screened

    def get(self, dataset=None):
        """Get all pairs data from Binance API."""
        dataset = get_conversion_table(client=self.client, exchange_info=self.exchange_info, 
                                       offset_s=self.offset_s, dump_raw=False, as_pair=self.as_pair, 
                                       minimal=True, extra_minimal=True, super_extra_minimal=True, 
                                       convert_to_USDT=not self.as_pair)
        dataset.index = dataset.index.round(self.interval)
        dataset.index.name = 'date'
        return dataset
