#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:        users.py
# By:          Jonathan Fournier
# For:         Myself
# Description: This file implements user utilities.

class User:
    def __init__(self, sid=None):
        self.sid = sid
        self.id = None

class DummyLock:
    def acquire(self):
        pass

    def release(self):
        pass

users_lock = DummyLock()
inactive_users_lock = DummyLock()

def iterate_users(user_list):
    users_lock.acquire()
    yield from list(user_list.items())
    users_lock.release()

