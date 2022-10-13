#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        crypto_logger_output_1d.py
# By:          Samuel Duclos
# For          Myself
# Description: Simple Binance logger output for the 1 day interval.

# Library imports.
from cryptocurrency.crypto_logger_output import Crypto_logger_output

crypto_logger_output_1d = Crypto_logger_output(delay=44, 
                                               interval_input='12h', 
                                               interval='1d', 
                                               buffer_size=1000, 
                                               input_log_name='output')
crypto_logger_output_1d.start(append=False, roll=1000)
