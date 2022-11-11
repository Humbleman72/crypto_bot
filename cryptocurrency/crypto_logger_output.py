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
    def __init__(self, delay=12, interval_input='15s', interval='15s', buffer_size=60, 
                 input_log_name='input'):
        """
        :param delay: delay between logger/screener service interruptions.
        :param interval_input: OHLCV interval from input log. Default is 15 seconds.
        :param interval: OHLCV interval to log. Default is 15 seconds.
        :param buffer_size: buffer size to avoid crashing on memory accesses.
        :param input_log_name: the directory where to take the logs from.
        """
        self.data_before = pd.DataFrame()
        input_log_name = 'crypto_' + input_log_name + '_log_'
        self.load_from_ohlcv = interval_input != interval
        super().__init__(interval=interval, delay=delay, buffer_size=buffer_size, 
                         directory='crypto_logs', log_name='crypto_output_log_' + interval, 
                         raw=False)

        self.input_log_name = \
            join(self.directory, input_log_name + interval_input + '.txt')
        self.input_log_screened_name = \
            join(self.directory, input_log_name + interval_input + '_screened.txt')

    def screen(self, dataset):
        input_filtered = None
        if exists(self.input_log_screened_name):
            input_filtered = pd.read_csv(self.input_log_screened_name, header=0, index_col=0)
            input_filter = set(input_filtered['symbol'].tolist())
            old_columns = set(dataset.columns.get_level_values(0).tolist())
            new_columns = list(input_filter & old_columns)
            dataset = dataset[new_columns]
            assets = filter_in_market(screen_one, dataset)
            input_filtered = input_filtered[input_filtered['symbol'].isin(assets)]
        return input_filtered

    def resample_from_raw(self, df):
        df = df[['symbol', 'close', 'rolling_base_volume', 'rolling_quote_volume']]
        df['base_volume'] = df['rolling_base_volume'].copy()
        df['quote_volume'] = df['rolling_quote_volume'].copy()
        df = df.pivot_table(index=['date'], columns=['symbol'], 
                            values=['close', 'rolling_base_volume', 
                                    'rolling_quote_volume', 
                                    'base_volume', 'quote_volume'], 
                            aggfunc={'close': ['first', 'max', 'min', 'last'], 
                                     'base_volume': 'max', 'quote_volume': 'max', 
                                     'rolling_base_volume': 'max', 
                                     'rolling_quote_volume': 'max'})
        df.columns = pd.MultiIndex.from_tuples([('_'.join(col[:2]), col[2]) 
                                                for col in df.columns.values], 
                                               names=('pair', 'symbol'))
        df = df.rename(columns={'close_first': 'open', 'close_max': 'high', 
                                'close_min': 'low', 'close_last': 'close', 
                                'base_volume_max': 'base_volume', 
                                'quote_volume_max': 'quote_volume', 
                                'rolling_base_volume_max': 'rolling_base_volume', 
                                'rolling_quote_volume_max': 'rolling_quote_volume'}, 
                       level=0)
        df['base_volume'] = df['base_volume'].fillna(0)
        df['quote_volume'] = df['quote_volume'].fillna(0)
        df['rolling_base_volume'] = df['rolling_base_volume'].fillna(method='pad').fillna(method='backfill')
        df['rolling_quote_volume'] = df['rolling_quote_volume'].fillna(method='pad').fillna(method='backfill')
        df = df.sort_index().iloc[1:]
        df.columns = df.columns.swaplevel(0, 1)
        return df

    def get(self):
        dataset = self.get_from_file(log_name=self.input_log_name, 
                                     from_raw=not self.load_from_ohlcv)
        if not self.load_from_ohlcv:
            dataset = self.resample_from_raw(dataset)
        return dataset.tail(2)
