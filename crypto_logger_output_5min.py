#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        crypto_logger_output_5min.py
# By:          Samuel Duclos
# For          Myself
# Description: Simple Binance logger output for the 5 minute interval.

# Library imports.
from cryptocurrency.crypto_logger_output import Crypto_logger_output

crypto_logger_output_5min = Crypto_logger_output(delay=66, 
                                                 interval_input='1min', 
                                                 interval='5min', 
                                                 buffer_size=100, 
                                                 input_log_name='output')
crypto_logger_output_5min.start(append=False, roll=1000)
