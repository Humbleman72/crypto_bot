#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        crypto_logger_output_30s.py
# By:          Samuel Duclos
# For          Myself
# Description: Simple Binance logger output for the 30 second interval.

# Library imports.
from cryptocurrency.crypto_logger_output import Crypto_logger_output

crypto_logger_output_30s = Crypto_logger_output(delay=12, 
                                                interval_input='15s', 
                                                interval='30s', 
                                                buffer_size=20, 
                                                input_log_name='output')
crypto_logger_output_30s.start(append=False, roll=1000)
