#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        cryptocurrency/conversion_table.py
# By:          Samuel Duclos
# For          Myself
# Description: Binance pair conversion table retrieval and basic pair filtering.

# Library imports.
from cryptocurrency.conversion import convert_price, get_base_asset_from_pair, get_quote_asset_from_pair
import datetime
import pandas as pd

def get_conversion_table(client, exchange_info, offset_s=0, as_pair=False, 
                         dump_raw=False, minimal=True, extra_minimal=True, convert_to_USDT=True):
    """
    Fetches and prepares data used to calculate prices, volumes and other stats.
    :param client: object from python-binance useful for calling client.get_ticker().
    :param exchange_info: Pre-calculated exchange information on all tickers.
    :return: pd.DataFrame containing all preprocessed conversion table info.
    :column is_shorted: is the symbol made from inversion.
    :column symbol: concatenated string made from base_asset and quote_asset.
    :column shorted_symbol: symbol with inverted base_asset and quote_asset.
    :column base_asset: asset on the left.
    :column quote_asset: asset on the right.
    :column price_change: (close - open).
    :column price_change_percent: (((close - open) / open) * 100).
    :column USDT_price_change: (USDT_close - USDT_open).
    :column USDT_price_change_percent: (((USDT_close - USDT_open) / USDT_open) * 100).
    :column weighted_average_price: weighted average price.
    :column close_shifted: close price of the previous day.
    :column open: open price of the day.
    :column high: high price of the day.
    :column low: low price of the day.
    :column close: close price of the day.
    :column last_volume: volume of the last price update.
    :column USDT_bid_price: USDT-converted bid price.
    :column USDT_ask_price: USDT-converted ask price.
    :column USDT_bid_volume: USDT-converted bid volume.
    :column USDT_ask_volume: USDT-converted ask volume.
    :column bid_price: price of the bid.
    :column bid_volume: volume of the bid at bid_price.
    :column ask_price: price of the ask.
    :column ask_volume: volume of the ask at ask_price.
    :column rolling_base_volume: rolling_base_volume given by the API.
    :column rolling_quote_volume: rolling_quote_volume given by the API.
    :column open_time: close_time minus 24 hours.
    :column close_time: time from epoch in milliseconds of the last price update.
    :column first_ID: transaction ID from 1 day ago.
    :column last_ID: latest transaction ID.
    :column count: value calculated by subtracting first_ID from last_ID.
    :column USDT_open: USDT-converted open price.
    :column USDT_high: USDT-converted high price.
    :column USDT_low: USDT-converted low price.
    :column USDT_price: USDT-converted close price.
    :column rolling_USDT_base_volume: USDT-converted rolling_base_volume.
    :column rolling_USDT_quote_volume: USDT-converted rolling_quote_volume.
    :column rolling_traded_volume: sum by base_asset of all USDT-converted volumes.
    :column importance: rolling_USDT_base_volume divided by rolling_traded_volume.
    :column traded_price: sum by base_asset of all (close prices times importance).
    :column traded_bid_price: sum by base_asset of all (bid prices times importance).
    :column traded_ask_price: sum by base_asset of all (ask prices times importance).
    :column bid_ask_percent_change: ((ask_price - bid_price) / ask_price) * 100).
    :column bid_ask_volume_percent_change: ((bid_volume / (bid_volume + ask_volume)) * 100).
    :column traded_bid_ask_percent_change: ((traded_ask_price - traded_bid_price) / traded_ask_price) * 100).
    :column traded_bid_ask_volume_percent_change: ((traded_bid_volume / (traded_bid_volume + traded_ask_volume)) * 100).
    """
    if not as_pair:
        convert_to_USDT = True

    if extra_minimal:
        minimal = True

    conversion_table = pd.DataFrame(client.get_ticker())

    conversion_table = conversion_table[conversion_table['symbol'].isin(exchange_info['symbol'])]
    conversion_table['base_asset'] = \
        conversion_table['symbol'].apply(lambda x: get_base_asset_from_pair(x, exchange_info=exchange_info))
    conversion_table['quote_asset'] = \
        conversion_table['symbol'].apply(lambda x: get_quote_asset_from_pair(x, exchange_info=exchange_info))

    if minimal:
        conversion_table = \
            conversion_table[['symbol', 'base_asset', 'quote_asset', 'openPrice', 'lastPrice', 
                              'volume', 'quoteVolume', 'count', 'bidPrice', 'askPrice', 'bidQty', 
                              'askQty', 'closeTime', 'priceChangePercent']]

    conversion_table = \
        conversion_table.rename(columns={'openPrice': 'open', 'lastPrice': 'close', 
                                         'volume': 'rolling_base_volume', 
                                         'quoteVolume': 'rolling_quote_volume', 
                                         'bidPrice': 'bid_price', 'askPrice': 'ask_price', 
                                         'bidQty': 'bid_volume', 'askQty': 'ask_volume', 
                                         'closeTime': 'close_time', 
                                         'priceChangePercent': 'price_change_percent'})

    if not minimal:
        conversion_table = \
            conversion_table.rename(columns={'highPrice': 'high', 'lowPrice': 'low', 
                                             'lastQty': 'last_volume', 'firstId': 'first_ID', 
                                             'lastId': 'last_ID', 'openTime': 'open_time', 
                                             'prevClosePrice': 'close_shifted', 
                                             'weightedAvgPrice': 'weighted_average_price', 
                                             'priceChange': 'price_change'})
    if dump_raw:
        conversion_table.to_csv('crypto_logs/conversion_table.txt')

    if minimal:
        conversion_table[['open', 'close', 'rolling_base_volume', 'rolling_quote_volume', 'bid_price', 
                          'ask_price', 'bid_volume', 'ask_volume', 'price_change_percent']] = \
            conversion_table[['open', 'close', 'rolling_base_volume', 'rolling_quote_volume', 'bid_price', 
                              'ask_price', 'bid_volume', 'ask_volume', 'price_change_percent']].astype(float)
    else:
        conversion_table[['open', 'high', 'low', 'close', 'close_shifted', 'rolling_base_volume', 
                          'rolling_quote_volume', 'bid_price', 'ask_price', 'bid_volume', 'ask_volume', 
                          'price_change_percent']] = \
            conversion_table[['open', 'high', 'low', 'close', 'close_shifted', 'rolling_base_volume', 
                              'rolling_quote_volume', 'bid_price', 'ask_price', 'bid_volume', 'ask_volume', 
                              'price_change_percent']].astype(float)

    conversion_table[['close_time', 'count']] = \
        conversion_table[['close_time', 'count']].astype(int)
    conversion_table['close_time'] = (conversion_table['close_time'] + offset_s * 1000)

    conversion_table['rolling_base_quote_volume'] = \
        conversion_table['rolling_quote_volume'] / conversion_table['close']

    if convert_to_USDT:
        if not minimal:
            conversion_table['USDT_high'] = \
                conversion_table.apply(
                    lambda x: convert_price(size=1, from_asset=x['base_asset'], to_asset='USDT', 
                                            conversion_table=conversion_table, 
                                            exchange_info=exchange_info, key='close', 
                                            priority='accuracy'), axis='columns')
            conversion_table['USDT_low'] = \
                conversion_table.apply(
                    lambda x: convert_price(size=1, from_asset=x['base_asset'], to_asset='USDT', 
                                            conversion_table=conversion_table, 
                                            exchange_info=exchange_info, key='close', 
                                            priority='accuracy'), axis='columns')
        conversion_table['USDT_open'] = \
            conversion_table.apply(lambda x: convert_price(size=1, from_asset=x['base_asset'], to_asset='USDT', 
                                                           conversion_table=conversion_table, 
                                                           exchange_info=exchange_info, key='open', 
                                                           priority='accuracy'), axis='columns')
        conversion_table['USDT_price'] = \
            conversion_table.apply(lambda x: convert_price(size=1, from_asset=x['base_asset'], to_asset='USDT', 
                                                           conversion_table=conversion_table, 
                                                           exchange_info=exchange_info, key='close', 
                                                           priority='accuracy'), axis='columns')
        conversion_table['rolling_USDT_base_volume'] = \
            conversion_table['rolling_base_volume'] * conversion_table['USDT_price'].astype(float)
        conversion_table['rolling_USDT_quote_volume'] = \
            conversion_table['rolling_base_quote_volume'] * conversion_table['USDT_price'].astype(float)
        conversion_table = conversion_table.drop(columns=['rolling_base_quote_volume'])

        if not extra_minimal:
            conversion_table['USDT_bid_price'] = \
                conversion_table.apply(lambda x: convert_price(size=x['bid_price'], from_asset=x['base_asset'], 
                                                               to_asset='USDT', conversion_table=conversion_table, 
                                                               exchange_info=exchange_info, key='close', 
                                                               priority='accuracy'), axis='columns')
            conversion_table['USDT_ask_price'] = \
                conversion_table.apply(lambda x: convert_price(size=x['ask_price'], from_asset=x['base_asset'], 
                                                               to_asset='USDT', conversion_table=conversion_table, 
                                                               exchange_info=exchange_info, key='close', 
                                                               priority='accuracy'), axis='columns')
            conversion_table['USDT_bid_volume'] = \
                conversion_table['bid_volume'] * conversion_table['USDT_bid_price'].astype(float)
            conversion_table['USDT_ask_volume'] = \
                conversion_table['ask_volume'] * conversion_table['USDT_ask_price'].astype(float)

        conversion_table['USDT_price_change'] = \
            (conversion_table['USDT_price'].astype(float) - conversion_table['USDT_open'].astype(float))
        conversion_table['USDT_price_change_percent'] = \
            ((conversion_table['USDT_price_change'] / conversion_table['USDT_open'].astype(float)) * 100)

        conversion_table['is_shorted'] = False

        conversion_table_swapped = conversion_table.copy()
        if minimal:
            if extra_minimal:
                conversion_table_swapped.loc[:, ['symbol', 'price_change_percent', 'close', 'ask_price', 
                                                 'ask_volume', 'bid_price', 'bid_volume', 'open', 
                                                 'rolling_quote_volume', 'rolling_base_volume', 'close_time', 
                                                 'count', 'quote_asset', 'base_asset', 'USDT_open', 'USDT_price', 
                                                 'rolling_USDT_quote_volume', 'rolling_USDT_base_volume', 
                                                 'USDT_price_change_percent', 'is_shorted']] = \
                    conversion_table_swapped.loc[:, ['symbol', 'price_change_percent', 'close', 'bid_price', 
                                                     'bid_volume', 'ask_price', 'ask_volume', 'open', 
                                                     'rolling_base_volume', 'rolling_quote_volume', 'close_time', 
                                                     'count', 'base_asset', 'quote_asset', 'USDT_open', 'USDT_price', 
                                                     'rolling_USDT_base_volume', 'rolling_USDT_quote_volume', 
                                                     'USDT_price_change_percent', 'is_shorted']].values
            else:
                conversion_table_swapped.loc[:, ['symbol', 'price_change_percent', 'close', 'ask_price', 
                                                 'ask_volume', 'bid_price', 'bid_volume', 'open', 
                                                 'rolling_quote_volume', 'rolling_base_volume', 'close_time', 
                                                 'count', 'quote_asset', 'base_asset', 'USDT_open', 'USDT_price', 
                                                 'rolling_USDT_quote_volume', 'rolling_USDT_base_volume', 
                                                 'USDT_ask_price', 'USDT_bid_price', 'USDT_ask_volume', 
                                                 'USDT_bid_volume', 'USDT_price_change_percent', 'is_shorted']] = \
                    conversion_table_swapped.loc[:, ['symbol', 'price_change_percent', 'close', 'bid_price', 
                                                     'bid_volume', 'ask_price', 'ask_volume', 'open', 
                                                     'rolling_base_volume', 'rolling_quote_volume', 'close_time', 
                                                     'count', 'base_asset', 'quote_asset', 'USDT_open', 'USDT_price', 
                                                     'rolling_USDT_base_volume', 'rolling_USDT_quote_volume', 
                                                     'USDT_bid_price', 'USDT_ask_price', 'USDT_bid_volume', 
                                                     'USDT_ask_volume', 'USDT_price_change_percent', 
                                                     'is_shorted']].values
        else:
            conversion_table_swapped.loc[:, ['symbol', 'price_change', 'price_change_percent', 
                                             'weighted_average_price', 'close_shifted', 'close', 
                                             'last_volume', 'ask_price', 'ask_volume', 'bid_price', 
                                             'bid_volume', 'open', 'high', 'low', 'rolling_quote_volume', 
                                             'rolling_base_volume', 'open_time', 'close_time', 'first_ID', 
                                             'last_ID', 'count', 'quote_asset', 'base_asset', 'USDT_open', 
                                             'USDT_high', 'USDT_low', 'USDT_price', 'rolling_USDT_quote_volume', 
                                             'rolling_USDT_base_volume', 'USDT_ask_price', 'USDT_bid_price', 
                                             'USDT_ask_volume', 'USDT_bid_volume', 'USDT_price_change', 
                                             'USDT_price_change_percent', 'is_shorted']] = \
                conversion_table_swapped.loc[:, ['symbol', 'price_change', 'price_change_percent', 
                                                 'weighted_average_price', 'close_shifted', 'close', 
                                                 'last_volume', 'bid_price', 'bid_volume', 'ask_price', 
                                                 'ask_volume', 'open', 'high', 'low', 'rolling_base_volume', 
                                                 'rolling_quote_volume', 'open_time', 'close_time', 'first_ID', 
                                                 'last_ID', 'count', 'base_asset', 'quote_asset', 
                                                 'USDT_open', 'USDT_high', 'USDT_low', 'USDT_price', 
                                                 'rolling_USDT_base_volume', 'rolling_USDT_quote_volume', 
                                                 'USDT_bid_price', 'USDT_ask_price', 'USDT_bid_volume', 
                                                 'USDT_ask_volume', 'USDT_price_change', 
                                                 'USDT_price_change_percent', 'is_shorted']].values

        conversion_table_swapped['symbol'] = \
            conversion_table_swapped['base_asset'] + conversion_table_swapped['quote_asset']

        if minimal:
            if extra_minimal:
                conversion_table_swapped.loc[:, ['open', 'close', 'bid_price', 'ask_price', 'USDT_open', 
                                                 'USDT_price', 'USDT_price_change_percent']] = \
                    1 / conversion_table_swapped.loc[:, ['open', 'close', 'bid_price', 'ask_price', 'USDT_open', 
                                                         'USDT_price', 'USDT_price_change_percent']].astype(float)
            else:
                conversion_table_swapped.loc[:, ['open', 'close', 'bid_price', 'ask_price', 'USDT_open', 
                                                 'USDT_price', 'USDT_bid_price', 'USDT_ask_price', 
                                                 'USDT_price_change_percent']] = \
                    1 / conversion_table_swapped.loc[:, ['open', 'close', 'bid_price', 'ask_price', 'USDT_open', 
                                                         'USDT_price', 'USDT_bid_price', 'USDT_ask_price', 
                                                         'USDT_price_change_percent']].astype(float)
        else:
            conversion_table_swapped.loc[:, ['open', 'high', 'low', 'close', 'close_shifted', 'bid_price', 
                                             'ask_price', 'USDT_open', 'USDT_high', 'USDT_low', 'USDT_price', 
                                             'USDT_bid_price', 'USDT_ask_price', 'USDT_price_change', 
                                             'USDT_price_change_percent']] = \
                1 / conversion_table_swapped.loc[:, ['open', 'high', 'low', 'close', 'close_shifted', 
                                                     'bid_price', 'ask_price', 'USDT_open', 'USDT_high', 
                                                     'USDT_low', 'USDT_price', 'USDT_bid_price', 'USDT_ask_price', 
                                                     'USDT_price_change', 'USDT_price_change_percent']].astype(float)
        conversion_table_swapped['is_shorted'] = True

        conversion_table = pd.concat([conversion_table, conversion_table_swapped], join='outer', axis='index')

        traded_volume = conversion_table.groupby(by='base_asset').agg('sum')
        traded_volume = traded_volume['rolling_USDT_base_volume']
        conversion_table['rolling_traded_volume'] = \
            conversion_table.apply(lambda x: traded_volume.loc[x['base_asset']], axis='columns')
        traded_bid_volume = conversion_table.groupby(by='base_asset').agg('sum')
        if not extra_minimal:
            traded_bid_volume = traded_bid_volume['USDT_bid_volume']
            conversion_table['traded_bid_volume'] = \
                conversion_table.apply(lambda x: traded_bid_volume.loc[x['base_asset']], axis='columns')
            traded_ask_volume = conversion_table.groupby(by='base_asset').agg('sum')
            traded_ask_volume = traded_ask_volume['USDT_ask_volume']
            conversion_table['traded_ask_volume'] = \
                conversion_table.apply(lambda x: traded_ask_volume.loc[x['base_asset']], axis='columns')

            conversion_table['importance'] = \
                conversion_table['rolling_USDT_base_volume'] / conversion_table['rolling_traded_volume']

            conversion_table['importance_weighted_price'] = \
                conversion_table['USDT_price'].astype(float) * conversion_table['importance']
            conversion_table['importance_weighted_bid_price'] = \
                conversion_table['USDT_bid_price'].astype(float) * conversion_table['importance']
            conversion_table['importance_weighted_ask_price'] = \
                conversion_table['USDT_ask_price'].astype(float) * conversion_table['importance']

            importance_weighted_price = conversion_table.groupby(by='base_asset').agg('sum')
            importance_weighted_price = importance_weighted_price['importance_weighted_price']
            conversion_table['traded_price'] = \
                conversion_table.apply(lambda x: importance_weighted_price.loc[x['base_asset']], axis='columns')
            importance_weighted_bid_price = conversion_table.groupby(by='base_asset').agg('sum')
            importance_weighted_bid_price = importance_weighted_bid_price['importance_weighted_bid_price']
            conversion_table['traded_bid_price'] = \
                conversion_table.apply(lambda x: importance_weighted_bid_price.loc[x['base_asset']], axis='columns')
            importance_weighted_ask_price = conversion_table.groupby(by='base_asset').agg('sum')
            importance_weighted_ask_price = importance_weighted_ask_price['importance_weighted_ask_price']
            conversion_table['traded_ask_price'] = \
                conversion_table.apply(lambda x: importance_weighted_ask_price.loc[x['base_asset']], axis='columns')

            conversion_table['traded_bid_ask_percent_change'] = \
                ((conversion_table['traded_ask_price'] - conversion_table['traded_bid_price']) / \
                 conversion_table['traded_ask_price'])
            conversion_table['traded_bid_ask_volume_percent_change'] = \
                (conversion_table['traded_bid_volume'] / (conversion_table['traded_bid_volume'] + \
                                                          conversion_table['traded_ask_volume']))
            conversion_table[['traded_bid_ask_percent_change', 'traded_bid_ask_volume_percent_change']] *= 100

        conversion_table = conversion_table[~conversion_table['is_shorted']]

    conversion_table['bid_ask_percent_change'] = \
        ((conversion_table['ask_price'] - conversion_table['bid_price']) / conversion_table['ask_price'])
    conversion_table['bid_ask_volume_percent_change'] = \
        (conversion_table['bid_volume'] / (conversion_table['bid_volume'] + conversion_table['ask_volume']))
    conversion_table[['bid_ask_percent_change', 'bid_ask_volume_percent_change']] *= 100
    if as_pair and convert_to_USDT:
        if minimal:
            if extra_minimal:
                conversion_table = \
                    conversion_table[['symbol', 'base_asset', 'quote_asset', 'price_change_percent', 'close', 
                                      'bid_price', 'bid_volume', 'ask_price', 'ask_volume', 'close_time', 
                                      'count', 'rolling_base_volume', 'rolling_quote_volume', 
                                      'USDT_price_change_percent', 'USDT_price', 'rolling_USDT_base_volume', 
                                      'rolling_USDT_quote_volume', 'rolling_traded_volume', 
                                      'bid_ask_percent_change', 'bid_ask_volume_percent_change']]
            else:
                conversion_table = \
                    conversion_table[['symbol', 'base_asset', 'quote_asset', 'price_change_percent', 'close', 
                                      'bid_price', 'bid_volume', 'ask_price', 'ask_volume', 'close_time', 
                                      'count', 'rolling_base_volume', 'rolling_quote_volume', 
                                      'USDT_price_change_percent', 'USDT_price', 'rolling_USDT_base_volume', 
                                      'rolling_USDT_quote_volume', 'USDT_bid_price', 'USDT_ask_price', 
                                      'USDT_bid_volume', 'USDT_ask_volume', 'rolling_traded_volume', 
                                      'traded_bid_volume', 'traded_ask_volume', 'traded_price', 
                                      'traded_bid_price', 'traded_ask_price', 'bid_ask_percent_change', 
                                      'bid_ask_volume_percent_change', 'traded_bid_ask_percent_change', 
                                      'traded_bid_ask_volume_percent_change']]
        else:
            conversion_table = \
                conversion_table[['symbol', 'base_asset', 'quote_asset', 'is_shorted', 'price_change_percent', 
                                  'weighted_average_price', 'open', 'high', 'low', 'close', 'close_shifted', 
                                  'last_volume', 'bid_price', 'bid_volume', 'ask_price', 'ask_volume', 
                                  'close_time', 'last_ID', 'count', 'rolling_base_volume', 'rolling_quote_volume', 
                                  'importance', 'USDT_price_change_percent', 'USDT_open', 
                                  'USDT_high', 'USDT_low', 'USDT_price', 'rolling_USDT_base_volume', 
                                  'rolling_USDT_quote_volume', 'USDT_bid_price', 'USDT_ask_price', 
                                  'USDT_bid_volume', 'USDT_ask_volume', 'rolling_traded_volume', 
                                  'traded_bid_volume', 'traded_ask_volume', 'traded_price', 
                                  'traded_bid_price', 'traded_ask_price', 'bid_ask_percent_change', 
                                  'bid_ask_volume_percent_change', 'traded_bid_ask_percent_change', 
                                  'traded_bid_ask_volume_percent_change']]
    else:
        if convert_to_USDT:
            if minimal:
                if extra_minimal:
                    conversion_table = \
                        conversion_table[['base_asset', 'USDT_price_change_percent', 'close_time', 
                                          'bid_volume', 'ask_volume', 'bid_price', 'close', 'ask_price', 
                                          'count', 'rolling_traded_volume', 'bid_ask_percent_change', 
                                          'bid_ask_volume_percent_change']]
                else:
                    conversion_table = \
                        conversion_table[['base_asset', 'USDT_price_change_percent', 'close_time', 'count', 
                                          'rolling_traded_volume', 'traded_bid_volume', 
                                          'traded_ask_volume', 'traded_price', 'traded_bid_price', 
                                          'traded_ask_price', 'traded_bid_ask_percent_change', 
                                          'traded_bid_ask_volume_percent_change']]
            else:
                conversion_table = \
                    conversion_table[['base_asset', 'USDT_price_change_percent', 'close_time', 'last_ID', 
                                      'count', 'rolling_traded_volume', 'traded_bid_volume', 
                                      'traded_ask_volume', 'traded_price', 'traded_bid_price', 
                                      'traded_ask_price', 'traded_bid_ask_percent_change', 
                                      'traded_bid_ask_volume_percent_change']]
            conversion_table['rolling_quote_volume'] = conversion_table['rolling_traded_volume'].copy()
            if extra_minimal:
                conversion_table = \
                    conversion_table.rename(columns={'USDT_price_change_percent': 'price_change_percent', 
                                                     'rolling_traded_volume': 'rolling_base_volume', 
                                                     'traded_price': 'close'})
            else:
                conversion_table = \
                    conversion_table.rename(columns={'USDT_price_change_percent': 'price_change_percent', 
                                                     'rolling_traded_volume': 'rolling_base_volume', 
                                                     'traded_bid_volume': 'bid_volume', 
                                                     'traded_ask_volume': 'ask_volume', 
                                                     'traded_price': 'close', 
                                                     'traded_bid_price': 'bid_price', 
                                                     'traded_ask_price': 'ask_price', 
                                                     'traded_bid_ask_percent_change': 'bid_ask_percent_change', 
                                                     'traded_bid_ask_volume_percent_change': 
                                                             'bid_ask_volume_percent_change'})
        if not as_pair:
            conversion_table['symbol'] = conversion_table['base_asset'].copy()
            conversion_table['quote_asset'] = conversion_table['base_asset'].copy()
            if minimal:
                df = conversion_table.groupby(by=['base_asset']).agg({'close_time': 'max', 'count': 'sum'})
                conversion_table.loc[:, ['close_time', 'count']] = \
                    conversion_table.apply(lambda x: df.loc[x['base_asset']], axis='columns')
                if extra_minimal:
                    df = conversion_table.groupby(by=['base_asset']).agg({'bid_ask_percent_change': 'min', 
                                                                          'bid_ask_volume_percent_change': 'max'})
                    conversion_table.loc[:, ['bid_ask_percent_change', 'bid_ask_volume_percent_change']] = \
                        conversion_table.apply(lambda x: df.loc[x['base_asset']], axis='columns')
            else:
                df = conversion_table.groupby(by=['base_asset']).agg({'close_time': 'max', 
                                                                      'last_ID': 'sum', 
                                                                      'count': 'sum'})
                conversion_table.loc[:, ['close_time', 'last_ID', 'count']] = \
                    conversion_table.apply(lambda x: df.loc[x['base_asset']], axis='columns')
            conversion_table = conversion_table.drop_duplicates(subset=['base_asset'], keep='first')
        conversion_table = conversion_table.reset_index(drop=True)

    conversion_table = conversion_table.sort_values(by='close_time')
    conversion_table['close_time'] /= 1000
    conversion_table['close_time'] = conversion_table['close_time'].apply(datetime.datetime.fromtimestamp)
    conversion_table['close_time'] = pd.DatetimeIndex(conversion_table['close_time'])
    return conversion_table.set_index('close_time').sort_index()

