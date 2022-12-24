#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        cryptocurrency/mqtt_sub.py
# By:          Jonathan Fournier
# For:         Myself
# Description: This file implements an MQTT subscriber.

# Library imports.
import paho.mqtt.client as mqtt
import json
#import threading

latest_records = [{'symbol': 'FET', 'price': 0.1033, 'buy_price': 0.1045999999999999, 'percent_change': -0.012428298279157741, 'min_percent': -0.018164435946461662, 'min_percent_time': '00h 03m 43s', 'max_percent': -0.01147227533460691, 'max_percent_time': '00h 01m 58s', 'date_added': '09h 42m 43s'},
                  {'symbol': 'NULS', 'price': 0.2118, 'buy_price': 0.2192, 'percent_change': -0.03375912408759132, 'min_percent': -0.03421532846715319, 'min_percent_time': '00h 02m 58s', 'max_percent': -0.03193430656934322, 'max_percent_time': '00h 01m 28s', 'date_added': '10h 15m 28s'},
                  {'symbol': 'CTXC', 'price': 0.17050000000000004, 'buy_price': 0.1741, 'percent_change': -0.020677771395749365, 'min_percent': -0.025272831705916068, 'min_percent_time': '00h 01m 28s', 'max_percent': -0.020103388856978606, 'max_percent_time': '00h 01m 13s', 'date_added': '09h 11m 43s'}]


class MQTTSub:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.keep_alive = 60  # 60s
        self.topic = None
        self.client = mqtt.Client()

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.topic, qos=0)
        print(f'MQTT: subscribed to {self.topic}.')

    def subscribe(self, topic, callback):
        self.client.on_connect = self.on_connect
        self.client.on_message = callback
        self.topic = topic
        self.client.connect(self.server_ip, self.server_port, self.keep_alive)
        self.client.loop_start()


if __name__ == '__main__':
    def on_message(client, userdata, msg):
        payload = json.loads(msg.payload.decode('utf8'))
        print(f'Data received on {msg.topic}:')
        print(payload)

    mqtt_sub = MQTTSub('192.168.20.32', 1883)
    mqtt_sub.subscribe('test1', on_message)
