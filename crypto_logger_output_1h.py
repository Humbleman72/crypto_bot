#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        crypto_logger_output_1h.py
# By:          Samuel Duclos
# For          Myself
# Description: Simple Binance logger output for the 1 hour interval.

# Library imports.
from cryptocurrency.crypto_logger_output import Crypto_logger_output

crypto_logger_output_1h = Crypto_logger_output(delay=188, 
                                               interval_input='30min', 
                                               interval='1h', 
                                               buffer_size=100, 
                                               input_log_name='output')
crypto_logger_output_1h.start(append=False, roll=1000)
