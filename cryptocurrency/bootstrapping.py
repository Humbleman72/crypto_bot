#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        cryptocurrency/bootstrapping.py
# By:          Samuel Duclos
# For          Myself
# Description: Populate OHLCV DataFrames from the Binance API.

# Library imports.
from cryptocurrency.authentication import Cryptocurrency_authenticator
from cryptocurrency.exchange import Cryptocurrency_exchange
from cryptocurrency.conversion import convert_ohlcvs_from_pairs_to_assets
from cryptocurrency.conversion_table import get_conversion_table
from cryptocurrency.ohlcvs import download_pairs
from cryptocurrency.resampling import resample
from cryptocurrency.volume_conversion import add_rolling_volumes
from tqdm import tqdm
import pandas as pd

# Function definitions.
def bootstrap_loggers(client, assets, intervals=None, pairs=None, 
                      download_interval='1m', period=2880, second_period=None):
    if intervals is None:
        intervals = ['1min', '5min', '15min', '30min', '1h', '2h', '4h', '12h', '1d']
    pairs = {} if pairs is None else pairs
    base_interval = intervals[0]
    if len(intervals) > 1:
        intervals = intervals[1:] 
    log_file = 'crypto_logs/crypto_output_log_{}.txt'
    authenticator = Cryptocurrency_authenticator(use_keys=False, testnet=False)
    client = authenticator.spot_client
    exchange = Cryptocurrency_exchange(client=client, directory='crypto_logs')
    exchange_info = exchange.info
    pairs[base_interval] = download_pairs(client=client, assets=assets, 
                                          interval=download_interval, period=period, 
                                          second_period=second_period)
    pairs[base_interval] = pd.read_csv(log_file.format(base_interval), header=[0, 1], index_col=0)
    pairs[base_interval].index = pd.DatetimeIndex(pairs[base_interval].index)
    pairs[base_interval].columns.names = ['symbol', 'pair']
    pairs[base_interval] = convert_ohlcvs_from_pairs_to_assets(pairs[base_interval], exchange_info)
    pairs[base_interval] = add_rolling_volumes(pairs[base_interval])
    pairs[base_interval].to_csv(log_file.format(base_interval))
    if len(intervals) > 0:
        for interval in tqdm(intervals, unit=' pair'):
            pairs[interval] = resample(pairs[base_interval], interval=interval)
            pairs[interval].to_csv(log_file.format(interval))
    subminute_intervals = ['15s', '30s']
    for subminute_interval in tqdm(subminute_intervals, unit=' pair'):
        pairs[subminute_interval] = pairs[base_interval].tail(50)
        pairs[subminute_interval] = pairs[subminute_interval].resample(subminute_interval).agg('max')
        pairs[subminute_interval] = pairs[subminute_interval].fillna(method='pad')
        pairs[subminute_interval].to_csv(log_file.format(subminute_interval))
    return pairs
