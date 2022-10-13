#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        cryptocurrency/ohlcvs.py
# By:          Samuel Duclos
# For          Myself
# Description: Populate OHLCV DataFrames from the Binance API.

# Library imports.
from cryptocurrency.ohlcv import download_pair
from tqdm import tqdm
import pandas as pd

# Function definitions.
def download_pairs(client, assets, interval='1m', period=1000):
    def named_pairs_to_df(assets, pairs):
        df = pd.DataFrame()
        column_names = pairs[0].columns.tolist()
        for (asset, pair) in tqdm(zip(assets, pairs), unit=' named pair'):
            columns = [(asset, column) for column in column_names]
            pair.columns = pd.MultiIndex.from_tuples(columns, names=['symbol', 'pair'])
            df = pd.concat([df, pair], axis='columns')
        return df
    pairs = [download_pair(client=client, symbol=symbol, interval=interval, 
                           period=period) for symbol in tqdm(assets, unit=' pair')]
    return named_pairs_to_df(assets, pairs)
