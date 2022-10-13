#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        cryptocurrency/conversion.py
# By:          Samuel Duclos
# For          Myself
# Description: Binance asset conversion.

# Library imports.
import pandas as pd

def get_assets_from_pair(pair, exchange_info):
     try:
         pair_info = exchange_info[exchange_info['symbol'] == pair]
         base_asset = pair_info['baseAsset'].iloc[-1]
         quote_asset = pair_info['quoteAsset'].iloc[-1]
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
    connected_base_assets = exchange_info['baseAsset'] == asset
    connected_base_assets = exchange_info[connected_base_assets]
    connected_base_assets = connected_base_assets['quoteAsset'].tolist()
    connected_quote_assets = exchange_info['quoteAsset'] == asset
    connected_quote_assets = exchange_info[connected_quote_assets]
    connected_quote_assets = connected_quote_assets['baseAsset'].tolist()
    return sorted(list(set(connected_base_assets + connected_quote_assets)))

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
        from_asset_is_base = exchange_info['baseAsset'] == from_asset
        from_asset_is_quote = exchange_info['quoteAsset'] == from_asset
        to_asset_is_base = exchange_info['baseAsset'] == to_asset
        to_asset_is_quote = exchange_info['quoteAsset'] == to_asset
        from_asset_is_base_and_to_asset_is_quote = from_asset_is_base & to_asset_is_quote
        from_asset_is_quote_and_to_asset_is_base = from_asset_is_quote & to_asset_is_base
        pair = from_asset_is_base_and_to_asset_is_quote | from_asset_is_quote_and_to_asset_is_base
        if pair.any():
            pair = exchange_info[pair]
            base_asset = pair['baseAsset'].iloc[0]
            quote_asset = pair['quoteAsset'].iloc[0]
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
        price = connection['lastPrice'].iloc[0]
        size = size * price if base_asset == from_asset else size / price
        from_asset = to_asset
    return size

def select_asset_with_biggest_wallet(client, conversion_table, exchange_info):
    def get_account_balances():
        balances = pd.DataFrame(client.get_account()['balances'])[['asset', 'free']]
        balances = balances.set_index('asset').drop(index=['XPR']).astype(float)
        balances = balances[balances['free'] > 0]
        return balances.sort_values(by=['free'], ascending=False).T
    balances = get_account_balances()
    ls = []
    for (asset, quantity) in balances.iteritems():
        quantity = quantity.iloc[0]
        converted_quantity = convert_price(size=quantity, from_asset=asset, to_asset='USDT', 
                                           exchange_info=exchange_info, conversion_table=conversion_table)
        ls.append((asset, converted_quantity, quantity))

    return sorted(ls, key=lambda x: float(x[1]), reverse=True)[0]
