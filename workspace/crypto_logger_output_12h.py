#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        crypto_logger_output_12h.py
# By:          Samuel Duclos
# For          Myself
# Description: Simple Binance logger output for the 12 hour interval.

# Library imports.
from cryptocurrency.crypto_logger_output import Crypto_logger_output

crypto_logger_output_12h = Crypto_logger_output(delay=36, 
                                                interval_input='1h', 
                                                interval='12h', 
                                                buffer_size=100, 
                                                input_log_name='output')
crypto_logger_output_12h.start(append=False, roll=1000)
