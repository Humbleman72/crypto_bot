#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        services/crypto_logger_input_15s.py
# By:          Samuel Duclos
# For          Myself
# Description: Simple Binance logger circular buffered for 15 second precision.

# Library imports.
from cryptocurrency.crypto_logger_input import Crypto_logger_input

crypto_logger_input_15s = Crypto_logger_input(delay=4.7, interval='15s', buffer_size=3000, 
                                              price_percent=1.0, volume_percent=0.0, 
                                              as_pair=False)
crypto_logger_input_15s.start(append=True, roll=60)
