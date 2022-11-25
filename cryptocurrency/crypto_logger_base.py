#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        cryptocurrency/crypto_logger_base.py
# By:          Samuel Duclos
# For          Myself
# Description: Simple Binance logger base class.

# Library imports.
from cryptocurrency.resample import resample
from binance.client import Client
from abc import abstractmethod, ABC
from os.path import exists, join
from os import mkdir
import time
import pandas as pd

class Crypto_logger_base(ABC):
    def __init__(self, delay=4.7, interval='15s', interval_input='', buffer_size=3000, 
                 directory='crypto_logs', log_name='crypto_log', input_log_name='', 
                 raw=False, append=False, roll=0, log=True):
        """
        :param delay: delay between Binance API requests. Minimum calculated was 4.7 seconds.
        :param interval: OHLCV interval to log. Default is 15 seconds.
        :param interval_input: OHLCV interval from input log. Default is 15 seconds.
        :param buffer_size: buffer size to avoid crashing on memory accesses.
        :param directory: the directory where to output the logs.
        :param log_name: name of the log file.
        :param input_log_name: either input or output (this ends up in the log file name).
        :param raw: whether the log dumps raw (instantaneous) or OHLCV data.
        :param append: whether to append the latest screened data to the log dumps or not.
        :param roll: buffer size to cut oldest data (0 means don't cut).
        :param log: whether to log to files.
        """
        input_log_name = 'crypto_' + input_log_name + '_log_' + interval_input

        self.load_from_ohlcv = not raw and interval_input != interval

        self.delay = delay
        self.interval = interval
        self.interval_input = interval_input
        self.buffer_size = buffer_size
        self.directory = directory
        self.raw = raw
        self.append = append
        self.roll = roll
        self.log = log

        self.input_log_name = join(directory, input_log_name + '.txt')
        self.input_log_screened_name = join(directory, input_log_name + '_screened.txt')

        self.log_name = join(directory, log_name + '.txt')
        self.log_screened_name = join(directory, log_name + '_screened.txt')

        if not exists(directory):
            mkdir(directory)

    #self.get_from_file(log_name=self.log_name, from_raw=False)
    #self.get_from_file(log_name=self.input_log_name, from_raw=not self.load_from_ohlcv)
    def get_from_file(self, log_name, from_raw=False):
        if exists(log_name):
            header = 0 if from_raw else [0, 1]
            dataset = pd.read_csv(log_name, header=header, index_col=0)
            dataset.index = pd.DatetimeIndex(dataset.index)
            return dataset.sort_index(axis='index')
        else:
            return None

    def init(self):
        """Initialization of the main logger loop."""
        if 'output' in self.log_name:
            self.dataset = self.get_from_file(log_name=self.log_name, from_raw=False)
        else:
            self.dataset = self.get()
        self.dataset_screened = None
        self.dataset = self.dataset.tail(self.buffer_size)
        self.min_index = self.dataset.index[-1]
        self.dataset = self.put(self.dataset)

    @abstractmethod
    def get(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def screen(self, **kwargs):
        raise NotImplementedError()

    def put(self, dataset):
        dataset = dataset.copy().reset_index()
        if self.raw:
            dataset = dataset.drop_duplicates(subset=['symbol', 'count'], 
                                              keep='first', ignore_index=True)
        else:
            dataset = dataset.drop_duplicates(keep='last', ignore_index=True)

        if 'date' in dataset.columns:
            min_index_int = dataset[dataset['date'] == self.min_index].index[0]
            dataset = dataset.set_index('date')
        if not self.raw:
            dataset = resample(dataset, self.interval)
        if 'date' in dataset.columns:
            dataset = dataset.iloc[min_index_int:]

        dataset = dataset.tail(self.buffer_size)
        dataset.to_csv(self.log_name)
        self.min_index = dataset.index[0]
        return dataset

    def concat_next(self):
        """Concatenate old dataset with new dataset in main logger loop."""
        return pd.concat([self.dataset, self.get()], axis='index', join='outer')

    def process_next(self, dataset):
        """Process dataset in main logger loop."""
        self.dataset = self.put(dataset)
        return self.dataset

    def screen_next(self, dataset=None, dataset_screened=None):
        """Log dataset in main logger loop."""
        if dataset is None:
            dataset = self.dataset
        if dataset_screened is None:
            self.dataset_screened_old = self.get_from_file(log_name=self.log_screened_name, from_raw=True)
        else:
            self.dataset_screened_old = dataset_screened
        self.dataset_screened = self.screen(dataset, dataset_screened=self.dataset_screened_old)
        if self.dataset_screened is not None:
            if self.append:
                if self.dataset_screened_old is not None:
                    self.dataset_screened = pd.concat([self.dataset_screened_old, self.dataset_screened], axis='index')
                self.dataset_screened = self.dataset_screened.sort_index(axis='index')
                self.dataset_screened = self.dataset_screened.drop_duplicates(subset=['symbol'], keep='last')
            if self.roll > 0:
                self.dataset_screened = self.dataset_screened.tail(self.roll)
        return self.dataset_screened

    def log_screened_next(self, dataset_screened=None):
        """Log dataset in main logger loop."""
        if self.dataset_screened is not None and self.log:
            self.dataset_screened.to_csv(self.log_screened_name)

    def loop(self):
        """Main logger loop."""
        print('Starting crypto logger.')
        try:
            t2 = time.time()
            while True:
                t1 = t2
                t2 = time.time()
                print('Time spent for one loop:', t2 - t1)
                dataset = self.concat_next()
                dataset = self.process_next(dataset)
                dataset_screened = self.screen_next(dataset=dataset, dataset_screened=dataset_screened)
                self.log_screened_next(dataset_screened=dataset_screened)
                time.sleep(self.delay)
        except (KeyboardInterrupt, SystemExit):
            print('Saving latest complete dataset...')
            self.process_next(dataset)
            dataset_screened = self.screen_next(dataset=dataset, dataset_screened=dataset_screened)
            self.log_screened_next(dataset_screened=dataset_screened)
            print('User terminated crypto logger process.')
        except Exception as e:
            print(e)
        finally:
            # Release resources.
            print('crypto_logger process done.')

    def start(self):
        """Main logger initialization and loop."""
        self.init()
        self.loop()
