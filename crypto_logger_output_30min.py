#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        crypto_logger_output_30min.py
# By:          Samuel Duclos
# For          Myself
# Description: Simple Binance logger output for the 30 minute interval.

# Library imports.
from cryptocurrency.crypto_logger_output import Crypto_logger_output

crypto_logger_output_30min = Crypto_logger_output(delay=220, 
                                                  interval_input='15min', 
                                                  interval='30min', 
                                                  buffer_size=100, 
                                                  input_log_name='output')
crypto_logger_output_30min.start(append=False, roll=1000)
