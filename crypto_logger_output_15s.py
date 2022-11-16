#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        crypto_logger_output_15s.py
# By:          Samuel Duclos
# For          Myself
# Description: Simple Binance logger output for the 15 second interval.

# Library imports.
from cryptocurrency.crypto_logger_output import Crypto_logger_output

crypto_logger_output_15s = Crypto_logger_output(delay=12, 
                                                interval_input='15s', 
                                                interval='15s', 
                                                buffer_size=60, 
                                                input_log_name='input', 
                                                append=False, 
                                                roll=1000, 
                                                log=True)
crypto_logger_output_15s.start()
