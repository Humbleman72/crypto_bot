#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        cryptocurrency/indicators.py
# By:          Samuel Duclos
# For          Myself
# Description: Indicators and triggers for output screeners.


# Library imports.
from cryptocurrency.renko import get_renko_trigger
from sys import float_info as sflt
from numpy import log
from pandas_ta.utils._core import signed_series, recent_minimum_index

import pandas_ta as ta
import pandas as pd
pd.options.mode.chained_assignment = None

def filter_in_market(function, dataset):
    def f(x):
        x = x.loc[:,~x.columns.duplicated()]
        return function(x)
    tickers_list = dataset.columns.get_level_values(0).unique().tolist()
    return pd.Series([ticker for ticker in tickers_list if f(dataset[ticker])], dtype='str')

def get_relative_volume_levels_smoothed_trigger(data, average1=26, average2=14, threshold=0.1):
    volume = data['volume']
    volume_average = ta.sma(close=volume, length=average1)
    relative_volume = volume / volume_average
    smoothed_relative_volume = ta.sma(close=relative_volume, length=average2)
    return (smoothed_relative_volume > threshold).iat[-1]

def get_relative_volume_levels_at_time_smoothed_thresholded(data):
    try:
        volume = data['volume']
        #volume = volume.groupby(pd.Grouper(freq='D')).cumsum()
        cum_volume = volume.groupby(pd.Grouper(freq='24h')).cumsum()
        #volume = volume.groupby(pd.Grouper(freq='60m')).cumsum()
        cum_rvol = (cum_volume / cum_volume.shift(1)).fillna(method='pad')
        rvol = (volume / volume.shift(1)).fillna(method='pad')
        bar_up = (data['close'] > data['open'])
        bar_up |= (data['close'] == data['open']) & (data['close'].diff() > 0)
        bar_up = bar_up.astype(int)
        bar_up = bar_up * 2 - 1
        cum_rvol_dir = cum_rvol * bar_up
        rvol_dir = rvol * bar_up
        rvol_indicator = ta.hma(rvol, length=14, talib=True)
        rvol_dir_indicator = ta.hma(rvol_dir, length=14, talib=True)
        cum_rvol_indicator = ta.hma(cum_rvol, length=14, talib=True)
        cum_rvol_dir_indicator = ta.hma(cum_rvol_dir, length=14, talib=True)
        rvol_indicator = rvol_indicator.rename('relative_volume_levels_smoothed')
        rvol_dir_indicator = rvol_dir_indicator.rename('relative_volume_levels_dir_smoothed')
        cum_rvol_indicator = cum_rvol_indicator.rename('cum_relative_volume_levels_smoothed')
        cum_rvol_dir_indicator = cum_rvol_dir_indicator.rename('cum_relative_volume_levels_dir_smoothed')
        #threshold = (ta.sma(rvol, length=100, talib=True) + ta.stdev(rvol, length=100, talib=True))
        threshold_dir = 0
        threshold = 2
        rvol_thresholded = (rvol_indicator > threshold)
        rvol_dir_thresholded = (rvol_dir_indicator > threshold_dir)
        cum_rvol_thresholded = (cum_rvol_indicator > threshold)
        cum_rvol_dir_thresholded = (cum_rvol_dir_indicator > threshold_dir)
        trigger = (rvol_thresholded | rvol_dir_thresholded | cum_rvol_thresholded | cum_rvol_dir_thresholded)
        trigger = trigger.at[-1]
    except Exception as e:
        print('rvol exception:', e)
        trigger = False
    return trigger

def get_not_square_wave_trigger_1(data):
    return not (data.iloc[-4:]['close'].unique().size < 2)

def get_not_square_wave_trigger_2(data):
    return not (data.iloc[-15:]['close'].unique().size < 6)

def get_not_square_wave_triggers(data, multiplier_schedule):
    triggers = True
    for multiplier in multiplier_schedule:
        period_1 = -4 * multiplier
        uniques_1 = 2 * multiplier
        square_wave_trigger_1 = (data.iloc[period_1:]['close'].unique().size < uniques_1)
        if square_wave_trigger_1:
            triggers = False
            break
        else:
            period_2 = -15 * multiplier
            uniques_2 = 6 * multiplier
            square_wave_trigger_2 = (data.iloc[period_2:]['close'].unique().size < uniques_2)
            if square_wave_trigger_2:
                triggers = False
                break
    return triggers

def get_not_square_wave_trigger_3(data):
    return (data[['open', 'high', 'low', 'close']].nunique(axis='columns') > 2).tail(2).all()

def get_bullish_price_trigger(data):
    return (data['close'] > data['high'].shift(1)).iat[-1]

def get_positive_RSI_trigger(data):
    RSI_6 = data.ta.rsi(length=6, talib=True)
    RSI_12 = data.ta.rsi(length=12, talib=True)
    RSI_24 = data.ta.rsi(length=24, talib=True)
    data = ((RSI_6 > RSI_12) | (RSI_6 > RSI_24) | (RSI_12 > RSI_24))
    return data.iat[-1]

