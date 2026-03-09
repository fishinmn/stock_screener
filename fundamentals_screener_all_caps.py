# -*- coding: utf-8 -*-
"""
Merged screener for all market cap categories
Combines: mega caps, large caps, mid caps, and small caps
Created on Fri Sep 16 08:36:15 2016

@author: efischer
"""
import pandas as pd
import numpy as np
import os
from investing_functions import *

pd.set_option("display.max_colwidth", 10000)
dir_path = os.path.dirname(os.path.realpath(__file__))

# Define screener configurations for each market cap category
screeners = [
    {
        'name': 'Mega Caps',
        'input_file': 'nasdaq_screener_megacap.csv',
        'output_file': 'fundamentals_screener_mega_caps.csv'
    },
    {
        'name': 'Large Caps',
        'input_file': 'nasdaq_screener_lrgcap.csv',
        'output_file': 'fundamentals_screener_large.csv'
    },
    {
        'name': 'Mid Caps',
        'input_file': 'nasdaq_screener_midcap.csv',
        'output_file': 'fundamentals_screener_mid_caps.csv'
    },
    {
        'name': 'Small Caps',
        'input_file': 'nasdaq_screener_smallcap_with_coverage.csv',
        'output_file': 'fundamentals_screener_small_cap.csv'
    }
]

# Columns to select
columns_to_keep = [
    'Symbol', 'longName', 'sector', 'industry', 'industryKey', 'marketCap',
    'priceToSalesTrailing12Months', 'currentRatio', 'quickRatio', 'revenueGrowth',
    'grossMargins', 'trailingPE', 'forwardPE', 'PS_adj', 'pegRatio', 'dividendYield',
    'earningsGrowth', 'profitMargins', 'shortPercentOfFloat', 'roe', 'score'
]

# Process each screener
for screener in screeners:
    print(f"Processing {screener['name']}...")
    
    # Read input CSV
    input_filepath = os.path.join(dir_path, 'data', screener['input_file'])
    df = pd.read_csv(input_filepath, encoding='iso-8859-1')
    
    # Filter fundamentals and score
    df_with_score = df_filter_fundamentals(df)
    
    # Select relevant columns
    df_with_score = df_with_score[columns_to_keep]
    
    # Sort by score and save output
    output_filepath = os.path.join(dir_path, 'data', screener['output_file'])
    df_with_score.sort_values(by='score', ascending=False).to_csv(output_filepath, index=False)
    
    print(f"  Saved {len(df_with_score)} records to {screener['output_file']}")

print("All screeners completed successfully!")
