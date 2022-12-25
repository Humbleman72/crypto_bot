#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        cryptocurrency/trader/trade.py
# By:          Samuel Duclos
# For          Myself
# Description: Binance asset trading.

# Library imports.
from cryptocurrency.conversion import make_tradable_quantity, convert_price
from cryptocurrency.conversion import get_shortest_pair_path_between_assets
from cryptocurrency.conversion import select_pair_with_highest_quote_volume_from_base_asset
from cryptocurrency.conversion_table import get_conversion_table
from cryptocurrency.trader.order_book import get_order_book_trigger
from cryptocurrency.trader.wallet import select_asset_with_biggest_wallet
from binance.exceptions import BinanceAPIException
from time import sleep
import pandas as pd

# Function definitions.
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
    from_asset, converted_quantity, quantity, priority = \
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

def make_empty_blacklist():
    return pd.DataFrame(columns=['symbol', 'base_asset', 'close', 'take_profit_count', 'stop_loss_count'])

def add_entry_to_blacklist(blacklist, pair, conversion_table, exchange_info, reason='stop_loss'):
    base_asset_from_pair = exchange_info[exchange_info['symbol'] == pair]['base_asset'].iat[0]
    if base_asset_from_pair not in blacklist['base_asset'].tolist():
        new_blacklist_entry = conversion_table[conversion_table['symbol'] == pair][['symbol', 'close']].copy()
        new_blacklist_entry['base_asset'] = base_asset_from_pair
        new_blacklist_entry['take_profit_count'] = 0
        new_blacklist_entry['stop_loss_count'] = 0
        new_blacklist_entry = new_blacklist_entry[['symbol', 'base_asset', 'close', 
                                                   'take_profit_count', 'stop_loss_count']]
        blacklist = pd.concat([blacklist, new_blacklist_entry], axis='index')
    else:
        pair = blacklist[blacklist['base_asset'] == base_asset_from_pair]['symbol'].iat[0]
        new_blacklist_entry = conversion_table[conversion_table['symbol'] == pair][['symbol', 'close']].copy()
        new_blacklist_entry['base_asset'] = base_asset_from_pair
        new_blacklist_entry['take_profit_count'] = \
            blacklist[blacklist['base_asset'] == base_asset_from_pair]['take_profit_count'].iat[0]
        new_blacklist_entry['stop_loss_count'] = \
            blacklist[blacklist['base_asset'] == base_asset_from_pair]['stop_loss_count'].iat[0]
        new_blacklist_entry = new_blacklist_entry[['symbol', 'base_asset', 'close', 
                                                   'take_profit_count', 'stop_loss_count']]
        blacklist = pd.concat([blacklist, new_blacklist_entry], axis='index')
        blacklist = blacklist.drop_duplicates(subset=['base_asset'], keep='last')
    pair = blacklist[blacklist['base_asset'] == base_asset_from_pair]['symbol'].iat[0]
    if reason == 'take_profit':
        blacklist.loc[blacklist['symbol'] == pair,'take_profit_count'] += 1
    if reason == 'stop_loss':
        blacklist.loc[blacklist['symbol'] == pair,'stop_loss_count'] += 1
    return blacklist

def check_if_asset_from_pair_is_buyable(blacklist, pair, exchange_info, 
                                        take_profit_count=6, stop_loss_count=3):
    base_asset_from_pair = exchange_info[exchange_info['symbol'] == pair]['base_asset'].iat[0]
    is_buyable = True
    if base_asset_from_pair in blacklist['base_asset'].tolist():
        pair = blacklist[blacklist['base_asset'] == base_asset_from_pair]['symbol'].iat[0]
        if blacklist.loc[blacklist['symbol'] == pair,'take_profit_count'].iat[0] >= take_profit_count:
            is_buyable = False
        if blacklist.loc[blacklist['symbol'] == pair,'stop_loss_count'].iat[0] >= stop_loss_count:
            is_buyable = False
    return is_buyable

