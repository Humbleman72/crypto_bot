#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        services/crypto_logger_input_1min.py
# By:          Samuel Duclos
# For          Myself
# Description: Simple Binance logger circular buffered for 1 minute precision.

# Library imports.
from cryptocurrency.crypto_logger_input import Crypto_logger_input

crypto_logger_input_1min = Crypto_logger_input(delay=4.7, interval='1min', buffer_size=1000, 
                                               price_percent=5.0, volume_percent=0.0)
crypto_logger_input_1min.start(append=True, roll=120)
