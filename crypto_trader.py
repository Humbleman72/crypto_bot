#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        crypto_trader.py
# By:          Samuel Duclos
# For          Myself
# Description: Binance asset trading.

# Variable definitions.
sell_asset = 'BUSD'
take_profit = 5.0
stop_loss = 2.0
take_profit_count = 2
stop_loss_count = 1
keys_file = 'server_keys.txt'
input_log = '~/workspace/crypto_logs/crypto_input_log_15s.txt'
output_log_screened = '~/workspace/crypto_logs/crypto_output_log_1d_screened.txt'

# Time prelude for optimization purposes.
import time
t1 = time.time()

# Import libraries.
from cryptocurrency.authentication import Cryptocurrency_authenticator
from cryptocurrency.exchange import Cryptocurrency_exchange
from cryptocurrency.conversion import get_timezone_offset_in_seconds
from cryptocurrency.conversion_table import get_conversion_table
from cryptocurrency.trader.ssh import Ssh
from cryptocurrency.trader.wallet import select_asset_with_biggest_wallet
from cryptocurrency.trader.trade import trade
from cryptocurrency.trader.trade import add_entry_to_blacklist
from cryptocurrency.trader.trade import make_empty_blacklist
from cryptocurrency.trader.trade import check_if_asset_from_pair_is_buyable
from cryptocurrency.trader.trade import check_take_profit_and_stop_loss
from cryptocurrency.trader.trade import remove_older_entries_in_blacklist
from cryptocurrency.trader.trade import choose_to_asset, trade_conditionally

# Manage API keys.
authenticator = Cryptocurrency_authenticator(use_keys=False, testnet=False)
client = authenticator.spot_client

# Get all available pair information for trading.
exchange = Cryptocurrency_exchange(client=client, directory='crypto_logs')
exchange_info = exchange.info

# Precalculate UTC offset for inter-server communication coherence.
offset_s = get_timezone_offset_in_seconds()

# Precalculate conversion_table.
conversion_table = get_conversion_table(client=client, 
                                        exchange_info=exchange_info, 
                                        offset_s=offset_s, 
                                        dump_raw=False, 
                                        as_pair=True, 
                                        minimal=False, 
                                        extra_minimal=False, 
                                        super_extra_minimal=False, 
                                        convert_to_USDT=False)

# Get highest USDT-converted held asset and determine priority.
from_asset, converted_quantity, quantity, priority = \
    select_asset_with_biggest_wallet(client=client, 
                                     conversion_table=conversion_table, 
                                     exchange_info=exchange_info)

# Initialize an empty blacklist.
blacklist = make_empty_blacklist()

# Connect to the server through SSH.
ssh = Ssh(input_log=input_log, output_log_screened=output_log_screened, keys_file=keys_file)

# Display how long the prelude took.
t2 = time.time()
print('Initialization time:', t2 - t1, 'seconds.')

# Main trader loop.
to_asset = sell_asset
latest_asset = from_asset
try:
    while True:
        latest_asset, to_asset = choose_to_asset(
            ssh, blacklist, from_asset, sell_asset, to_asset, latest_asset, take_profit_count, 
            stop_loss_count, conversion_table, exchange_info, output_log_screened)
        if from_asset != to_asset:
            blacklist, from_asset, to_asset = trade_conditionally(
                ssh=ssh, blacklist=blacklist, client=client, exchange_info=exchange_info, 
                to_asset=to_asset, offset_s=offset_s)
        elif from_asset != sell_asset:
            #conversion_table = ssh.get_logs_from_server(server_log=ssh.input_log)
            conversion_table = get_conversion_table(
                client=client, exchange_info=exchange_info, offset_s=offset_s, dump_raw=False, as_pair=True, 
                minimal=False, extra_minimal=False, super_extra_minimal=False, convert_to_USDT=False)
            blacklist, to_asset = check_take_profit_and_stop_loss(
                blacklist, from_asset, to_asset, conversion_table, exchange_info, 
                latest_asset, take_profit=take_profit, stop_loss=stop_loss)
        blacklist = remove_older_entries_in_blacklist(blacklist, frequency='15min')
except (KeyboardInterrupt, SystemExit):
    ssh.close()
    print('Closed SSH connection to server.')
except Exception as e:
    print(e)
finally:
    # Release resources.
    print('Crypto trader process done.')
