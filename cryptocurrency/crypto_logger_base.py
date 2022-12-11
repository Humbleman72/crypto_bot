#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        cryptocurrency/crypto_logger_base.py
# By:          Samuel Duclos
# For          Myself
# Description: Simple Binance logger base class.

# Library imports.
from cryptocurrency.resample import resample
from abc import abstractmethod, ABC
from os.path import exists, join
from os import mkdir
import time
import pandas as pd

# Class definition.
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
            return dataset
        else:
            return None

    def init(self):
        """Initialization of the main logger loop."""
        if 'output' in self.log_name:
            self.dataset = self.get_from_file(log_name=self.log_name, from_raw=False)
        else:
            self.dataset = self.get()
        self.dataset = self.dataset.tail(self.buffer_size)
        self.dataset = self.put(self.dataset)

    @abstractmethod
    def get(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def screen(self, **kwargs):
        raise NotImplementedError()

    def put(self, dataset):
        if dataset is not None:
            dataset = dataset.copy().reset_index()
            if self.raw:
                dataset = dataset.drop_duplicates(subset=['symbol', 'count'], 
                                                  keep='first', ignore_index=True)
            else:
                dataset = dataset.drop_duplicates(keep='last', ignore_index=True)
            dataset = dataset.set_index('date')
            if not self.raw:
                dataset = resample(dataset, self.interval)
            dataset = dataset.tail(self.buffer_size)
            dataset.to_csv(self.log_name)
        return dataset

    def concat_next(self, dataset=None):
        """Concatenate old dataset with new dataset in main logger loop."""
        self.dataset = pd.concat([self.dataset, self.get(dataset)], axis='index', join='outer')

    def process_next(self):
        """Process dataset in main logger loop."""
        self.dataset = self.put(self.dataset)
        return self.dataset

    def screen_next(self, dataset_screened=None):
        """Screen dataset in main logger loop."""
        if dataset_screened is None:
            dataset_screened = self.get_from_file(log_name=self.log_screened_name, from_raw=True)
        self.dataset_screened = self.screen(self.dataset, dataset_screened=dataset_screened)
        if self.dataset_screened is not None:
            self.dataset_screened = self.dataset_screened.sort_index(axis='index')
            if self.append and self.dataset_screened is not None:
                self.dataset_screened = pd.concat([dataset_screened, self.dataset_screened], axis='index')
                self.dataset_screened = self.dataset_screened.drop_duplicates(subset=['symbol'], keep='last')
            if self.roll != 0:
                self.dataset_screened = self.dataset_screened.tail(self.roll)
        return dataset_screened

    def log_next(self):
        """Log dataset in main logger loop."""
        if self.log:
            #if self.dataset is not None:
            #    self.dataset.to_csv(self.log_name)
            if self.dataset_screened is not None:
                self.dataset_screened.to_csv(self.log_screened_name)
