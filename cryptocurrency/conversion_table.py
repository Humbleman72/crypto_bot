#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        cryptocurrency/conversion_table.py
# By:          Samuel Duclos
# For          Myself
# Description: Binance pair conversion table retrieval and basic pair filtering.

# Library imports.
from cryptocurrency.conversion import convert_price, get_base_asset_from_pair, get_quote_asset_from_pair
from pandas import concat, DataFrame

def get_conversion_table(client, exchange_info):
    conversion_table = DataFrame(client.get_ticker())
    conversion_table = conversion_table[conversion_table['symbol'].isin(exchange_info['symbol'])]
    conversion_table = conversion_table.sort_values(by='closeTime').reset_index(drop=True)
    conversion_table['base_asset'] = \
        conversion_table['symbol'].apply(lambda x: get_base_asset_from_pair(x, exchange_info=exchange_info))
    conversion_table['quote_asset'] = \
        conversion_table['symbol'].apply(lambda x: get_quote_asset_from_pair(x, exchange_info=exchange_info))
    conversion_table['shorted_symbol'] = conversion_table['quote_asset'] + conversion_table['base_asset']
    conversion_table[['priceChangePercent', 'lastPrice', 'volume', 'quoteVolume', 
                      'bidPrice', 'askPrice', 'bidQty', 'askQty', 'count']] = \
        conversion_table[['priceChangePercent', 'lastPrice', 'volume', 'quoteVolume', 
                          'bidPrice', 'askPrice', 'bidQty', 'askQty', 'count']].astype(float)
    conversion_table['bidAskChangePercent'] = \
        ((conversion_table['askPrice'] - conversion_table['bidPrice']) / conversion_table['askPrice'])
    conversion_table['bidAskQtyPercent'] = \
        (conversion_table['bidQty'] / (conversion_table['bidQty'] + conversion_table['askQty']))
    conversion_table[['bidAskChangePercent', 'bidAskQtyPercent']] *= 100
    conversion_table = conversion_table.dropna()
    conversion_table = \
        conversion_table.rename(columns={'lastPrice': 'close', 'volume': 'rolling_base_volume', 
                                         'quoteVolume': 'rolling_quote_volume'})
    conversion_table['rolling_base_quote_volume'] = \
        conversion_table['rolling_quote_volume'] / conversion_table['close']
    conversion_table['USDT_base_price'] = \
        conversion_table.apply(lambda x: convert_price(size=1, from_asset=x['base_asset'], to_asset='USDT', 
                                                       conversion_table=conversion_table), axis='columns')
    conversion_table['rolling_USDT_base_volume'] = \
        conversion_table['rolling_base_volume'] * conversion_table['USDT_base_price']
    conversion_table['rolling_USDT_quote_volume'] = \
        conversion_table['rolling_base_quote_volume'] * conversion_table['USDT_base_price']
    conversion_table = conversion_table.drop(columns=['rolling_base_quote_volume'])
    conversion_table['is_shorted'] = False

    conversion_table_swapped = conversion_table.copy()
    conversion_table_swapped = \
        conversion_table_swapped.reindex(columns=['shorted_symbol', 'priceChange', 'priceChangePercent', 
                                                  'weightedAvgPrice', 'prevClosePrice', 'close', 'lastQty', 
                                                  'bidPrice', 'bidQty', 'askPrice', 'askQty', 'openPrice', 
                                                  'highPrice', 'lowPrice', 'rolling_quote_volume', 
                                                  'rolling_base_volume', 'openTime', 'closeTime', 'firstId', 
                                                  'lastId', 'count', 'quote_asset', 'base_asset', 'symbol', 
                                                  'bidAskChangePercent', 'bidAskQtyPercent', 'USDT_base_price', 
                                                  'rolling_USDT_quote_volume', 'rolling_USDT_base_volume', 
                                                  'is_shorted'])
    conversion_table_swapped['close'] = 1 / conversion_table_swapped['close']
    conversion_table_swapped['is_shorted'] = True

    conversion_table = concat([conversion_table, conversion_table_swapped], axis='index')
    conversion_table = conversion_table.sort_values(by='closeTime')
    conversion_table = conversion_table.reset_index(drop=True)

    traded_USDT_volume = conversion_table.groupby(by='base_asset').agg('sum')['rolling_USDT_base_volume']
    conversion_table['rolling_traded_USDT_volume'] = \
        conversion_table.apply(lambda x: traded_USDT_volume.loc[x['base_asset']], 
                               axis='columns')
    conversion_table = conversion_table.reset_index(drop=True)

    conversion_table['importance'] = \
        conversion_table['rolling_USDT_base_volume'] / conversion_table['rolling_traded_USDT_volume']

    conversion_table['importance_weighted_price'] = \
        conversion_table['USDT_base_price'] * conversion_table['importance']

    importance_weighted_price = conversion_table.groupby(by='base_asset').agg('sum')['importance_weighted_price']
    conversion_table['weighted_price'] = \
        conversion_table.apply(lambda x: importance_weighted_price.loc[x['base_asset']], axis='columns')

    conversion_table = conversion_table[~conversion_table['is_shorted']]
    conversion_table = conversion_table.drop(columns=['is_shorted'])
    return conversion_table.reset_index(drop=True)

def get_tradable_tickers_info(conversion_table):
    conversion_table = \
        conversion_table[['symbol', 'close', 'priceChangePercent', 'bidPrice', 'askPrice', 'bidQty', 
                          'askQty', 'bidAskChangePercent', 'bidAskQtyPercent', 'rolling_base_volume', 
                          'rolling_quote_volume', 'rolling_USDT_base_volume', 'USDT_base_price', 
                          'rolling_traded_USDT_volume', 'count']]
    conversion_table[['priceChangePercent', 'close', 'bidPrice', 'askPrice', 'bidQty', 'askQty', 
                      'rolling_base_volume', 'rolling_quote_volume', 'count']] = \
        conversion_table[['priceChangePercent', 'close', 'bidPrice', 'askPrice', 'bidQty', 'askQty', 
                          'rolling_base_volume', 'rolling_quote_volume', 'count']].astype(float)
    conversion_table = conversion_table[conversion_table['rolling_traded_USDT_volume'] > 1000000]
    conversion_table = conversion_table[conversion_table['bidAskChangePercent'] < 0.1]
    return conversion_table.sort_index(axis='index')

def get_new_tickers(conversion_table):
    return list(conversion_table['symbol'].unique())

def get_new_filtered_tickers(conversion_table):
    return list(get_tradable_tickers_info(conversion_table=conversion_table)['symbol'].unique())
