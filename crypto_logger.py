#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        crypto_logger.py
# By:          Samuel Duclos
# For:         Myself
# Description: This file implements the main for the crypto_logger.

# Library imports.
from cryptocurrency.crypto_logger_input import Crypto_logger_input
from cryptocurrency.crypto_logger_output import Crypto_logger_output
import time

# Setup basic logging.
import logging
logging.basicConfig()
LOGLEVEL = logging.getLogger().getEffectiveLevel()

def start_loggers():
    """Main logger loop."""
    print('Starting crypto logger.')
    crypto_logger_input_15s = Crypto_logger_input(delay=4.7, interval='15s', buffer_size=3000, 
                                                  price_percent=5.0, volume_percent=0.0, 
                                                  as_pair=False, append=True, roll=60, log=True)
    crypto_logger_output_15s = Crypto_logger_output(delay=12, 
                                                    interval_input='15s', 
                                                    interval='15s', 
                                                    buffer_size=60, 
                                                    input_log_name='input', 
                                                    append=False, 
                                                    roll=1000, 
                                                    log=True)
    crypto_logger_output_1min = Crypto_logger_output(delay=33, 
                                                     interval_input='15s', 
                                                     interval='1min', 
                                                     buffer_size=1500, 
                                                     input_log_name='output', 
                                                     append=False, 
                                                     roll=1000, 
                                                     log=True)
    crypto_logger_output_30min = Crypto_logger_output(delay=66, 
                                                      interval_input='1min', 
                                                      interval='30min', 
                                                      buffer_size=60, 
                                                      input_log_name='output', 
                                                      append=False, 
                                                      roll=1000, 
                                                      log=True)
    crypto_logger_output_1h = Crypto_logger_output(delay=111, 
                                                   interval_input='30min', 
                                                   interval='1h', 
                                                   buffer_size=60, 
                                                   input_log_name='output', 
                                                   append=False, 
                                                   roll=1000, 
                                                   log=True)
    crypto_logger_output_1d = Crypto_logger_output(delay=222, 
                                                   interval_input='1h', 
                                                   interval='1d', 
                                                   buffer_size=60, 
                                                   input_log_name='output', 
                                                   append=False, 
                                                   roll=1000, 
                                                   log=True)
    crypto_loggers = [
        crypto_logger_input_15s, 
        crypto_logger_output_15s, 
        crypto_logger_output_1min, 
        crypto_logger_output_30min, 
        crypto_logger_output_1h, 
        crypto_logger_output_1d
    ]
    for crypto_logger in crypto_loggers:
        crypto_logger.init()
    try:
        while True:
            #t1 = time.time()
            for crypto_logger in crypto_loggers:
                dataset = crypto_logger.concat_next()
                crypto_logger.process_next(dataset)
                crypto_logger.log_next()
            #t2 = time.time()
            #print('Time spent for one loop:', t2 - t1)
            #time.sleep(crypto_loggers[0].delay)
    except (KeyboardInterrupt, SystemExit):
        print('Saving latest complete dataset...')
        crypto_logger.process_next(dataset)
        print('User terminated crypto logger process.')
    except Exception as e:
        print(e)
    finally:
        # Release resources.
        print('crypto_logger process done.')

def main():
    """crypto_logger main."""
    start_loggers()

if __name__ == '__main__':
    main()
