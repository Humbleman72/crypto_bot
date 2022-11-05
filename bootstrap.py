#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        bootstrap.py
# By:          Samuel Duclos
# For          Myself
# Description: Populate OHLCV DataFrames from the Binance API.

# Library imports.
from cryptocurrency.authentication import Cryptocurrency_authenticator
from cryptocurrency.exchange import Cryptocurrency_exchange
from cryptocurrency.conversion_table import get_conversion_table, get_new_tickers
from cryptocurrency.bootstrap import bootstrap_loggers
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
    conversion_table = get_conversion_table(client=client, exchange_info=exchange_info, as_pair=True)
    assets = get_new_tickers(conversion_table=conversion_table)
    pairs = bootstrap_loggers(client=client, assets=assets, pairs={}, 
                              download_interval='1d', exchange_info=exchange_info, as_pair=as_pair)
    pairs = bootstrap_loggers(client=client, assets=assets, pairs=pairs, 
                              download_interval='1h', exchange_info=exchange_info, as_pair=as_pair)
    pairs = bootstrap_loggers(client=client, assets=assets, additional_intervals=['30min'], 
                              upsampled_intervals=['5s', '15s'], pairs=pairs, 
                              download_interval='1m', exchange_info=exchange_info, as_pair=as_pair)
    print('Bootstrapping done!')

if __name__ == '__main__':
    main()
