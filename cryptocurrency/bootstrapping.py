#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        cryptocurrency/bootstrapping.py
# By:          Samuel Duclos
# For          Myself
# Description: Populate OHLCV DataFrames from the Binance API.

# Library imports.
from cryptocurrency.ohlcvs import download_pairs
from cryptocurrency.volume_conversion import add_rolling_volumes
from cryptocurrency.resampling import resample
from tqdm import tqdm

# Function definitions.
def bootstrap_loggers(client, assets, intervals=None, pairs=None, 
                      download_interval='1m', period=2000):
    if intervals is None:
        intervals = ['1min', '5min', '15min', '30min', '1h', '2h', '4h', '12h', '1d']
    pairs = {} if pairs is None else pairs
    base_interval = intervals[0]
    if len(intervals) > 1:
        intervals = intervals[1:] 
    log_file = 'crypto_logs/crypto_output_log_{}.txt'
    pairs[base_interval] = download_pairs(client=client, assets=assets, 
                                          interval=download_interval, period=period)
    pairs[base_interval].columns = pairs[base_interval].columns.swaplevel(0, 1)
    pairs[base_interval] = pairs[base_interval][['open', 'high', 'low', 'close', 
                                                 'base_volume', 'quote_volume']]
    pairs[base_interval].columns = pairs[base_interval].columns.swaplevel(0, 1)
    pairs[base_interval] = add_rolling_volumes(pairs[base_interval])
    pairs[base_interval].to_csv(log_file.format(base_interval))
    if len(intervals) > 0:
        for interval in tqdm(intervals, unit=' pair'):
            pairs[interval] = resample(pairs[base_interval], interval=interval)
            pairs[interval].to_csv(log_file.format(interval))
    subminute_intervals = ['15s', '30s']
    for subminute_interval in tqdm(subminute_intervals, unit=' pair'):
        pairs[subminute_interval] = pairs[base_interval].tail(20)
        pairs[subminute_interval] = pairs[subminute_interval].resample(subminute_interval).agg('max')
        pairs[subminute_interval] = pairs[subminute_interval].fillna(method='pad')
        pairs[subminute_interval].to_csv(log_file.format(subminute_interval))
    return pairs
