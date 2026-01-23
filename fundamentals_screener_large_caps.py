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
from investing_functions import *

pd.set_option("display.max_colwidth", 10000)
dir_path = os.path.dirname(os.path.realpath(__file__))
#filepath = os.path.join(dir_path, 'nasdaq_screener_1694542554936.csv')#all
filepath = os.path.join(dir_path, 'data', 'nasdaq_screener_lrgcap.csv')#.csv
#filepath = os.path.join(dir_path, 'nasdaq_screener_megacap.csv')#.csv
#filepath = os.path.join(dir_path, 'nasdaq_screener_midap.csv')#.csv
#filepath = os.path.join(dir_path, 'nasdaq_screener_smallcap_with_coverage.csv')#.csv
#filepath = os.path.join(dir_path, 'nasdaq_screener_microcap_with_coverage.csv')#.csv
df = pd.read_csv(filepath, encoding='iso-8859-1')
#ticker_list = ['msft', 'mrna', 'isrg']
#ticker_list = ['envx', 'isrg', 'apps', 'fl', 'pypl', 'pton', 'spsc', 'smar', 'cwh', 'dks', 'wday', 'splk', 'mndy', 'zura', 'mrk', 'mrna', 'cgem', 'ostk', 'tgt', 'usb', 'baba', 'goog','grvy', 'bcc',  't', 'gtn', 'kr', 'powi', 'prim', 'mth', 'stc', 'intc', 'hzo', 'flgt', 'erii', 'swbi',  'lad', 'hear', 'amkr', 'hd', 'cvna', 'maxn', 'enph', 'arry', 'csiq', 'fitb', 'sedg', 'tan', 'fslr', 'meli', 'msft', 'amzn', 'para', 'coke', 'fis', 'dis', 'frg', 'big', 'bcpc', 'xbi', 'djd', 'mttr', 'nxst', 'ftai', 'cgnx', 'rcl', 'meta', 'nflx', 'nvda', 'tsla', 'mmm', 'kre', 'dlhc', 'brt', 'kmx', 'aapl', 'bki', 'f', 'tm', 'hibb', 'shop', 'asx', 'pdex', 'gis', 'mrna', 'qrtea', 'an', 'dci', 'bah', 'adus']
#df = pd.DataFrame(ticker_list,columns=['Symbol'])

df_with_score = df_filter_fundamentals(df)
df_with_score = df_with_score[['Symbol',  'longName', 'sector', 'industry', 'industryKey', 'marketCap', 'priceToSalesTrailing12Months', 'currentRatio', 'quickRatio', 'revenueGrowth', 'grossMargins', 'trailingPE', 'forwardPE', 'PS_adj', 'pegRatio', 'dividendYield', 'earningsGrowth', 'profitMargins',  'shortPercentOfFloat', 'pegRatio', 'score']]

filepath = os.path.join(dir_path, 'data', 'fundamentals_screener_large.csv')
df_with_score.sort_values(by='score', ascending=False).to_csv(filepath, index = False)
