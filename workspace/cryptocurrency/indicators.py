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

def get_relative_volume_levels_smoothed_thresholded(data):
    try:
        volume = data['volume']
        #volume = volume.groupby(pd.Grouper(freq='D')).cumsum()
        volume = volume.groupby(pd.Grouper(freq='24h')).cumsum()
        #volume = volume.groupby(pd.Grouper(freq='60m')).cumsum()
        rvol = (volume / volume.shift(1))
        rvol = rvol.fillna(method='pad')
        bar_up = (ticker['close'] > ticker['open'])
        bar_up |= (ticker['close'] == ticker['open']) & (ticker['close'].diff() > 0)
        bar_up = bar_up.astype(int)
        bar_up = bar_up * 2 - 1
        rvol *= bar_up
        rvol_indicator = ta.hma(rvol, length=14, talib=True)
        rvol_indicator = rvol_indicator.rename('relative_volume_levels_smoothed')
        #threshold = (ta.sma(rvol, length=100, talib=True) + ta.stdev(rvol, length=100, talib=True))
        threshold = 2
        rvol_thresholded = (rvol_indicator > threshold).iloc[-1]
    except:
        rvol_thresholded = False
    return rvol_thresholded

def get_not_square_wave_trigger_1(data):
    return not (data.iloc[-4:]['close'].unique().size < 2)

def get_not_square_wave_trigger_2(data):
    return not (data.iloc[-15:]['close'].unique().size < 6)

def get_not_square_wave_trigger_3(data):
    return (data[['open', 'high', 'low', 'close']].nunique(axis='columns') > 2).tail(2).all()

def get_bullish_price_trigger(data):
    return (data['close'] > data['high'].shift(1)).iloc[-1]

def get_positive_RSI_trigger(data):
    RSI_6 = data.ta.rsi(length=6, talib=True)
    RSI_12 = data.ta.rsi(length=12, talib=True)
    RSI_24 = data.ta.rsi(length=24, talib=True)
    data = ((RSI_6 > RSI_12) | (RSI_6 > RSI_24) | (RSI_12 > RSI_24))
    return data.iloc[-1]

def get_positive_momentum_trigger(data):
    KDJ = data.ta.kdj(length=5, signal=3, talib=True)
    return ((KDJ['J_5_3'] > KDJ['D_5_3']) & (KDJ['J_5_3'] > KDJ['K_5_3'])).iloc[-1]

def get_positive_JMA_trigger(data):
    JMA = data.ta.jma(length=7, phase=0, talib=True)
    return (data['close'] < JMA).iloc[-1]

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
    return trigger.iloc[-1]

'''
def get_positive_PVR_trigger(data):
    price = data['close']
    volume = data['volume']
    volume.iloc[-1] *= volume_multiplier
    price_trigger = (price.diff() > 0)
    volume_trigger = (volume.diff() > 0)
    trigger = (price_trigger & volume_trigger)
    return trigger.iloc[-1]
'''

def get_rising_volume_trigger(data):
    return (data['rolling_base_volume'].diff(1) > 0).iloc[-1]

def get_RSI_reversal_trigger(data, rsi_length=2, upper_threshold=95, 
                             lower_threshold=5, positive=True):
    RSI = data.ta.rsi(length=rsi_length, talib=True)
    RSI_prev = RSI.shift(1)
    thresholds_bear = -((RSI_prev >= upper_threshold) & (RSI < upper_threshold)).astype(int)
    thresholds_bull = ((RSI_prev <= lower_threshold) & (RSI > lower_threshold)).astype(int)
    thresholds = (thresholds_bear + thresholds_bull)
    thresholds = thresholds.replace(to_replace=0, method='pad')
    return (thresholds == (1 if positive else -1)).iloc[-1]

def get_heikin_ashi_trigger(data):
    def get_positive_trend_strength_trigger(data):
        ADX = data.ta.adx(talib=True)
        return (ADX['ADX_14'] < 0.20).iloc[-3] and (ADX['ADX_14'] > 0.20).iloc[-2]

    def get_not_negative_trend_strength_trigger(data):
        ADX = data.ta.adx(length=14, lensig=8, talib=True)
        return ((ADX['DMP_14'] > ADX['DMN_14']) and (ADX['ADX_14'] > 0.30)).iloc[-1]

    def get_not_negative_rebound_trigger(data):
        CCI = data.ta.cci(length=22, talib=True)
        MFI = data.ta.mfi(length=11, talib=True)
        return ((CCI > 0) or (MFI > 20)).iloc[-1]

    def get_positive_choppiness_trigger(data):
        CHOP = data.ta.chop(talib=True)
        return CHOP.iloc[-1] < 38.2

    def get_positive_phase_trigger(data):
        MACD = data.ta.macd(talib=True)
        histogram = MACD['MACDs_12_26_9'] - MACD['MACD_12_26_9']
        return ((histogram.iloc[-1] > histogram.iloc[-2]) or \
                (MACD['MACD_12_26_9'].iloc[-1] > MACD['MACDs_12_26_9'].iloc[-1]))

    def get_positive_RSI_trigger(data):
        RSI_5 = data.ta.rsi(length=5, talib=True)
        return ((RSI_5 >= 60) & (RSI_5 <= 65)).iloc[-1]

    def get_negative_PVR_trigger(data):
        price_trigger = (data['close'].iloc[-1] < data['close'].iloc[-2])
        volume_trigger = (data['volume'].iloc[-1] > data['volume'].iloc[-2])
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
    if frequency < frequency_1min:
        pair['volume'] = pair['rolling_base_volume'].copy()
    else:
        pair['volume'] = pair['base_volume'].copy()
    if frequency == frequency_30min:
        if get_not_square_wave_trigger_1(pair):
            if get_not_square_wave_trigger_2(pair):
                #if get_bullish_price_trigger(pair):
                #if get_heikin_ashi_trigger(pair):
                if get_renko_trigger(pair, compress=False, 
                                     direction_type='long', 
                                     trigger_type='simple', 
                                     method='atr', plot=False):
                    return True
    elif frequency == frequency_1h:
        if get_relative_volume_levels_smoothed_thresholded(pair):
            return True
    else:
        if get_not_square_wave_trigger_1(pair):
            if get_not_square_wave_trigger_2(pair):
                #if frequency < frequency_1min:
                #    return True
                #else:
                    #if get_rising_volume_trigger(pair):
                #if get_heikin_ashi_trigger(pair):
                return True
    return False
