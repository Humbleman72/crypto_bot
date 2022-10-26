#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        cryptocurrency/trade.py
# By:          Samuel Duclos
# For          Myself
# Description: Binance asset trading.

# Library imports.
from cryptocurrency.conversion import convert_price, get_shortest_pair_path_between_assets, select_asset_with_biggest_wallet
from binance.exceptions import BinanceAPIException
from typing import Union
from decimal import Decimal
from time import sleep

def trade_assets(client, quantity, from_asset, to_asset, base_asset, quote_asset, 
                 conversion_table, exchange_info, verbose=False):
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
        quantity = compact_float_string(float(quantity), precision)
        return quantity
    pair = base_asset + quote_asset
    side = 'BUY' if from_asset != base_asset else 'SELL'
    if side == 'SELL':
        quantity = convert_price(float(quantity), from_asset=from_asset, to_asset=to_asset, 
                                 conversion_table=conversion_table, exchange_info=exchange_info)
    ticks = 0
    while True:
        try:
            if verbose:
                print(quantity)
            while True:
                quantity = make_tradable_quantity(pair, float(quantity), 
                                                  subtract=ticks, exchange_info=exchange_info)
                qty = float(quantity)
                if qty <= 0:
                    ticks = (qty // 2) + (qty // 4)
                else:
                    break
            if verbose:
                print(quantity)

            request = client.create_order(symbol=pair, side=side, type='MARKET', 
                                          quoteOrderQty=quantity, recvWindow=2000)
            break
        except BinanceAPIException as e:
            request = None
            if str(e) == 'APIError(code=-2010): Account has insufficient balance for requested action.':
                ticks = ticks * 2 if ticks != 0 else 1
            else:
                break
    if verbose:
        print('ticks:', ticks)
    return request

def trade(client, to_asset, conversion_table, exchange_info, verbose=True):
    from_asset, converted_quantity, quantity = \
        select_asset_with_biggest_wallet(client=client, conversion_table=conversion_table, 
                                         exchange_info=exchange_info)
    shortest_path = \
        get_shortest_pair_path_between_assets(from_asset, to_asset, exchange_info=exchange_info)
    if verbose:
        print(shortest_path)
    if from_asset == to_asset:
        print("Error: Can't trade asset with itself!\nIgnoring...")
    elif len(shortest_path) < 1:
        print("Error: A path from from_asset to to_asset does not exist!\nIgnoring...")
    else:
        for (base_asset, quote_asset) in shortest_path:
            if from_asset == base_asset:
                from_asset = base_asset
                to_asset = quote_asset
            else:
                from_asset = quote_asset
                to_asset = base_asset
            request = trade_assets(client=client, quantity=quantity, from_asset=from_asset, 
                                   to_asset=to_asset, base_asset=base_asset, quote_asset=quote_asset, 
                                   conversion_table=conversion_table, exchange_info=exchange_info, 
                                   verbose=False)
            if request is None:
                return trade(client=client, to_asset=to_asset, conversion_table=conversion_table, 
                             exchange_info=exchange_info)
            quantity = request['cummulativeQuoteQty']
            from_asset = to_asset
            sleep(0.01)
        return request

