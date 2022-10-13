#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        cryptocurrency/crypto_logger_output.py
# By:          Samuel Duclos
# For          Myself
# Description: Simple Binance logger output for arbitrary intervals.


# Library imports.
from cryptocurrency.crypto_logger_base import Crypto_logger_base
from cryptocurrency.indicators import filter_in_market, screen_one
from os.path import exists, join

import pandas as pd
pd.options.mode.chained_assignment = None

class Crypto_logger_output(Crypto_logger_base):
    def __init__(self, delay=6, interval_input='15s', interval='15s', buffer_size=100, 
                 input_log_name='input', second_screener=False):
        """
        :param delay: delay between Binance API requests. Minimum calculated was 5 seconds.
        :param interval_input: OHLCV interval from input log. Default is 15 seconds.
        :param interval: OHLCV interval to log. Default is 15 seconds.
        :param buffer_size: buffer size to avoid crashing on low memory.
        :param directory: the directory where to output the logs.
        """
        self.data_before = pd.DataFrame()
        input_log_name = 'crypto_' + input_log_name + '_log_'
        self.load_from_ohlcv = interval_input != interval
        super().__init__(interval=interval, delay=delay, buffer_size=buffer_size, 
                         directory='crypto_logs', log_name='crypto_output_log_' + interval, 
                         second_screener=second_screener, raw=False, precise=True)

        #if not self.load_from_ohlcv:
        #    self.input_log_screened_up_name = \
        #        join(self.directory, input_log_name + interval_input + '_screened_up.txt')

        self.input_log_name = \
            join(self.directory, input_log_name + interval_input + '.txt')
        self.input_log_screened_name = \
            join(self.directory, input_log_name + interval_input + '_screened.txt')

    def get_screened(self, data_after, price_threshold=5.0, volume_threshold=300.0):
        price_movers = pd.DataFrame()
        volume_movers = pd.DataFrame()
        data_before = self.data_before
        if data_before.size != 0:
            data_before.columns = data_before.columns.swaplevel(0, 1)
            data_after.columns = data_after.columns.swaplevel(0, 1)
            price_before = data_before['close'].pct_change(1)
            price_after = data_after['close'].pct_change(1)
            volume_before = data_before['volume'].shift(1)
            volume_after = data_after['volume'].shift(1)
            price_percent_change_before = \
                ((data_before['close'].pct_change(1) - price_before) / price_before)
            price_percent_change_after = \
                ((data_after['close'].pct_change(1) - price_after) / price_after)
            volume_percent_change_before = ((data_before['volume'] - volume_before) / volume_before)
            volume_percent_change_after = ((data_after['volume'] - volume_after) / volume_after)
            price_movers = \
                ((price_percent_change_after - price_percent_change_before) * 100) > price_threshold
            volume_movers = \
                ((volume_percent_change_after - volume_percent_change_before) * 100) > volume_threshold
            price_movers = data_after[price_movers].columns.tolist()
            volume_movers = data_after[volume_movers].columns.tolist()
            data_before.columns = data_before.columns.swaplevel(0, 1)
            data_after.columns = data_after.columns.swaplevel(0, 1)
        self.data_before = data_after
        return price_movers + volume_movers

    def screen(self, dataset):
        #if not self.load_from_ohlcv:
        #    if exists(self.input_log_screened_up_name):
        #        input_filtered_up = pd.read_csv(self.input_log_screened_up_name, header=0, index_col=None)
        if exists(self.input_log_screened_name):
            input_filtered = pd.read_csv(self.input_log_screened_name, header=0, index_col=0)
            input_filter = set(input_filtered['symbol'].tolist())
            #if not self.load_from_ohlcv:
            #    input_filter = input_filter & set(input_filtered_up['symbol'].tolist())
            old_columns = set(dataset.columns.get_level_values(0).tolist())
            new_columns = list(input_filter & old_columns)
            dataset = dataset[new_columns]

            #assets = self.get_screened(dataset, price_threshold=1.0, volume_threshold=1.0)
            #input_filtered_movers = input_filtered[input_filtered['symbol'].isin(assets)]
            #input_filtered_movers.to_csv(self.input_log_screened_name, mode='a')
            #dataset.columns = dataset.columns.swaplevel(0, 1)
            #dataset = dataset.rename(columns={'base_volume': 'volume'})
            #dataset.columns = dataset.columns.swaplevel(0, 1)
            assets = filter_in_market(screen_one, dataset)
            #dataset.columns = dataset.columns.swaplevel(0, 1)
            #dataset = dataset.rename(columns={'volume': 'base_volume'})
            #dataset.columns = dataset.columns.swaplevel(0, 1)
            return input_filtered[input_filtered['symbol'].isin(assets)]
        else:
            return None

    def screen_(self, dataset):
        return dataset

    '''
    def resample_from_raw(self, df, interval='1min'):
        df = df[['symbol', 'lastPrice', 'lastQty']]
        df = df.rename(columns={'lastPrice': 'close', 'lastQty': 'volume'})
        df = df.pivot_table(index=['date'], columns=['symbol'], 
                            values=['close', 'volume'], 
                            aggfunc={'close': ['first', 'max', 'min', 'last'], 
                                     'volume': 'sum'})
        df = df.sort_index().iloc[1:]
        df.columns = df.columns.droplevel(0)
        df = df.rename(columns={'first': 'open', 'max': 'high', 'min': 'low', 
                                'last': 'close', 'sum': 'volume'})
        df.columns = df.columns.swaplevel(0, 1)
        return df
    '''

    def resample_from_raw(self, df):
        df = df[['symbol', 'close', 'rolling_base_volume', 'rolling_quote_volume']]
        df = df.pivot_table(index=['date'], columns=['symbol'], 
                            values=['close', 'rolling_base_volume', 
                                    'rolling_quote_volume'], 
                            aggfunc={'close': ['first', 'max', 'min', 'last'], 
                                     'rolling_base_volume': 'max', 
                                     'rolling_quote_volume': 'max'})
        df.columns = pd.MultiIndex.from_tuples([('_'.join(col[:2]), col[2]) for col in df.columns.values], 
                                               names=('pair', 'symbol'))
        df = df.rename(columns={'close_first': 'open', 'close_max': 'high', 
                                'close_min': 'low', 'close_last': 'close', 
                                'rolling_base_volume_max': 'rolling_base_volume', 
                                'rolling_quote_volume_max': 'rolling_quote_volume'}, 
                       level=0)
        df['rolling_base_volume'] = df['rolling_base_volume'].fillna(method='pad')
        df['rolling_base_volume'].iloc[0] = 0
        df['rolling_quote_volume'] = df['rolling_quote_volume'].fillna(method='pad')
        df['rolling_quote_volume'].iloc[0] = 0
        df = df.sort_index().iloc[1:]
        df.columns = df.columns.swaplevel(0, 1)
        return df

    def get(self):
        if self.load_from_ohlcv:
            dataset = pd.read_csv(self.input_log_name, header=[0, 1], index_col=0)
        else:
            dataset = pd.read_csv(self.input_log_name, header=0, index_col=0)
            dataset = self.resample_from_raw(dataset)
        return dataset.sort_index().tail(2)
