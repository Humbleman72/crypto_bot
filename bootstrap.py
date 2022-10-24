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
from cryptocurrency.bootstrapping import bootstrap_loggers

import os
import shutil

def main():
    authenticator = Cryptocurrency_authenticator(use_keys=False, testnet=False)
    client = authenticator.spot_client
    exchange = Cryptocurrency_exchange(client=client, directory='crypto_logs')
    exchange_info = exchange.info
    conversion_table = get_conversion_table(client=client, exchange_info=exchange_info)
    assets = get_new_tickers(conversion_table=conversion_table)

    directory = 'crypto_logs'
    shutil.rmtree(directory)
    os.mkdir(directory)

    #pairs = bootstrap_loggers(client=client, assets=assets, 
    #                          intervals=['1d', '7d', '30d'], pairs=None, 
    #                          download_interval='1d', period=1000, second_period=None)
    #pairs = bootstrap_loggers(client=client, assets=assets, 
    #                          intervals=['1h', '2h', '4h', '12h'], pairs=pairs, 
    #                          download_interval='1h', period=1000, second_period=None)
    pairs = {}
    pairs = bootstrap_loggers(client=client, assets=assets, 
                              intervals=['1min', '5min', '15min', '30min'], pairs=pairs, 
                              download_interval='1m', period=2880, second_period=60)
    print('Bootstrapping done!')

if __name__ == '__main__':
    main()
