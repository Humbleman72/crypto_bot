#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        cryptocurrency/bootstrap.py
# By:          Samuel Duclos
# For          Myself
# Description: Populate OHLCV DataFrames from the Binance API.

# Library imports.
from cryptocurrency.conversion_df import convert_ohlcvs_from_pairs_to_assets
from cryptocurrency.ohlcvs import download_pairs
from cryptocurrency.resample import resample
from cryptocurrency.volume_conversion import add_rolling_volumes
from tqdm import tqdm
import pandas as pd

# Function definitions.
def bootstrap_loggers(client, assets, pairs=None, additional_intervals=None, upsampled_intervals=None, 
                      download_interval='1m', exchange_info=None, as_pair=False):
    log_file = 'crypto_logs/crypto_output_log_{}.txt'
    period = 2880 if download_interval == '1m' else 200
    second_period = 60 if download_interval == '1m' else None
    base_interval = download_interval + 'in' if download_interval[-1] == 'm' else download_interval
    frequency_1d = pd.tseries.frequencies.to_offset('1d')
    frequency = pd.tseries.frequencies.to_offset(base_interval)
    pairs[base_interval] = download_pairs(client=client, assets=assets, interval=download_interval, 
                                          period=period, second_period=second_period)
    if not as_pair:
        pairs[base_interval] = convert_ohlcvs_from_pairs_to_assets(pairs[base_interval], exchange_info)
    if frequency < frequency_1d:
        pairs[base_interval] = add_rolling_volumes(pairs[base_interval])
    if download_interval == '1m':
        pairs[base_interval] = pairs[base_interval].loc[pairs[base_interval].dropna().first_valid_index():]
    pairs[base_interval].to_csv(log_file.format(base_interval))
    if additional_intervals is not None:
        for additional_interval in tqdm(additional_intervals, unit=' pair'):
            pairs[additional_interval] = resample(pairs[base_interval], interval=additional_interval)
            pairs[additional_interval].to_csv(log_file.format(additional_interval))
    if upsampled_intervals is not None:
        for subminute_interval in tqdm(upsampled_intervals, unit=' pair'):
            pairs[subminute_interval] = pairs[base_interval].tail(25)
            pairs[subminute_interval] = pairs[subminute_interval].resample(subminute_interval).agg('max')
            pairs[subminute_interval] = pairs[subminute_interval].fillna(method='pad')
            pairs[subminute_interval].to_csv(log_file.format(subminute_interval))
    return pairs
