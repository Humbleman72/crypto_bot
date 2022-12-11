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

def init_loggers():
    """Main logger initialization."""
    crypto_logger_input_15s = Crypto_logger_input(delay=1, interval='15s', buffer_size=3000, 
                                                  price_percent=1.0, volume_percent=0.0, 
                                                  as_pair=False, append=True, roll=60, log=True)
    crypto_logger_output_15s = Crypto_logger_output(delay=1, 
                                                    interval_input='15s', 
                                                    interval='15s', 
                                                    buffer_size=60, 
                                                    input_log_name='input', 
                                                    append=False, 
                                                    roll=1000, 
                                                    log=True)
    crypto_logger_output_1min = Crypto_logger_output(delay=1, 
                                                     interval_input='15s', 
                                                     interval='1min', 
                                                     buffer_size=1500, 
                                                     input_log_name='output', 
                                                     append=False, 
                                                     roll=1000, 
                                                     log=True)
    crypto_logger_output_30min = Crypto_logger_output(delay=1, 
                                                      interval_input='1min', 
                                                      interval='30min', 
                                                      buffer_size=60, 
                                                      input_log_name='output', 
                                                      append=False, 
                                                      roll=1000, 
                                                      log=True)
    crypto_logger_output_1h = Crypto_logger_output(delay=1, 
                                                   interval_input='30min', 
                                                   interval='1h', 
                                                   buffer_size=60, 
                                                   input_log_name='output', 
                                                   append=False, 
                                                   roll=1000, 
                                                   log=True)
    crypto_logger_output_1d = Crypto_logger_output(delay=1, 
                                                   interval_input='1h', 
                                                   interval='1d', 
                                                   buffer_size=60, 
                                                   input_log_name='output', 
                                                   append=False, 
                                                   roll=1000, 
                                                   log=True)
    crypto_loggers = {
        'input_15s': crypto_logger_input_15s, 
        'output_15s': crypto_logger_output_15s, 
        'output_1min': crypto_logger_output_1min, 
        'output_30min': crypto_logger_output_30min, 
        'output_1h': crypto_logger_output_1h, 
        'output_1d': crypto_logger_output_1d
    }
    for i in list(crypto_loggers.keys()):
        crypto_loggers[i].init()
    return crypto_loggers

def loop_loggers(crypto_loggers):
    """Main logger loop."""
    print('Starting crypto loggers.')
    try:
        t2 = time.time()
        while True:
            t1 = t2
            t2 = time.time()
            print('Time spent for one loop:', t2 - t1)
            dataset = dataset_screened = None
            for i in list(crypto_loggers.keys()):
                dataset = crypto_loggers[i].concat_next(dataset)
                dataset = crypto_loggers[i].process_next(dataset)
                dataset_screened = \
                    crypto_loggers[i].screen_next(dataset=dataset, 
                                                  dataset_screened=dataset_screened)
            for i in list(crypto_loggers.keys()):
                crypto_loggers[i].log_next()
    except (KeyboardInterrupt, SystemExit):
        print('Saving latest complete dataset...')
        dataset = crypto_loggers[i].process_next(dataset)
        dataset_screened = \
            crypto_loggers[i].screen_next(dataset=dataset, 
                                          dataset_screened=dataset_screened)
        for i in list(crypto_loggers.keys()):
            crypto_loggers[i].log_next()
        print('User terminated crypto logger processes.')
    except Exception as e:
        print(e)
    finally:
        # Release resources.
        print('Crypto logger processes done.')

def main():
    """crypto_logger main."""
    crypto_loggers = init_loggers()
    loop_loggers(crypto_loggers)

if __name__ == '__main__':
    main()
