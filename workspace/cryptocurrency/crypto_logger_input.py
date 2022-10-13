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
from cryptocurrency.conversion import get_base_asset_from_pair, get_quote_asset_from_pair
from os import mkdir
from os.path import exists, join

import datetime
import pandas as pd
pd.options.mode.chained_assignment = None

class Crypto_logger_input(Crypto_logger_base):
    def __init__(self, client=None, delay=4.7, interval='1min', buffer_size=20000, 
                 price_percent=5.0, volume_percent=1.0):
        """
        :param interval: OHLCV interval to log. Default is 1 minute.
        :param delay: delay between Binance API requests. Minimum calculated was 5 seconds.
        :param buffer_size: buffer size to avoid crashing on low memory.
        :param directory: the directory where to output the logs.
        """
        self.resample = None
        self.price_percent = price_percent
        self.volume_percent = volume_percent
        super().__init__(interval=interval, delay=delay, buffer_size=buffer_size, 
                         directory='crypto_logs', log_name='crypto_input_log_' + interval, 
                         second_screener=False, raw=True, precise=False)

        #self.log_screened_up_name = self.log_name.replace('.txt', '') + '_screened_up.txt'

        authenticator = Cryptocurrency_authenticator(use_keys=False, testnet=False)
        self.client = authenticator.spot_client

        exchange = Cryptocurrency_exchange(client=self.client, directory=self.directory)
        self.exchange_info = exchange.info

    def filter_movers(self, dataset, count=1000, price_percent=5.0, volume_percent=1.0):
        dataset = dataset.reset_index()
        dataset[['priceChangePercent', 'rolling_quote_volume']] = \
            dataset[['priceChangePercent', 'rolling_quote_volume']].astype(float)
        dataset['last_price_move'] = dataset['priceChangePercent'].copy()
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
        #price_movers_int = price_movers.copy().dropna().astype(int)
        #price_movers_int = price_movers_int[price_movers_int >= 0]
        price_movers = price_movers.to_frame(name='last_price_move')
        volume_movers = volume_movers.to_frame(name='last_volume_move')
        #price_movers_int.to_csv(self.log_screened_up_name)
        movers = pd.concat([price_movers, volume_movers], axis='columns')
        movers = movers.reset_index()
        price_movers_mask = movers['last_price_move'] > price_percent
        volume_movers_mask = movers['last_volume_move'] > volume_percent
        movers = movers[price_movers_mask & volume_movers_mask]
        movers = movers.sort_values(by=['last_volume_move', 'last_price_move'], ascending=False)
        movers = movers.tail(count).reset_index(drop=True)
        return dataset.merge(right=movers, how='right', on=['symbol']).set_index('date')

    def get_highest_daily_volume_pair_associated_with_base_asset(self, base_asset):
        pairs = self.exchange_info[self.exchange_info['baseAsset'] == base_asset]['symbol'].tolist()
        filtered_pairs = self.conversion_table[self.conversion_table['symbol'].isin(pairs)]
        filtered_pairs = filtered_pairs.sort_values(by=['rolling_quote_volume'], ascending=False)
        try:
            filtered_pairs = filtered_pairs['symbol'].iloc[0]
        except IndexError:
            filtered_pairs = None
        return filtered_pairs

    def screen(self, dataset):
        dataset = dataset[['symbol', 'close', 'priceChangePercent', 
                           'bidPrice', 'askPrice', 'bidQty', 'askQty', 
                           'rolling_base_volume', 'rolling_quote_volume', 'count']]
        dataset[['priceChangePercent', 'close', 'bidPrice', 'askPrice', 
                 'bidQty', 'askQty', 'rolling_base_volume', 'rolling_quote_volume', 'count']] = \
            dataset[['priceChangePercent', 'close', 'bidPrice', 'askPrice', 
                     'bidQty', 'askQty', 'rolling_base_volume', 'rolling_quote_volume', 'count']].astype(float)
        #dataset = dataset[dataset['rolling_quote_volume'] > 50000]
        dataset['bidAskChangePercent'] = \
            ((dataset['askPrice'] - dataset['bidPrice']) / dataset['askPrice'])
        dataset['bidAskQtyPercent'] = \
            (dataset['bidQty'] / (dataset['bidQty'] + dataset['askQty']))
        dataset[['bidAskChangePercent', 'bidAskQtyPercent']] *= 100
        dataset = dataset.dropna()
        dataset = dataset[dataset['bidAskChangePercent'] < 0.8]
        #dataset = dataset[dataset['bidAskQtyPercent'] > 100.0]
        dataset = self.filter_movers(dataset, count=1000, price_percent=self.price_percent, 
                                     volume_percent=self.volume_percent)
        dataset = dataset.drop_duplicates(subset=['symbol', 'count'], keep='last')
        dataset['base_asset'] = dataset['symbol'].apply(lambda x: get_base_asset_from_pair(x, exchange_info=self.exchange_info))
        dataset['quote_asset'] = dataset['symbol'].apply(lambda x: get_quote_asset_from_pair(x, exchange_info=self.exchange_info))
        #dataset['symbol_2'] = dataset['base_asset'].apply(lambda x: self.get_highest_daily_volume_pair_associated_with_base_asset(base_asset=x))
        #dataset[dataset['symbol_2'] == None]['symbol_2'] = dataset[dataset['symbol_2'] == None]['symbol']
        #dataset['symbol'] = dataset['symbol_2'].copy()
        #dataset = dataset.drop(columns=['symbol_2'])
        return dataset

    def prepare_downsampling(self, dataset):
        dataset['closeTime'] /= 1000
        dataset['openTime'] /= 1000
        dataset['openTime'] = \
            dataset['openTime'].apply(datetime.datetime.fromtimestamp)
        dataset['closeTime'] = \
            dataset['closeTime'].apply(datetime.datetime.fromtimestamp)
        dataset['date'] = pd.DatetimeIndex(dataset['closeTime']).round(self.interval)
        return dataset.set_index('date').sort_index()

    def get(self):
        """Get all pairs data from Binance API."""
        dataset = pd.DataFrame(self.client.get_ticker())
        dataset = dataset.rename(columns={'lastPrice': 'close', 
                                          'volume': 'rolling_base_volume', 
                                          'quoteVolume': 'rolling_quote_volume'})
        self.conversion_table = dataset.copy()
        self.conversion_table.to_csv(self.log_name.replace('.txt', '') + '_conversion_table.txt')
        return self.prepare_downsampling(self.conversion_table)
