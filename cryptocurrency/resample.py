#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        cryptocurrency/resample.py
# By:          Samuel Duclos
# For          Myself
# Description: Provides whole market downsampling.

# Library imports.
from cryptocurrency.volume_conversion import recalculate_volumes
import pandas as pd

# Function definitions.
def resample(df, interval='1min'):
    df.index = pd.DatetimeIndex(df.index).round(interval)
    df = df.stack(level=0).reset_index(level=1)
    frequency = pd.tseries.frequencies.to_offset((df.index[1:] - df.index[:-1]).min())
    frequency_interval = pd.tseries.frequencies.to_offset(interval)
    frequency_1min = pd.tseries.frequencies.to_offset('1min')
    frequency_1d = pd.tseries.frequencies.to_offset('1d')
    volume_operation = 'sum' if frequency > frequency_1min else 'max'
    values = ['open', 'high', 'low', 'close', 'base_volume', 'quote_volume']
    aggfunc = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 
               'base_volume': volume_operation, 'quote_volume': volume_operation}
    if frequency_interval < frequency_1d:
        values += ['rolling_base_volume', 'rolling_quote_volume']
        aggfunc['rolling_base_volume'] = volume_operation
        aggfunc['rolling_quote_volume'] = volume_operation
    #else:
    #    df = df.drop(columns=['rolling_base_volume', 'rolling_quote_volume'])
    df = df.pivot_table(index=['date'], columns=['symbol'], 
                        values=values, aggfunc=aggfunc)
    df['base_volume'] = df['base_volume'].fillna(0)
    df['quote_volume'] = df['quote_volume'].fillna(0)
    if frequency_interval < frequency_1d:
        df['rolling_base_volume'] = df['rolling_base_volume'].fillna(0)
        df['rolling_quote_volume'] = df['rolling_quote_volume'].fillna(0)
    df = df.fillna(method='pad')
    df.columns = df.columns.swaplevel(0, 1)
    df = df.sort_index(axis='index')
    if interval == '1min':
        df = recalculate_volumes(df)
    return df
