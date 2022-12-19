#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        cryptocurrency/conversion.py
# By:          Samuel Duclos
# For          Myself
# Description: Binance asset conversion.

# Library imports.
from typing import Union
from decimal import Decimal
import time

# Function definitions.
def get_timezone_offset_in_seconds():
    is_dst = time.localtime().tm_isdst
    timezone = time.tzname[is_dst]
    offset_s = time.altzone if is_dst else time.timezone
    #offset = (offset_s / 60 / 60)
    return offset_s

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

def get_connected_assets(asset, exchange_info, priority='accuracy'):
    def reorder(connected_assets, priority):
        prioritized = \
            [asset for asset in priority if asset in connected_assets]
        order = {asset: i for i, asset in enumerate(prioritized)}
        connected_assets_items = \
            [asset for asset in connected_assets if asset in order]
        connected_assets_items.sort(key=order.get)
        connected_assets_iter = iter(connected_assets_items)
        return [next(connected_assets_iter) if asset in order 
                else asset for asset in connected_assets]
    if priority == 'accuracy':
        priority = ['USDT', 'BTC', 'BUSD', 'ETH', 'BNB']
    elif priority == 'fees':
        priority = ['BUSD', 'BTC', 'BNB', 'ETH', 'USDT']
    elif priority == 'wallet':
        priority = ['BTC', 'ETH', 'BUSD', 'BNB', 'USDT']
    priority += ['BRL', 'AUD']
    connected_base_assets = exchange_info['quote_asset'] == asset
    connected_base_assets = exchange_info[connected_base_assets]
    connected_base_assets = connected_base_assets['base_asset']
    connected_base_assets = connected_base_assets.tolist()
    connected_quote_assets = exchange_info['base_asset'] == asset
    connected_quote_assets = exchange_info[connected_quote_assets]
    connected_quote_assets = connected_quote_assets['quote_asset']
    connected_quote_assets = connected_quote_assets.tolist()
    connected_assets = \
        list(set(connected_base_assets + connected_quote_assets))
    return reorder(connected_assets, priority)

def select_pair_with_highest_quote_volume_from_base_asset(base_asset, 
                                                          conversion_table, 
                                                          exchange_info):
    connected_pairs = exchange_info[exchange_info['base_asset'] == base_asset]
    connected_pairs = connected_pairs['symbol']
    connected_pairs = \
        conversion_table[conversion_table['symbol'].isin(connected_pairs)]
    connected_pairs = connected_pairs.sort_values(by='rolling_quote_volume', 
                                                  ascending=False)
    return connected_pairs['symbol'].iat[0]

def get_shortest_pair_path_between_assets(from_asset, to_asset, exchange_info, 
                                          priority='accuracy'):
    def get_shortest_path_between_assets(priority):
        path_list = [[from_asset]]
        path_index = 0
        previous_nodes = [from_asset]
        if from_asset == to_asset:
            return path_list[0]
        while path_index < len(path_list):
            current_path = path_list[path_index]
            last_node = current_path[-1]
            next_nodes = get_connected_assets(last_node, 
                                              exchange_info=exchange_info, 
                                              priority=priority)
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
        from_asset_is_base_and_to_asset_is_quote = \
            from_asset_is_base & to_asset_is_quote
        from_asset_is_quote_and_to_asset_is_base = \
            from_asset_is_quote & to_asset_is_base
        pair = from_asset_is_base_and_to_asset_is_quote
        pair |= from_asset_is_quote_and_to_asset_is_base
        if pair.any():
            pair = exchange_info[pair]
            base_asset = pair['base_asset'].iat[0]
            quote_asset = pair['quote_asset'].iat[0]
            return base_asset, quote_asset
        else:
            return None
    shortest_path = get_shortest_path_between_assets(priority=priority)
    pairs = []
    while len(shortest_path) > 1:
        base_asset, quote_asset = \
            get_pair_from_assets(shortest_path[0], shortest_path[1])
        pairs += [(base_asset, quote_asset)]
        shortest_path = shortest_path[1:]
    return pairs

def make_tradable_quantity(pair, coins_available, exchange_info, subtract=0):
    def compact_float_string(number, precision):
        return "{:0.0{}f}".format(number, precision).rstrip('0').rstrip('.')
    def round_step_size(quantity: Union[float, Decimal], 
                        step_size: Union[float, Decimal]) -> float:
        """Rounds a given quantity to a specific step size
        :param quantity: required
        :param step_size: required
        :return: decimal
        """
        quantity = Decimal(str(quantity))
        return float(quantity - quantity % Decimal(str(step_size)))
    pair_exchange_info = exchange_info[exchange_info['symbol'] == pair].iloc[0]
    tick_size = float(pair_exchange_info['tick_size'])
    step_size = float(pair_exchange_info['step_size'])
    precision = pair_exchange_info['quote_precision']
    coins_available = float(coins_available) - subtract * tick_size
    quantity = round_step_size(quantity=coins_available, step_size=tick_size)
    return compact_float_string(float(quantity), precision)

def convert_price(size, from_asset, to_asset, conversion_table, exchange_info, 
                  key='close', priority='accuracy', shortest_path=None):
    if from_asset != to_asset:
        size = float(size)
        if shortest_path is None:
            shortest_path = get_shortest_pair_path_between_assets(
                from_asset=from_asset, to_asset=to_asset, 
                exchange_info=exchange_info, priority=priority)
        for (base_asset, quote_asset) in shortest_path:
            to_asset = quote_asset if from_asset == base_asset else base_asset
            pair = base_asset + quote_asset
            connection = conversion_table[conversion_table['symbol'] == pair]
            price = connection[key].iat[0]
            size = size * price if base_asset == from_asset else size / price
            from_asset = to_asset
        size = make_tradable_quantity(pair, float(size), subtract=0, 
                                      exchange_info=exchange_info)
    return size
