#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        crypto_logger_output_15s.py
# By:          Samuel Duclos
# For          Myself
# Description: Simple Binance logger output for the 15 second interval.

# Library imports.
from cryptocurrency.crypto_logger_output import Crypto_logger_output

crypto_logger_output_15s = Crypto_logger_output(delay=10, 
                                                interval_input='15s', 
                                                interval='15s', 
                                                buffer_size=20, 
                                                input_log_name='input')
crypto_logger_output_15s.start(append=False, roll=1000)
