#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        cryptocurrency/volume_conversion.py
# By:          Samuel Duclos
# For          Myself
# Description: Whole market volume to/from 24h rolling volume conversion.

# Library imports.
import numpy as np
import pandas as pd

# Function definitions.
def add_rolling_volumes(df):
    df.sort_index(axis='columns', inplace=True)
    df.columns = df.columns.swaplevel(0, 1)
    df_rolling = df[['base_volume', 'quote_volume']].copy()
    df_rolling.rename(columns={'base_volume': 'rolling_base_volume', 
                               'quote_volume': 'rolling_quote_volume'}, 
                      inplace=True)
    df_rolling = df_rolling.rolling('1440min').agg(np.sum)
    df = pd.concat([df, df_rolling], join='outer', axis='columns')
    df = df[['open', 'high', 'low', 'close', 'base_volume', 'quote_volume', 
             'rolling_base_volume', 'rolling_quote_volume']]
    df.columns = df.columns.swaplevel(0, 1)
    return df

def recalculate_volumes(df):
    df.iloc[-2:,df.columns.get_level_values(1) == 'base_volume'] = \
        df.xs('rolling_base_volume', axis=1, level=1).diff(1).tail(2) + \
        df.xs('base_volume', axis=1, level=1).shift(1440).tail(2)
    df.iloc[-2:,df.columns.get_level_values(1) == 'quote_volume'] = \
        df.xs('rolling_quote_volume', axis=1, level=1).diff(1).tail(2) + \
        df.xs('quote_volume', axis=1, level=1).shift(1440).tail(2)
    return df