def get_tradable_tickers_info(conversion_table, as_pair=False):
    if as_pair:
        conversion_table = \
            conversion_table[['symbol', 'close', 'price_change_percent', 'bid_price', 'ask_price', 'bid_volume', 
                              'ask_volume', 'bid_ask_percent_change', 'bid_ask_volume_percent_change', 'rolling_base_volume', 
                              'rolling_quote_volume', 'USDT_price', 'rolling_traded_volume', 'count']]
    else:
        conversion_table = \
            conversion_table[['symbol', 'close', 'price_change_percent', 'bid_price', 'ask_price', 'bid_volume', 
                              'ask_volume', 'bid_ask_percent_change', 'bid_ask_volume_percent_change', 'rolling_base_volume', 
                              'rolling_quote_volume', 'count']]
    conversion_table[['price_change_percent', 'close', 'bid_price', 'ask_price', 'bid_volume', 'ask_volume', 
                      'rolling_base_volume', 'rolling_quote_volume', 'count']] = \
        conversion_table[['price_change_percent', 'close', 'bid_price', 'ask_price', 'bid_volume', 'ask_volume', 
                          'rolling_base_volume', 'rolling_quote_volume', 'count']].astype(float)
    #conversion_table = conversion_table[conversion_table['bid_ask_percent_change'] < 0.1]
    #conversion_table = conversion_table[conversion_table['bid_ask_volume_percent_change'] > 0.0]
    return conversion_table.sort_index(axis='index')

def get_new_tickers(conversion_table):
    return list(conversion_table['symbol'].unique())

def get_new_filtered_tickers(conversion_table, as_pair):
    return list(get_tradable_tickers_info(conversion_table=conversion_table, as_pair=as_pair)['symbol'].unique())
