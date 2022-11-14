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
    frequency = (df.index[1:] - df.index[:-1]).min()
    frequency = pd.tseries.frequencies.to_offset(frequency)
    frequency_interval = pd.tseries.frequencies.to_offset(interval)
    frequency_1min = pd.tseries.frequencies.to_offset('1min')
    frequency_1d = pd.tseries.frequencies.to_offset('1d')
    volume_operation = 'sum' if frequency >= frequency_1min else 'last'
    values = ['open', 'high', 'low', 'close', 'base_volume', 'quote_volume']
    aggfunc = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 
               'base_volume': volume_operation, 'quote_volume': volume_operation}
    values += ['rolling_base_volume', 'rolling_quote_volume']
    if frequency_interval >= frequency_1d:
        aggfunc['rolling_base_volume'] = 'sum'
        aggfunc['rolling_quote_volume'] = 'sum'
    else:
        aggfunc['rolling_base_volume'] = 'last'
        aggfunc['rolling_quote_volume'] = 'last'
    df = df.pivot_table(index=['date'], columns=['symbol'], values=values, aggfunc=aggfunc)
    df['base_volume'] = df['base_volume'].fillna(0)
    df['quote_volume'] = df['quote_volume'].fillna(0)
    df['rolling_base_volume'] = df['rolling_base_volume'].fillna(method='pad').fillna(method='backfill')
    df['rolling_quote_volume'] = df['rolling_quote_volume'].fillna(method='pad').fillna(method='backfill')
    df = df.fillna(method='pad').fillna(method='backfill') # Last resort.
    df.columns = df.columns.swaplevel(0, 1)
    df = df.sort_index(axis='index')
    if interval == '1min':
        df = recalculate_volumes(df)
    return df
