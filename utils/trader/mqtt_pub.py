#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        utils/trader/mqtt_pub.py
# By:          Jonathan Fournier
# For:         Myself
# Description: This file implements an MQTT publisher.

# Library imports.
import paho.mqtt.client as mqtt
import json

latest_records = [{'symbol': 'FET', 'price': 0.1033, 'buy_price': 0.1045999999999999, 'percent_change': -0.012428298279157741, 'min_percent': -0.018164435946461662, 'min_percent_time': '00h 03m 43s', 'max_percent': -0.01147227533460691, 'max_percent_time': '00h 01m 58s', 'date_added': '09h 42m 43s'},
                  {'symbol': 'NULS', 'price': 0.2118, 'buy_price': 0.2192, 'percent_change': -0.03375912408759132, 'min_percent': -0.03421532846715319, 'min_percent_time': '00h 02m 58s', 'max_percent': -0.03193430656934322, 'max_percent_time': '00h 01m 28s', 'date_added': '10h 15m 28s'},
                  {'symbol': 'CTXC', 'price': 0.17050000000000004, 'buy_price': 0.1741, 'percent_change': -0.020677771395749365, 'min_percent': -0.025272831705916068, 'min_percent_time': '00h 01m 28s', 'max_percent': -0.020103388856978606, 'max_percent_time': '00h 01m 13s', 'date_added': '09h 11m 43s'}]


class MQTTPublisher:
    def __init__(self, server_ip, server_port):
        keep_alive = 60  # 60s
        self.client = mqtt.Client()

        self.client.connect(server_ip, server_port, keep_alive)
        self.client.on_publish = self.on_publish

    def on_publish(self, client, userdata, message):
        print(f'MQTT Client published message: {message}')

    def publish(self, topic, payload):
        if not isinstance(payload, str):
            payload = json.dumps(payload)
        self.client.publish(topic, payload=payload, qos=0, retain=False)


if __name__ == '__main__':
    mqtt_client = MQTTPublisher('192.168.20.32', 1883)
    mqtt_client.publish('test1', latest_records)
