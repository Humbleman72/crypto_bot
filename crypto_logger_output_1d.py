#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        crypto_logger_output_1d.py
# By:          Samuel Duclos
# For          Myself
# Description: Simple Binance logger output for the 1 day interval.

# Library imports.
from cryptocurrency.crypto_logger_output import Crypto_logger_output

crypto_logger_output_1d = Crypto_logger_output(delay=222, 
                                               interval_input='1h', 
                                               interval='1d', 
                                               buffer_size=60, 
                                               input_log_name='output', 
                                               append=True, 
                                               roll=12, 
                                               log=True)
crypto_logger_output_1d.start()
