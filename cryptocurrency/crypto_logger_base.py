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
    def __init__(self, interval='15s', delay=4.7, buffer_size=3000, directory='crypto_logs', 
                 log_name='crypto_log', raw=False, append=False, roll=0, log=True):
        """
        :param interval: OHLCV interval to log. Default is 15 seconds.
        :param delay: delay between Binance API requests. Minimum calculated was 4.7 seconds.
        :param buffer_size: buffer size to avoid crashing on memory accesses.
        :param directory: the directory where to output the logs.
        :param log_name: name of the log file.
        :param raw: whether the log dumps raw (instantaneous) or OHLCV data.
        :param append: whether to append the latest screened data to the log dumps or not.
        :param roll: buffer size to cut oldest data (0 means don't cut).
        :param log: whether to log to files.
        """
        self.interval = interval
        self.delay = delay
        self.buffer_size = buffer_size
        self.directory = directory
        self.raw = raw
        self.append = append
        self.roll = roll
        self.log = log

        self.log_name = join(self.directory, log_name + '.txt')
        self.log_screened_name = join(self.directory, log_name + '_screened.txt')

        if not exists(self.directory):
            mkdir(self.directory)

    #self.get_from_file(log_name=self.log_name, from_raw=False)
    #self.get_from_file(log_name=self.input_log_name, from_raw=self.load_from_ohlcv)
    def get_from_file(self, log_name, from_raw=False):
        if from_raw:
            dataset = pd.read_csv(log_name, header=0, index_col=0)
        else:
            dataset = pd.read_csv(log_name, header=[0, 1], index_col=0)
        dataset.index = pd.DatetimeIndex(dataset.index)
        return dataset.sort_index(axis='index')

    def init(self):
        """Initialization of the main logger loop."""
        if exists(self.log_name) and 'output' in self.log_name:
            self.dataset = self.get_from_file(log_name=self.log_name, from_raw=False)
            self.dataset = self.dataset.tail(self.buffer_size)
        else:
            self.dataset = self.get()
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

    def log_next(self):
        """Log dataset in main logger loop."""
        if exists(self.log_screened_name):
            dataset_screened_old = \
                pd.read_csv(self.log_screened_name, index_col=0, header=0)
        else:
            dataset_screened_old = None
        dataset_screened = self.screen(self.dataset)
        if dataset_screened is not None:
            if self.roll != 0:
                if self.append and exists(self.log_screened_name):
                    dataset_screened = \
                        pd.concat([dataset_screened_old, dataset_screened], axis='index')
                    dataset_screened = \
                        dataset_screened.drop_duplicates(subset=['symbol'], keep='last')
                dataset_screened = dataset_screened.tail(self.roll)
                dataset_screened.to_csv(self.log_screened_name)
            elif self.append:
                dataset_screened.to_csv(self.log_screened_name, mode='a')
            else:
                dataset_screened.to_csv(self.log_screened_name)

    def start(self):
        """Main logger loop."""
        print('Starting crypto logger.')
        self.init()
        try:
            while True:
                t1 = time.time()
                dataset = self.concat_next()
                self.process_next(dataset)
                self.log_next()
                t2 = time.time()
                print('Time spent for one loop:', t2 - t1)
                time.sleep(self.delay)
        except (KeyboardInterrupt, SystemExit):
            print('Saving latest complete dataset...')
            self.process_next(dataset)
            print('User terminated crypto logger process.')
        except Exception as e:
            print(e)
        finally:
            # Release resources.
            print('crypto_logger process done.')
