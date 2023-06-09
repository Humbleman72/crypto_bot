#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        crypto_mqtt_pub.py
# By:          Samuel Duclos
# Modified by: Jonathan Fournier
# For:         Myself
# Description: This file implements the main for the crypto_logger.

# Library imports.
from utils.crypto_logger_input import Crypto_logger_input
from utils.crypto_logger_output import Crypto_logger_output
from utils.trader.mqtt_pub import MQTTPublisher
from crypto_monitor import CryptoMonitor
from datetime import datetime
import time

def init_loggers():
    """Main logger initialization."""
    crypto_logger_input_15s = Crypto_logger_input(delay=0, interval='15s', buffer_size=3000, 
                                                  price_percent=1.0, volume_percent=0.0, 
                                                  as_pair=False, append=True, roll=60, log=True)
    crypto_logger_output_15s = Crypto_logger_output(delay=0, 
                                                    interval_input='15s', 
                                                    interval='15s', 
                                                    buffer_size=60, 
                                                    input_log_name='input', 
                                                    append=False, 
                                                    roll=1000, 
                                                    log=True)
    crypto_logger_output_1min = Crypto_logger_output(delay=0, 
                                                     interval_input='15s', 
                                                     interval='1min', 
                                                     buffer_size=1500, 
                                                     input_log_name='output', 
                                                     append=False, 
                                                     roll=1000, 
                                                     log=True)
    crypto_logger_output_30min = Crypto_logger_output(delay=0, 
                                                      interval_input='1min', 
                                                      interval='30min', 
                                                      buffer_size=60, 
                                                      input_log_name='output', 
                                                      append=False, 
                                                      roll=1000, 
                                                      log=True)
    crypto_logger_output_1h = Crypto_logger_output(delay=0, 
                                                   interval_input='30min', 
                                                   interval='1h', 
                                                   buffer_size=60, 
                                                   input_log_name='output', 
                                                   append=False, 
                                                   roll=1000, 
                                                   log=True)
    crypto_logger_output_1d = Crypto_logger_output(delay=0, 
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
    return crypto_loggers


def loop_loggers(crypto_loggers):
    """Main logger loop."""
    print('Starting crypto loggers.')
    input_15s = crypto_loggers['input_15s'].maybe_get_from_file(dataset=None, inputs=False, screened=False)
    output_15s = crypto_loggers['output_15s'].maybe_get_from_file(dataset=None, inputs=False, screened=False)
    output_1min = crypto_loggers['output_1min'].maybe_get_from_file(dataset=None, inputs=False, screened=False)
    output_30min = crypto_loggers['output_30min'].maybe_get_from_file(dataset=None, inputs=False, screened=False)
    output_1h = crypto_loggers['output_1h'].maybe_get_from_file(dataset=None, inputs=False, screened=False)
    output_1d = crypto_loggers['output_1d'].maybe_get_from_file(dataset=None, inputs=False, screened=False)
    input_15s_screened = crypto_loggers['input_15s'].maybe_get_from_file(dataset=None, inputs=False, screened=True)
    output_15s_screened = crypto_loggers['output_15s'].maybe_get_from_file(dataset=None, inputs=False, screened=True)
    output_1min_screened = crypto_loggers['output_1min'].maybe_get_from_file(dataset=None, inputs=False, screened=True)
    output_30min_screened = crypto_loggers['output_30min'].maybe_get_from_file(dataset=None, inputs=False, screened=True)
    output_1h_screened = crypto_loggers['output_1h'].maybe_get_from_file(dataset=None, inputs=False, screened=True)
    output_1d_screened = crypto_loggers['output_1d'].maybe_get_from_file(dataset=None, inputs=False, screened=True)

    crypto_monitor = CryptoMonitor()
    mqtt_pub = MQTTPublisher('192.168.20.32', 1883)

    try:
        t2 = time.time()
        while True:
            t1 = t2
            t2 = time.time()
            print('Time spent for one loop:', t2 - t1)
            input_15s = crypto_loggers['input_15s'].get_and_put_next(old_dataset=input_15s, dataset=None)
            new_dataset = crypto_loggers['input_15s'].get(None)
            update_df = crypto_monitor.process(new_dataset)
            print('Length of processed dataset: ', len(update_df))
            if not update_df.empty and mqtt_pub is not None:
                mqtt_pub.publish('asset_df', update_df.to_json(orient='records'))
                print('Publishing dataset.')
            else:
                print('Not publishing dataset.')

            output_15s = crypto_loggers['output_15s'].get_and_put_next(old_dataset=output_15s, dataset=input_15s)
            output_1min = crypto_loggers['output_1min'].get_and_put_next(old_dataset=output_1min, dataset=output_15s)
            output_30min = crypto_loggers['output_30min'].get_and_put_next(old_dataset=output_30min, dataset=output_1min)
            output_1h = crypto_loggers['output_1h'].get_and_put_next(old_dataset=output_1h, dataset=output_30min)
            output_1d = crypto_loggers['output_1d'].get_and_put_next(old_dataset=output_1d, dataset=output_1h)
            input_15s_screened = crypto_loggers['input_15s'].screen_next(old_dataset_screened=input_15s_screened, 
                                                                         dataset_screened=None, dataset=input_15s)
            output_15s_screened = crypto_loggers['output_15s'].screen_next(old_dataset_screened=output_15s_screened, 
                                                                           dataset_screened=input_15s_screened, dataset=output_15s)
            output_1min_screened = crypto_loggers['output_1min'].screen_next(old_dataset_screened=output_1min_screened, 
                                                                             dataset_screened=output_15s_screened, dataset=output_1min)
            output_30min_screened = crypto_loggers['output_30min'].screen_next(old_dataset_screened=output_30min_screened, 
                                                                               dataset_screened=output_1min_screened, dataset=output_30min)
            output_1h_screened = crypto_loggers['output_1h'].screen_next(old_dataset_screened=output_1h_screened, 
                                                                         dataset_screened=output_30min_screened, dataset=output_1h)
            output_1d_screened = crypto_loggers['output_1d'].screen_next(old_dataset_screened=output_1d_screened, 
                                                                         dataset_screened=output_1h_screened, dataset=output_1d)
            if not output_1d_screened.empty:
                now = datetime.now()
                now_str = now.strftime("[%Y-%m-%d %H:%M:%S]")
                print(now_str, 'Found assets to trade.')
                for index, row in output_1d_screened.iterrows():
                    symbol = row['symbol']
                    price = row['close']
                    print(now_str, symbol, price)
                    crypto_monitor.add_crypto(symbol, price, index.to_pydatetime())


            crypto_loggers['output_1d'].log_next(dataset=None, dataset_screened=output_1d_screened)
    except (KeyboardInterrupt, SystemExit):
        print('Saving latest complete dataset...')
        crypto_loggers['input_15s'].log_next(dataset=input_15s, dataset_screened=input_15s_screened)
        crypto_loggers['output_15s'].log_next(dataset=output_15s, dataset_screened=output_15s_screened)
        crypto_loggers['output_1min'].log_next(dataset=output_1min, dataset_screened=output_1min_screened)
        crypto_loggers['output_30min'].log_next(dataset=output_30min, dataset_screened=output_30min_screened)
        crypto_loggers['output_1h'].log_next(dataset=output_1h, dataset_screened=output_1h_screened)
        crypto_loggers['output_1d'].log_next(dataset=output_1d, dataset_screened=output_1d_screened)
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
