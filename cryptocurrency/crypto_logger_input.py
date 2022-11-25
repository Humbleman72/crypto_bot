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
        dataset = get_tradable_tickers_info(dataset, as_pair=False)
        movers = dataset.reset_index()
        movers['price_change_percent'] = movers['price_change_percent'].astype(float)
        movers = movers[['symbol', 'price_change_percent']]
        movers = movers.groupby(['symbol'])
        movers = movers.agg(lambda x: x.diff(1).abs().iloc[-1])
        movers = movers['price_change_percent']
        movers = movers.dropna()
        movers = movers.sort_values(ascending=False)
        movers = movers.tail(count)
        movers = movers[movers > price_percent]
        movers = movers.index.tolist()
        dataset = dataset[dataset['symbol'].isin(movers)]
        return dataset.drop_duplicates(subset=['symbol', 'count'], keep='last')

    def screen(self, dataset, dataset_screened=None):
        dataset = get_tradable_tickers_info(dataset, as_pair=self.as_pair)
        return self.filter_movers(dataset, count=1000, 
                                  price_percent=self.price_percent, 
                                  volume_percent=self.volume_percent)

    def get(self, dataset=None):
        """Get all pairs data from Binance API."""
        dataset = get_conversion_table(self.client, self.exchange_info, offset_s=self.offset_s, 
                                       as_pair=self.as_pair, dump_raw=False, minimal=True, 
                                       convert_to_USDT=True)
        dataset.index = dataset.index.round(self.interval)
        dataset.index.name = 'date'
        return dataset
