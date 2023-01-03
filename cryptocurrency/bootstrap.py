#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        cryptocurrency/bootstrap.py
# By:          Samuel Duclos
# For          Myself
# Description: Populate OHLCV DataFrames from the Binance API.

# Library imports.
from .conversion_ohlcv import convert_ohlcvs_from_pairs_to_assets
from .ohlcvs import download_pairs
from .resample import resample
from .volume_conversion import add_rolling_volumes
from typing import Dict, List, Optional
from binance.client import Client
from tqdm import tqdm
import pandas as pd

# Function definitions.
def bootstrap_loggers(client: Client, 
                      assets: List[str], 
                      pairs: Optional[Dict[str, pd.DataFrame]] = None, 
                      additional_intervals: Optional[List[str]] = None, 
                      upsampled_intervals: Optional[List[str]] = None, 
                      download_interval: str = '1m', 
                      exchange_info: Optional[Dict[str, Dict[str, List[str]]]] = None, 
                      as_pair: bool = False) -> Dict[str, pd.DataFrame]:
    log_file = 'crypto_logs/crypto_output_log_{}.txt'
    period = 2880 if download_interval == '1m' else 60
    second_period = 60 if download_interval == '1m' else None
    base_interval = download_interval + 'in' if download_interval[-1] == 'm' else download_interval
    frequency_1min = pd.tseries.frequencies.to_offset('1min')
    frequency_1d = pd.tseries.frequencies.to_offset('1d')
    frequency = pd.tseries.frequencies.to_offset(base_interval)
    pairs[base_interval] = download_pairs(client=client, assets=assets, interval=download_interval, 
                                          period=period, second_period=second_period)
    if not as_pair:
        pairs[base_interval] = convert_ohlcvs_from_pairs_to_assets(pairs[base_interval], exchange_info)
    pairs[base_interval] = add_rolling_volumes(pairs[base_interval])
    if frequency < frequency_1d:
        pairs[base_interval] = pairs[base_interval].loc[pairs[base_interval].dropna().first_valid_index():]
    if additional_intervals is not None:
        for additional_interval in tqdm(additional_intervals, unit=' pair'):
            pairs[additional_interval] = resample(pairs[base_interval].copy(), interval=additional_interval)
            pairs[additional_interval] = pairs[additional_interval].tail(60)
            pairs[additional_interval].to_csv(log_file.format(additional_interval))
    truncated_frequency = 60 if frequency > frequency_1min else 1500
    pairs[base_interval] = pairs[base_interval].tail(truncated_frequency)
    pairs[base_interval].to_csv(log_file.format(base_interval))
    if upsampled_intervals is not None:
        for subminute_interval in tqdm(upsampled_intervals, unit=' pair'):
            pairs[subminute_interval] = pairs[base_interval].tail(25)
            pairs[subminute_interval] = pairs[subminute_interval].resample(subminute_interval).agg('max')
            pairs[subminute_interval] = pairs[subminute_interval].fillna(method='pad').tail(60)
            pairs[subminute_interval].to_csv(log_file.format(subminute_interval))
    return pairs
