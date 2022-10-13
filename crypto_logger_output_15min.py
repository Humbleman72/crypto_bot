#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        crypto_logger_output_15min.py
# By:          Samuel Duclos
# For          Myself
# Description: Simple Binance logger output for the 15 minute interval.

# Library imports.
from cryptocurrency.crypto_logger_output import Crypto_logger_output

crypto_logger_output_15min = Crypto_logger_output(delay=22, 
                                                  interval_input='5min', 
                                                  interval='15min', 
                                                  buffer_size=100, 
                                                  input_log_name='output')
crypto_logger_output_15min.start(append=False, roll=1000)
