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
import errno
import os
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

        self.delay = delay
        self.interval = interval
        self.interval_input = interval_input
        self.buffer_size = buffer_size
        self.directory = directory
        self.raw = raw
        self.append = append
        self.roll = roll
        self.log = log

        self.connected_to_raw = self.interval_input == self.interval
        self.input_log_name = join(directory, input_log_name + '.txt')
        self.input_log_screened_name = join(directory, input_log_name + '_screened.txt')

        self.log_name = join(directory, log_name + '.txt')
        self.log_screened_name = join(directory, log_name + '_screened.txt')

        if not exists(directory):
            mkdir(directory)

    def maybe_get_from_file(self, dataset=None, inputs=False, screened=False):
        if dataset is None:
            if screened:
                header = 0
                if inputs:
                    if self.raw:
                        dataset = None
                    else:
                        dataset = self.input_log_screened_name
                else:
                    dataset = self.log_screened_name
            else:
                if inputs:
                    if self.raw:
                        dataset = None
                    else:
                        dataset = self.input_log_name
                        if self.interval_input == self.interval:
                            header = 0
                        else:
                            header = [0, 1]
                else:
                    dataset = self.log_name
                    if self.raw:
                        header = 0
                    else:
                        header = [0, 1]
            if dataset is not None:
                if exists(dataset):
                    dataset = pd.read_csv(dataset, header=header, index_col=0)
                    dataset.index = pd.DatetimeIndex(dataset.index)
                else:
                    dataset = None
        return dataset

    @abstractmethod
    def get(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def screen(self, **kwargs):
        raise NotImplementedError()

    def get_and_put_next(self, old_dataset=None, dataset=None):
        """Concatenate old dataset with new dataset in main logger loop and process."""
        dataset = self.maybe_get_from_file(dataset=dataset, inputs=self.raw, screened=False)
        if self.raw:
            dataset = self.get()
            if old_dataset is not None:
                dataset = pd.concat([old_dataset, dataset], axis='index', join='outer')
            dataset = dataset.copy().reset_index()
            dataset = dataset.drop_duplicates(subset=['symbol', 'count'], 
                                              keep='first', ignore_index=True)
            dataset = dataset.set_index('date')
            if not self.raw:
                dataset = resample(dataset, self.interval)
            dataset = dataset.tail(self.buffer_size)
        else:
            if dataset is None:
                if old_dataset is not None:
                    dataset = old_dataset
            else:
                dataset = self.get(dataset)
                if old_dataset is not None:
                    dataset = pd.concat([old_dataset, dataset], axis='index', join='outer')
                dataset = dataset.copy().reset_index()
                dataset = dataset.drop_duplicates(keep='last', ignore_index=True)
                dataset = dataset.set_index('date')
                dataset = resample(dataset, self.interval)
                dataset = dataset.tail(self.buffer_size)
        return dataset

    def screen_next(self, old_dataset_screened=None, dataset_screened=None, dataset=None):
        """Screen dataset in main logger loop."""
        if not self.raw:
            dataset_screened = self.maybe_get_from_file(dataset=dataset_screened, inputs=True, screened=True)
        dataset_screened = self.screen(dataset, dataset_screened=dataset_screened)
        if dataset_screened is not None:
            dataset_screened = dataset_screened.sort_index(axis='index')
            if self.append and dataset_screened is not None:
                dataset_screened = pd.concat([old_dataset_screened, dataset_screened], axis='index')
                dataset_screened = dataset_screened.drop_duplicates(subset=['symbol'], keep='last')
            if self.roll > 0:
                dataset_screened = dataset_screened.tail(self.roll)
        return dataset_screened

    def log_next(self, dataset=None, dataset_screened=None):
        """Log dataset in main logger loop."""
        if self.log:
            if dataset is not None:
                dataset.to_csv(self.log_name)
            if dataset_screened is not None:
                dataset_screened.to_csv(self.log_screened_name)
