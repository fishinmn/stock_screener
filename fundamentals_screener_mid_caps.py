# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 08:36:15 2016

@author: efischer
"""
import pandas as pd
import os
from investing_functions import *

pd.set_option("display.max_colwidth", 10000)
dir_path = os.path.dirname(os.path.realpath(__file__))
filepath = os.path.join(dir_path, 'data', 'nasdaq_screener_midcap.csv')#.csv
df = pd.read_csv(filepath, encoding='iso-8859-1')


df_with_score = df_filter_fundamentals(df)
df_with_score = df_with_score[['Symbol',  'longName', 'sector', 'industry', 'industryKey', 'marketCap', 'priceToSalesTrailing12Months', 'currentRatio', 'quickRatio', 'revenueGrowth', 'grossMargins', 'trailingPE', 'forwardPE', 'PS_adj', 'pegRatio', 'dividendYield', 'earningsGrowth', 'profitMargins',  'shortPercentOfFloat', 'pegRatio', 'score']]

filepath = os.path.join(dir_path, 'data', 'fundamentals_screener_mid_caps.csv')
df_with_score.sort_values(by='score', ascending=False).to_csv(filepath, index = False)
