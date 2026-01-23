# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 08:36:15 2016

@author: efischer
"""
import pandas as pd
import numpy as np
import os
import json
import time
import logging
import yfinance as yf
import traceback

pd.set_option("display.max_colwidth", 10000)
dir_path = os.path.dirname(os.path.realpath(__file__))


mega_path = os.path.join(dir_path, 'data', 'fundamentals_screener_mega_caps.csv')#.csv
mega_pd = pd.read_csv(mega_path, encoding='iso-8859-1')

lrg_path = os.path.join(dir_path, 'data', 'fundamentals_screener_large.csv')#.csv
lrg_pd = pd.read_csv(lrg_path, encoding='iso-8859-1')

mid_path = os.path.join(dir_path, 'data', 'fundamentals_screener_mid_caps.csv')#.csv
mid_pd = pd.read_csv(mid_path, encoding='iso-8859-1')

small_path = os.path.join(dir_path, 'data', 'fundamentals_screener_small_cap.csv')#.csv
small_pd = pd.read_csv(small_path, encoding='iso-8859-1')

vertical_concat = pd.concat([mega_pd, lrg_pd, mid_pd, small_pd], axis=0)

filepath = os.path.join(dir_path, 'data', 'all_caps_fundamentals.csv')#.csv
vertical_concat.sort_values(by='Symbol', ascending=True).to_csv(filepath, index = False)

