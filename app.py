#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        app.py
# By:          Jonathan Fournier
# Modified by: Samuel Duclos
# For:         Myself
# Description: This file implements the main flask application.

# Library imports.
from cryptocurrency.mqtt_sub import MQTTSub
from website.users import iterate_users, DummyLock, User
from website.crypto_monitor import CryptoMonitor
from crypto_logger_mqtt import init_loggers, loop_loggers
from datetime import datetime
from urllib.parse import urljoin

import time
import os
import queue
import json
import requests
import flask
import flask_socketio
import pandas as pd
import eventlet
eventlet.monkey_patch()


template_dir = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
template_dir = os.path.join(template_dir, 'website')
template_dir = os.path.join(template_dir, 'templates')
app = flask.Flask(__name__, template_folder=template_dir)
socketio = flask_socketio.SocketIO(app)

users = {}
users_lock = DummyLock()

last_asset_info_list = None
last_update_str = ''

@app.route('/')
def index():
    return flask.render_template('index_test.html')

@socketio.on('connect')
def socket_connect():
    global last_asset_info_list
    print('New client {} connected'.format(flask.request.sid))
    users_lock.acquire()
    user = User(sid=flask.request.sid)
    users[flask.request.sid] = user
    users_lock.release()
    if last_asset_info_list is not None:
        for ai in last_asset_info_list:
            ai['date_added'] = ai['date_added'] + ' (old)'
        print('\tPrevious asset info available')
        socketio.emit('update_records', last_asset_info_list, to=flask.request.sid)
        socketio.emit('last_update', last_update_str, to=flask.request.sid)
    else:
        print('\tNo previous asset info available')
        # socketio.emit('last_update', 'No recent update (cached data).', to=flask.request.sid)

@socketio.on('disconnect')
def socket_disconnect():
    print('Client {} disconnected'.format(flask.request.sid))

    if flask.request.sid in users:
        users_lock.acquire()
        del users[flask.request.sid]
        users_lock.release()

def process_dataset(client, userdata, msg):
    global last_asset_info_list
    asset_info_list = json.loads(msg.payload.decode('utf8'))
    print(f'Data received on {msg.topic}:')

    for asset_info in asset_info_list:
        print(asset_info)

    last_asset_info_list = asset_info_list
    last_update_str = f'Last update: {datetime.now().strftime("%Y-%m-%d   %H:%M:%S")}'

    with app.app_context():
        for _, user in iterate_users(users):
            socketio.emit('update_records', asset_info_list, to=user.sid)
            socketio.emit('last_update', last_update_str, to=user.sid)
    time.sleep(10)

def get_price():
    base_url = 'https://api.binance.com'
    path = '/api/v3/ticker/price'
    params = {'symbol': 'BTCUSDT'}

    url = urljoin(base_url, path)
    r = requests.get(url, params=params)
    if r.status_code == 200:
        return r.json()['price']
    else:
        print('Error')

def generate_data():
    time.sleep(0.5)


# Start server
if __name__ == '__main__':
    # crypto_monitor = CryptoMonitor()
    # crypto_loggers = init_loggers()
    # queue = queue.Queue(maxsize=10)

    print('Application started.')
    # socketio.start_background_task(loop_loggers, crypto_loggers, queue)
    # socketio.start_background_task(process_data, socketio, queue)

    mqtt_sub = MQTTSub('192.168.20.32', 1883)
    mqtt_sub.subscribe('asset_df', process_dataset)

    socketio.run(app, host='0.0.0.0', port=5001, debug=False)
