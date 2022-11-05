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
from time import sleep, time
from os.path import exists, join
from os import mkdir

import pandas as pd

class Crypto_logger_base(ABC):
    def __init__(self, interval='15s', delay=4.7, buffer_size=3000, directory='crypto_logs', 
                 log_name='crypto_log', raw=False):
        """
        :param interval: OHLCV interval to log. Default is 15 seconds.
        :param delay: delay between Binance API requests. Minimum calculated was 4.7 seconds.
        :param buffer_size: buffer size to avoid crashing on memory accesses.
        :param directory: the directory where to output the logs.
        :param log_name: name of the log file.
        :param raw: whether the log dumps raw (instantaneous) or OHLCV data.
        """
        self.interval = interval
        self.delay = delay
        self.buffer_size = buffer_size
        self.directory = directory
        self.raw = raw

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

    def start(self, append=False, roll=0):
        """Main logger loop."""
        print('Starting crypto logger.')

        if exists(self.log_name) and 'output' in self.log_name:
            self.dataset = self.get_from_file(log_name=self.log_name, from_raw=False)
            self.dataset = self.dataset.tail(self.buffer_size)
        else:
            self.dataset = self.get()

        self.min_index = self.dataset.index[-1]
        self.dataset = self.put(self.dataset)

        while True:
            try:
                dataset = pd.concat([self.dataset, self.get()], axis='index', join='outer')
            except (KeyboardInterrupt, SystemExit):
                print('User terminated crypto logger process.')
                break
            except Exception as e:
                print(e)
            try:
                self.dataset = self.put(dataset)
            except (KeyboardInterrupt, SystemExit):
                print('Saving latest complete dataset...')
                self.dataset = self.put(dataset)
                print('User terminated crypto logger process.')
                break
            except Exception as e:
                print(e)
            try:
                if exists(self.log_screened_name):
                    dataset_screened_old = \
                        pd.read_csv(self.log_screened_name, index_col=0, header=0)
                else:
                    dataset_screened_old = None
                dataset_screened = self.screen(self.dataset)
                if dataset_screened is not None:
                    if roll != 0:
                        if append and exists(self.log_screened_name):
                            dataset_screened = \
                                pd.concat([dataset_screened_old, dataset_screened], axis='index')
                            dataset_screened = \
                                dataset_screened.drop_duplicates(subset=['symbol'], keep='last')
                        dataset_screened = dataset_screened.tail(roll)
                        dataset_screened.to_csv(self.log_screened_name)
                    elif append:
                        dataset_screened.to_csv(self.log_screened_name, mode='a')
                    else:
                        dataset_screened.to_csv(self.log_screened_name)
            except (KeyboardInterrupt, SystemExit):
                print('User terminated crypto logger process.')
                break
            except Exception as e:
                print(e)
            sleep(self.delay)
        print('Crypto logger process done.')
