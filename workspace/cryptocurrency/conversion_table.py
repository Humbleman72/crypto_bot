#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        cryptocurrency/conversion_table.py
# By:          Samuel Duclos
# For          Myself
# Description: Binance pair conversion table retrieval and basic pair filtering.

# Library imports.
from datetime import datetime
from pandas import DataFrame

def get_conversion_table(client, exchange_info):
    conversion_table = DataFrame(client.get_ticker())
    conversion_table = \
        conversion_table[conversion_table['symbol'].isin(exchange_info['symbol'])].reset_index(drop=True)
    conversion_table[['priceChangePercent', 'lastPrice', 'volume', 'bidPrice', 
                      'askPrice', 'bidQty', 'askQty', 'count']] = \
        conversion_table[['priceChangePercent', 'lastPrice', 'volume', 'bidPrice', 
                          'askPrice', 'bidQty', 'askQty', 'count']].astype(float)
    return conversion_table

def get_tradable_tickers_info(conversion_table):
    conversion_table = conversion_table.copy()
    conversion_table = conversion_table[['symbol', 'lastPrice', 'priceChangePercent', 
                                         'bidPrice', 'askPrice', 'bidQty', 'askQty', 'volume', 'count']]
    conversion_table[['priceChangePercent', 'lastPrice', 'bidPrice', 'askPrice', 
                      'bidQty', 'askQty', 'volume', 'count']] = \
        conversion_table[['priceChangePercent', 'lastPrice', 
                          'bidPrice', 'askPrice', 'bidQty', 'askQty', 'volume', 'count']].astype(float)
    conversion_table = conversion_table[conversion_table['volume'] > 3000]
    conversion_table['bidAskChangePercent'] = \
        ((conversion_table['askPrice'] - conversion_table['bidPrice']) / conversion_table['bidPrice'])
    conversion_table['bidAskQtyChangePercent'] = \
        ((conversion_table['askQty'] - conversion_table['bidQty']) / conversion_table['bidQty']).apply(abs)
    conversion_table[['bidAskChangePercent', 'bidAskQtyChangePercent']] *= 100
    conversion_table = conversion_table.dropna()
    conversion_table = conversion_table[conversion_table['bidAskChangePercent'] < 0.8]
    return conversion_table.sort_index()

def get_new_tickers(conversion_table):
    return list(get_tradable_tickers_info(conversion_table=conversion_table)['symbol'].unique())
