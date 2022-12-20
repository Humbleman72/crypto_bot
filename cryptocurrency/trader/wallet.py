#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        cryptocurrency/trader/wallet.py
# By:          Samuel Duclos
# For          Myself
# Description: Binance asset trading.

# Library imports.
from cryptocurrency.conversion import convert_price
import pandas as pd

# Function definitions.
def select_asset_with_biggest_wallet(client, conversion_table, exchange_info):
    def get_account_balances():
        balances = pd.DataFrame(client.get_account()['balances'])[['asset', 'free']]
        balances = balances.set_index('asset').drop(index=['XPR']).astype(float)
        balances = balances[balances['free'] > 0]
        return balances.sort_values(by=['free'], ascending=False).T
    account_balances = get_account_balances()
    ls = []
    for (asset, quantity) in account_balances.items():
        quantity = quantity.iat[0]
        converted_quantity = convert_price(size=quantity, from_asset=asset, to_asset='USDT', 
                                           conversion_table=conversion_table, 
                                           exchange_info=exchange_info, key='close', 
                                           priority='accuracy')
        ls.append((asset, converted_quantity, quantity))
    return sorted(ls, key=lambda x: float(x[1]), reverse=True)[0]