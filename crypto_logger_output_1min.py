#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        crypto_logger_output_1min.py
# By:          Samuel Duclos
# For          Myself
# Description: Simple Binance logger output for the 1 minute interval.

# Library imports.
from cryptocurrency.crypto_logger_output import Crypto_logger_output

crypto_logger_output_1min = Crypto_logger_output(delay=33, 
                                                 interval_input='15s', 
                                                 interval='1min', 
                                                 buffer_size=1500, 
                                                 input_log_name='output')
crypto_logger_output_1min.start(append=False, roll=1000)
