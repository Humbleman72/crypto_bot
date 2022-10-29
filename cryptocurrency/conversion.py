#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        cryptocurrency/conversion.py
# By:          Samuel Duclos
# For          Myself
# Description: Binance asset conversion.

# Library imports.
from cryptocurrency.ohlcvs import named_pairs_to_df
from tqdm import tqdm
import pandas as pd

def get_assets_from_pair(pair, exchange_info):
     try:
         pair_info = exchange_info[exchange_info['symbol'] == pair]
         base_asset = pair_info['base_asset'].iat[-1]
         quote_asset = pair_info['quote_asset'].iat[-1]
         return base_asset, quote_asset
     except Exception as e:
         print(e)
         print(pair_info)
     return None

def get_base_asset_from_pair(pair, exchange_info):
    asset = get_assets_from_pair(pair, exchange_info=exchange_info)
    base_asset = None
    if asset is not None:
        base_asset, quote_asset = asset
    return base_asset

def get_quote_asset_from_pair(pair, exchange_info):
    asset = get_assets_from_pair(pair, exchange_info=exchange_info)
    quote_asset = None
    if asset is not None:
        base_asset, quote_asset = asset
    return quote_asset

def get_connected_assets(asset, exchange_info):
    connected_base_assets = exchange_info['base_asset'] == asset
    connected_base_assets = exchange_info[connected_base_assets]
    connected_base_assets = connected_base_assets['quote_asset'].tolist()
    connected_quote_assets = exchange_info['quote_asset'] == asset
    connected_quote_assets = exchange_info[connected_quote_assets]
    connected_quote_assets = connected_quote_assets['base_asset'].tolist()
    connected_assets = sorted(list(set(connected_base_assets + connected_quote_assets)))
    if 'BNB' in connected_assets and 'BTC' in connected_assets:
        BNB, BTC = connected_assets.index('BNB'), connected_assets.index('BTC')
        connected_assets[BNB], connected_assets[BTC] = \
            connected_assets[BTC], connected_assets[BNB]
    return connected_assets

def get_shortest_pair_path_between_assets(from_asset, to_asset, exchange_info):
    def get_shortest_path_between_assets():
        path_list = [[from_asset]]
        path_index = 0
        previous_nodes = [from_asset]
        if from_asset == to_asset:
            return path_list[0]
        while path_index < len(path_list):
            current_path = path_list[path_index]
            last_node = current_path[-1]
            next_nodes = get_connected_assets(last_node, exchange_info=exchange_info)
            if to_asset in next_nodes:
                current_path.append(to_asset)
                return current_path
            for next_node in next_nodes:
                if not next_node in previous_nodes:
                    new_path = current_path[:]
                    new_path.append(next_node)
                    path_list.append(new_path)
                    previous_nodes.append([next_node])
            path_index += 1
        return []
    def get_pair_from_assets(from_asset, to_asset):
        from_asset_is_base = exchange_info['base_asset'] == from_asset
        from_asset_is_quote = exchange_info['quote_asset'] == from_asset
        to_asset_is_base = exchange_info['base_asset'] == to_asset
        to_asset_is_quote = exchange_info['quote_asset'] == to_asset
        from_asset_is_base_and_to_asset_is_quote = from_asset_is_base & to_asset_is_quote
        from_asset_is_quote_and_to_asset_is_base = from_asset_is_quote & to_asset_is_base
        pair = from_asset_is_base_and_to_asset_is_quote | from_asset_is_quote_and_to_asset_is_base
        if pair.any():
            pair = exchange_info[pair]
            base_asset = pair['base_asset'].iat[0]
            quote_asset = pair['quote_asset'].iat[0]
            return base_asset, quote_asset
        else:
            return None
    shortest_path = get_shortest_path_between_assets()
    pairs = []
    while len(shortest_path) > 1:
        base_asset, quote_asset = \
            get_pair_from_assets(shortest_path[0], shortest_path[1])
        pairs += [(base_asset, quote_asset)]
        shortest_path = shortest_path[1:]
    return pairs

def convert_price(size, from_asset, to_asset, conversion_table, exchange_info):
    shortest_path = get_shortest_pair_path_between_assets(from_asset=from_asset, 
                                                          to_asset=to_asset, 
                                                          exchange_info=exchange_info)
    for (base_asset, quote_asset) in shortest_path:
        to_asset = quote_asset if from_asset == base_asset else base_asset
        size = float(size)
        pair = base_asset + quote_asset
        connection = conversion_table[conversion_table['symbol'] == pair]
        price = connection['close'].iat[0]
        size = size * price if base_asset == from_asset else size / price
        from_asset = to_asset
    return size

