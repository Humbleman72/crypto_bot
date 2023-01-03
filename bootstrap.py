#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        bootstrap.py
# By:          Samuel Duclos
# For          Myself
# Description: Populate OHLCV DataFrames from the Binance API.

# Library imports.
from utils.authentication import Cryptocurrency_authenticator
from utils.exchange import Cryptocurrency_exchange
from utils.conversion import get_timezone_offset_in_seconds
from utils.conversion_table import get_conversion_table, get_new_tickers
from utils.bootstrap import bootstrap_loggers
import os
import shutil

def main():
    as_pair = False
    directory = 'crypto_logs'
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)
    authenticator = Cryptocurrency_authenticator(use_keys=False, testnet=False)
    client = authenticator.spot_client
    exchange = Cryptocurrency_exchange(client=client, directory=directory)
    exchange_info = exchange.info
    offset_s = get_timezone_offset_in_seconds()
    conversion_table = get_conversion_table(client=client, exchange_info=exchange_info, 
                                            offset_s=offset_s, dump_raw=False, 
                                            as_pair=True, minimal=False, 
                                            extra_minimal=False, convert_to_USDT=True)
    assets = get_new_tickers(conversion_table=conversion_table)
    #pairs = bootstrap_loggers(client=client, assets=assets, pairs={}, 
    #                          download_interval='1d', exchange_info=exchange_info, as_pair=as_pair)
    #pairs = bootstrap_loggers(client=client, assets=assets, pairs=pairs, 
    #                          download_interval='1h', exchange_info=exchange_info, as_pair=as_pair)
    #pairs = bootstrap_loggers(client=client, assets=assets, additional_intervals=['30min'], 
    #                          upsampled_intervals=['5s', '15s'], pairs=pairs, 
    #                          download_interval='1m', exchange_info=exchange_info, as_pair=as_pair)
    pairs = bootstrap_loggers(client=client, assets=assets, additional_intervals=['30min'], 
                              upsampled_intervals=['5s', '15s'], pairs={}, 
                              download_interval='1m', exchange_info=exchange_info, as_pair=as_pair)
    print('Bootstrapping done!')

if __name__ == '__main__':
    main()
