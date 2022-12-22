#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        cryptocurrency/trader/ssh.py
# By:          Samuel Duclos
# For          Myself
# Description: SSH client using Paramiko to retrieve logs from server.

# Library imports.
from os.path import exists
import time
import sys
import pandas as pd
import paramiko

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

# Class definition.
class Ssh:
    input_log = '~/workspace/crypto_logs/crypto_input_log_15s.txt'
    output_log_screened = \
        '~/workspace/crypto_logs/crypto_output_log_1d_screened.txt'

    def __init__(self, input_log=None, output_log_screened=None, 
                 keys_file='server_keys.txt'):
        if input_log is not None:
            self.input_log = input_log
        if output_log_screened is not None:
            self.output_log_screened = output_log_screened
        ip_address, password = self.init_credentials(keys_file=keys_file)
        self.ssh = self.init_ssh(ip_address=ip_address, username='sam', 
                                 port=22, password=password)

    def init_credentials(self, keys_file='server_keys.txt'):
        if exists(keys_file):
            with open(keys_file, 'r') as f:
                ip_address, password = \
                    f.readline().replace('\n', '').split(':')
        return ip_address, password

    def init_ssh(self, ip_address='0.0.0.0', username='sam', 
                 port=22, password=''):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip_address, username='sam', port=22, password=password)
        return ssh

    def get_logs_from_server(self, server_log=output_log_screened):
        ssh_stdin, ssh_stdout, ssh_stderr = \
            self.ssh.exec_command('cat {}'.format(server_log))
        df = StringIO(str(ssh_stdout.read().decode('utf-8')))
        try:
            df = pd.read_csv(df)
            if df.shape[0] < 1:
                df = None
        except (IndexError, pd.errors.EmptyDataError):
            df = None
            time.sleep(0.5)
        return df
