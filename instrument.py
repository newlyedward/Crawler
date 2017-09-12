# -*- coding: utf-8 -*-
"""
get financial instrument info from file or database
"""
import os
import numpy as np
import pandas as pd
import datetime as dt
from pymongo import MongoClient

from utils import get_congfig_handle, LogHandler
from settings import *

log = LogHandler('future')


class Instrument(object):
    config = get_congfig_handle()
    mongo_host = config.get('Mongo', 'host')
    mongo_port = config.getint('Mongo', 'port')
    mongo = MongoClient(mongo_host, mongo_port)

    base_dir = config.get('FinData', 'base_dir')
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    def __init__(self, market, period='day'):
        self.period = period.lower()
        self.market = market.lower()

    def __del__(self):
        self.mongo.close()