def check_take_profit_and_stop_loss(blacklist, from_asset, to_asset, conversion_table, exchange_info, 
                                    latest_asset, take_profit=None, stop_loss=None):
    if from_asset in blacklist['base_asset'].tolist():
        pair = blacklist[blacklist['base_asset'] == from_asset]['symbol'].iat[0]
        purchased_price = blacklist[blacklist['base_asset'] == from_asset]['close'].iat[0]
        price_now = conversion_table[conversion_table['symbol'] == pair]['close'].iat[0]
        percent_gain = ((price_now - purchased_price) / purchased_price) * 100.0
        if take_profit is not None:
            if percent_gain >= take_profit:
                to_asset = latest_asset
                blacklist = add_entry_to_blacklist(
                    blacklist, pair, conversion_table, exchange_info, reason='take_profit')
        if stop_loss is not None:
            if percent_gain <= -stop_loss:
                to_asset = latest_asset
                blacklist = add_entry_to_blacklist(
                    blacklist, pair, conversion_table, exchange_info, reason='stop_loss')
    return blacklist, to_asset

def remove_older_entries_in_blacklist(blacklist, frequency='15min'):
    frequency = pd.tseries.frequencies.to_offset(frequency)
    return blacklist.loc[(pd.Timestamp.utcnow().tz_localize(None) - blacklist.index) < frequency]

def choose_to_asset(ssh, blacklist, sell_asset, from_asset, to_asset, latest_asset, take_profit_count, 
                    stop_loss_count, conversion_table, exchange_info, output_log_screened):
    tradable_pairs = ssh.get_logs_from_server(server_log=ssh.output_log_screened)
    if tradable_pairs is None:
        to_asset = sell_asset
    else:
        print('.', end='')
        tradable_pairs = tradable_pairs.sort_values(by='last_price_move', ascending=False)
        tradable_assets = list(set(tradable_pairs['symbol'].tolist()))
        if from_asset in tradable_assets:
            to_asset = latest_asset = from_asset
        else:
            is_buyable = False
            for test_asset in tradable_assets:
                test_pair = select_pair_with_highest_quote_volume_from_base_asset(
                    base_asset=test_asset, conversion_table=conversion_table, exchange_info=exchange_info)
                #time.sleep(0.2)
                if check_if_asset_from_pair_is_buyable(
                    blacklist, test_pair, exchange_info, take_profit_count=take_profit_count, 
                    stop_loss_count=stop_loss_count):
                    #if get_order_book_trigger(client=client, symbol=test_pair, threshold=10000):
                    latest_asset = test_asset
                    is_buyable = True
                    break
            to_asset = latest_asset if is_buyable else sell_asset
    return latest_asset, to_asset

def trade_conditionally(ssh, blacklist, client, exchange_info, to_asset, offset_s):
    #conversion_table = ssh.get_logs_from_server(server_log=ssh.input_log)
    conversion_table = get_conversion_table(
        client=client, exchange_info=exchange_info, offset_s=offset_s, dump_raw=False, as_pair=True, 
        minimal=False, extra_minimal=False, super_extra_minimal=False, convert_to_USDT=False)
    from_asset, converted_quantity, quantity, priority = \
        select_asset_with_biggest_wallet(client=client, conversion_table=conversion_table, 
                                         exchange_info=exchange_info)
    request = trade(client=client, to_asset=to_asset, conversion_table=conversion_table, 
                    exchange_info=exchange_info, priority=priority)
    if request is not None:
        if to_asset != sell_asset:
            pair = select_pair_with_highest_quote_volume_from_base_asset(
                to_asset, conversion_table, exchange_info)
            blacklist = add_entry_to_blacklist(blacklist, pair, conversion_table, exchange_info, reason=None)
            base_asset_from_pair = exchange_info[exchange_info['symbol'] == pair]['base_asset'].iat[0]
            pair = blacklist[blacklist['base_asset'] == base_asset_from_pair]['symbol'].iat[0]
            blacklist.loc[blacklist['symbol'] == pair,'symbol'] = request['symbol']
            blacklist.loc[blacklist['symbol'] == pair,'close'] = float(request['fills'][0]['price'])
        from_asset = to_asset
    return blacklist, from_asset, to_asset