'''
def convert_ohlcv(from_asset, to_asset, conversion_table, exchange_info):
    shortest_path = get_shortest_pair_path_between_assets(from_asset=from_asset, 
                                                          to_asset=to_asset, 
                                                          exchange_info=exchange_info)
    base_asset, quote_asset = shortest_path[0]
    to_asset = quote_asset if from_asset == base_asset else base_asset
    pair = base_asset + quote_asset
    size = conversion_table[pair].copy()
    size['quote_volume'] = size['quote_volume'] / size['close']
    for (base_asset, quote_asset) in shortest_path[1:]:
        to_asset = quote_asset if from_asset == base_asset else base_asset
        pair = base_asset + quote_asset
        connection = conversion_table[pair]
        if base_asset == from_asset:
            size['open'] = size['open'] * connection['open']
            size['high'] = size['close'] * connection['high']
            size['low'] = size['close'] * connection['low']
            size['close'] = size['close'] * connection['close']
        else:
            size['open'] = size['open'] / connection['open']
            size['high'] = size['close'] / connection['high']
            size['low'] = size['close'] / connection['low']
            size['close'] = size['close'] / connection['close']
        from_asset = to_asset
    size['base_volume'] = size['close'] * size['base_volume']
    size['quote_volume'] = size['close'] * size['quote_volume']
    size.replace([float('inf'), float('-inf')], float('nan'), inplace=True)
    size.loc[:, ['base_volume', 'quote_volume']] = \
        size.loc[:, ['base_volume', 'quote_volume']].fillna(0)
    return size.fillna(method='pad')

def convert_ohlcvs(to_asset, conversion_table, exchange_info):
    def convert_ohlcv_prices(from_asset, to_asset, conversion_table, exchange_info):
        shortest_path = get_shortest_pair_path_between_assets(from_asset=from_asset, 
                                                              to_asset=to_asset, 
                                                              exchange_info=exchange_info)
        base_asset, quote_asset = shortest_path[0]
        to_asset = quote_asset if from_asset == base_asset else base_asset
        pair = base_asset + quote_asset
        size = conversion_table[pair].copy()
        size['quote_volume'] = size['quote_volume'] / size['close']
        for (base_asset, quote_asset) in shortest_path[1:]:
            to_asset = quote_asset if from_asset == base_asset else base_asset
            pair = base_asset + quote_asset
            connection = conversion_table[pair]
            if base_asset == from_asset:
                size['open'] = size['open'] * connection['open']
                size['high'] = size['close'] * connection['high']
                size['low'] = size['close'] * connection['low']
                size['close'] = size['close'] * connection['close']
            else:
                size['open'] = size['open'] / connection['open']
                size['high'] = size['close'] / connection['high']
                size['low'] = size['close'] / connection['low']
                size['close'] = size['close'] / connection['close']
            from_asset = to_asset
        return size
    def convert_ohlcv_volumes(symbol, conversion_table, exchange_info):
        from_asset = get_base_asset_from_pair(symbol, exchange_info)
        size = conversion_table[symbol].copy()
        size['base_volume'] = size['close'] * size['base_volume']
        size['quote_volume'] = size['close'] * size['quote_volume']
        size.replace([float('inf'), float('-inf')], float('nan'), inplace=True)
        size.loc[:, ['base_volume', 'quote_volume']] = \
            size.loc[:, ['base_volume', 'quote_volume']].fillna(0)
        return size.fillna(method='pad')
    def convert_ohlcv_prices_helper(symbol):
        from_asset = get_base_asset_from_pair(symbol, exchange_info)
        if from_asset == to_asset:
            size = conversion_table[symbol].copy()
            size['quote_volume'] = size['quote_volume'] / size['close']
        else:
            size = convert_ohlcv_prices(from_asset, to_asset, 
                                        conversion_table, exchange_info)
        return size
    conversion_table = conversion_table.astype(float).copy()
    symbols = conversion_table.columns.get_level_values(0).unique().tolist()
    conversion_table = [convert_ohlcv_prices_helper(symbol) 
                        for symbol in tqdm(symbols, unit=' pair conversion')]
    conversion_table = named_pairs_to_df(symbols, conversion_table)
    conversion_table = [convert_ohlcv_volumes(symbol, conversion_table, 
                                              exchange_info) 
                        for symbol in tqdm(symbols, unit=' pair conversion')]
    conversion_table = named_pairs_to_df(symbols, conversion_table)
    return conversion_table
'''

def select_asset_with_biggest_wallet(client, conversion_table):
    def get_account_balances():
        balances = pd.DataFrame(client.get_account()['balances'])[['asset', 'free']]
        balances = balances.set_index('asset').drop(index=['XPR']).astype(float)
        balances = balances[balances['free'] > 0]
        return balances.sort_values(by=['free'], ascending=False).T
    balances = get_account_balances()
    ls = []
    for (asset, quantity) in balances.iteritems():
        quantity = quantity.iat[0]
        converted_quantity = convert_price(size=quantity, from_asset=asset, to_asset='USDT', 
                                           conversion_table=conversion_table)
        ls.append((asset, converted_quantity, quantity))

    return sorted(ls, key=lambda x: float(x[1]), reverse=True)[0]