def get_positive_momentum_trigger(data):
    KDJ = data.ta.kdj(length=5, signal=3, talib=True)
    return ((KDJ['J_5_3'] > KDJ['D_5_3']) & (KDJ['J_5_3'] > KDJ['K_5_3'])).iat[-1]

def get_positive_JMA_trigger(data):
    JMA = data.ta.jma(length=7, phase=0, talib=True)
    return (data['close'] < JMA).iat[-1]

def get_ease_of_movement(data):
    eom = ((data['high'] - data['low']) / (2 * data['volume'] + 1))
    eom *= (data['high'].diff(1) + data['low'].diff(1))
    precision = eom.abs().max()
    if precision < 1:
        eom *= 1 / precision
    return eom

def get_ease_of_movement_trigger(data):
    data[['open', 'high', 'low', 'close']] += sflt.epsilon
    data[['volume']] += 1
    log_price = log(data['close'])
    price_trough_index = recent_minimum_index(signed_series(log_price, initial=None))
    price_slope = ta.slope(close=log_price, length=price_trough_index, as_angle=True, 
                           to_degrees=True, talib=True)

    EOM = get_ease_of_movement(data)
    EOM_trough_index = recent_minimum_index(signed_series(EOM, initial=None))
    EOM_slope = ta.slope(close=EOM, length=EOM_trough_index, as_angle=True, 
                         to_degrees=True, talib=True)

    trigger = (price_slope <= EOM_slope)
    #trigger &= (EOM_slope >= 0.25)
    trigger &= (EOM_slope > 0.0)

    #breakout_trigger = ((EOM.shift(1) < 0.0) & (EOM > 0.0))
    #trigger |= breakout_trigger
    return trigger.iat[-1]

'''
def get_positive_PVR_trigger(data):
    price = data['close']
    volume = data['volume']
    volume.iat[-1] *= volume_multiplier
    price_trigger = (price.diff() > 0)
    volume_trigger = (volume.diff() > 0)
    trigger = (price_trigger & volume_trigger)
    return trigger.iat[-1]
'''

def get_daily_volume_minimum_trigger(data):
    return (data['volume'] > 1000000).iat[-1]

def get_daily_volume_change_trigger(data):
    return ((data['volume'].pct_change(1) * 100) > 300).iat[-1]

def get_minute_daily_volume_minimum_trigger(data):
    return (data['rolling_base_volume'] > 1000000).iat[-1]

def get_minute_daily_volume_change_trigger(data):
    return ((data['rolling_base_volume'].pct_change(1440) * 100) > 300).iat[-1]

def get_rising_volume_trigger(data):
    return (data['rolling_base_volume'].diff(1) > 0).iat[-1]

def get_RSI_reversal_trigger(data, rsi_length=2, upper_threshold=95, 
                             lower_threshold=5, positive=True):
    RSI = data.ta.rsi(length=rsi_length, talib=True)
    RSI_prev = RSI.shift(1)
    thresholds_bear = -((RSI_prev >= upper_threshold) & (RSI < upper_threshold)).astype(int)
    thresholds_bull = ((RSI_prev <= lower_threshold) & (RSI > lower_threshold)).astype(int)
    thresholds = (thresholds_bear + thresholds_bull)
    thresholds = thresholds.replace(to_replace=0, method='pad')
    return (thresholds == (1 if positive else -1)).iat[-1]

