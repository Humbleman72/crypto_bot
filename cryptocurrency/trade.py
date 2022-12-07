#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        cryptocurrency/trade.py
# By:          Samuel Duclos
# For          Myself
# Description: Binance asset trading.

# Library imports.
from cryptocurrency.conversion import make_tradable_quantity, convert_price
from cryptocurrency.conversion import get_shortest_pair_path_between_assets
from binance.exceptions import BinanceAPIException
from time import sleep
import pandas as pd

# Function definitions.
def select_asset_with_biggest_wallet(client, conversion_table, exchange_info, as_pair=True):
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
                                           conversion_table=conversion_table, 
                                           exchange_info=exchange_info, key='close', 
                                           priority='accuracy')
        ls.append((asset, converted_quantity, quantity))
    return sorted(ls, key=lambda x: float(x[1]), reverse=True)[0]

def trade_assets(client, quantity, from_asset, to_asset, base_asset, quote_asset, 
                 conversion_table, exchange_info, priority='accuracy', verbose=False):
    pair = base_asset + quote_asset
    side = 'BUY' if from_asset != base_asset else 'SELL'
    if side == 'SELL':
        quantity = convert_price(float(quantity), from_asset=from_asset, to_asset=to_asset, 
                                 conversion_table=conversion_table, exchange_info=exchange_info, 
                                 key='close', priority=priority)
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

def trade(client, to_asset, conversion_table, exchange_info, priority='accuracy', verbose=True):
    from_asset, converted_quantity, quantity = \
        select_asset_with_biggest_wallet(client=client, conversion_table=conversion_table, 
                                         exchange_info=exchange_info)
    shortest_path = \
        get_shortest_pair_path_between_assets(from_asset, to_asset, exchange_info=exchange_info, 
                                              priority=priority)
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
                                   priority=priority, verbose=False)
            if request is None:
                return trade(client=client, to_asset=to_asset, conversion_table=conversion_table, 
                             exchange_info=exchange_info)
            quantity = request['cummulativeQuoteQty']
            from_asset = to_asset
            sleep(0.01)
        return request
