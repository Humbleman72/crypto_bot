#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        cryptocurrency/authentication.py
# By:          Samuel Duclos
# For:         Myself
# Description: This file handles python-binance authentication.

# Library imports.
from os.path import exists
from binance.client import Client

# Class definition.
class Cryptocurrency_authenticator:
    def __init__(self, use_keys=False, testnet=False, keys_path='keys.txt'):
        api_key, secret_key = self.get_API_keys(keys_path=keys_path)
        self.spot_client = Client(api_key=api_key, api_secret=secret_key, testnet=False) if use_keys is not None else Client('', '')

    def get_API_keys(self, keys_path='keys.txt'):
        if exists(keys_path):
            with open(keys_path, 'r') as f:
                return f.readline().replace('\n', '').split(':')
        else:
            return ('', '')