def get_heikin_ashi_trigger(data):
    def get_positive_trend_strength_trigger(data):
        ADX = data.ta.adx(talib=True)
        return (ADX['ADX_14'] < 0.20).iat[-3] and (ADX['ADX_14'] > 0.20).iat[-2]

    def get_not_negative_trend_strength_trigger(data):
        ADX = data.ta.adx(length=14, lensig=8, talib=True)
        return ((ADX['DMP_14'] > ADX['DMN_14']) and (ADX['ADX_14'] > 0.30)).iat[-1]

    def get_not_negative_rebound_trigger(data):
        CCI = data.ta.cci(length=22, talib=True)
        MFI = data.ta.mfi(length=11, talib=True)
        return ((CCI > 0) or (MFI > 20)).iat[-1]

    def get_positive_choppiness_trigger(data):
        CHOP = data.ta.chop(talib=True)
        return CHOP.iat[-1] < 38.2

    def get_positive_phase_trigger(data):
        MACD = data.ta.macd(talib=True)
        histogram = MACD['MACDs_12_26_9'] - MACD['MACD_12_26_9']
        return ((histogram.iat[-1] > histogram.iat[-2]) or \
                (MACD['MACD_12_26_9'].iat[-1] > MACD['MACDs_12_26_9'].iat[-1]))

    def get_positive_RSI_trigger(data):
        RSI_5 = data.ta.rsi(length=5, talib=True)
        return ((RSI_5 >= 60) & (RSI_5 <= 65)).iat[-1]

    def get_negative_PVR_trigger(data):
        price_trigger = (data['close'].iat[-1] < data['close'].iat[-2])
        volume_trigger = (data['volume'].iat[-1] > data['volume'].iat[-2])
        return price_trigger and volume_trigger

    def get_buy_trigger(data):
        return get_not_negative_rebound_trigger(data) and \
                (get_positive_choppiness_trigger(data) or \
                get_positive_trend_strength_trigger(data))

    def get_sell_trigger(data):
        return (((not get_positive_choppiness_trigger(data)) or \
                 get_negative_trend_strength_trigger(data) or \
                 (not get_positive_phase_trigger(data))) or \
                get_not_negative_rebound_trigger(data))

    heikin_ashi = data.ta.ha(talib=True)
    heikin_ashi_dataset_1 = heikin_ashi.rename(columns={'HA_open': 'open', 
                                                        'HA_high': 'high', 
                                                        'HA_low': 'low', 
                                                        'HA_close': 'close'})
    #heikin_ashi = heikin_ashi_dataset_1.ta.ha(talib=True)
    #heikin_ashi_dataset_2 = heikin_ashi.rename(columns={'HA_open': 'open', 
    #                                                    'HA_high': 'high', 
    #                                                    'HA_low': 'low', 
    #                                                    'HA_close': 'close'})
    #heikin_ashi = heikin_ashi_dataset_2.ta.ha(talib=True)
    #heikin_ashi_dataset_3 = heikin_ashi.rename(columns={'HA_open': 'open', 
    #                                                    'HA_high': 'high', 
    #                                                    'HA_low': 'low', 
    #                                                    'HA_close': 'close'})

    return True \
        if get_positive_phase_trigger(heikin_ashi_dataset_1) \
        else (get_not_negative_rebound_trigger(heikin_ashi_dataset_1) or \
              get_not_negative_trend_strength_trigger(heikin_ashi_dataset_1))

def screen_one(pair):
    frequency = pd.tseries.frequencies.to_offset((pair.index[1:] - pair.index[:-1]).min())
    frequency_1min = pd.tseries.frequencies.to_offset('1min')
    frequency_30min = pd.tseries.frequencies.to_offset('30min')
    frequency_1h = pd.tseries.frequencies.to_offset('1h')
    frequency_1d = pd.tseries.frequencies.to_offset('1d')
    if frequency == frequency_1min:
        pair['volume'] = pair['rolling_base_volume'].copy()
    else:
        pair['volume'] = pair['base_volume'].copy()
    if frequency < frequency_1min: # 15s for now, 5s later.
        # Supports 15s and 30s not_square_wave_triggers.
        if get_not_square_wave_triggers(pair, multiplier_schedule=[1, 2]):
            return True
    elif frequency == frequency_1min:
        # Supports 1min, 2min, 3min, 5min, 10min, 15min, 20min and 45min not_square_wave_triggers.
        if get_not_square_wave_triggers(pair, multiplier_schedule=[1, 2, 3, 5, 10, 15, 20, 45]):
            if get_bullish_price_trigger(pair):
                if get_rising_volume_trigger(pair):
                    if get_minute_daily_volume_minimum_trigger(pair):
                        if get_minute_daily_volume_change_trigger(pair):
                            if get_heikin_ashi_trigger(pair):
                                return True
    elif frequency == frequency_30min:
        # Supports 30min not_square_wave_triggers.
        if get_not_square_wave_triggers(pair, multiplier_schedule=[1]):
            if get_renko_trigger(pair, compress=False, 
                                 direction_type='long', 
                                 trigger_type='simple', 
                                 method='atr', plot=False):
                return True
    elif frequency == frequency_1h: # 1h intervals and up won't be active for at least a day after bootstrapping.
        # Supports 1h, 2h, 3h, 4h, 6h, 8h and 12h not_square_wave_triggers (too much for buffer size).
        if get_not_square_wave_triggers(pair, multiplier_schedule=[1, 2, 3, 4, 6, 8, 12]):
            if get_relative_volume_levels_at_time_smoothed_thresholded(pair):
                return True
    elif frequency == frequency_1d: # 1d intervals and up won't be active for at least a day after bootstrapping.
        # Supports 1d, 3d, 7d and 28d not_square_wave_triggers (too much for buffer size).
        if get_not_square_wave_triggers(pair, multiplier_schedule=[1, 3, 7, 28]):
            if get_daily_volume_minimum_trigger(pair):
                if get_daily_volume_change_trigger(pair):
                    if get_relative_volume_levels_smoothed_trigger(pair, average1=26, average2=14, threshold=0.1):
                        return True
    else:
        # Supports 1T not_square_wave_triggers.
        if get_not_square_wave_triggers(pair, multiplier_schedule=[1]):
            if get_rising_volume_trigger(pair):
                return True
    return False
