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
import yahooquery as yq
import traceback
from finta import TA as ta
import plotly.graph_objects as go
import matplotlib
import matplotlib.pyplot as plt 
import mplfinance as mpf 
import requests
from datetime import timedelta
import pickle
import boto3
from html_functions import *
import datetime
import random
import matplotlib.dates as mdates 
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from unidecode import unidecode
import re
from sklearn.preprocessing import MinMaxScaler
import math
from botocore.exceptions import ClientError
import traceback
from bs4 import BeautifulSoup
import pytz
import plotly.express as px
import plotly.subplots as sp

def remove_non_ascii(text):
    return unidecode(text)

matplotlib.use('Agg')

def convert_alpaca_date_to_yf_date(utc_date):
    utc_date = datetime.datetime.strptime(utc_date, "%Y-%m-%dT%H:%M:%SZ")
    utc_date = utc_date.replace(tzinfo=pytz.UTC)
    et_tz = pytz.timezone('US/Eastern')
    et_date = utc_date.astimezone(et_tz)
    formatted_date = et_date.strftime("%Y-%m-%d %H:%M:%S%z")
    return formatted_date

def convert_to_mpf_date(dt):
    """
    Convert a datetime (with or without time/timezone) to a date-only,
    timezone-naive pandas.Timestamp for use as index in mpf.plot().
    """

    # Convert to pandas.Timestamp if not already
    ts = pd.Timestamp(dt)
    # Remove timezone if present
    if ts.tzinfo is not None:
        ts = ts.tz_convert(None)
    # Normalize to midnight (removes time part)
    ts = ts.normalize()
    return ts

def add_1month(date_str):
    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    new_date_obj = date_obj + timedelta(days=30)  # Approximate 30 days per month
    new_date_str = new_date_obj.strftime("%Y-%m-%d")
    return new_date_str

def upload_html_to_aws_from_file_dirpath(file_name_html, bucketname):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'html', file_name_html)
    #this will move in bat file to html folder

    #bucketname = "data.fuzzyforrest.ai"
    #s3 = boto3.resource('s3')
    #data = open(file_name, 'rb')
    #s3.Bucket(bucketname).put_object(Key=file_name_html, Body=data)
    s3 = boto3.client('s3')
    s3.upload_file(filepath, bucketname, file_name_html)
    s3.put_object_acl(Bucket=bucketname, Key=file_name_html, ACL='public-read')
    s3 = boto3.resource('s3')
    s3_object = s3.Object(bucketname, file_name_html)
    #s3_object.metadata.update({'Content-Type':'text/html'})
    s3_object.copy_from(CopySource={'Bucket': bucketname,
                                'Key': file_name_html},
                    MetadataDirective="REPLACE",
                    ContentType="text/html",
                    ACL='public-read')



def get_ticker_history(symbol, period_value, interval_value):
    the_ticker = yf.Ticker(symbol)
    #df = the_ticker.history()
    df = the_ticker.history(period=period_value, interval=interval_value, rounding ="True")
    return df
#https://aroussi.com/post/python-yahoo-finance

def get_daily_alpaca_data_as_df(symbol, date_field):
    try:
        secrets = get_secrets()
        url = f"https://data.alpaca.markets/v2/stocks/bars?symbols={symbol}&timeframe=1D&start={date_field}&end={add_1month(date_field)}&limit=1000&adjustment=raw&feed=sip&sort=asc"
        headers = {
            "accept": "application/json",
            "APCA-API-KEY-ID": secrets['ALPACA_GMAIL_KEY'],
            "APCA-API-SECRET-KEY": secrets['ALPACA_GMAIL_SECRET_KEY']
        }
        response = requests.get(url, headers=headers)
        list_dicts = response.json()['bars'][symbol]
        df = pd.DataFrame(list_dicts)
        df['Date'] = df['t'].apply(convert_alpaca_date_to_yf_date)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        df.rename(columns={'o': 'Open', 'h': 'High', 'l': 'Low', 'c': 'Close', 'v': 'Volume'}, inplace=True)
        df['Dividends'] = 0.0
        df['Stock Splits'] = 0.0
        columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
        df = df[columns]
        return df
    except Exception as e:
        print(e)
        
#save_algo10_early_winners

def get_daily_alpaca_data_as_df_all(symbol, date_field):
    try:
        secrets = get_secrets()
        url = f"https://data.alpaca.markets/v2/stocks/bars?symbols={symbol}&timeframe=1D&start={date_field}&limit=1000&adjustment=raw&feed=sip&sort=asc"
        headers = {
            "accept": "application/json",
            "APCA-API-KEY-ID": secrets['ALPACA_GMAIL_KEY'],
            "APCA-API-SECRET-KEY": secrets['ALPACA_GMAIL_SECRET_KEY']
        }
        response = requests.get(url, headers=headers)
        list_dicts = response.json()['bars'][symbol]
        df = pd.DataFrame(list_dicts)
        df['Date'] = df['t'].apply(convert_alpaca_date_to_yf_date)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        df.rename(columns={'o': 'Open', 'h': 'High', 'l': 'Low', 'c': 'Close', 'v': 'Volume'}, inplace=True)
        df['Dividends'] = 0.0
        df['Stock Splits'] = 0.0
        columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
        df = df[columns]
        print(df)
        return df
    except Exception as e:
        print(e)


def get_daily_alpaca_data_as_df_all_new(symbol, date_field):
    try:
        secrets = get_secrets()
        url = f"https://data.alpaca.markets/v2/stocks/bars?symbols={symbol}&timeframe=1D&start={date_field}&limit=1000&adjustment=raw&feed=sip&sort=asc"
        headers = {
            "accept": "application/json",
            "APCA-API-KEY-ID": secrets['ALPACA_GMAIL_KEY'],
            "APCA-API-SECRET-KEY": secrets['ALPACA_GMAIL_SECRET_KEY']
        }
        response = requests.get(url, headers=headers)
        list_dicts = response.json()['bars'][symbol]
        df = pd.DataFrame(list_dicts)
        df['Date'] = df['t'].apply(convert_to_mpf_date)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        df.rename(columns={'o': 'Open', 'h': 'High', 'l': 'Low', 'c': 'Close', 'v': 'Volume'}, inplace=True)
        df['Dividends'] = 0.0
        df['Stock Splits'] = 0.0
        columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
        df = df[columns]
        print(df)
        return df
    except Exception as e:
        print(e)

def get_ticker_history_offset(symbol, period_value, interval_value, start):
    the_ticker = yf.Ticker(symbol)
    #df = the_ticker.history()
    df = the_ticker.history(period=period_value, interval=interval_value, start = start, rounding ="True")
    return df

def get_ticker_history_offset_new(symbol, period_value, interval_value, start):
    the_ticker = yf.Ticker(symbol)
    #df = the_ticker.history()
    df = the_ticker.history(period=period_value, interval=interval_value, start = start, rounding ="True")
    return df

def get_ticker_history_offset_return(symbol, period_value, interval_value, start):
    the_ticker = yf.Ticker(symbol)
    #df = the_ticker.history()
    df = the_ticker.history(period=period_value, interval=interval_value, start = start, rounding ="True")
    pct_return = (df.tail(1)['Close'].values[0] - df.head(1)['Close'].values[0])/df.head(1)['Close'].values[0]
    return pct_return

def get_ticker_history_offset_30d_details(symbol, interval_value, start):
    the_ticker = yf.Ticker(symbol)
    #df = the_ticker.history()
    current_time = datetime.datetime.now()
    today_date = current_time.strftime("%Y-%m-%d")  
    start_date = datetime.datetime.strptime(start, "%Y-%m-%d")
    date_30d = start_date + timedelta(days=39)
    date_30d_fmt = date_30d.strftime("%Y-%m-%d")
    if date_30d_fmt < today_date:
         end_date = date_30d_fmt
    else:
         end_date = today_date
    df = the_ticker.history(interval=interval_value, start = start, end = end_date, rounding ="True")
    #pct_return = (df.tail(1)['Close'].values[0] - df.head(1)['Close'].values[0])/df.head(1)['Close'].values[0]
    return df


def get_ticker_history_offset_5d_details(symbol, interval_value, start):
    the_ticker = yf.Ticker(symbol)
    #df = the_ticker.history()
    current_time = datetime.datetime.now()
    today_date = current_time.strftime("%Y-%m-%d")  
    start_date = datetime.datetime.strptime(start, "%Y-%m-%d")
    date_30d = start_date + timedelta(days=7)
    date_30d_fmt = date_30d.strftime("%Y-%m-%d")
    if date_30d_fmt < today_date:
         end_date = date_30d_fmt
    else:
         end_date = today_date
    df = the_ticker.history(interval=interval_value, start = start, end = end_date, rounding ="True")
    return df

def get_ticker_history_offset_3d_details(symbol, interval_value, start):
    the_ticker = yf.Ticker(symbol)
    #df = the_ticker.history()
    current_time = datetime.datetime.now()
    today_date = current_time.strftime("%Y-%m-%d")  
    start_date = datetime.datetime.strptime(start, "%Y-%m-%d")
    date_30d = start_date + timedelta(days=4)
    date_30d_fmt = date_30d.strftime("%Y-%m-%d")
    if date_30d_fmt < today_date:
         end_date = date_30d_fmt
    else:
         end_date = today_date
    df = the_ticker.history(interval=interval_value, start = start, end = end_date, rounding ="True")
    return df


def get_ticker_history_offset_1d_details(symbol, interval_value, start):
    the_ticker = yf.Ticker(symbol)
    #df = the_ticker.history()
    current_time = datetime.datetime.now()
    today_date = current_time.strftime("%Y-%m-%d")  
    start_date = datetime.datetime.strptime(start, "%Y-%m-%d")
    date_30d = start_date + timedelta(days=3)
    date_30d_fmt = date_30d.strftime("%Y-%m-%d")
    if date_30d_fmt < today_date:
         end_date = date_30d_fmt
    else:
         end_date = today_date
    df = the_ticker.history(interval=interval_value, start = start, end = end_date, rounding ="True")
    return df

def get_ticker_history_offset_1d_details_try_again(symbol, interval_value, start):
    the_ticker = yf.Ticker(symbol)
    df = the_ticker.history(interval="1d", period="30d", start = start, rounding ="True")
    return df.iloc[0:2]

def get_ticker_history_offset_2d_details_try_again(symbol, interval_value, start):
    the_ticker = yf.Ticker(symbol)
    df = the_ticker.history(interval="1d", period="30d", start = start, rounding ="True")
    return df.iloc[0:3]

def get_ticker_history_offset_3d_details_try_again(symbol, interval_value, start):
    the_ticker = yf.Ticker(symbol)
    df = the_ticker.history(interval="1d", period="30d", start = start, rounding ="True")
    return df.iloc[0:4]

def get_ticker_history_offset_1y_details_try_again(symbol, interval_value, start):
    the_ticker = yf.Ticker(symbol)
    df = the_ticker.history(interval="1d", period="1y", start = start, rounding ="True")
    return df

def get_ticker_history_offset_x_days(symbol, interval_value, start, x_days):
    the_ticker = yf.Ticker(symbol)
    df = the_ticker.history(interval="1d", period="30d", start = start, rounding ="True")
    x_days = x_days + 1
    df = df.iloc[0:x_days]
    return df

def get_ticker_history_offset_5d_details_try_again(symbol, interval_value, start):
    the_ticker = yf.Ticker(symbol)
    df = the_ticker.history(interval="1d", period="30d", start = start, rounding ="True")
    return df.iloc[0:6]

def get_ticker_history_offset_0d_details(symbol, interval_value, start):
    the_ticker = yf.Ticker(symbol)
    #df = the_ticker.history()
    current_time = datetime.datetime.now()
    today_date = current_time.strftime("%Y-%m-%d")  
    start_date = datetime.datetime.strptime(start, "%Y-%m-%d")
    date_30d = start_date + timedelta(days=2)
    date_30d_fmt = date_30d.strftime("%Y-%m-%d")
    if date_30d_fmt < today_date:
         end_date = date_30d_fmt
    else:
         end_date = today_date
    df = the_ticker.history(interval=interval_value, start = start, end = end_date, rounding ="True")
    return df

def get_roe(symbol):
    try:
        ticker = yf.Ticker(symbol)  # Example: Apple Inc.

        # Get financial statements
        income_statement = ticker.income_stmt
        balance_sheet = ticker.balance_sheet

        balance_sheet.to_csv('balance_sheet.csv')
        # Extract Net Income and Shareholder's Equity
        net_income = income_statement.loc['Net Income', :].iloc[0]  # Get the most recent value
        shareholders_equity = balance_sheet.loc['Common Stock Equity', :].iloc[0]

        
        # Calculate ROE
        roe = (net_income / shareholders_equity) * 100  # Express as a percentage
        return roe
    except Exception as e:
        print("oops roe:  ", e)
        traceback.print_exc() 
        return 0


def get_next_business_day(date):
  #from Google labs genai
  """Returns the next business day given a date in "%Y-%m-%d" format."""
    # Example usage:
    #date = "2023-05-26"
    #next_business_day = get_next_business_day(date)
    #print(next_business_day)
  date = datetime.datetime.strptime(date, "%Y-%m-%d")

  # If the date is a Saturday or Sunday, return the next Monday.
  if date.weekday() == 5 or date.weekday() == 6:
    return date + datetime.timedelta(days=2)

  # If the date is a holiday, return the next business day.
  # Here is a list of holidays in the United States:
  holidays = ["2023-01-02", "2023-05-29", "2023-07-04", "2023-09-04", "2023-11-23", "2023-12-25"]
  if date.strftime("%Y-%m-%d") in holidays:
    return date + datetime.timedelta(days=1)

  # Otherwise, return the next day.
  return date + datetime.timedelta(days=1)



def get_ticker_history_offset_30d_return(symbol, interval_value, start):
    try:
        the_ticker = yf.Ticker(symbol)
        #df = the_ticker.history()
        current_time = datetime.datetime.now()
        today_date = current_time.strftime("%Y-%m-%d")  
        start_date = datetime.datetime.strptime(start, "%Y-%m-%d")
        date_30d = start_date + timedelta(days=30)
        date_30d_fmt = date_30d.strftime("%Y-%m-%d")
        if date_30d_fmt < today_date:
            end_date = date_30d_fmt
        else:
            end_date = today_date
        the_ticker.history()
        df = the_ticker.history(interval=interval_value, start = start, end = end_date, rounding ="True")
        pct_return = (df.tail(1)['Close'].values[0] - df.head(1)['Close'].values[0])/df.head(1)['Close'].values[0]
    except:
        pct_return = np.nan
    return pct_return

def get_ticker_history_offset_1d_return(symbol, interval_value, start):
    try:
        the_ticker = yf.Ticker(symbol)
        df = the_ticker.history(interval="1d", period = "30d", start = start, rounding ="True")
        pct_return = (df.iloc[1]['Close'] - df.iloc[1]['Open'])/df.iloc[1]['Open']
    except Exception as e:
        print(e)
        pct_return = np.nan
    return pct_return


def get_yesterday_string(date_string, format_string):
    """
    Converts a string date to yesterday's date string in the same format.

    Args:
        date_string: The string representing the date.
        format_string: The format of the date string (e.g. "%Y-%m-%d").

    Returns:
        A string representing yesterday's date.
    """

    # Convert the string to a datetime object
    date_object = datetime.datetime.strptime(date_string, format_string)

    # Calculate yesterday's date
    yesterday_date = date_object - timedelta(days=1)

    # Convert yesterday's date back to a string
    yesterday_string = yesterday_date.strftime(format_string)

    return yesterday_string


def days_until_10_percent_higher(df, pct):
    day1_open =df['Open'].iloc[0]
    day1_close =df['Close'].iloc[0]
#    day1_open = df.loc[0, 'Open']
#    day1_close = df.loc[0, 'Close']
    avg_day_1 = (day1_open + day1_close) / 2
    lowest_low = avg_day_1
    n=0
    length = len(df)
    for idx, row in df.iterrows():
        n = n + 1
        if lowest_low > row.Low:
            lowest_low = row.Low
        if row.High > (avg_day_1 * (1.00+pct)):
            break 
        else:
            print("Not yet at 10% gain")
    if n >= length:
        n = 999999
    drawdown = (lowest_low - avg_day_1)/avg_day_1
    return {"days_to_10pct": n, "drawdown": drawdown}



def get_ticker_history_days_to_10_pct(symbol, interval_value, start, pct):
    #problem was old approach got open to close.  Not prior close to close.
    #pct = .10
    try:
        print(start)
        print(type(start))
        the_ticker = yf.Ticker(symbol)
        the_ticker.history()
        df = the_ticker.history(interval="1d", period = "1y", start = get_yesterday_string(start, '%Y-%m-%d'), rounding ="True")
    except Exception as e:
        print(e)
        pct_return = np.nan
    return days_until_10_percent_higher(df, pct)

def get_ticker_history_offset_1d_high_return(symbol, interval_value, start):
    try:
        the_ticker = yf.Ticker(symbol)
        the_ticker.history()
        df = the_ticker.history(interval="1d", period = "30d", start = start, rounding ="True")
        pct_return = (df.iloc[1]['High'] - df.iloc[1]['Open'])/df.iloc[1]['Open']
    except Exception as e:
        print(e)
        pct_return = np.nan
        traceback.print_exc()
    return pct_return

def get_ticker_history_offset_1d_low_return(symbol, interval_value, start):
    try:
        the_ticker = yf.Ticker(symbol)
        the_ticker.history()
        df = the_ticker.history(interval="1d", period = "30d", start = start, rounding ="True")
        pct_return = (df.iloc[1]['Low'] - df.iloc[1]['Open'])/df.iloc[1]['Open']
    except Exception as e:
        print(e)
        pct_return = np.nan
        traceback.print_exc()
    return pct_return

def get_ticker_history_offset_2d_return(symbol, interval_value, start):
    try:
        the_ticker = yf.Ticker(symbol)
        print(the_ticker)
        df = the_ticker.history(interval="1d", period = "30d", start = start, rounding ="True")
        print(df)
        pct_return = (df.iloc[2]['Close'] - df.iloc[1]['Open'])/df.iloc[1]['Open']
    except Exception as e:
        print(e)
        pct_return = np.nan
        traceback.print_exc()
    return pct_return

def get_ticker_history_offset_3d_return(symbol, interval_value, start):
    try:
        the_ticker = yf.Ticker(symbol)
        print(the_ticker)
        df = the_ticker.history(interval="1d", period = "30d", start = start, rounding ="True")
        print(df)
        pct_return = (df.iloc[3]['Close'] - df.iloc[1]['Open'])/df.iloc[1]['Open']
    except Exception as e:
        print(e)
        pct_return = np.nan
        traceback.print_exc()
    return pct_return

def get_ticker_history_offset_4d_return(symbol, interval_value, start):
    try:
        the_ticker = yf.Ticker(symbol)
        df = the_ticker.history(interval="1d", period = "30d", start = start, rounding ="True")
        pct_return = (df.iloc[4]['Close'] - df.iloc[1]['Open'])/df.iloc[1]['Open']
    except Exception as e:
        print(e)
        pct_return = np.nan
        traceback.print_exc()
    return pct_return

def get_ticker_history_offset_5d_return(symbol, interval_value, start):
    try:
        the_ticker = yf.Ticker(symbol)
        df = the_ticker.history(interval="1d", period = "30d", start = start, rounding ="True")
        pct_return = (df.iloc[5]['Close'] - df.iloc[1]['Open'])/df.iloc[1]['Open']
    except:
        pct_return = np.nan
    return pct_return

def get_ticker_history_offset_7d_return(symbol, interval_value, start):
    try:
        the_ticker = yf.Ticker(symbol)
        df = the_ticker.history(interval="1d", period = "30d", start = start, rounding ="True")
        pct_return = (df.iloc[7]['Close'] - df.iloc[1]['Open'])/df.iloc[1]['Open']
    except:
        pct_return = np.nan
    return pct_return

def get_ticker_history_offset_30d_return_top(symbol, interval_value, start):
    try:
        the_ticker = yf.Ticker(symbol)
        current_time = datetime.datetime.now()
        today_date = current_time.strftime("%Y-%m-%d")  
        start_date = datetime.datetime.strptime(start, "%Y-%m-%d")
        date_30d = start_date + timedelta(days=30)
        date_30d_fmt = date_30d.strftime("%Y-%m-%d")
        if date_30d_fmt < today_date:
            end_date = date_30d_fmt
        else:
            end_date = today_date
        df = the_ticker.history(interval=interval_value, start = start, end = end_date, rounding ="True")
        start_close = df.head(1)['Close'].values[0]
        df = df.sort_values(by='Close', ascending=False)
        max_close = df.head(1)['Close'].values[0]
        pct_return = (max_close - start_close)/start_close
    except:
        pct_return = np.nan
    return pct_return


def get_ticker_history_offset_30d_return_short_top(symbol, interval_value, start):
    try:
        the_ticker = yf.Ticker(symbol)
        #df = the_ticker.history()
        current_time = datetime.datetime.now()
        today_date = current_time.strftime("%Y-%m-%d")  
        start_date = datetime.datetime.strptime(start, "%Y-%m-%d")
        date_30d = start_date + timedelta(days=30)
        date_30d_fmt = date_30d.strftime("%Y-%m-%d")
        if date_30d_fmt < today_date:
            end_date = date_30d_fmt
        else:
            end_date = today_date
        the_ticker.history()
        df = the_ticker.history(interval=interval_value, start = start, end = end_date, rounding ="True")
        start_close = df.head(1)['Close'].values[0]
        df = df.sort_values(by='Close', ascending=True)
        max_close = df.head(1)['Close'].values[0]
        pct_return = (max_close - start_close)/start_close
    except:
        pct_return = np.nan
    return pct_return

# def get_ticker_history_offset_30d_return_top(symbol, interval_value, start):
#     the_ticker = yf.Ticker(symbol)
#     df = the_ticker.history()
#     df = df.sort_values(by='Close', ascending=False)

#     end_date = datetime.datetime.strftime(df['Close'].idxmax().to_pydatetime(), "%Y-%m-%d") 
#     max_close = 
#     df = the_ticker.history(interval=interval_value, start = start, end = end_date, rounding ="True")
# #    pct_return = (df.tail(1)['Close'].values[0] - df.head(1)['Close'].values[0])/df.head(1)['Close'].values[0]
#     pct_return = (max_close - df.head(1)['Close'].values[0])/df.head(1)['Close'].values[0]
#     return pct_return


def get_spy_1d_return():
    the_ticker = yf.Ticker('SPY')
    df = the_ticker.history(period='2d', interval='1d', rounding ="True")
    pct_return = (df.tail(1)['Close'].values[0] - df.head(1)['Close'].values[0])/df.head(1)['Close'].values[0]
    return pct_return


def get_info(symbol):
    the_ticker = yf.Ticker(symbol)
    return the_ticker.info
    #ex. get_info('msft')['longName']

def get_info2(symbol):
    the_ticker = yq.Ticker(symbol)
    return the_ticker
    #get_info2(x.ticker).summary_detail[list(get_info2(x.ticker).summary_detail)[0]].trailingPE
    #get_info2(x.ticker).summary_detail[list(get_info2(x.ticker).summary_detail)[0]].forwardPE
    #get_info2(x.ticker).summary_detail[list(get_info2(x.ticker).summary_detail)[0]].priceToSalesTrailing12Months
    #get_info2(x.ticker).summary_detail[list(get_info2(x.ticker).summary_detail)[0]].dividendYield

    #get_info2(x.ticker).financialData[list(get_info2(x.ticker).financialData)[0]].revenueGrowth
    #get_info2(x.ticker).financialData[list(get_info2(x.ticker).financialData)[0]].grossMargins
    #get_info2(x.ticker).financialData[list(get_info2(x.ticker).financialData)[0]].earningsGrowth
    #get_info2(x.ticker).financialData[list(get_info2(x.ticker).financialData)[0]].profitMargins

    #summary_detail = the_ticker.summary_detail[list(yq_data.summary_detail)[0]]         
    #summary_detail = the_ticker.summary_detail[list(yq_data.summary_detail)[0]].trailingPE       
                #summaryDetail.trailingPE 
                #summaryDetail.forwardPE     
                #summaryDetail.priceToSalesTrailing12Months 
                #summaryDetail.dividendYield 
    #financialData = yq_data.financial_data[list(yq_data.financial_data)[0]]
                #financialData.revenueGrowth
                #financialData.grossMargins
                #financialData.earningsGrowth
                #financialData.profitMargins
    #indexTrend = yq_data.index_trend[list(yq_data.index_trend)[0]]
                #indexTrend.pegRatio 
    #defaultKeyStatistics = yq_data.key_stats[list(yq_data.key_stats)[0]]
                #defaultKeyStatistics.shortPercentOfFloat

def get_trialingPE(symbol):
    the_ticker = yq.Ticker(symbol)
    the_ticker_summary_detail = the_ticker.price[list(the_ticker.summary_detail)[0]]
    return the_ticker_summary_detail['trailingPE']

def get_bid(symbol):
    the_ticker = yf.Ticker(symbol)
    return the_ticker.info['bid']

def get_ask(symbol):
    the_ticker = yf.Ticker(symbol)
    return the_ticker.info['ask']

def get_open(symbol):
    the_ticker = yf.Ticker(symbol)
    return the_ticker.info['open']

def get_currentPrice(symbol):
    the_ticker = yf.Ticker(symbol)
    return the_ticker.info['currentPrice']



def get_company_name(symbol):
    #the_ticker = yq.Ticker(symbol)
    #the_ticker_price = the_ticker.price[list(the_ticker.price)[0]]
    try:
        print("trying to get company name")
        print(symbol)
        the_ticker = yf.Ticker(symbol)
        return the_ticker.info['longName']
    except Exception as e:
        print(e)
        return "asdfsdfsdfsdf"


def get_summary(symbol):
    try:
        print("trying to get company summary")
        print(symbol)
        the_ticker = yf.Ticker(symbol)
        result = the_ticker.info['longBusinessSummary']
        bytes_str = result.encode('utf-8', errors='ignore')
        new_str = bytes_str.decode('utf-8')
        #new_str = new_str.replace(r"[^a-zA-Z0-9]","")
        new_str = re.sub('[^a-zA-Z0-9]','', new_str)
        return new_str
    except Exception as e:
        print(e)
        return "asdfsdfsdfsdf"
    
def get_earnings_dates(ticker):
    data = yf.Ticker(ticker)
    # get stock info
    #msft.info
    #print (msft.info)
    earnings_dates = data.get_earnings_dates()
    print(earnings_dates)
    earnings_dates_last_date = earnings_dates[earnings_dates['Reported EPS'].notnull()].index[0].to_pydatetime()#.strftime('%Y-%m-%d')
    earnings_dates_next_date = earnings_dates[earnings_dates['EPS Estimate'].notnull()].index[0].to_pydatetime()
    start_date_1 = earnings_dates_last_date + timedelta(days=1)
    start_date_2 = earnings_dates_last_date + timedelta(days=2)
    start_date_3 = earnings_dates_last_date + timedelta(days=3)
    end_date = earnings_dates_next_date - timedelta(days=10)
    return earnings_dates


def get_days_to_earnings(ticker):
    data = yf.Ticker(ticker)
    earnings_dates = data.get_earnings_dates()
    earnings_dates_next_date = earnings_dates[earnings_dates['EPS Estimate'].notnull()].index[0].to_pydatetime()
    today = datetime.date.today()
    earnings_dates_next_date = earnings_dates_next_date.date()
    weekdays_between = 0
    current_date = today
    while current_date <= earnings_dates_next_date:
        # Check if the current day is a weekday and increment the counter
        if current_date.weekday() < 5:  # Weekday numbers are 0 (Monday) to 4 (Friday)
            weekdays_between += 1
        # Move to the next day
        current_date += timedelta(days=1)
    return weekdays_between

def get_days_to_earnings_given_date(earnings_dates_next_date, current_date):
    #earnings_dates_next_date = earnings_dates_next_date.date()
    weekdays_between = 0
    while current_date <= earnings_dates_next_date:
        # Check if the current day is a weekday and increment the counter
        if current_date.weekday() < 5:  # Weekday numbers are 0 (Monday) to 4 (Friday)
            weekdays_between += 1
        # Move to the next day
        current_date += timedelta(days=1)
    return weekdays_between

def get_days_to_earnings_in_df(ticker, df):
    data = yf.Ticker(ticker)
    earnings_dates = data.get_earnings_dates()
    earnings_dates_next_date = earnings_dates[earnings_dates['EPS Estimate'].notnull()].index[0].to_pydatetime()
    earnings_dates_next_date = earnings_dates_next_date.date()
    print(earnings_dates_next_date)
    df['days_until_earnings'] = df['date_field'].map(lambda x: get_days_to_earnings_given_date(earnings_dates_next_date, x))
    return df

def get_days_to_friday_given_date(today):
    days_until_friday = (4 - today.weekday()) % 7
    days_until_friday = 7 if days_until_friday == 0 else days_until_friday
    return days_until_friday

def get_days_to_friday_given_date_normalized(today):
    days_until_friday = (4 - today.weekday()) % 7
    days_until_friday = 7 if days_until_friday == 0 else days_until_friday
    days_until_friday = days_until_friday / 5
    return days_until_friday

def investor_sentiment():
    with open('C:/git/stock_analysis_app/fng_cnn_data.pickle', 'rb') as handle:
        response = pickle.load(handle)
    return response

def spotgamma_hiro_tickers():
    with open('C:/git/stock_analysis_app/most_traded_tickers.pickle', 'rb') as handle:
        response = pickle.load(handle)
    return response

def get_secrets():
    #dir_path = os.path.dirname(os.path.realpath(__file__))
    #filepath = os.path.join(dir_path, 'secret_stock_analysis_app.pickle')#.csv
    with open('C:/git/secret_stock_analysis_app.pickle', 'rb') as handle:
        response = pickle.load(handle)
    # print(response['SPOTGAMMA_USERNAME'])
    # print(response['SPOTGAMMA_PWD'])
    # print(response['ALPACA_PAPER_GMAIL_KEY'])
    # print(response['ALPACA_PAPER_GMAIL_SECRET_KEY'])
    return response

def save_algo10_early_winners(the_list):
    with open('C:/git/early_winners_algo10.pickle', 'wb') as handle:
        pickle.dump(the_list, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return None

def get_algo10_early_winners():
    with open('C:/git/early_winners_algo10.pickle', 'rb') as handle:
        response = pickle.load(handle)
    return response

def get_fng_df():
    fear_and_greed_historical_data = investor_sentiment()["fear_and_greed_historical"]['data']
    fng_list = []
    for i in fear_and_greed_historical_data:
        fng_list.append(round(i["y"], 0))
    df = pd.DataFrame.from_records(fear_and_greed_historical_data)
    df = df.head(-1)
    df['x'] = pd.to_datetime(df['x'], unit='ms')
    return df

#list_lists = ['fear_and_greed_historical', 'market_momentum_sp500', 'market_momentum_sp125', 'stock_price_strength', 'stock_price_breadth', 'put_call_options', 'market_volatility_vix', 'market_volatility_vix_50', 'junk_bond_demand', 'safe_haven_demand']
def get_fng_market_momentum_sp500():
    fear_and_greed_historical_data = investor_sentiment()["market_momentum_sp500"]['data']
    fng_list = []
    for i in fear_and_greed_historical_data:
        fng_list.append(round(i["y"], 0))
    df = pd.DataFrame.from_records(fear_and_greed_historical_data)
    df = df.head(-1)
    df['x'] = pd.to_datetime(df['x'], unit='ms')
    return df

def get_fng_market_momentum_sp125():
    fear_and_greed_historical_data = investor_sentiment()["market_momentum_sp125"]['data']
    fng_list = []
    for i in fear_and_greed_historical_data:
        fng_list.append(round(i["y"], 0))
    df = pd.DataFrame.from_records(fear_and_greed_historical_data)
    df = df.head(-1)
    df['x'] = pd.to_datetime(df['x'], unit='ms')
    return df

def get_fng_stock_price_strength():
    fear_and_greed_historical_data = investor_sentiment()["stock_price_strength"]['data']
    fng_list = []
    for i in fear_and_greed_historical_data:
        fng_list.append(round(i["y"], 0))
    df = pd.DataFrame.from_records(fear_and_greed_historical_data)
    df = df.head(-1)
    df['x'] = pd.to_datetime(df['x'], unit='ms')
    return df

def get_fng_stock_price_breadth():
    fear_and_greed_historical_data = investor_sentiment()["stock_price_breadth"]['data']
    fng_list = []
    for i in fear_and_greed_historical_data:
        fng_list.append(round(i["y"], 0))
    df = pd.DataFrame.from_records(fear_and_greed_historical_data)
    df = df.head(-1)
    df['x'] = pd.to_datetime(df['x'], unit='ms')
    return df

def get_fng_put_call_options():
    fear_and_greed_historical_data = investor_sentiment()["put_call_options"]['data']
    fng_list = []
    for i in fear_and_greed_historical_data:
        fng_list.append(round(i["y"], 0))
    df = pd.DataFrame.from_records(fear_and_greed_historical_data)
    df = df.head(-1)
    df['x'] = pd.to_datetime(df['x'], unit='ms')
    return df

def get_fng_junk_bond_demand():
    fear_and_greed_historical_data = investor_sentiment()["junk_bond_demand"]['data']
    fng_list = []
    for i in fear_and_greed_historical_data:
        fng_list.append(round(i["y"], 0))
    df = pd.DataFrame.from_records(fear_and_greed_historical_data)
    df = df.head(-1)
    df['x'] = pd.to_datetime(df['x'], unit='ms')
    return df

def get_fng_safe_haven_demand():
    fear_and_greed_historical_data = investor_sentiment()["safe_haven_demand"]['data']
    fng_list = []
    for i in fear_and_greed_historical_data:
        fng_list.append(round(i["y"], 0))
    df = pd.DataFrame.from_records(fear_and_greed_historical_data)
    df = df.head(-1)
    df['x'] = pd.to_datetime(df['x'], unit='ms')
    return df

def appendData(maindf, dataarray, namesarray=None):
    if namesarray==None:
        return maindf.join(pd.DataFrame(dataarray), how='outer')
    return maindf.join(pd.DataFrame(dataarray,columns=namesarray), how='outer')


def add_ml_indicators(ticker_history):
    df = ticker_history
    sma_ema_averages = [50, 200]
    for i in sma_ema_averages:
        df = appendData(df,ta.EMA(df, i))
    df = appendData(df,ta.ADX(df))
    df = appendData(df,ta.STOCH(df))
    df = appendData(df,ta.RSI(df))
    df = appendData(df,ta.BBANDS(df))
    df = appendData(df,ta.BBWIDTH(df))
    return df

def explore_indicators(ticker_history):
    df = ticker_history
    sma_ema_averages = [50, 200]
    df = appendData(df,ta.MACD(df))
    for i in sma_ema_averages:
        df = appendData(df,ta.EMA(df, i))
#    df = appendData(df,ta.MOBO(df))#AttributeError: 'int' object has no attribute 'lower'
#    df = appendData(df,ta.WILLIAMS(df))
#    df = appendData(df,ta.KST(df))
#    df = appendData(df,ta.PIVOT_FIB(df))
    df = appendData(df,ta.DMI(df))
    df = appendData(df,ta.ADX(df))
#    df = appendData(df,ta.QSTICK(df))
#    df = appendData(df,ta.VORTEX(df))    
    df = appendData(df,ta.KC(df)) #results are KC_UPPER adn KC_LOWER
    df = appendData(df,ta.STOCH(df))
    df = appendData(df,ta.RSI(df))
#    df = appendData(df,ta.EFI(df))
#    df = appendData(df,ta.EBBP(df))
    df = appendData(df,ta.BBANDS(df))
    df = appendData(df,ta.BBWIDTH(df))
#    df = appendData(df,ta.VW_MACD(df))

    df = appendData(df,ta.SAR(df)) #if above SAR, 
    df['SAR'] = df[0]
    df = df.drop(0, axis=1)

#    df = appendData(df,ta.PSAR(df)) #do not use.  Causes missing values to be dropped and is worthless anyway
    df = appendData(df,ta.WILLIAMS_FRACTAL(df))
    df = appendData(df,ta.PIVOT(df))
    df = appendData(df,ta.MFI(df))
    return df


def simon_ree_flag(ticker, ticker_history):
    df = ticker_history
    sma_ema_averages = [8,21,34,55,89, 200]
    for i in sma_ema_averages:
        df = appendData(df,ta.EMA(df, i))
    ## ADX
    df = appendData(df,ta.ADX(df))
    ## DMI (Added to aid in interpreting ADX)
    df = appendData(df,ta.DMI(df, 14))
    ## Sto-%K
    df = appendData(df,ta.STOCH(df))
    
    row = df.iloc[-1]

    try:
        if row['8 period EMA'] > row['21 period EMA'] and row['21 period EMA'] > row['34 period EMA'] and row['34 period EMA'] > row['55 period EMA'] and row['55 period EMA'] > row['89 period EMA']:
            trend = 'Yes'
            if row['14 period ADX.'] > 20:
                trend = 'Yes and confirmed'
            else:
                pass
        else:
            trend = 'No'
            if row['14 period ADX.'] > 20:
                trend = 'No, but ADX diagrees'
            else:
                pass
        if row['14 period STOCH %K'] < 40:
            oscillator = "Buy the dip"
        else:
            oscillator = "Wait for pull back"
    except Exception as e:
        print("oops:  ", e)
        traceback.print_exc()   
    
    trend_analysis_results = row.to_list()
    trend_analysis_results.append(trend)
    trend_analysis_results.append(oscillator)
    trend_analysis_results.insert(0,ticker)
    return trend_analysis_results


def checkTrend(ticker, ticker_history):
    df = ticker_history
    sma_ema_averages = [8,21,34,55,89, 200]
    for i in sma_ema_averages:
        df = appendData(df,ta.EMA(df, i))
    ## ADX
    df = appendData(df,ta.ADX(df))
    ## DMI (Added to aid in interpreting ADX)
    df = appendData(df,ta.DMI(df, 14))
    ## Sto-%K
    df = appendData(df,ta.STOCH(df))
    
    row = df.iloc[-1]

    try:
        if row['8 period EMA'] > row['21 period EMA'] and row['21 period EMA'] > row['34 period EMA'] and row['34 period EMA'] > row['55 period EMA'] and row['55 period EMA'] > row['89 period EMA']:
            trend = 'Yes'
            if row['14 period ADX.'] > 20:
                trend = 'Yes and confirmed'
            else:
                pass
        else:
            trend = 'No'
            if row['14 period ADX.'] > 20:
                trend = 'No, but ADX diagrees'
            else:
                pass
        if row['14 period STOCH %K'] < 40:
            oscillator = "Buy the dip"
        else:
            oscillator = "Wait for pull back"
    except Exception as e:
        print("oops:  ", e)   
        traceback.print_exc()
    trend_analysis_results = row.to_list()
    trend_analysis_results.append(trend)
    trend_analysis_results.append(oscillator)
    trend_analysis_results.insert(0,ticker)
    return trend_analysis_results


def macd_crossover(df):
#    df = appendData(df,ta.MACD(df))
    df['MACD_DIFF'] = df['MACD'] - df['SIGNAL']
    df['first'] = df['MACD_DIFF'].shift(1) #yesterday's MACD_DIFF
    df['last'] = df['MACD_DIFF']#today's MACD_DIFF
#    df['first'] = df['MACD_DIFF'].rolling(2).agg(lambda rows: rows[0])
#    df['last']  = df['MACD_DIFF'].rolling(2).agg(lambda rows: rows[-1])
    df['BULLISH_MACD_CROSSOVER']  = df.apply(lambda row: 1 if row['first'] <= 0 and row['last'] > 0 else 0, axis=1)
    df['BEARISH_MACD_CROSSOVER']  = df.apply(lambda row: 1 if row['first'] >= 0 and row['last'] < 0 else 0, axis=1)
    df = df.drop('MACD_DIFF', axis=1)
    df = df.drop('first', axis=1)
    df = df.drop('last', axis=1)
    df = df.drop('MACD', axis=1)
    df = df.drop('SIGNAL', axis=1)
    return df

def screenerTrend(ticker_list):
    trend_stocks_list = []
    for ticker in ticker_list:
        ticker_history = get_ticker_history(ticker, '1y', '1d')
        checkResult = checkTrend(ticker, ticker_history)
        # trend_stocks_list.append(ticker)
        trend_stocks_list.append(checkResult)
        # if checkResult[-2] == 'Yes' or checkResult[-2] == 'Yes and confirmed':
        #     trend_stocks_list.append(checkResult)
        # else:
        #     pass
    return trend_stocks_list

def get_fractals_levels(df):
    supports = df[df.Low == df.Low.rolling(5, center=True).min()].Low
    resistances = df[df.High == df.High.rolling(5, center=True).max()].High
    levels = pd.concat([supports,resistances])
    levels = levels[abs(levels.diff()) > (df.Close.iat[-1] *.10)].to_list()
    levels = [float(i) for i in levels]
    levels = [ '%.2f' % elem for elem in levels]
    return levels


def fib_retrace(df):
    highest_swing = -1
    lowest_swing = -1
    for i in range(1,df.shape[0]-1):
        if df['High'][i] > df['High'][i-1] and df['High'][i] > df['High'][i+1] and (highest_swing == -1 or df['High'][i] > df['High'][highest_swing]):
            highest_swing = i
        if df['Low'][i] < df['Low'][i-1] and df['Low'][i] < df['Low'][i+1] and (lowest_swing == -1 or df['Low'][i] < df['Low'][lowest_swing]):
            lowest_swing = i
    ratios = [0,0.236, 0.382, 0.5 , 0.618, 0.786,1]
    colors = ["black","red","green","blue","cyan","magenta","yellow"]
    levels = []
    max_level = df['High'][highest_swing]#
    min_level = df['Low'][lowest_swing]
    for ratio in ratios:
        if highest_swing > lowest_swing: # Uptrend
            levels.append(max_level - (max_level-min_level)*ratio)
        else: # Downtrend
            levels.append(min_level + (max_level-min_level)*ratio)
    levels = [float(i) for i in levels]
    levels = [ '%.2f' % elem for elem in levels]
    return levels

def next_buy_level(price, levels):
    buy_level = 0
    levels = [float(i) for i in levels]
    #print (type(price))
    try: 
        for i in levels:
            #print (type(i))
            if price > i and i > buy_level: 
#            if price > i and i < buy_level: 
                buy_level = i
            else:
                pass
    except Exception as e:
        print(e)
        traceback.print_exc()
    return buy_level

def make_clickable_both(name, url): 
    return f'<a href="{url}">{name}</a>'

def bearish_reversal(df):
#from Simon Ree
#A bearish key reversal is a relatively uncommon technical analysis pattern that occurs when a bar opens above the previous bar's high and closes below the previous bar's low. It shows there was decent buying pressure at the open, but the bears eventually won the day and took price down.
#Bearish key reversals often lead to further downside momentum in price and when they occur at a swing high, they can help us identify potential turning points in the market.
#SPY recorded a bearish key reversal at its cycle high on 27th July. It recorded another one last Friday. This has short-term bearish implications for $SPY
#Eric note: I'm finding this is not very valuable by itself.  More false positives that not.
    bearish_reversal_dates = df[(df.High == df.High.rolling(2).max()) & (df.Close < df.Low.shift(periods = 1))].index
    return bearish_reversal_dates

def plot_ticker(ticker):
    #add other parameters later such as BB, fib, fractals, ema, etc
    df = get_ticker_history(ticker, '1y', '1d')
    df['Prior_Low'] = df.shift(1).Low
    #levels = get_fractals_levels(df)
    fib_levels = fib_retrace(df)
    #df = appendData(df,ta.PIVOT(df))
    sma_ema_averages = [50,200]
    for i in sma_ema_averages:
        df = appendData(df,ta.EMA(df, i))
    #levels_lists = fib_levels + levels
    levels_lists = [float(i) for i in fib_levels]
    #mpf.plot(df, type = 'candle', hlines=levels_lists, style='charles')
    #mpf.plot(df, type = 'candle', hlines=fib_levels, style='charles')
    emas = mpf.make_addplot(df[['200 period EMA', '50 period EMA']])
    #fifty = mpf.make_addplot(df['50 period EMA'])
    #ap = mpf.make_addplot(fib_levels)
    #colors=('r','g','b','c', 'm', 'y')
#    path = os.getcwd()
    path = os.path.dirname(os.path.realpath(__file__))
    filename = os.path.join(path, 'plots', f'{ticker}_plot.png')
    mpf.plot(df, type = 'candle', hlines=levels_lists, style='charles', addplot=emas, savefig=filename)
    #html_tag = f"""<img src='{filename}'  style="height: 200px;">"""
    #No, go.Table (from plotly.py) has a very different interface and does not support images in any way AFAIK. You can use a very limited subset of HTML in cell contents (<a>, <b>, <em>, <i>, <br>, <span>, <sub>, <sup>, with style attributes and href for <a>) but that's it.
#    path = "file:///C:/Users/fish_/"
#    filename = path + f'{ticker}_plot.png'
    print (filename)
    bucketname = "data.fuzzyforrest.ai"
    #s3 = boto3.resource('s3')
    #data = open(file_name, 'rb')
    #s3.Bucket(bucketname).put_object(Key=file_name, Body=data)

    s3 = boto3.client('s3')
    s3.upload_file(filename, bucketname, f'{ticker}_plot.png')

    #s3.put_object_acl(Body=bucketname, Key=f'{ticker}_plot.png', ACL='public-read')

    #update content type
    s3 = boto3.resource('s3')
    s3_object = s3.Object(bucketname, f'{ticker}_plot.png')
    s3_object.copy_from(
        CopySource={'Bucket': bucketname,'Key': f'{ticker}_plot.png'},
        MetadataDirective="REPLACE",
        ContentType='image/png',
        ACL='public-read'
    ) 

    return  filename


def plot_ticker_with_algo10_TA(ticker):
    """
    Plots the ticker's price chart (as in plot_ticker), and overlays Total_TA from all_stocks_section_history.csv as a line chart on a secondary Y axis.
    Saves as plots/{ticker}_plot_new.png and uploads to S3.
    """
    # --- Main price chart (same as plot_ticker) ---
    date_field = (datetime.datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    print (date_field)
    print (type(date_field))
    df = get_daily_alpaca_data_as_df_all_new(ticker, date_field)

    df.index = df.index.normalize()  # Normalize to remove time part, keeping only date

    #check data types
    print(df.dtypes)
    #df = get_ticker_history(ticker, '1y', '1d')
    df['Prior_Low'] = df.shift(1).Low
    fib_levels = fib_retrace(df)
    sma_ema_averages = [50, 200]
    for i in sma_ema_averages:
        df = appendData(df, ta.EMA(df, i))
    levels_lists = [float(i) for i in fib_levels]
    emas = mpf.make_addplot(df[['200 period EMA', '50 period EMA']])
    path = os.path.dirname(os.path.realpath(__file__))
    filename = os.path.join(path, 'plots', f'{ticker}_plot_new.png')

    # --- Algo10 TA overlay ---
    hist_csv = os.path.join(path, 'all_stocks_section_history.csv')
    hist_df = pd.read_csv(hist_csv)
    hist_df.columns = [c.strip() for c in hist_df.columns]
    ta_df = hist_df[hist_df['ticker'] == ticker]
    if ta_df.empty:
        print(f"No TA data for {ticker} in all_stocks_section_history.csv")
        ta_dates = []
        ta_values = []
    else:
        ta_dates = pd.to_datetime(ta_df['last_modified'])
        ta_values = ta_df['Total_TA']

    # --- Plot with secondary Y axis ---
    fig, ax1 = mpf.plot(
        df,
        type='candle',
        hlines=levels_lists,
        style='charles',
        addplot=emas,
        returnfig=True
    )
    ax2 = ax1[0].twinx()
    if len(ta_dates) > 0:
        ax2.plot(ta_dates, ta_values, color='orange', label='Total_TA', linewidth=2, alpha=0.7)
        ax2.set_ylabel('Total_TA', color='orange')
        ax2.tick_params(axis='y', labelcolor='orange')
    #ax1.xaxis.set_major_locator(mdates.MonthLocator())
    #ax1.xaxis.set_major_formatter(mdates.ConciseDateFormatter(mdates.MonthLocator()))
    fig.tight_layout()
    fig.savefig(filename)

    # --- S3 upload (same as plot_ticker) ---
    bucketname = "data.fuzzyforrest.ai"
    s3 = boto3.client('s3')
    s3.upload_file(filename, bucketname, f'{ticker}_plot_new.png')
    s3 = boto3.resource('s3')
    s3_object = s3.Object(bucketname, f'{ticker}_plot_new.png')
    s3_object.copy_from(
        CopySource={'Bucket': bucketname, 'Key': f'{ticker}_plot_new.png'},
        MetadataDirective="REPLACE",
        ContentType='image/png',
        ACL='public-read'
    )
    print(filename)
    return filename

def plot_ticker_with_algo10_TA_plotly(ticker):
    """
    Plots the price chart for the given ticker using plotly,
    and plots the Total_TA time series from all_stocks_section_history.csv
    as a line chart in a subplot below the price chart.
    """
    # --- Load price data ---
    df = get_ticker_history(ticker, '1y', '1d')
    # Ensure index is DatetimeIndex and timezone-naive
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    if getattr(df.index, 'tz', None) is not None:
        df.index = df.index.tz_localize(None)

    # --- Load TA history data ---
    path = os.path.dirname(os.path.realpath(__file__))
    hist_csv = os.path.join(path, 'all_stocks_section_history.csv')
    hist_df = pd.read_csv(hist_csv)
    print(hist_df.shape)
    print(hist_df)
    print(hist_df.columns)
    hist_df = hist_df[hist_df['ticker'] == ticker]  # Ensure ticker column is not null
    # Filter for ticker
    ta_df = hist_df[hist_df['ticker'].astype(str).str.upper() == ticker.upper()].copy()
    print(ta_df.shape)
    print(ta_df)
    if ta_df.empty:
        print(f"No TA data found for {ticker}")
        return
    # Parse last_modified as datetime and sort
    ta_df['last_modified'] = pd.to_datetime(ta_df['last_modified'], errors='coerce')
    ta_df = ta_df.dropna(subset=['last_modified', 'Total_TA'])
    ta_df = ta_df.sort_values('last_modified')
    print(ta_df)

    # --- Plotting with plotly ---
    fig = sp.make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                          row_heights=[0.7, 0.3],
                          subplot_titles=(f"{ticker} Price Chart", "Total_TA History"))

    # Candlestick chart for price
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            name='Price'),
        row=1, col=1
    )
    # TA line chart
    fig.add_trace(
        go.Scatter(
            x=ta_df['last_modified'],
            y=ta_df['Total_TA'],
            mode='lines+markers',
            name='Total_TA',
            line=dict(color='blue')
        ),
        row=2, col=1
    )
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Total_TA", row=2, col=1)
    fig.update_layout(height=800, width=1200, showlegend=False, title_text=f"{ticker} Price and Total_TA History")
    outname = os.path.join(path, 'plots', f"{ticker}_plot_new.png")
    fig.write_image(outname)
    print(f"Saved: {outname}")
    return outname



def plot_performance_1line_plotly(df, filename, label_my):
    #df.index = pd.to_datetime(df.index)
    # Create the line graph
    fig = px.line(df, x=df.index, y=df.values, title=label_my)

    # Customize the layout if needed
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Value',
        hovermode='x unified'
    )

    # Show the plot
    fig.write_image(filename)


def plot_performance_1line(my_df, my_df_daytrade, filename, label_my):
    myxpoints = my_df.index.values
    myypoints = my_df.values

    myxpoints_daytrade = my_df_daytrade.index.values
    myypoints_daytrade = my_df_daytrade.values


    plt.plot(myxpoints, myypoints, label = label_my) 
    plt.plot(myxpoints_daytrade, myypoints_daytrade, label = f"daytrade") 
    plt.title(f"Performance {label_my}")
    plt.ylabel("Cumulative Return %")
    plt.legend(loc="upper left")

    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'plots', filename)


    plt.Axes.set_autoscale_on
    locator = mdates.MonthLocator() 
    #locator = mdates.AutoDateLocator(minticks = 3, maxticks = 7) 
    formatter = mdates.ConciseDateFormatter(locator) 

    ax = plt.gca()
    ax.xaxis.set_major_locator(locator) 
    ax.xaxis.set_major_formatter(formatter) 
    plt.savefig(fname = filepath)

    bucketname = "data.fuzzyforrest.ai"

    s3 = boto3.client('s3')
    s3.upload_file(filepath, bucketname, filename)
    s3 = boto3.resource('s3')
    s3_object = s3.Object(bucketname, filename)
    s3_object.copy_from(
        CopySource={'Bucket': bucketname,'Key': filename},
        MetadataDirective="REPLACE",
        ContentType='image/png',
        ACL='public-read'
    ) 
    return  filename


def plot_performance_3line(my_df, my_df_daytrade, my_df_overnight, filename, label_my):
    myxpoints = my_df.index.values
    myypoints = my_df.values

    myxpoints_daytrade = my_df_daytrade.index.values
    myypoints_daytrade = my_df_daytrade.values

    myxpoints_overnight = my_df_overnight.index.values
    myypoints_overnight = my_df_overnight.values


    plt.plot(myxpoints, myypoints, label = label_my) 
    plt.plot(myxpoints_daytrade, myypoints_daytrade, label = f"daytrade") 
    plt.plot(myxpoints_overnight, myypoints_overnight, label = f"overnight") 
    plt.title(f"Performance {label_my}")
    plt.ylabel("Cumulative Return %")
    plt.legend(loc="upper left")

    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'plots', filename)


    plt.Axes.set_autoscale_on
    locator = mdates.YearLocator() 
    #locator = mdates.AutoDateLocator(minticks = 3, maxticks = 7) 
    formatter = mdates.ConciseDateFormatter(locator) 

    ax = plt.gca()
    ax.xaxis.set_major_locator(locator) 
    ax.xaxis.set_major_formatter(formatter) 
    plt.savefig(fname = filepath)

    return  filename


def plot_performance(my_df, benchmark_df, filename, label_my, label_benchmark):
    myxpoints = my_df.index.values
    myypoints = my_df.values

    spyxpoints = benchmark_df.index.values
    spyypoints = benchmark_df.values

    plt.plot(myxpoints, myypoints, label = label_my) 
    plt.plot(spyxpoints, spyypoints, label = label_benchmark)     
    plt.title("Performance Compared to Benchmark")
    plt.ylabel("Cumulative Return %")
    plt.legend(loc="upper left")

    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'plots', filename)


    plt.Axes.set_autoscale_on
    locator = mdates.MonthLocator() 
    #locator = mdates.AutoDateLocator(minticks = 3, maxticks = 7) 
    formatter = mdates.ConciseDateFormatter(locator) 

    ax = plt.gca()
    ax.xaxis.set_major_locator(locator) 
    ax.xaxis.set_major_formatter(formatter) 
    plt.savefig(fname = filepath)

    bucketname = "data.fuzzyforrest.ai"

    s3 = boto3.client('s3')
    s3.upload_file(filepath, bucketname, filename)
    s3 = boto3.resource('s3')
    s3_object = s3.Object(bucketname, filename)
    s3_object.copy_from(
        CopySource={'Bucket': bucketname,'Key': filename},
        MetadataDirective="REPLACE",
        ContentType='image/png',
        ACL='public-read'
    ) 
    return  filename

def plot_performance_with_random(my_df, random_df, random_overnight_df, random_daytrade_df, overnight_df, daytrade_df, benchmark_df, spy_overnight_df, filename, label_my, label_random, label_overnight, label_daytrade, label_benchmark):
    myxpoints = my_df.index.values
    myypoints = my_df.values

    randomxpoints = random_df.index.values
    randomypoints = random_df.values

    randomovernightxpoints = random_overnight_df.index.values
    randomovernightypoints = random_overnight_df.values

    
    randomdaytradexpoints = random_daytrade_df.index.values
    randomdaytradeypoints = random_daytrade_df.values

    overnightxpoints = overnight_df.index.values
    overnightypoints = overnight_df.values

    daytradexpoints = daytrade_df.index.values
    daytradeypoints = daytrade_df.values

    benchmarkxpoints = benchmark_df.index.values
    benchmarkypoints = benchmark_df.values

    spyovernightxpoints = spy_overnight_df.index.values
    spyovernightypoints = spy_overnight_df.values



    plt.plot(myxpoints, myypoints, label = label_my) 
    plt.plot(overnightxpoints, overnightypoints, label = label_overnight) 
    plt.plot(daytradexpoints, daytradeypoints, label = label_daytrade) 
    plt.plot(randomxpoints, randomypoints, label = label_random) 
    plt.plot(randomovernightxpoints, randomovernightypoints, label = "random overnight") 
    plt.plot(randomdaytradexpoints, randomdaytradeypoints, label = "random daytrade") 
    plt.plot(benchmarkxpoints, benchmarkypoints, label = label_benchmark)     
    plt.plot(spyovernightxpoints, spyovernightypoints, label = "SPY overnight")     
    plt.title("Performance Compared to Benchmark")
    plt.ylabel("Cumulative Return %")
    plt.legend(loc="upper left")

    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'plots', filename)


    plt.Axes.set_autoscale_on
    locator = mdates.MonthLocator() 
#    locator = mdates.AutoDateLocator(minticks = 3, maxticks = 7) 
    formatter = mdates.ConciseDateFormatter(locator) 

    ax = plt.gca()
    ax.xaxis.set_major_locator(locator) 
    ax.xaxis.set_major_formatter(formatter) 
    plt.savefig(fname = filepath)

    bucketname = "data.fuzzyforrest.ai"

    s3 = boto3.client('s3')
    s3.upload_file(filepath, bucketname, filename)
    s3 = boto3.resource('s3')
    s3_object = s3.Object(bucketname, filename)
    s3_object.copy_from(
        CopySource={'Bucket': bucketname,'Key': filename},
        MetadataDirective="REPLACE",
        ContentType='image/png',
        ACL='public-read'
    ) 
    return  filename

def plot_performance_to(df, filename, label_my, label_benchmark):

    myxpoints = df.groupby(['date_field_min']).mean()['MyActualReturn'].index.values
    myypoints = df.groupby(['date_field_min']).mean()['MyActualReturn'].values
#VMCTX
#VV
#IWR
#IJR
#SH
    spyxpoints = df.groupby(['date_field_min']).mean()['BenchmarkActualReturn'].index.values
    spyypoints = df.groupby(['date_field_min']).mean()['BenchmarkActualReturn'].values

    plt.plot(myxpoints, myypoints, label = label_my) 
    plt.plot(spyxpoints, spyypoints, label = label_benchmark)     
    plt.title("Performance Compared to Benchmark")
    plt.ylabel("Cumulative Return %")
    plt.legend(loc="upper left")

    path = os.getcwd()
    filepath = os.path.join(path, 'plots', filename)



    bucketname = "data.fuzzyforrest.ai"

    s3 = boto3.client('s3')
    s3.upload_file(filepath, bucketname, filename)
    s3 = boto3.resource('s3')
    s3_object = s3.Object(bucketname, filename)
    s3_object.copy_from(
        CopySource={'Bucket': bucketname,'Key': filename},
        MetadataDirective="REPLACE",
        ContentType='image/png',
        ACL='public-read'
    ) 
    return  filename


def get_logo(ticker):
    x = get_company_name(ticker)
    x = x.upper()
    #stopwords = ['CORPORATION', 'CORP', 'INC', 'INC.', 'LTD', 'LIMITED', 'MEDICAL', 'HEALTHCARE', 'HEALTH', 'CO','COMPANY', 'CO.', 'LLC', 'LLP', 'LP', 'SPA', 'GMBH', 'OY', 'AB', 'LA', 'AG', 'KG']
    #x = ' '.join([part for part in x.split() if part not in stopwords])
    x = x + ' logo ' + ticker 
    print (x)
    payload = {'q': x, 'num': '1', 'fileType': 'jpg','searchType': 'image', 'rights': 'cc_publicdomain, cc_attribute, cc_sharealike', 'safe': 'active', 'key': 'AIzaSyAdyj_IjQAFxubiyGY3I4EMucjDYbLUFa0', 'cx': '024c26fc975f147b1'}
    #old credentials???  payload = {'q': x, 'num': '1', 'fileType': 'jpg','searchType': 'image', 'rights': 'cc_publicdomain, cc_attribute, cc_sharealike', 'safe': 'active', 'key': 'AIzaSyBLRJ5thehOqaw0ztgaMvbudO6hugBLndc', 'cx': '002626279200420637858:r66zdkomfa4'}
    r = requests.get('https://www.googleapis.com/customsearch/v1', params=payload, verify = False).content
    r_json = json.loads(r)
    try:
        link = r_json['items'][0]['link']
    except:
        link = 'https://vollrath.com/ClientCss/images/VollrathImages/No_Image_Available.jpg'
    return link


def df_filter_fundamentals(df): #not validating here, but the input needs be a dataframe wtih "Symbol" as ticker
    df['previousClose'] = np.nan
    df['fullTimeEmployees'] = np.nan
    #df['website'] = np.nan
    df['website'] = 'blah'
    df['longBusinessSummary'] = 'blah'
    #df['longBusinessSummary'].astype(str)
    df['fiftyDayAverage'] = np.nan
    df['twoHundredDayAverage'] = np.nan
    df['fiftyTwoWeekLow'] = np.nan
    df['fiftyTwoWeekHigh'] = np.nan
    df['52WeekChange'] = np.nan
    df['averageDailyVolume10Day'] = np.nan
    df['averageVolume'] = np.nan
    df['trailingEps'] = np.nan
    df['forwardEps'] = np.nan
    df['trailingPE'] = 0
    df['forwardPE'] = 0
    #df['year'] = np.nan
    df['revenue'] = 'blah'
    df['earnings'] = 'blah'
    df['2020 Rev'] = 0
    df['2019 Rev'] = 0
    df['2018 Rev'] = 0
    df['2020 Earnings'] = 0
    df['2019 Earnings'] = 0
    df['2018 Earnings'] = 0
    df['Standard Deviation Max'] = 0
    df['Standard Deviation 2Y'] = 0
    df['shortPercentOfFloat'] = 0
    df['beta'] = np.nan
    df['score'] = 0
    df['lastDividendValue'] = np.nan
    df['Last Recommendation'] = 'blah'
    df['marketCap'] = 0
    df['enterpriseToEbitda'] = 0
    df['enterpriseToRevenue'] = 0
    df['profitMargins'] = 0
    df['grossMargins'] = 0
    df['earningsGrowth'] = 0
    df['revenueGrowth'] = 0
    df['priceToSalesTrailing12Months'] = 0
    df['PS_adj'] = 0
    df['sharesOutstanding'] = 0
    df['sharesShort'] = 0
    df['sharesPercentSharesOut'] = 0
    df['floatShares'] = 0
    df['shortPercentOfFloat'] = 0
    df['pegRatio'] = 0
    df['roe'] = 0
    df['enterpriseValue'] = 0
    df['dividendRate'] = 0
    df['currentRatio'] = 0
    df['quickRatio'] = 0
    df['industry'] = 'unknown'
    df['sector'] = 'unknown'
    df['dividendYield'] = 0
    df['lastDividendValue'] = 'unknown'
    df['currency'] = 'unknown'
    df['PS_adj'] = 0
    df['marketCap'] = 0
    df['industryKey'] = 'unknown'
    df['sector'] = 'unknown'
    df['industry'] = 'unknown'
    df['longName'] = 'unknown'

    for idx, row in df.iterrows():
        try:
            time.sleep(1)  # To avoid hitting API rate limits
            stock_ticker = row['Symbol']
            print(stock_ticker)
            yf_data = yf.Ticker(stock_ticker)
            info = yf_data.info
            try:
                    df.at[idx, 'longName'] = info['longName']
            except Exception as e:
                print("oops longName:  ", e)
                traceback.print_exc()
            try:
                    df.at[idx, 'marketCap'] = info['marketCap']
            except Exception as e:
                print("oops marketCap:  ", e)
                traceback.print_exc()
            try:
                    df.at[idx, 'industryKey'] = info['industryKey']
            except Exception as e:
                print("oops industryKey:  ", e)
                traceback.print_exc()
            try:
                    df.at[idx, 'sector'] = info['sector']
            except Exception as e:
                print("oops sector:  ", e)
                traceback.print_exc()
            try:
                    df.at[idx, 'previousClose'] = info['previousClose']
            except Exception as e:
                print("oops previousClose:  ", e)
                traceback.print_exc()
            try:
                    df.at[idx, 'lastDividendValue'] = info['lastDividendValue']
            except Exception as e:
                print("oops lastDividendValue:  ", e)
            try:
                    df.at[idx, 'currency'] = info['currency']
            except Exception as e:
                print("oops currency:  ", e)
                traceback.print_exc()
            try:
                    df.at[idx, 'sector'] = info['sector']
            except Exception as e:
                print("oops sector:  ", e)
                traceback.print_exc()
            try:
                    df.at[idx, 'dividendYield'] = info['dividendYield']
            except Exception as e:
                print("oops dividendYield:  ", e)
                traceback.print_exc()
            try:
                    df.at[idx, 'lastDividendValue'] = info['lastDividendValue']
            except Exception as e:
                print("oops lastDividendValue:  ", e)
                traceback.print_exc()
            try:
                    df.at[idx, 'dividendRate'] = info['dividendRate']
            except Exception as e:
                print("oops dividendRate:  ", e)
                traceback.print_exc()
            try:
                df.at[idx, 'industry'] = info['industry']
            except Exception as e:
                print("oops industry:  ", e)
                traceback.print_exc()
            #try:
            #    df.at[idx, 'pegRatio'] = info['pegRatio']
            #except Exception as e:
            #    print("oops pegRatio:  ", e)
            #    traceback.print_exc()

            try:
                df.at[idx, 'roe'] = get_roe(stock_ticker)
            except Exception as e:
                print("oops roe:  ", e)
                traceback.print_exc()

            try:
                    df.at[idx, 'enterpriseValue'] = info['enterpriseValue']
            except Exception as e:
                print("oops enterpriseValue:  ", e)
                traceback.print_exc()
            try:
                    df.at[idx, 'floatShares'] = info['floatShares']
            except Exception as e:
                print("oops floatShares:  ", e)
                traceback.print_exc()
            try:
                    df.at[idx, 'shortPercentOfFloat'] = info['shortPercentOfFloat']
            except Exception as e:
                print("oops shortPercentOfFloat:  ", e)
            try:
                    df.at[idx, 'sharesPercentSharesOut'] = info['sharesPercentSharesOut']
            except Exception as e:
                print("oops sharesPercentSharesOut:  ", e)
            try:
                    df.at[idx, 'sharesShort'] = info['sharesShort']
            except Exception as e:
                print("oops sharesShort:  ", e)
            try:
                    df.at[idx, 'sharesOutstanding'] = info['sharesOutstanding']
            except Exception as e:
                print("oops sharesOutstanding:  ", e)
            try:
                    df.at[idx, 'enterpriseToEbitda'] = info['enterpriseToEbitda']
            except Exception as e:
                print("oops enterpriseToEbitda:  ", e)

            try:
                    df.at[idx, 'profitMargins'] = info['profitMargins']
            except Exception as e:
                print("oops profitMargins:  ", e)
            try:
                    df.at[idx, 'grossMargins'] = info['grossMargins']
            except Exception as e:
                print("oops grossMargins:  ", e)

            try:
                    df.at[idx, 'earningsGrowth'] = info['earningsGrowth']
            except Exception as e:
                print("oops earningsGrowth:  ", e)
            try:
                    df.at[idx, 'revenueGrowth'] = info['revenueGrowth']
            except Exception as e:
                print("oops revenueGrowth:  ", e)

            try:
                if info['revenueGrowth'] > 0:
                    test = info['priceToSalesTrailing12Months'] * (1-(info['revenueGrowth'])) * (1-info['grossMargins'])
                else:
                    test = info['priceToSalesTrailing12Months'] * (1-(info['revenueGrowth'])) 
                df.at[idx, 'PS_adj'] = test
            except Exception as e:
                print("oops PS_adj:  ", e)
    # df['grossMargins'] = 0
    # df['earningsGrowth'] = 0
    # df['revenueGrowth'] = 0
    # df['priceToSalesTrailing12Months'] = 0
    # df['PS_adj'] = 0

            try:
                    df.at[idx, 'enterpriseToRevenue'] = info['enterpriseToRevenue']
            except Exception as e:
                print("oops enterpriseToRevenue:  ", e)

            try:
                    df.at[idx, 'marketCap'] = info['marketCap']
            except Exception as e:
                print("oops marketCap:  ", e)
            try:
                    df.at[idx, 'priceToSalesTrailing12Months'] = info['priceToSalesTrailing12Months']
            except Exception as e:
                print("oops priceToSalesTrailing12Months:  ", e)


            try:
                df.at[idx, 'currentRatio'] = info['currentRatio']
            except Exception as e:
                print("oops currentRatio:  ", e)

            try:
                df.at[idx, 'quickRatio'] = info['quickRatio']
            except Exception as e:
                print("oops quickRatio:  ", e)


            try:
                    df.at[idx, 'beta'] = info['beta']
            except Exception as e:
                print("oops beta:  ", e)
            try:
                    df.at[idx, 'shortPercentOfFloat'] = info['shortPercentOfFloat']
            except Exception as e:
                print("oops shortPercentOfFloat:  ", e)
            try:
                    df.at[idx, 'longBusinessSummary'] = info['longBusinessSummary']
            except Exception as e:
                print("oops longBusinessSummary:  ", e)
            try:
                    df.at[idx, 'fullTimeEmployees'] = info['fullTimeEmployees']
            except Exception as e:
                print("oops fullTimeEmployees:  ", e)
            try:
                    df.at[idx, 'website'] = info['website']
            except Exception as e:
                print("oops website:  ", e)
            df.at[idx, 'fiftyDayAverage'] = info['fiftyDayAverage']
            df.at[idx, 'twoHundredDayAverage'] = info['twoHundredDayAverage']
            df.at[idx, 'fiftyTwoWeekLow'] = info['fiftyTwoWeekLow']
            df.at[idx, 'fiftyTwoWeekHigh'] = info['fiftyTwoWeekHigh']
            df.at[idx, '52WeekChange'] = info['52WeekChange']
            df.at[idx, 'averageDailyVolume10Day'] = info['averageDailyVolume10Day']
            df.at[idx, 'averageVolume'] = info['averageVolume']
            try:
                    df.at[idx, 'trailingEps'] = info['trailingEps']
            except Exception as e:
                print("oops trailingEps:  ", e)
            try:
                df.at[idx, 'forwardEps'] = info['forwardEps']
            except Exception as e:
                print("oops forwardEps:  ", e)
            try:
                df.at[idx, 'trailingPE'] = info['trailingPE']
            except Exception as e:
                print("oops trailingPE:  ", e)
            try:
                df.at[idx, 'forwardPE'] = info['forwardPE']
            except Exception as e:
                print("oops forwardPE:  ", e)
            # try:
            #     json_earnings = json.loads(yf_data.earnings.to_json())
            #     df.at[idx, '2022 Rev'] = int(json_earnings['Revenue']['2022'])
            #     df.at[idx, '2021 Rev'] = int(json_earnings['Revenue']['2021'])
            #     df.at[idx, '2020 Rev'] = int(json_earnings['Revenue']['2020'])
            #     df.at[idx, '2022 Earnings'] = int(json_earnings['Earnings']['2022'])
            #     df.at[idx, '2021 Earnings'] = int(json_earnings['Earnings']['2021'])
            #     df.at[idx, '2020 Earnings'] = int(json_earnings['Earnings']['2020'])
            # except Exception as e:
            #     print("oops rev breakouts:  ", e)
            #     traceback.print_exc()
        except Exception as e:
            print("oops - iteration:  ", e)

    #get top picks
    #df['Rev Growth 2022'] = (df['2022 Rev'] - df['2021 Rev'])/df['2021 Rev']
    #df['Rev Growth 2021'] = (df['2021 Rev'] - df['2020 Rev'])/df['2020 Rev']
    #df['Earnings Growth 2022'] = (df['2022 Earnings'] - df['2021 Earnings'])/df['2021 Earnings']
    #df['Earnings Growth 2021'] = (df['2021 Earnings'] - df['2020 Earnings'])/df['2020 Earnings']
    #df['Growth Goal'] = df['Standard Deviation 2Y']/df['previousClose']
    #df['beta']
    #df['shortPercentOfFloat']
    df['Growth to High'] = df['fiftyTwoWeekHigh'] - df['previousClose']/df['previousClose']

    for idx, row in df.iterrows():

        score = 0
        try:
            if row['trailingPE'] < 5 and row['trailingPE'] != None and row['trailingPE'] > 0:
                score = score + 2
            if row['trailingPE']  < 10 and row['trailingPE'] != None and row['trailingPE'] > 0:
                score = score + 2   
            if row['trailingPE']  < 20 and row['trailingPE'] != None and row['trailingPE'] > 0:
                score = score + 2
            if row['trailingPE']  < 40 and row['trailingPE'] != None and row['trailingPE'] > 0:
                score = score + 2 
            if row['trailingPE']  < 80 and row['trailingPE'] != None and row['trailingPE'] > 0:
                score = score + 2 
            if row['trailingPE']  < 200 and row['trailingPE'] != None and row['trailingPE'] > 0:
                score = score + 2 



            if (row['revenueGrowth'] != None and row['revenueGrowth'] > 0) and row['PS_adj'] < 2 and row['grossMargins'] > 0:
                score = score + 2
            if (row['revenueGrowth'] != None and row['revenueGrowth'] > 0.1) and row['PS_adj'] < 2.1 and row['grossMargins'] > 0:
                score = score + 2  
            if (row['revenueGrowth'] != None and row['revenueGrowth'] > 0.2) and row['PS_adj'] < 2.2 and row['grossMargins'] > 0:
                score = score + 2  
            if (row['revenueGrowth'] != None and row['revenueGrowth'] > 0.3) and row['PS_adj'] < 2.3 and row['grossMargins'] > 0:
                score = score + 2  
            if (row['revenueGrowth'] != None and row['revenueGrowth'] > 0.4) and row['PS_adj'] < 2.4 and row['grossMargins'] > 0:
                score = score + 2



    #        if row['grossMargins'] > 0.6 and row['grossMargins'] != 1:
    #            score = score + 1   
    #        if row['grossMargins'] > 0.8 and row['grossMargins'] != 1:
    #            score = score + 1

    #        if row['profitMargins'] > 0.1 and row['profitMargins'] != 1:
    #            score = score + 1   
    #        if row['profitMargins'] > 0.2 and row['profitMargins'] != 1:
    #            score = score + 1   
    #        if row['profitMargins'] > 0.3 and row['profitMargins'] != 1:
    #            score = score + 1   
    #        if row['profitMargins'] > 0.4 and row['profitMargins'] != 1:
    #            score = score + 1

            if row['pegRatio'] < 1:
                score = score + 2

            # if row['dividendYield'] > 0.02:
            #     score = score + 1
            # if row['dividendYield'] > 0.04:
            #     score = score + 1
            # if row['dividendYield'] > 0.06:
            #     score = score + 1
            # if row['dividendYield'] > 0.08:
            #     score = score + 1
            # if row['dividendYield'] > 0.10:
            #     score = score + 1

    #        if row['shortPercentOfFloat'] < .05:
    #            score = score + 1
            df.at[idx, 'score'] = score
        except Exception as e:
            print("oops - score:  ", e)
    df['priceToSalesTrailing12Months'].astype(float)
    df['revenueGrowth'].astype(float)
    df['grossMargins'].astype(float)
    df['trailingPE'].astype(float)
    df['forwardPE'].astype(float)
    df['PS_adj'].astype(float)
    #f['pegRatio'].astype(float)
    df['roe'].astype(float)
    df['earningsGrowth'].astype(float)
    df['profitMargins'].astype(float)
    df['shortPercentOfFloat'].astype(float)
    df['dividendYield'].astype(float)
    df['currentRatio'].astype(float)
    df['quickRatio'].astype(float)

    df['priceToSalesTrailing12Months'] = df['priceToSalesTrailing12Months'].map(lambda x: round(x, 2) if isinstance(x, float) else 0)
    df['revenueGrowth'] = round(df['revenueGrowth'], 4)*100
    df['grossMargins'] = round(df['grossMargins'], 4)*100
    df['trailingPE'] = df['trailingPE'].map(lambda x: round(x, 2) if isinstance(x, float) else 0)
#    df['trailingPE'] = round(df['trailingPE'], 2)
    df['forwardPE'] = df['forwardPE'].map(lambda x: round(x, 2) if isinstance(x, float) else 0)
#    df['forwardPE'] = round(df['forwardPE'], 2)
    df['PS_adj'] = df['PS_adj'].map(lambda x: round(x, 2) if isinstance(x, float) else 0)
#    df['PS_adj'] = round(df['PS_adj'], 2)
    #df['pegRatio'] = df['pegRatio'].map(lambda x: round(x, 2) if isinstance(x, float) else 0)
#    df['pegRatio'] = round(df['pegRatio'], 2)
    df['roe'] = round(df['roe'], 2)
    df['earningsGrowth'] = round(df['earningsGrowth'], 4)*100
    df['profitMargins'] = round(df['profitMargins'], 4)*100
    df['shortPercentOfFloat'] = round(df['shortPercentOfFloat'], 4)*100
    df['dividendYield'] = round(df['dividendYield'], 2)
    df = df[['Symbol', 'longName', 'sector','industry','industryKey', 'marketCap', 'priceToSalesTrailing12Months', 'currentRatio', 'quickRatio', 'revenueGrowth', 'grossMargins', 'trailingPE', 'forwardPE', 'PS_adj', 'pegRatio', 'dividendYield', 'earningsGrowth', 'profitMargins',  'shortPercentOfFloat', 'roe', 'score']]
    return df

def specific_ticker_ta(ticker):
    try:
        print (ticker)
        ticker_data = yf.Ticker(ticker)
        ticker_history = get_ticker_history(ticker, '30y', '1d')#end = earnings_dates_past['er_date_string'].iloc[0], rounding ="True"  ##why doent; ticker_date.history work?
        levels = get_fractals_levels(ticker_history)
        fib_levels = fib_retrace(ticker_history)
        levels_lists = fib_levels + levels
        result = explore_indicators(ticker_history)
        result['pct_to_50ema'] = (result['50 period EMA'] - result['Close'])/result['Close']
        result['pct_to_200ema'] = (result['200 period EMA'] - result['Close'])/result['Close']
        result['BB_UPPER_PRICE'] = result['BB_UPPER']
        result['BB_UPPER'] = (result['BB_UPPER'] - result['Close'])/result['Close']
        result['BB_LOWER_PRICE'] = result['BB_LOWER']
        result['BB_LOWER'] = (result['BB_LOWER'] - result['Close'])/result['Close']
        result['BB_MIDDLE'] = result['BB_UPPER_PRICE'] - ((result['BB_UPPER_PRICE'] - result['BB_LOWER_PRICE'])/2)
        result['BB_BUCKET_1'] = result.apply(lambda x: 1 if x.Close > x.BB_UPPER_PRICE else 0, axis = 1)
        result['BB_BUCKET_2'] = result.apply(lambda x: 1 if x.Close < x.BB_UPPER_PRICE and x.Close >= x.BB_MIDDLE else 0, axis = 1)
        result['BB_BUCKET_3'] = result.apply(lambda x: 1 if x.Close < x.BB_MIDDLE and x.Close > x.BB_LOWER_PRICE  else 0, axis = 1)
        result['BB_BUCKET_4'] = result.apply(lambda x: 1 if x.Close < x.BB_LOWER_PRICE else 0, axis = 1)
        result['KC_MIDDLE'] = result['KC_UPPER'] - ((result['KC_UPPER'] - result['KC_LOWER'])/2)
        result['KC_BUCKET_1'] = result.apply(lambda x: 1 if x.Close > x.KC_UPPER else 0, axis = 1)
        result['KC_BUCKET_2'] = result.apply(lambda x: 1 if x.Close < x.KC_UPPER and x.Close >= x.KC_MIDDLE else 0, axis = 1)
        result['KC_BUCKET_3'] = result.apply(lambda x: 1 if x.Close < x.KC_MIDDLE and x.Close > x.KC_LOWER  else 0, axis = 1)
        result['KC_BUCKET_4'] = result.apply(lambda x: 1 if x.Close < x.KC_LOWER else 0, axis = 1)
        sma_ema_averages = [8,21,34,55,89]
        for i in sma_ema_averages:
            result = appendData(result,ta.EMA(result, i))
        result['Target'] = result['Close'].shift(-2) #predicting 10 days out
        result = result[result['Target'].notnull()]
        result['pct_target'] = ((result['Target'] - result['Close'])/result['Close'])* 100
        result = result[(result['pct_target'] <=  20)]
        result = result[(result['pct_target'] >  -20)]
    #    result = result.drop('Dividends', axis=1)
    #    result = result.drop('Stock Splits', axis=1)
    #    result = result.drop('Capital Gains', axis=1)
        result['date_field'] = result.index
        result['date_field'] = result['date_field'].dt.date
        result['SAR_level'] = result['SAR']
        result['next_support'] = result['Close'].apply(lambda x: next_buy_level(x, levels_lists))
        result['pct_to_SAR_support'] = (result['Close'] - result['SAR_level'])/result['Close'] * 100
        result['pct_to_other_support'] = (result['Close'] - result['next_support'])/result['Close'] * 100
    except Exception as e:
        print("oops:  ", e)   
    final_result = result

    final_result['DI+_prior'] = final_result['DI+'].shift(5) #10 days prior
    final_result['DI-_prior'] = final_result['DI-'].shift(5) #10 days prior
    final_result['DI_diff_prior'] = final_result['DI+_prior'] - final_result['DI-_prior']
    final_result['DI_diff'] = final_result['DI+'] - final_result['DI-']
    final_result['DI_crossover'] = final_result.apply(lambda x: 1 if x.DI_diff_prior < 0 and x.DI_diff > 1 else 0, axis=1)
    final_result['DI_uptrend'] = final_result.apply(lambda x: 1 if x['DI+_prior'] < x['DI+'] else 0, axis=1)

    final_result['BullishFractal'] = final_result['BullishFractal'].shift(2) #predicting 10 days out
    final_result['BearishFractal'] = final_result['BearishFractal'].shift(2) #predicting 10 days out

    final_result['BB_breakout'] = final_result['BB_UPPER'].apply(lambda x: 1 if x < 0 else 0)
    final_result['ree_flag'] = final_result.apply(lambda row: 1 if  row['8 period EMA'] > row['21 period EMA'] and row['21 period EMA'] > row['34 period EMA'] and row['34 period EMA'] > row['55 period EMA'] and row['55 period EMA'] > row['89 period EMA'] and row['14 period ADX.'] > 20 and row['14 period STOCH %K'] < 40 else 0, axis=1)
    final_result['ree_flag2'] = final_result.apply(lambda row: 1 if  row['21 period EMA'] > row['34 period EMA'] and row['34 period EMA'] > row['55 period EMA'] and row['55 period EMA'] > row['89 period EMA'] and row['14 period ADX.'] > 20 and row['14 period STOCH %K'] < 50 else 0, axis=1)
    final_result['ema_downtrend_lt'] = final_result.apply(lambda row: 1 if row['8 period EMA'] < row['21 period EMA'] and row['21 period EMA'] < row['34 period EMA'] and row['34 period EMA'] < row['55 period EMA'] else 0, axis=1)
    final_result['ema_downtrend_st'] = final_result.apply(lambda row: 1 if row['8 period EMA'] < row['21 period EMA'] and row['21 period EMA'] < row['34 period EMA'] else 0, axis=1)
    final_result['ema_uptrend_st'] = final_result.apply(lambda row: 1 if row['8 period EMA'] > row['21 period EMA'] and row['21 period EMA'] > row['34 period EMA'] else 0, axis=1)
    final_result['BB_lower_hold'] = final_result.apply(lambda row: 1 if row['BB_LOWER'] > 0 and row['BB_LOWER'] < .01 and row['8 period EMA'] > row['BB_LOWER_PRICE'] and row['21 period EMA'] < row['34 period EMA'] and row['34 period EMA'] < row['55 period EMA'] and row['55 period EMA'] < row['89 period EMA'] and row['14 period RSI'] > 40 else 0, axis=1)
    final_result['ema_downtrends'] = final_result.apply(lambda row: 1 if row['8 period EMA'] < row['21 period EMA']  and row['21 period EMA'] < row['34 period EMA'] and row['34 period EMA'] < row['55 period EMA'] and row['55 period EMA'] < row['89 period EMA'] else 0, axis=1)
    final_result['stoch_low'] = final_result.apply(lambda row: 1 if  row['14 period STOCH %K'] < 40 else 0, axis=1)
    final_result['stoch_really_low'] = final_result.apply(lambda row: 1 if  row['14 period STOCH %K'] < 30 else 0, axis=1)
    final_result['rsi_low'] = final_result.apply(lambda row: 1 if  row['14 period RSI'] < 30 and row['14 period RSI'] > 1 else 0, axis=1)
    final_result['not_macd'] = final_result.apply(lambda row: 1 if  row['8 period EMA'] > row['21 period EMA'] and row['21 period EMA'] < row['34 period EMA'] else 0, axis=1)
    final_result = macd_crossover(final_result)
    final_result['SAR'] = final_result.apply(lambda row: 1 if  row['Open'] > row['SAR'] else 0, axis=1)
    final_result['pivot_check'] = final_result.apply(lambda row: 1 if  row['Open'] > row['pivot'] and (row['Open'] - row['pivot'])/ row['pivot'] > .0025 else 0, axis=1)
    final_result['ADX_CHECK1'] = final_result.apply(lambda row: 1 if  row['8 period EMA'] > row['34 period EMA'] and row['Open'] > row['SAR'] and row['14 period ADX.'] > 40 else 0, axis=1)
    final_result['ADX_CHECK2'] = final_result.apply(lambda row: 1 if row['BEARISH_MACD_CROSSOVER'] == 1 and row['14 period ADX.'] > 50 and row['14 period RSI'] < 60 else 0, axis=1)
    final_result['ADX_CHECK3'] = final_result.apply(lambda row: 1 if row['14 period ADX.'] > 50 and row['14 period RSI'] < 60 else 0, axis=1)
    final_result['ADX_CHECK4'] = final_result.apply(lambda row: 1 if row['14 period ADX.'] > 50 and row['14 period RSI'] > 40 and row['14 period RSI'] < 60 else 0, axis=1)
    final_result['ADX_CHECK5'] = final_result.apply(lambda row: 1 if row['14 period ADX.'] > 50 and row['14 period RSI'] > 40 and row['14 period RSI'] < 70 else 0, axis=1)
    final_result['ADX_CHECK6'] = final_result.apply(lambda row: 1 if row['14 period ADX.'] > 50 else 0, axis=1)
    final_result['ADX_CHECK7'] = final_result.apply(lambda row: 1 if row['14 period ADX.'] > 50 and row['8 period EMA'] > row['34 period EMA'] else 0, axis=1)
    final_result['ADX_CHECK8'] = final_result.apply(lambda row: 1 if row['14 period ADX.'] > 50 and row['8 period EMA'] < row['34 period EMA'] else 0, axis=1)
    final_result['ADX_CHECK9'] = final_result.apply(lambda row: 1 if row['14 period ADX.'] > 50 and row['14 period RSI'] < 40 else 0, axis=1)
    final_result['combo_top_indicator'] = final_result.apply(lambda row: 1 if row['14 period ADX.'] > 50 and (row['BB_BUCKET_1'] == 1 or row['BB_BUCKET_2'] == 1) and row['8 period EMA'] > row['21 period EMA'] and row['21 period EMA'] > row['34 period EMA'] and row['14 period RSI'] > 70 else 0, axis=1)
    final_result['MFI_high'] = final_result.apply(lambda row: 1 if row['14 period MFI'] > 80 else 0, axis=1)
    final_result['MFI_low'] = final_result.apply(lambda row: 1 if row['14 period MFI'] < 20 else 0, axis=1)
    final_result['pct_to_SAR_support'] = final_result.apply(lambda row: 1 if row['pct_to_SAR_support'] > 5 and row['SAR'] == 1 else 0, axis=1)
    final_result['pct_to_other_support'] = final_result.apply(lambda row: 1 if row['pct_to_other_support'] > 5 and row['SAR'] == 1 else 0, axis=1)
    final_result['rsi_lower_25'] = final_result.apply(lambda row: 1 if  row['14 period RSI'] < 25 and row['14 period RSI'] > 1 else 0, axis=1)
    final_result['rsi_lower_25_30'] = final_result.apply(lambda row: 1 if  row['14 period RSI'] > 25 and row['14 period RSI'] < 30 else 0, axis=1)
    final_result['rsi_lower_30_40'] = final_result.apply(lambda row: 1 if  row['14 period RSI'] > 30 and row['14 period RSI'] < 40 else 0, axis=1)
    final_result['rsi_lower_70_80'] = final_result.apply(lambda row: 1 if  row['14 period RSI'] > 70 and row['14 period RSI'] < 80 else 0, axis=1)
    final_result['rsi_lower_80'] = final_result.apply(lambda row: 1 if  row['14 period RSI'] > 80 else 0, axis=1)
    final_result['combo_SAR_bull_fractal'] = final_result.apply(lambda row: 1 if  row['Open'] > row['SAR'] and row['BullishFractal'] == 1 else 0, axis=1)
    final_result['combo_RSI_bull_fractal'] = final_result.apply(lambda row: 1 if  row['rsi_low'] < 30  and row['BullishFractal'] == 1 else 0, axis=1)
    final_result['combo_SAR_not_macd'] = final_result.apply(lambda row: 1 if  row['Open'] > row['SAR'] and row['not_macd'] == 1 else 0, axis=1)
    final_result['combo_bull_fractal_EMA_ADX'] = final_result.apply(lambda row: 1 if  row['8 period EMA'] > row['34 period EMA'] and row['14 period ADX.'] > 25 and row['BullishFractal'] == 1 else 0, axis=1)
    final_result['combo_bull_fractal_EMA_ADX_RSI'] = final_result.apply(lambda row: 1 if  row['8 period EMA'] > row['34 period EMA'] and row['14 period ADX.'] > 25 and row['BullishFractal'] == 1 and row['rsi_low'] < 40 else 0, axis=1)
    final_result['di_crossover_trend'] = final_result.apply(lambda row: 1 if  row['DI_uptrend'] == 1 and row['DI_crossover'] == 1 else 0, axis=1)
    final_result['di_crossover_bullish_fractal'] = final_result.apply(lambda row: 1 if  row['BullishFractal'] == 1 and row['DI_crossover'] == 1 else 0, axis=1)
    final_result['di_uptrend_ADX'] = final_result.apply(lambda row: 1 if  row['DI_uptrend'] == 1 and row['14 period ADX.'] > 20 else 0, axis=1)

#evaluate effectiveness of indcators
    test_BB_breakout = final_result[final_result['BB_breakout'] == 1]['pct_target'].mean() if len(final_result[final_result['BB_breakout'] == 1]) > 3 else None
    test_ree_flag = final_result[final_result['ree_flag'] == 1]['pct_target'].mean() if len(final_result[final_result['ree_flag'] == 1]) > 3 else None
    test_ree_flag2 = final_result[final_result['ree_flag2'] == 1]['pct_target'].mean() if len(final_result[final_result['ree_flag2'] == 1]) > 3 else None
    test_ema_downtrend_lt = final_result[final_result['ema_downtrend_lt'] == 1]['pct_target'].mean() if len(final_result[final_result['ema_downtrend_lt'] == 1]) > 3 else None
    test_ema_downtrend_st = final_result[final_result['ema_downtrend_st'] == 1]['pct_target'].mean() if len(final_result[final_result['ema_downtrend_st'] == 1]) > 3 else None
    test_ema_uptrend_st = final_result[final_result['ema_uptrend_st'] == 1]['pct_target'].mean() if len(final_result[final_result['ema_uptrend_st'] == 1]) > 3 else None
    test_BB_lower_hold = final_result[final_result['BB_lower_hold'] == 1]['pct_target'].mean() if len(final_result[final_result['BB_lower_hold'] == 1]) > 3 else None
    test_stoch_low = final_result[final_result['stoch_low'] == 1]['pct_target'].mean() if len(final_result[final_result['stoch_low'] == 1]) > 3 else None
    test_stoch_really_low = final_result[final_result['stoch_really_low'] == 1]['pct_target'].mean() if len(final_result[final_result['stoch_really_low'] == 1]) > 3 else None
    test_not_macd = final_result[final_result['not_macd'] == 1]['pct_target'].mean() if len(final_result[final_result['not_macd'] == 1]) > 3 else None
    test_BULLISH_MACD_CROSSOVER = final_result[final_result['BULLISH_MACD_CROSSOVER'] == 1]['pct_target'].mean() if len(final_result[final_result['BULLISH_MACD_CROSSOVER'] == 1]) > 3 else None
    test_BEARISH_MACD_CROSSOVER = final_result[final_result['BEARISH_MACD_CROSSOVER'] == 1]['pct_target'].mean() if len(final_result[final_result['BEARISH_MACD_CROSSOVER'] == 1]) > 3 else None
    test_SAR = final_result[final_result['SAR'] == 1]['pct_target'].mean() if len(final_result[final_result['SAR'] == 1]) > 3 else None
    test_BearishFractal = final_result[final_result['BearishFractal'] == 1]['pct_target'].mean() if len(final_result[final_result['BearishFractal'] == 1]) > 3 else None
    test_BullishFractal = final_result[final_result['BullishFractal'] == 1]['pct_target'].mean() if len(final_result[final_result['BullishFractal'] == 1]) > 3 else None
    test_pivot_check = final_result[final_result['pivot_check'] == 1]['pct_target'].mean() if len(final_result[final_result['pivot_check'] == 1]) > 3 else None
    test_ADX_CHECK1 = final_result[final_result['ADX_CHECK1'] == 1]['pct_target'].mean() if len(final_result[final_result['ADX_CHECK1'] == 1]) > 3 else None
    test_ADX_CHECK2 = final_result[final_result['ADX_CHECK2'] == 1]['pct_target'].mean() if len(final_result[final_result['ADX_CHECK2'] == 1]) > 3 else None
    test_ADX_CHECK3 = final_result[final_result['ADX_CHECK3'] == 1]['pct_target'].mean() if len(final_result[final_result['ADX_CHECK3'] == 1]) > 3 else None
    test_MFI_high = final_result[final_result['MFI_high'] == 1]['pct_target'].mean() if len(final_result[final_result['MFI_high'] == 1]) > 3 else None
    test_MFI_low = final_result[final_result['MFI_low'] == 1]['pct_target'].mean() if len(final_result[final_result['MFI_low'] == 1]) > 3 else None
    test_pct_to_SAR_support = final_result[final_result['pct_to_SAR_support'] == 1]['pct_target'].mean() if len(final_result[final_result['pct_to_SAR_support'] == 1]) > 3 else None
    test_pct_to_other_support = final_result[final_result['pct_to_other_support'] == 1]['pct_target'].mean() if len(final_result[final_result['pct_to_other_support'] == 1]) > 3 else None
    test_BB_BUCKET_1 = final_result[final_result['BB_BUCKET_1'] == 1]['pct_target'].mean() if len(final_result[final_result['BB_BUCKET_1'] == 1]) > 3 else None
    test_BB_BUCKET_2 = final_result[final_result['BB_BUCKET_2'] == 1]['pct_target'].mean() if len(final_result[final_result['BB_BUCKET_2'] == 1]) > 3 else None
    test_BB_BUCKET_3 = final_result[final_result['BB_BUCKET_3'] == 1]['pct_target'].mean() if len(final_result[final_result['BB_BUCKET_3'] == 1]) > 3 else None
    test_BB_BUCKET_4 = final_result[final_result['BB_BUCKET_4'] == 1]['pct_target'].mean() if len(final_result[final_result['BB_BUCKET_4'] == 1]) > 3 else None
    test_KC_BUCKET_1 = final_result[final_result['KC_BUCKET_1'] == 1]['pct_target'].mean() if len(final_result[final_result['KC_BUCKET_1'] == 1]) > 3 else None
    test_KC_BUCKET_2 = final_result[final_result['KC_BUCKET_2'] == 1]['pct_target'].mean() if len(final_result[final_result['KC_BUCKET_2'] == 1]) > 3 else None
    test_KC_BUCKET_3 = final_result[final_result['KC_BUCKET_3'] == 1]['pct_target'].mean() if len(final_result[final_result['KC_BUCKET_3'] == 1]) > 3 else None
    test_KC_BUCKET_4 = final_result[final_result['KC_BUCKET_4'] == 1]['pct_target'].mean() if len(final_result[final_result['KC_BUCKET_4'] == 1]) > 3 else None
    test_rsi_low = final_result[final_result['rsi_low'] == 1]['pct_target'].mean() if len(final_result[final_result['rsi_low'] == 1]) > 3 else None
    test_rsi_lower_25 = final_result[final_result['rsi_lower_25'] == 1]['pct_target'].mean() if len(final_result[final_result['rsi_lower_25'] == 1]) > 3 else None
    test_rsi_lower_30_40 = final_result[final_result['rsi_lower_30_40'] == 1]['pct_target'].mean() if len(final_result[final_result['rsi_lower_30_40'] == 1]) > 3 else None
    test_rsi_lower_25_30 = final_result[final_result['rsi_lower_25_30'] == 1]['pct_target'].mean() if len(final_result[final_result['rsi_lower_25_30'] == 1]) > 3 else None
    test_rsi_lower_70_80 = final_result[final_result['rsi_lower_70_80'] == 1]['pct_target'].mean() if len(final_result[final_result['rsi_lower_70_80'] == 1]) > 3 else None
    test_rsi_lower_80 = final_result[final_result['rsi_lower_80'] == 1]['pct_target'].mean() if len(final_result[final_result['rsi_lower_80'] == 1]) > 3 else None
    test_combo_SAR_bull_fractal = final_result[final_result['combo_SAR_bull_fractal'] == 1]['pct_target'].mean() if len(final_result[final_result['combo_SAR_bull_fractal'] == 1]) > 3 else None
    test_combo_RSI_bull_fractal = final_result[final_result['combo_RSI_bull_fractal'] == 1]['pct_target'].mean() if len(final_result[final_result['combo_RSI_bull_fractal'] == 1]) > 3 else None
    test_combo_SAR_not_macd = final_result[final_result['combo_SAR_not_macd'] == 1]['pct_target'].mean() if len(final_result[final_result['combo_SAR_not_macd'] == 1]) > 3 else None
    test_combo_bull_fractal_EMA_ADX = final_result[final_result['combo_bull_fractal_EMA_ADX'] == 1]['pct_target'].mean() if len(final_result[final_result['combo_bull_fractal_EMA_ADX'] == 1]) > 3 else None
    test_di_crossover_trend = final_result[final_result['di_crossover_trend'] == 1]['pct_target'].mean() if len(final_result[final_result['di_crossover_trend'] == 1]) > 3 else None
    test_di_crossover_bullish_fractal = final_result[final_result['di_crossover_bullish_fractal'] == 1]['pct_target'].mean() if len(final_result[final_result['di_crossover_bullish_fractal'] == 1]) > 3 else None
    test_di_uptrend_ADX = final_result[final_result['di_uptrend_ADX'] == 1]['pct_target'].mean() if len(final_result[final_result['di_uptrend_ADX'] == 1]) > 3 else None
    test_ADX_CHECK4 = final_result[final_result['ADX_CHECK4'] == 1]['pct_target'].mean() if len(final_result[final_result['ADX_CHECK4'] == 1]) > 3 else None
    test_ADX_CHECK5 = final_result[final_result['ADX_CHECK5'] == 1]['pct_target'].mean() if len(final_result[final_result['ADX_CHECK5'] == 1]) > 3 else None
    test_ADX_CHECK6 = final_result[final_result['ADX_CHECK6'] == 1]['pct_target'].mean() if len(final_result[final_result['ADX_CHECK6'] == 1]) > 3 else None
    test_ADX_CHECK7 = final_result[final_result['ADX_CHECK7'] == 1]['pct_target'].mean() if len(final_result[final_result['ADX_CHECK7'] == 1]) > 3 else None
    test_ADX_CHECK8 = final_result[final_result['ADX_CHECK8'] == 1]['pct_target'].mean() if len(final_result[final_result['ADX_CHECK8'] == 1]) > 3 else None
    test_ADX_CHECK9 = final_result[final_result['ADX_CHECK9'] == 1]['pct_target'].mean() if len(final_result[final_result['ADX_CHECK9'] == 1]) > 3 else None
    test_combo_top_indicator = final_result[final_result['combo_top_indicator'] == 1]['pct_target'].mean() if len(final_result[final_result['combo_top_indicator'] == 1]) > 3 else None

    labels = ['ticker', 'test_BB_breakout',
        'test_ree_flag',
        'test_ree_flag2',
        'test_ema_downtrend_lt',
        'test_ema_downtrend_st',
        'test_ema_uptrend_st',
        'test_BB_lower_hold',
        'test_stoch_low',
        'test_stoch_really_low',
        'test_not_macd',
        'test_BULLISH_MACD_CROSSOVER',
        'test_BEARISH_MACD_CROSSOVER',
        'test_SAR',
        'test_BearishFractal',
        'test_BullishFractal',
        'test_pivot_check',
        'test_ADX_CHECK1',
        'test_ADX_CHECK2',
        'test_ADX_CHECK3',
        'test_MFI_high',
        'test_MFI_low',
        'test_pct_to_SAR_support',
        'test_pct_to_other_support',
        'test_BB_BUCKET_1',
        'test_BB_BUCKET_2',
        'test_BB_BUCKET_3',
        'test_BB_BUCKET_4',
        'test_KC_BUCKET_1',
        'test_KC_BUCKET_2',
        'test_KC_BUCKET_3',
        'test_KC_BUCKET_4',
        'test_rsi_low',
        'test_rsi_lower_25',
        'test_rsi_lower_30_40',
        'test_rsi_lower_25_30',
        'test_rsi_lower_70_80',
        'test_rsi_lower_80',
        'test_combo_SAR_bull_fractal',
        'test_combo_RSI_bull_fractal',
        'test_combo_SAR_not_macd',
        'test_combo_bull_fractal_EMA_ADX',
        'test_di_crossover_trend',
        'test_di_crossover_bullish_fractal',
        'test_di_uptrend_ADX',
        'test_ADX_CHECK4',
        'test_ADX_CHECK5',
        'test_ADX_CHECK6',
        'test_ADX_CHECK7',
        'test_ADX_CHECK8',
        'test_ADX_CHECK9',
        'test_combo_top_indicator']

    values = [ticker, \
        test_BB_breakout, \
        test_ree_flag, \
        test_ree_flag2,\
        test_ema_downtrend_lt,\
        test_ema_downtrend_st,\
        test_ema_uptrend_st,\
        test_BB_lower_hold,\
        test_stoch_low,\
        test_stoch_really_low,\
        test_not_macd,\
        test_BULLISH_MACD_CROSSOVER,\
        test_BEARISH_MACD_CROSSOVER,\
        test_SAR,\
        test_BearishFractal,\
        test_BullishFractal,\
        test_pivot_check,\
        test_ADX_CHECK1,\
        test_ADX_CHECK2,\
        test_ADX_CHECK3,\
        test_MFI_high,\
        test_MFI_low,\
        test_pct_to_SAR_support,\
        test_pct_to_other_support,\
        test_BB_BUCKET_1,\
        test_BB_BUCKET_2,\
        test_BB_BUCKET_3,\
        test_BB_BUCKET_4,\
        test_KC_BUCKET_1,\
        test_KC_BUCKET_2,\
        test_KC_BUCKET_3,\
        test_KC_BUCKET_4,\
        test_rsi_low,\
        test_rsi_lower_25,\
        test_rsi_lower_30_40,\
        test_rsi_lower_25_30,\
        test_rsi_lower_70_80,\
        test_rsi_lower_80,\
        test_combo_SAR_bull_fractal,\
        test_combo_RSI_bull_fractal,\
        test_combo_SAR_not_macd,\
        test_combo_bull_fractal_EMA_ADX,\
        test_di_crossover_trend,\
        test_di_crossover_bullish_fractal,\
        test_di_uptrend_ADX,\
        test_ADX_CHECK4,\
        test_ADX_CHECK5,\
        test_ADX_CHECK6,\
        test_ADX_CHECK7,\
        test_ADX_CHECK8,\
        test_ADX_CHECK9,\
        test_combo_top_indicator]

    labels = labels[1:]#drop ticker label
    values = values[1:]#drop ticker value
    values = [0 if v is None else v for v in values]
    avg_move = sum(values)/len(values)
    values = [v for v in values]
    labels = [l[5:] for l in labels]
    dict_of_values = dict(zip(labels, values))
    final_result = final_result.tail(1)
    for key, value in dict_of_values.items():
        final_result[key] = float(final_result[key])  * float(value)

    final_result = final_result.reset_index(drop=True)
    story = final_result[labels].to_dict()
    story = {k:round(v.get(list(v.keys())[0]), 2) for (k,v) in story.items() if v.get(list(v.keys())[0]) > 0}
    story = sorted(story.items(), key=lambda x: x[1], reverse=True)

    print(story)
    final_story = ""
    for t in story:
        final_story = final_story + '-'.join(str(s) for s in t) + "; "
    return round(avg_move, 2), round(final_result[labels].sum(axis=1).values[0]/len(story), 2),  final_story


def backtest(ticker):  
    # ##backtest
    # wait_counter = 0
    # money_available = 1
    # portfolio_value = 100
    # price_paid = 0
    # num_stops = 0
    # num_gains = 0
    # num_buys = 0
    # for idx, row in df.head(2000).iterrows():
    #     try:
    #         #buy logic
    #         if row['8 period EMA'] > row['21 period EMA'] and row['21 period EMA'] > row['34 period EMA'] and row['34 period EMA'] > row['55 period EMA'] and row['55 period EMA'] > row['89 period EMA'] and row['14 period ADX.'] > 20 and row['14 period STOCH %K'] < 40 and wait_counter == 0 and money_available == 1:
    #             print ("buy")
    #             print(row['14 period STOCH %K'])
    #             price_paid = row['Close']
    #             money_available = 0
    #             num_buys = num_buys + 1
    #         #stop loss trigger
    #         elif money_available == 0 and row['Close'] <= (price_paid*.98):
    #             print ("stop loss")
    #             portfolio_value = portfolio_value * (row['Close']/price_paid)
    #             money_available = 1
    #             wait_counter = 2
    #             num_stops = num_stops + 1
    #         #sell gains trigger
    #         elif money_available == 0 and row['14 period STOCH %K'] > 80 and row['Close'] > (price_paid*1.03):
    #             print ("take gains")
    #             print(row['14 period STOCH %K'])
    #             portfolio_value = portfolio_value * (row['Close']/price_paid)
    #             money_available = 1
    #             wait_counter = 2
    #             num_gains = num_gains = 1
    #         elif wait_counter > 0 and wait_counter <= 24:
    #             print ("wait for cash to settle")
    #             wait_counter = wait_counter - 1
    #         elif wait_counter == 0 and money_available == 1:
    #             print ("waiting for dip")
    #         elif money_available == 0:
    #             print ("holding stock")
    #             portfolio_value = 100 * (row['Close']/price_paid)
    #         else:
    #             print ("TBD")
    #             pass
    #         print (str(idx), "---", row['Close'], "---", money_available, "---",  wait_counter, "---", portfolio_value)
    #     except Exception as e:
    #         print("oops:  ", e)   

    # print (df.head(1))

    # print (num_buys)
    # print (num_stops)
    # print (num_gains)

    # print (df.tail(30))

    #def buy_logic(df, dma200, dma200_std, dma100, dma100_std, dma50, dma50_std):
    #    if dma50 > dma200 and df.iloc[-1]["Close"] < (dma - dma200_std) and df.iloc[-1]["Close"] < (dma100 - dma100_std) and df.iloc[-1]["Close"] < (dma50 - dma50_std) and df.iloc[-1]["Close"] > (dma200 - (2 * dma200_std)):
    #    buy_limit_price = dma10 - dma10_std
    #    stop_loss_price = buy_limit_price - (dma10_std * .1)
    return np.nan


def what_next(x):
    x = np.nan
#repurpose this to get chart: https://github.com/samuelsmb/Plot_stocks_with_YahooFinanceAPI/tree/main/screenshots
#https://github.com/Hotshot824/stock-plotly
#wsb sentiment: https://github.com/eddwang/YahooBets
#for fun with ML: https://github.com/deepraj21/Realtime-Stock-Predictor
    return x

def df_filter_fundamentals_2(df): #not validating here, but the input needs be a dataframe wtih "Symbol" as ticker
    try:
        df['previousClose'] = np.nan
        df['trailingPE'] = 0.0000
        df['forwardPE'] = 0.0000
        df['score'] = 0
        df['profitMargins'] = 0.0000
        df['grossMargins'] = 0.0000
        df['earningsGrowth'] = 0.0000
        df['revenueGrowth'] = 0.0000
        df['priceToSalesTrailing12Months'] = 0.0000
        df['PS_adj'] = 0.0000
        df['shortPercentOfFloat'] = 0.0000
        df['pegRatio'] = 0.0000
        df['dividendYield'] = 0.0000
        df['currentRatio'] = 0.0000
        df['quickRatio'] = 0.0000

        for idx, row in df.iterrows():
            try:
                stock_ticker = row['Symbol']
                print(stock_ticker)
                print("1")
                yq_data = yq.Ticker(stock_ticker)
                print(yq_data)

                summaryDetail = yq_data.summary_detail[list(yq_data.summary_detail)[0]]
                #print (summaryDetail)
                financialData = yq_data.financial_data[list(yq_data.financial_data)[0]]
                indexTrend = yq_data.index_trend[list(yq_data.index_trend)[0]]
                print("3")
                defaultKeyStatistics = yq_data.key_stats[list(yq_data.key_stats)[0]]
                    #summaryDetail.priceToSalesTrailing12Months 
                    #financialData.revenueGrowth
                    #financialData.grossMargins
                    #summaryDetail.trailingPE 
                    #summaryDetail.forwardPE 
                    #indexTrend.pegRatio 
                    #summaryDetail.dividendYield 
                    #financialData.earningsGrowth
                    #financialData.profitMargins
                    #defaultKeyStatistics.shortPercentOfFloat

                print("4")
                try:
                    df.at[idx, 'previousClose'] = summaryDetail['previousClose']
                except Exception as e:
                    print("oops previousClose:  ", e)
                try:
                    df.at[idx, 'dividendYield'] = summaryDetail['dividendYield']
                except Exception as e:
                    print("oops dividendYield:  ", e)
                try:
                    df.at[idx, 'pegRatio'] = indexTrend['pegRatio']
                except Exception as e:
                    print("oops pegRatio:  ", e)
                try:
                    df.at[idx, 'shortPercentOfFloat'] = defaultKeyStatistics['shortPercentOfFloat']
                except Exception as e:
                    print("oops shortPercentOfFloat:  ", e)
                try:
                    df.at[idx, 'profitMargins'] = financialData['profitMargins']
                except Exception as e:
                    print("oops profitMargins:  ", e)
                try:
                    df.at[idx, 'grossMargins'] = financialData['grossMargins']
                except Exception as e:
                    print("oops grossMargins:  ", e)
                try:
                    df.at[idx, 'earningsGrowth'] = financialData['earningsGrowth']
                except Exception as e:
                    print("oops earningsGrowth:  ", e)
                try:
                    df.at[idx, 'revenueGrowth'] = financialData['revenueGrowth']
                except Exception as e:
                    print("oops revenueGrowth:  ", e)
                try:
                    df.at[idx, 'quickRatio'] = financialData['quickRatio']
                except Exception as e:
                    print("oops quickRatio:  ", e)
                try:
                    df.at[idx, 'currentRatio'] = financialData['currentRatio']
                except Exception as e:
                    print("oops currentRatio:  ", e)

                try:
                    if financialData['revenueGrowth'] > 0:
                        test = summaryDetail['priceToSalesTrailing12Months'] * (1-(financialData['revenueGrowth'])) * (1-financialData['grossMargins'])
                    else:
                        test = summaryDetail['priceToSalesTrailing12Months'] * (1-(financialData['revenueGrowth'])) 
                    df.at[idx, 'PS_adj'] = test
                except Exception as e:
                    print("oops PS_adj:  ", e)


                try:
                    df.at[idx, 'priceToSalesTrailing12Months'] = summaryDetail['priceToSalesTrailing12Months']
                except Exception as e:
                    print("oops priceToSalesTrailing12Months:  ", e)
                try:
                    df.at[idx, 'trailingPE'] = summaryDetail['trailingPE']
                except Exception as e:
                    print("oops trailingPE:  ", e)
                try:
                    df.at[idx, 'forwardPE'] = summaryDetail['forwardPE']
                except Exception as e:
                    print("oops forwardPE:  ", e)
            except Exception as e:
                print("oops - iteration:  ", e)

        for idx, row in df.iterrows():
            score = 0
            #Scoring is as follows:
            try:
                if row['trailingPE'] < 5 and row['trailingPE'] != None and row['trailingPE'] > 0:
                    score = score + 2
                if row['trailingPE']  < 10 and row['trailingPE'] != None and row['trailingPE'] > 0:
                    score = score + 2   
                if row['trailingPE']  < 20 and row['trailingPE'] != None and row['trailingPE'] > 0:
                    score = score + 2
                if row['trailingPE']  < 999 and row['trailingPE'] != None and row['trailingPE'] > 0:
                    score = score + 2 

                if (row['revenueGrowth'] != None and row['revenueGrowth'] > 0) and row['PS_adj'] < 2 and row['grossMargins'] > 0:
                    score = score + 2
                if (row['revenueGrowth'] != None and row['revenueGrowth'] > 0.1) and row['PS_adj'] < 2.1 and row['grossMargins'] > 0:
                    score = score + 2  
                if (row['revenueGrowth'] != None and row['revenueGrowth'] > 0.2) and row['PS_adj'] < 2.2 and row['grossMargins'] > 0:
                    score = score + 2  
                if (row['revenueGrowth'] != None and row['revenueGrowth'] > 0.3) and row['PS_adj'] < 2.3 and row['grossMargins'] > 0:
                    score = score + 2  
                if (row['revenueGrowth'] != None and row['revenueGrowth'] > 0.4) and row['PS_adj'] < 2.4 and row['grossMargins'] > 0:
                    score = score + 2

    #            if row['pegRatio'] < 1 and row['pegRatio'] > 0:
    #                score = score + 2

                df.at[idx, 'score'] = score
            except Exception as e:
                print("oops - score:  ", e)
        df['priceToSalesTrailing12Months'].astype(float)
        df['revenueGrowth'].astype(float)
        df['grossMargins'].astype(float)
        df['trailingPE'].astype(float)
        df['forwardPE'].astype(float)
        df['PS_adj'].astype(float)
        df['pegRatio'].astype(float)
        df['earningsGrowth'].astype(float)
        df['profitMargins'].astype(float)
        df['shortPercentOfFloat'].astype(float)
        df['dividendYield'].astype(float)
        df['quickRatio'].astype(float)
        df['currentRatio'].astype(float)

        df['priceToSalesTrailing12Months'] = df['priceToSalesTrailing12Months'].map(lambda x: round(x, 2) if isinstance(x, float) else 0)
        df['revenueGrowth'] = round(df['revenueGrowth'], 4)*100
        df['grossMargins'] = round(df['grossMargins'], 4)*100
        df['trailingPE'] = df['trailingPE'].map(lambda x: round(x, 2) if isinstance(x, float) else 0)
        df['forwardPE'] = df['forwardPE'].map(lambda x: round(x, 2) if isinstance(x, float) else 0)
        df['PS_adj'] = df['PS_adj'].map(lambda x: round(x, 2) if isinstance(x, float) else 0)
        df['pegRatio'] = df['pegRatio'].map(lambda x: round(x, 2) if isinstance(x, float) else 0)
        df['earningsGrowth'] = round(df['earningsGrowth'], 4)*100
        df['profitMargins'] = round(df['profitMargins'], 4)*100
        df['shortPercentOfFloat'] = round(df['shortPercentOfFloat'], 4)*100
        df['dividendYield'] = round(df['dividendYield'], 4)*100
        df = df[['Symbol', 'priceToSalesTrailing12Months', 'revenueGrowth', 'quickRatio', 'currentRatio', 'grossMargins', 'trailingPE', 'forwardPE', 'PS_adj', 'pegRatio', 'dividendYield', 'earningsGrowth', 'profitMargins',  'shortPercentOfFloat', 'score']]
        print (df)
    except: 
        df = df
    return df

def df_filter_fundamentals_3(df): #not validating here, but the input needs be a dataframe wtih "Symbol" as ticker
    try:
        df['previousClose'] = np.nan
        df['trailingPE'] = 0.0000
        df['forwardPE'] = 0.0000
        df['score'] = 0
        df['profitMargins'] = 0.0000
        df['grossMargins'] = 0.0000
        df['earningsGrowth'] = 0.0000
        df['revenueGrowth'] = 0.0000
        df['priceToSalesTrailing12Months'] = 0.0000
        df['PS_adj'] = 0.0000
        df['shortPercentOfFloat'] = 0.0000
        df['pegRatio'] = 0.0000
        df['dividendYield'] = 0.0000
        df['currentRatio'] = 0.0000
        df['quickRatio'] = 0.0000

        for idx, row in df.iterrows():
            try:
                stock_ticker = row['Symbol']
                print(stock_ticker)
                yq_data = yf.Ticker(stock_ticker)

                try:
                    previousClose = yq_data.basic_info['regularMarketPreviousClose']
                    df.at[idx, 'previousClose'] = previousClose
                except Exception as e:
                    print("oops previousClose:  ", e)
                try:
                    DividendYield = yq_data.dividends.head(4).sum()/previousClose
                    df.at[idx, 'dividendYield'] = DividendYield
                except Exception as e:
                    print("oops dividendYield:  ", e)
                try:
                    df.at[idx, 'pegRatio'] = .99
                except Exception as e:
                    print("oops pegRatio:  ", e)
                try:
                    df.at[idx, 'shortPercentOfFloat'] = .99
                except Exception as e:
                    print("oops shortPercentOfFloat:  ", e)
                try:
                    df.at[idx, 'profitMargins'] = .99
                except Exception as e:
                    print("oops profitMargins:  ", e)
                try:
                    BS = yq_data.quarterly_balancesheet
                    col1 = BS.columns[0]
                    #col5 = BS.columns[4]
                    currentRatio = BS.at[("Current Assets", col1)]/BS.at[("Current Liabilities", col1)]
                    quickRatio = (BS.at[("Current Assets", col1)] - BS.at[("Inventory", col1)])/BS.at[("Current Liabilities", col1)]
                    ###need to fix.  Too low typically.
                    #quickRatio = BS.at[("Cash And Cash Equivalents", col1)]/BS.at[("Current Liabilities", col1)]
                    df.at[idx, 'currentRatio'] = currentRatio
                    df.at[idx, 'quickRatio'] = quickRatio
                except Exception as e:
                    print("oops BALANCE SHEET STUFF:  ", e)
                try:
                    IS = yq_data.quarterly_incomestmt
                    income_col1 = IS.columns[0]
                    income_col2 = IS.columns[1]
                    income_col3 = yq_data.quarterly_incomestmt.columns[2]
                    income_col4 = IS.columns[3]
                    income_col5 = IS.columns[4]
                    PriceToSalesRatioTTM = yq_data.basic_info['marketCap']/(IS.at[("Total Revenue", income_col1)] + IS.at[("Total Revenue", income_col2)] + IS.at[("Total Revenue", income_col3)] + IS.at[("Total Revenue", income_col4)])
                    TrailingPE = yq_data.basic_info['marketCap']/(IS.at[("Net Income", income_col1)] + IS.at[("Net Income", income_col2)] + IS.at[("Net Income", income_col3)] + IS.at[("Net Income", income_col4)])
                    QuarterlyEarningsGrowthYOY = (IS.at[("Net Income", income_col1)] - IS.at[("Net Income", income_col5)] ) / IS.at[("Total Revenue", income_col1)] 
                    QuarterlyRevenueGrowthYOY = (IS.at[("Total Revenue", income_col1)] - IS.at[("Total Revenue", income_col5)] ) / IS.at[("Total Revenue", income_col1)] 
                    GrossProfitTTM = IS.at[("Gross Profit", income_col1)] / IS.at[("Total Revenue", income_col1)] 
                    df.at[idx, 'grossMargins'] = GrossProfitTTM
                    df.at[idx, 'earningsGrowth'] = QuarterlyEarningsGrowthYOY
                    df.at[idx, 'revenueGrowth'] = QuarterlyRevenueGrowthYOY
                    df.at[idx, 'priceToSalesTrailing12Months'] = PriceToSalesRatioTTM
                    df.at[idx, 'trailingPE'] = TrailingPE
                except Exception as e:
                    print("oops INCOME STMT STUFF:  ", e)

                try:
                    PS_adj = 0
                    if QuarterlyRevenueGrowthYOY > 0:
                        PS_adj = PriceToSalesRatioTTM * (1-QuarterlyRevenueGrowthYOY) * (1-GrossProfitTTM)
                    else:
                        PS_adj = PriceToSalesRatioTTM * (1-QuarterlyRevenueGrowthYOY) 
                    df.at[idx, 'PS_adj'] = PS_adj
                except Exception as e:
                    print("oops PS_adj:  ", e)
                try:
                    earnings_dates = pd.DataFrame()
                    earnings_dates = yq_data.earnings_dates
                    forwardPE = previousClose/earnings_dates[earnings_dates['EPS Estimate'].notnull()]['EPS Estimate'].head(4).sum()
                    df.at[idx, 'forwardPE'] = forwardPE
                    print(previousClose/earnings_dates[earnings_dates['Reported EPS'].notnull()]['Reported EPS'].head(4).sum())
                    try:
                        TrailingPE = previousClose/earnings_dates[earnings_dates['Reported EPS'].notnull()]['Reported EPS'].head(4).sum()
                #TrailingPE = yq_data.basic_info['marketCap']/(IS.at[("Net Income", income_col1)] + IS.at[("Net Income", income_col2)] + IS.at[("Net Income", income_col3)] + IS.at[("Net Income", income_col4)])
                        df.at[idx, 'trailingPE'] = TrailingPE
                    except Exception as e: 
                        print("oops Trailing PE retry no worky:  ", e)

                except Exception as e:
                    print("oops forwardPE:  ", e)
            except Exception as e:
                print("oops - iteration:  ", e)

        for idx, row in df.iterrows():
            score = 0
            #Scoring is as follows:
            try:
                if row['trailingPE'] < 5 and row['trailingPE'] != None and row['trailingPE'] > 0:
                    score = score + 2
                if row['trailingPE']  < 10 and row['trailingPE'] != None and row['trailingPE'] > 0:
                    score = score + 2   
                if row['trailingPE']  < 20 and row['trailingPE'] != None and row['trailingPE'] > 0:
                    score = score + 2
                if row['trailingPE']  < 999 and row['trailingPE'] != None and row['trailingPE'] > 0:
                    score = score + 2 

                if (row['revenueGrowth'] != None and row['revenueGrowth'] > 0) and row['PS_adj'] < 2 and row['grossMargins'] > 0:
                    score = score + 2
                if (row['revenueGrowth'] != None and row['revenueGrowth'] > 0.1) and row['PS_adj'] < 2.1 and row['grossMargins'] > 0:
                    score = score + 2  
                if (row['revenueGrowth'] != None and row['revenueGrowth'] > 0.2) and row['PS_adj'] < 2.2 and row['grossMargins'] > 0:
                    score = score + 2  
                if (row['revenueGrowth'] != None and row['revenueGrowth'] > 0.3) and row['PS_adj'] < 2.3 and row['grossMargins'] > 0:
                    score = score + 2  
                if (row['revenueGrowth'] != None and row['revenueGrowth'] > 0.4) and row['PS_adj'] < 2.4 and row['grossMargins'] > 0:
                    score = score + 2

    #            if row['pegRatio'] < 1 and row['pegRatio'] > 0:
    #                score = score + 2

                df.at[idx, 'score'] = score
            except Exception as e:
                print("oops - score:  ", e)
        df['priceToSalesTrailing12Months'].astype(float)
        df['revenueGrowth'].astype(float)
        df['grossMargins'].astype(float)
        df['trailingPE'].astype(float)
        df['forwardPE'].astype(float)
        df['PS_adj'].astype(float)
        df['pegRatio'].astype(float)
        df['earningsGrowth'].astype(float)
        df['profitMargins'].astype(float)
        df['shortPercentOfFloat'].astype(float)
        df['dividendYield'].astype(float)
        df['quickRatio'].astype(float)
        df['currentRatio'].astype(float)

        df['priceToSalesTrailing12Months'] = df['priceToSalesTrailing12Months'].map(lambda x: round(x, 2) if isinstance(x, float) else 0)
        df['revenueGrowth'] = round(df['revenueGrowth'], 4)*100
        df['grossMargins'] = round(df['grossMargins'], 4)*100
        df['trailingPE'] = df['trailingPE'].map(lambda x: round(x, 2) if isinstance(x, float) else 0)
        df['forwardPE'] = df['forwardPE'].map(lambda x: round(x, 2) if isinstance(x, float) else 0)
        df['PS_adj'] = df['PS_adj'].map(lambda x: round(x, 2) if isinstance(x, float) else 0)
        df['pegRatio'] = df['pegRatio'].map(lambda x: round(x, 2) if isinstance(x, float) else 0)
        df['earningsGrowth'] = round(df['earningsGrowth'], 4)*100
        df['profitMargins'] = round(df['profitMargins'], 4)*100
        df['shortPercentOfFloat'] = round(df['shortPercentOfFloat'], 4)*100
        df['dividendYield'] = round(df['dividendYield'], 4)*100
        df = df[['Symbol', 'priceToSalesTrailing12Months', 'revenueGrowth', 'quickRatio', 'currentRatio', 'grossMargins', 'trailingPE', 'forwardPE', 'PS_adj', 'pegRatio', 'dividendYield', 'earningsGrowth', 'profitMargins',  'shortPercentOfFloat', 'score']]
        print (df)
    except: 
        df = df
    return df

def create_html_section(filename, title):
    current_time = datetime.datetime.now()
    pd.set_option("display.max_colwidth", 10000)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'data', filename)
    data = pd.read_csv(filepath, encoding='iso-8859-1')
    print(data.shape)
    print(data.shape)
    #change made in July 2024 to change this from score + Total TA.  Focus more on TA
    data = data.sort_values(['Total_TA', 'score'], ascending=[False, False])
    data = data.head(5)
    print(data.shape)
    yday = current_time - timedelta(days=3)
    yday = yday.strftime("%Y-%m-%d")
    data = data[(data['date_field'] >= yday)]
    data = data.drop('Unnamed: 0', axis=1).head(5)

    #save to history to look back on later
    data.reset_index(inplace = True)
    data['daily_rank'] = data.index
    data = data.drop('index', axis=1)
    file_name_historical = filename[:-4] + "_historical.csv"
    try:
        filepath = os.path.join(dir_path, 'data', file_name_historical)
        if os.path.isfile(filepath) == True:
            historical_data = pd.read_csv(filepath, encoding='iso-8859-1')
            historical_data_concat = pd.concat([historical_data, data], axis=0, ignore_index=True)
            historical_data_concat.to_csv(filepath, index=False)
            bucketname = "data.fuzzyforrest.ai"
            s3 = boto3.client('s3')
            s3.upload_file(filepath, bucketname, file_name_historical)
            s3 = boto3.resource('s3')
            s3_object = s3.Object(bucketname, file_name_historical)
            s3_object.copy_from(
                CopySource={'Bucket': bucketname,'Key': file_name_historical},
                MetadataDirective="REPLACE",
                ContentType='text/csv',
                ACL='public-read'
            ) 
        else:
            pass
    except Exception as error:
        print("An exception occurred with historical merge:", error)

    print(data.shape)
    ticker_formatted_list = [('$' + x) for x in data['ticker'].to_list()]
    alternatives = ["Data helps navigate the markets", "Behold the beauty of data: ", "Transparent past performance of this algo available here: ", "View Stratify's past performance:", "Automated stock screener for today:", "Still using manual stock screeners?", "Solving the market mystery:", "Skip the hunch, trust the data", "No bias here - just data", "And the algo says...", "Here to help individual investors", "Looking for investment ideas?", "Setups based on historical patterns:",  "Wondering what to do on market open?", "Setups for tomorrow...", "Buy ideas:", "Want to go long individual stocks?", "Tickers of interest:", "Stratify's daily analysis is ready:", "Today's algo picks based on technicals and fundamentals:", "Daily algo picks:", "Full transparency of past performance", "Automated trading with Python", "#Python #Trading", "#quant", "#AutomatedTrading"]
    tweet = f""" {' '.join(ticker_formatted_list)} \r\r #{title.replace(" ", "")} \r\r {random.choice(alternatives)} \r\r https://stratifydataconsulting.com/daily_analysis.html"""
    tweet_txt_file = open(f"C:/git/stock_analysis_app/{title}_tweets.txt", "w")
    tweet_txt_file.write(tweet)
    tweet_txt_file.write("\r")
    tweet_txt_file.close()

    data['BestOptionsSymbol'] = ''
    data['longBusinessSummary']= ''
    data['CompanyName']= ''

    try:
        data['CompanyName'] = data.apply(lambda x: get_company_name(x.ticker), axis=1)
    except Exception as error:
        print("An exception occurred with companyname:", error)

    try:
        data['longBusinessSummary'] = data.apply(lambda x: get_summary(x.ticker), axis=1)
    except Exception as error:
        print("An exception occurred with summary:", error)

    print(data.shape)
    for idx, row in data.iterrows():
        print(row.ticker)
        try:
            data.at[idx,'BestOptionsSymbol'] = get_best_option(row.ticker)
        except:
            print("oops....exception occurred with BestOptionsSymbOL................")
    try:
        data['MyPlot'] = data['ticker'].map(lambda x: plot_ticker(x))
    except Exception as error:
        print("An exception occurred with plots:", error)

    html_add = f"""
    <div class="myDiv">
    <h2>{title} Analysis</h2>
        <p>The following is based on 20+ technical data points (e.g., RSI, moving averages, Bollinger Bands, ADX, MACD, fractal supports) and fundamentals (e.g., PE, PS, growth).</p>  
        <p>The data is then filtered to remove any going concerns (using current and quick ratios) and remove any fundamentally subpar companies.  The results are sorted by highest score.  </p>
        <p>Note: This should not be considered investing advice. The publisher makes no claims on the accuracy of the data provided. </p>
    </div>
    """


    html_card_scroll = f"""
    <section>
    <h2>{title} - Top Fundamental and Technical Combined Scoring</h2>
    <p>Updated {current_time.strftime("%B %d, %Y %H:%I")}</p>
    <div class="cards-wrapper">

    """
    html_cards = ""
    for idx, row in data.iterrows():
            html_cards = html_cards + generate_card_html(row)
            html_file_name = f"{row.ticker.upper()}_card.html"
            html_file_path = f"C:/git/stock_analysis_app/html/{html_file_name}"
            file_html = open(html_file_path, "w")
            file_html.write(get_html_header())
            file_html.write(html_add)
            file_html.write(remove_non_ascii(html_cards))
            file_html.write(get_html_end())
            file_html.close()
            upload_html_to_aws_from_file_dirpath(html_file_name, "data.fuzzyforrest.ai")
    html_card_scroll_end = """
    </div>
    </section>
    """
    html_header = """
    </style>
    <body>
    <center>
    <a href = "./index.html"><img src='./logo16.png'  width="100" height="100" align="center"></a>
    </center>
    <br>
    """
    # Creating the HTML file
    file_name_html = filename[:-12] + "section.html"
    file_html = open(f"C:/git/stock_analysis_app/{file_name_html}", "w")
    file_html.write(get_html_header())
    file_html.write(html_add)
    if len(data) != 0:
        file_html.write(html_card_scroll)
        file_html.write(remove_non_ascii(html_cards))
        file_html.write(html_card_scroll_end)
    else:
        file_html.write(f"""<h2>{title} - Top Fundamental and Technical Combined Scoring</h2> <p>Updated {current_time.strftime("%B %d, %Y %H:%I")}</p> <p> No good setups today</p>""")

    file_html.write(get_html_end())
    file_html.close()

    # Upload to AWS S3
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, file_name_html)
    #this will move in bat file to html folder

    bucketname = "data.fuzzyforrest.ai"
    #s3 = boto3.resource('s3')
    #data = open(file_name, 'rb')
    #s3.Bucket(bucketname).put_object(Key=file_name_html, Body=data)
    s3 = boto3.client('s3')
    s3.upload_file(filepath, bucketname, file_name_html)
    s3.put_object_acl(Bucket=bucketname, Key=file_name_html, ACL='public-read')
    s3 = boto3.resource('s3')
    s3_object = s3.Object(bucketname, file_name_html)
    #s3_object.metadata.update({'Content-Type':'text/html'})
    s3_object.copy_from(CopySource={'Bucket': bucketname,
                                'Key': file_name_html},
                    MetadataDirective="REPLACE",
                    ContentType="text/html",
                    ACL='public-read')
    return None

def get_ta_reasons(df, ta_cols):
    df['reasons'] = ""
    for idx, row in df.iterrows():
        all_cols = ""
        for item in ta_cols:
            if row[item]:
                if row[item] > 0:
                    all_cols = all_cols + item + "; "
                else:
                    pass
            else:
                pass
        df.at[idx,'reasons'] = all_cols
    return df


def get_all_tickers_list():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'data', 'all_caps_analysis.csv')#.csv
    data = pd.read_csv(filepath, encoding='iso-8859-1')
    return data['ticker'].to_list()

def get_all_algo_buys():
    the_tickers_to_buy = []
    #filename = 'large_caps_analysis.csv'

    print("-------------mega--------------")
    filename = 'mega_cap_analysis.csv'
    current_time = datetime.datetime.now()
    pd.set_option("display.max_colwidth", 10000)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'data', filename)
    data = pd.read_csv(filepath, encoding='iso-8859-1')
    data = data[(data['currentRatio'] > 1.2) & (data['quickRatio'] > 1.0)]
    data = data[((data['score'] >= 4) & (data['Total_TA'] > 8))]
    yday = current_time - timedelta(days=2)
    yday = yday.strftime("%Y-%m-%d")
    data = data[(data['date_field'] >= yday)]
    data = data.sort_values(by='t_and_f_score', ascending=False)
    data = data[['ticker', 'Total', 'score', 't_and_f_score']].head(10)
    print(data)
    print(data['t_and_f_score'].mean())
    the_tickers_to_buy.extend(data['ticker'].to_list())

    print("-------------large--------------")
    filename = 'large_cap_analysis.csv'
    current_time = datetime.datetime.now()
    pd.set_option("display.max_colwidth", 10000)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'data', filename)
    data = pd.read_csv(filepath, encoding='iso-8859-1')
    data = data[(data['currentRatio'] > 1.2) & (data['quickRatio'] > 1.0)]
    data = data[((data['score'] >= 4) & (data['Total_TA'] > 8))]

    yday = current_time - timedelta(days=2)
    yday = yday.strftime("%Y-%m-%d")
    data = data[(data['date_field'] >= yday)]
    data = data.sort_values(by='t_and_f_score', ascending=False)
    data = data[['ticker', 'Total', 'score', 't_and_f_score']].head(10)
    print(data)
    print(data['t_and_f_score'].mean())
    the_tickers_to_buy.extend(data['ticker'].to_list())

    print("-------------mid--------------")
    filename = 'mid_cap_analysis.csv'
    current_time = datetime.datetime.now()
    pd.set_option("display.max_colwidth", 10000)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'data', filename)
    data = pd.read_csv(filepath, encoding='iso-8859-1')
    data = data[(data['currentRatio'] > 1.2) & (data['quickRatio'] > 1.0)]
    data = data[((data['score'] >= 4) & (data['Total_TA'] > 8))]
    print(data[['ticker', 'date_field', 'Total', 'score', 't_and_f_score']])

    yday = current_time - timedelta(days=2)
    yday = yday.strftime("%Y-%m-%d")
    data = data[(data['date_field'] >= yday)]
    print(data.shape)
    data = data.sort_values(by='t_and_f_score', ascending=False)
    data = data[['ticker', 'Total', 'score', 't_and_f_score']].head(10)
    print(data)
    print(data['t_and_f_score'].mean())
    the_tickers_to_buy.extend(data['ticker'].to_list())

    print("-------------small--------------")
    filename = 'small_cap_analysis.csv'
    current_time = datetime.datetime.now()
    pd.set_option("display.max_colwidth", 10000)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'data', filename)
    data = pd.read_csv(filepath, encoding='iso-8859-1')
    data = data[(data['currentRatio'] > 1.2) & (data['quickRatio'] > 1.0)]
    data = data[((data['score'] >= 4) & (data['Total_TA'] > 8))]
    yday = current_time - timedelta(days=2)
    yday = yday.strftime("%Y-%m-%d")
    data = data[(data['date_field'] >= yday)]
    data = data.sort_values(by='t_and_f_score', ascending=False)
    data = data[['ticker', 'Total', 'score', 't_and_f_score']].head(10)
    print(data)
    print(data['t_and_f_score'].mean())
    the_tickers_to_buy.extend(data['ticker'].to_list())

    return the_tickers_to_buy



def get_all_algo_buys2():
    the_tickers_to_buy = []

    print("-------------mega--------------")
    filename = 'mega_cap_analysis.csv'
    pd.set_option("display.max_colwidth", 10000)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'data', filename)
    data = pd.read_csv(filepath, encoding='iso-8859-1')
    data = data.sort_values(by=['Total_TA', 't_and_f_score'], ascending=[False, False])
    data = data[['ticker', 'Total', 'score', 't_and_f_score']].head(1)
    the_tickers_to_buy.extend(data['ticker'].to_list())
    the_tickers_to_buy = [x.upper() for x in the_tickers_to_buy]

    print("-------------large--------------")
    filename = 'large_cap_analysis.csv'
    pd.set_option("display.max_colwidth", 10000)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'data', filename)
    data = pd.read_csv(filepath, encoding='iso-8859-1')
    data = data.sort_values(by=['Total_TA', 't_and_f_score'], ascending=[False, False])
    data = data[['ticker', 'Total', 'score', 't_and_f_score']].head(1)
    the_tickers_to_buy.extend(data['ticker'].to_list())
    the_tickers_to_buy = [x.upper() for x in the_tickers_to_buy]

    print("-------------mid--------------")
    filename = 'mid_cap_analysis.csv'
    pd.set_option("display.max_colwidth", 10000)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'data', filename)
    data = pd.read_csv(filepath, encoding='iso-8859-1')
    data = data.sort_values(by=['Total_TA', 't_and_f_score'], ascending=[False, False])
    data = data[['ticker', 'Total', 'score', 't_and_f_score']].head(1)
    the_tickers_to_buy.extend(data['ticker'].to_list())
    the_tickers_to_buy = [x.upper() for x in the_tickers_to_buy]

    print("-------------small--------------")
    filename = 'small_cap_analysis.csv'
    pd.set_option("display.max_colwidth", 10000)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'data', filename)
    data = pd.read_csv(filepath, encoding='iso-8859-1')
    data = data.sort_values(by=['Total_TA', 't_and_f_score'], ascending=[False, False])
    data = data[['ticker', 'Total', 'score', 't_and_f_score']].head(1)
    the_tickers_to_buy.extend(data['ticker'].to_list())
    the_tickers_to_buy = [x.upper() for x in the_tickers_to_buy]

    return the_tickers_to_buy



def get_all_algo_buys_new():

#get stocks ready to jump based on 15 min data
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'data', '15min_report_eric_stocks.csv')#.csv
    df = pd.read_csv(filepath, encoding='iso-8859-1')
    df = df[(df['Total_30min'] > 0)]
    df = df[(df['Total_4h'] > 0)]
    df = df[(df['score'] > 2)]
    df['agg_signals'] = df['Total_4h'] + df['Total_30min'] + df['Total_30d_TA'] + df['Total_kmeans_st'] 
    df = df.sort_values(by=['agg_signals'], ascending=False).head(10)
    buy_list = df.ticker.to_list()
    buy_list = [x.upper() for x in buy_list]

    return buy_list

def get_all_algo_buys_TA_best():

#get stocks ready to jump based on 15 min data
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'data', 'all_caps_analysis.csv')#.csv
    df = pd.read_csv(filepath, encoding='iso-8859-1')
    df = df[(df['Total_overfit'] >= 5)]
    df = df[(df['Total_kmeans'] >= 5)]
    df = df[(df['Total_kmeans_st'] >= 1)]
#    df['agg_signals'] = df['Total_4h'] + df['Total_30min'] + df['Total_30d_TA'] + df['Total_kmeans_st'] 
    df = df.sort_values(by=['Total_TA', 'score', 'marketCap'], ascending=[False, False, False]).head(1)
    print(df.shape)
    buy_list = df.ticker.to_list()
    return buy_list


def get_all_algo_buys_new_options():

#get stocks ready to jump based on 15 min data
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'data', '15min_report_eric_stocks.csv')#.csv
    #df = pd.read_csv(filepath, encoding='iso-8859-1')
    df = df[(df['Total_15min'] > 0)]
    df = df[(df['Total_15min_4h'] > 0)]
    df['agg_signals'] = df['Total_15min_4h'] + df['Total_15min_']
    df = df.sort_values(by=['agg_signals'], ascending=False).head(10)
    buy_list1 = df.tickers.to_list()


#get best valued options short list from my stocks
    exp_date = get_options_date_3mo('GOOG')
    ticker_list = get_my_ticker_list()
    final_list = []
    for ticker in ticker_list:
        the_ticker = yf.Ticker(ticker)
        try:
            #final_list.append(get_put_options_data_atm_price(ticker, exp_date))
            final_list.append(get_call_options_data_atm_price(ticker, exp_date))
        except:
            pass
    df = pd.DataFrame(final_list, columns = ['ticker', 'ATM Call Price / Underlying Price', 'IV', 'rate_return', 'openInterest', 'type'])
    df['options_value'] = df['ATM Call Price / Underlying Price']/(1 + df['IV'])
    df['exp_date'] = exp_date
    df.sort_values(by=['ATM Call Price / Underlying Price'], ascending=True)
    df = df.head(20)
    df.sort_values(by=['options_value'], ascending=False)
    df = df.head(10)
    buy_list2 = df.ticker.to_list() 

#merge buy lists
    buy_list = []
    for element in buy_list1:
        if element in buy_list2:
            buy_list.append(element)
    return buy_list

def get_random_tickers(x):
    the_tickers_to_buy = []
    filename = 'all_caps_analysis.csv'
    pd.set_option("display.max_colwidth", 10000)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'data', filename)
    data = pd.read_csv(filepath, encoding='iso-8859-1')
    data = data[['ticker', 'Total', 'score', 't_and_f_score']].sample(x)
    the_tickers_to_buy.extend(data['ticker'].to_list())
    the_tickers_to_buy = [x.upper() for x in the_tickers_to_buy]
    return the_tickers_to_buy

def get_random_ticker():
    the_tickers_to_buy = []
    filename = 'all_caps_analysis.csv'
    pd.set_option("display.max_colwidth", 10000)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'data', filename)
    data = pd.read_csv(filepath, encoding='iso-8859-1')
    data = data[['ticker', 'Total', 'score', 't_and_f_score']].sample(1)
    the_tickers_to_buy.extend(data['ticker'].to_list())
    the_tickers_to_buy = [x.upper() for x in the_tickers_to_buy]
    return the_tickers_to_buy[0]


def get_all_algo_shorts():
    the_tickers_to_short = []
    #filename = 'overvalued_short_analysis.csv'
    print("-------------short--------------")
    filename = 'overvalued_short_analysis.csv'
    current_time = datetime.datetime.now()
    pd.set_option("display.max_colwidth", 10000)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'data', filename)
    data = pd.read_csv(filepath, encoding='iso-8859-1')
    data = data[(data['combo_top_indicator'] < 0)]
    #data = data[(data['currentRatio'] < .07) | (data['quickRatio'] < .05) | (data['combo_top_indicator'] < 0)]
    current_time = datetime.datetime.now()
    yday = current_time - timedelta(days=2)
    yday = yday.strftime("%Y-%m-%d")
    data = data[(data['date_field'] >= yday)]
    the_tickers_to_short.extend(data['ticker'].to_list())

    return the_tickers_to_short

def get_best_option(symbol):
    the_ticker = yf.Ticker(symbol)
    current_price_underlying = the_ticker.info['currentPrice']
    highest_oi = 0
    cheapest = 10000
    return_contract_symbol = ""
    for x in the_ticker.options:
        current_time = datetime.datetime.now()
        exp_date = datetime.datetime.strptime(x, "%Y-%m-%d")
        min_theta_buffer = 60
        date_buffer = current_time + timedelta(days=min_theta_buffer)
        minimum_oi = 200
        if exp_date > date_buffer:
            the_chain_o_calls = the_ticker.option_chain(x).calls
            the_chain_o_calls['openInterest']
            call_options = pd.DataFrame(the_ticker.option_chain(x).calls)
            itm_call_options = call_options[call_options['inTheMoney'] == False]
            avg_atm_price = round(((itm_call_options.tail(1)['bid'].values[0] + itm_call_options.tail(1)['ask'].values[0])/2), 1)
            atm_price_pct_of_underlying = avg_atm_price/current_price_underlying
            iv = itm_call_options.head(1)['impliedVolatility'].values[0]
            openInterest = itm_call_options.head(1)['openInterest'].values[0]
            if openInterest >= highest_oi and openInterest >= minimum_oi:
                highest_oi = openInterest
                return_contract_symbol = itm_call_options.head(1)['contractSymbol'].values[0]
                # if atm_price_pct_of_underlying < cheapest: ###need to account for theta which is logritmic and not in scope now
                #     cheapest = atm_price_pct_of_underlying
                #     print("----cheapest-------")
                #     print (atm_price_pct_of_underlying)
                #     print(itm_call_options.head(1))
            else:
                pass
        else:
            pass
    return return_contract_symbol

# def get_best_option_v2(symbol):
#     the_ticker = yf.Ticker(symbol)
#     for x in the_ticker.options:
#         exp_date = datetime.datetime.strptime(x, "%Y-%m-%d")
#         min_theta_buffer = 60
#         date_buffer = current_time + timedelta(days=min_theta_buffer)
#         minimum_oi = 200
#         if exp_date > date_buffer:
#             the_chain_o_calls = the_ticker.option_chain(x).calls
#             the_chain_o_calls['openInterest']
#             call_options = pd.DataFrame(the_ticker.option_chain(x).calls)
#             itm_call_options = call_options[call_options['inTheMoney'] == True]
#             avg_atm_price = round(((itm_call_options.tail(1)['bid'].values[0] + itm_call_options.tail(1)['ask'].values[0])/2), 1)
#             openInterest = itm_call_options.head(1)['openInterest'].values[0]
#             if openInterest >= highest_oi and openInterest >= minimum_oi:
#                 highest_oi = openInterest
#                 return_contract_symbol = itm_call_options.head(1)['contractSymbol'].values[0]
#                 # if atm_price_pct_of_underlying < cheapest: ###need to account for theta which is logritmic and not in scope now
#                 #     cheapest = atm_price_pct_of_underlying
#                 #     print("----cheapest-------")
#                 #     print (atm_price_pct_of_underlying)
#                 #     print(itm_call_options.head(1))
#             else:
#                 pass
#         else:
#             pass
#     return return_contract_symbol


def get_option_3mo_out(symbol):
    the_ticker = yf.Ticker(symbol)
    current_price_underlying = the_ticker.info['currentPrice']
    highest_oi = 0
    cheapest = 10000
    return_contract_symbol = ""
    counter = 1
    for x in the_ticker.options:
        current_time = datetime.datetime.now()
        exp_date = datetime.datetime.strptime(x, "%Y-%m-%d")
        min_theta_buffer = 60
        date_buffer = current_time + timedelta(days=min_theta_buffer)
        if exp_date > date_buffer and counter ==1:
            the_chain_o_calls = the_ticker.option_chain(x).calls
            call_options = pd.DataFrame(the_ticker.option_chain(x).calls)
            itm_call_options = call_options[call_options['inTheMoney'] == False]
            print(itm_call_options)
            return_contract_symbol = itm_call_options.head(1)['contractSymbol'].values[0]
            #MSFT261218C00405000 85
            counter  = counter + 1
        else:
            pass
    return return_contract_symbol

def get_option_3mo_out_itm(symbol):
    the_ticker = yf.Ticker(symbol)
    current_price_underlying = the_ticker.info['currentPrice']
    highest_oi = 0
    cheapest = 10000
    return_contract_symbol = ""
    counter = 1
    for x in the_ticker.options:
        current_time = datetime.datetime.now()
        exp_date = datetime.datetime.strptime(x, "%Y-%m-%d")
        min_theta_buffer = 60
        date_buffer = current_time + timedelta(days=min_theta_buffer)
        if exp_date > date_buffer and counter ==1:
            the_chain_o_calls = the_ticker.option_chain(x).calls
            call_options = pd.DataFrame(the_ticker.option_chain(x).calls)
            itm_call_options = call_options[call_options['inTheMoney'] == True]
            print(itm_call_options)
            return_contract_symbol = itm_call_options.tail(1)['contractSymbol'].values[0]
            #MSFT261218C00405000 85
            counter  = counter + 1
        else:
            pass
    return return_contract_symbol


def get_option_1mo_out(symbol):
    the_ticker = yf.Ticker(symbol)
    current_price_underlying = the_ticker.info['currentPrice']
    highest_oi = 0
    cheapest = 10000
    return_contract_symbol = ""
    counter = 1
    for x in the_ticker.options:
        current_time = datetime.datetime.now()
        exp_date = datetime.datetime.strptime(x, "%Y-%m-%d")
        min_theta_buffer = 10
        date_buffer = current_time + timedelta(days=min_theta_buffer)
        if exp_date > date_buffer and counter ==1:
            the_chain_o_calls = the_ticker.option_chain(x).calls
            call_options = pd.DataFrame(the_ticker.option_chain(x).calls)
            itm_call_options = call_options[call_options['inTheMoney'] == False]
            print(itm_call_options)
            return_contract_symbol = itm_call_options.head(1)['contractSymbol'].values[0]
            #MSFT261218C00405000 85
            counter  = counter + 1
        else:
            pass
    return return_contract_symbol

def get_option_2dte(symbol):
    the_ticker = yf.Ticker(symbol)
    current_price_underlying = the_ticker.info['currentPrice']
    highest_oi = 0
    cheapest = 10000
    return_contract_symbol = ""
    counter = 1
    for x in the_ticker.options:
        current_time = datetime.datetime.now()
        exp_date = datetime.datetime.strptime(x, "%Y-%m-%d")
        min_theta_buffer = 2
        date_buffer = current_time + timedelta(days=min_theta_buffer)
        if exp_date > date_buffer and counter ==1:
            the_chain_o_calls = the_ticker.option_chain(x).calls
            call_options = pd.DataFrame(the_ticker.option_chain(x).calls)
            itm_call_options = call_options[call_options['inTheMoney'] == False]
            print(itm_call_options)
            return_contract_symbol = itm_call_options.head(1)['contractSymbol'].values[0]
            #MSFT261218C00405000 85
            counter  = counter + 1
        else:
            pass
    return return_contract_symbol

def get_option_2dte(symbol):
    the_ticker = yf.Ticker(symbol)
    current_price_underlying = the_ticker.info['currentPrice']
    highest_oi = 0
    cheapest = 10000
    return_contract_symbol = ""
    counter = 1
    for x in the_ticker.options:
        current_time = datetime.datetime.now()
        exp_date = datetime.datetime.strptime(x, "%Y-%m-%d")
        min_theta_buffer = 2
        date_buffer = current_time + timedelta(days=min_theta_buffer)
        if exp_date > date_buffer and counter ==1:
            the_chain_o_calls = the_ticker.option_chain(x).calls
            call_options = pd.DataFrame(the_ticker.option_chain(x).calls)
            itm_call_options = call_options[call_options['inTheMoney'] == False]
            print(itm_call_options)
            contract_symbol = itm_call_options.head(1)['contractSymbol'].values[0]
            counter  = counter + 1
        else:
            pass
    return contract_symbol

def get_options_with_data(symbol, min_theta_buffer):
    the_ticker = yf.Ticker(symbol)
    current_price_underlying = the_ticker.info['currentPrice']
    counter = 1
    for x in the_ticker.options:
        current_time = datetime.datetime.now()
        exp_date = datetime.datetime.strptime(x, "%Y-%m-%d")
#        min_theta_buffer = 2
        date_buffer = current_time + timedelta(days=min_theta_buffer)
        if exp_date > date_buffer and counter ==1:
            the_chain_o_calls = the_ticker.option_chain(x).calls
            call_options = pd.DataFrame(the_ticker.option_chain(x).calls)
            itm_call_options = call_options[call_options['inTheMoney'] == False]
            print(itm_call_options)
            contract_symbol = itm_call_options.head(1)['contractSymbol'].values[0]
            oi = itm_call_options.head(1)['openInterest'].values[0]
            bid = itm_call_options.head(1)['bid'].values[0]
            ask = itm_call_options.head(1)['ask'].values[0]
            bid_ask_spread = (ask-bid)/bid
            avg_atm_price = itm_call_options.head(1)['lastPrice'].values[0]
            atm_strike = itm_call_options.head(1)['strike'].values[0]
            atm_price_pct_of_underlying = avg_atm_price/current_price_underlying
            iv = itm_call_options.tail(1)['impliedVolatility'].values[0]
            diff_to_strike = (atm_strike - current_price_underlying)/current_price_underlying
            option_value_index = atm_price_pct_of_underlying * (1 + diff_to_strike + diff_to_strike)
            counter  = counter + 1
            return {"contract_symbol": contract_symbol, "oi": oi, "iv": iv, "bid_ask_spread": bid_ask_spread, "option_value_index": option_value_index, "diff_to_strike": diff_to_strike, "bid": bid, "ask": ask, "atm_price_pct_of_underlying": atm_price_pct_of_underlying}
        else:
            return None
        

def get_options_date_3mo(symbol):
    the_ticker = yf.Ticker(symbol)
    current_price_underlying = the_ticker.info['currentPrice']
    highest_oi = 0
    cheapest = 10000
    return_contract_symbol = ""
    for x in the_ticker.options:
        current_time = datetime.datetime.now()
        exp_date = datetime.datetime.strptime(x, "%Y-%m-%d")
        min_theta_buffer = 60
        date_buffer = current_time + timedelta(days=min_theta_buffer)
        if exp_date > date_buffer:
            return_exp_date = exp_date
        else:
            pass
    return return_exp_date


def check_indicators_daily(ticker_list):
    final_result_df = pd.DataFrame()
    for ticker in ticker_list:
        try:
####below is a change to switch to alpaca
#            ticker_data = yf.Ticker(ticker)
#            ticker_history = get_ticker_history(ticker, '1y', '1d')#end = earnings_dates_past['er_date_string'].iloc[0], rounding ="True"  ##why doent; ticker_date.history work?
            #replacing with Alpaca
            today = datetime.datetime.today() 
            one_year_ago = today - timedelta(days=365) 
            formatted_date = one_year_ago.strftime("%Y-%m-%d") 
            ticker_history = get_daily_alpaca_data_as_df_all(ticker, formatted_date)
            #also, this line  - 25 lines down - needed to be commented out to make it work.
            #result['date_field'] = result['date_field'].dt.date
###change done

            result = explore_indicators(ticker_history)
            levels = get_fractals_levels(ticker_history)
            fib_levels = fib_retrace(ticker_history)
            levels_lists = fib_levels + levels
            result['pct_to_50ema'] = (result['50 period EMA'] - result['Close'])/result['Close']
            result['pct_to_200ema'] = (result['200 period EMA'] - result['Close'])/result['Close']
            result['BB_UPPER_PRICE'] = result['BB_UPPER']
            result['BB_UPPER'] = (result['BB_UPPER'] - result['Close'])/result['Close']
            result['BB_LOWER_PRICE'] = result['BB_LOWER']
            result['BB_LOWER'] = (result['BB_LOWER'] - result['Close'])/result['Close']
            result['BB_MIDDLE'] = result['BB_UPPER_PRICE'] - ((result['BB_UPPER_PRICE'] - result['BB_LOWER_PRICE'])/2)
            result['BB_BUCKET_1'] = result.apply(lambda x: 1 if x.Close > x.BB_UPPER_PRICE else 0, axis = 1)
            result['BB_BUCKET_2'] = result.apply(lambda x: 1 if x.Close < x.BB_UPPER_PRICE and x.Close >= x.BB_MIDDLE else 0, axis = 1)
            result['BB_BUCKET_3'] = result.apply(lambda x: 1 if x.Close < x.BB_MIDDLE and x.Close > x.BB_LOWER_PRICE  else 0, axis = 1)
            result['BB_BUCKET_4'] = result.apply(lambda x: 1 if x.Close < x.BB_LOWER_PRICE else 0, axis = 1)

            result['KC_MIDDLE'] = result['KC_UPPER'] - ((result['KC_UPPER'] - result['KC_LOWER'])/2)
            result['KC_BUCKET_1'] = result.apply(lambda x: 1 if x.Close > x.KC_UPPER else 0, axis = 1)
            result['KC_BUCKET_2'] = result.apply(lambda x: 1 if x.Close < x.KC_UPPER and x.Close >= x.KC_MIDDLE else 0, axis = 1)
            result['KC_BUCKET_3'] = result.apply(lambda x: 1 if x.Close < x.KC_MIDDLE and x.Close > x.KC_LOWER  else 0, axis = 1)
            result['KC_BUCKET_4'] = result.apply(lambda x: 1 if x.Close < x.KC_LOWER else 0, axis = 1)

            sma_ema_averages = [8,21,34,55,89]
            for i in sma_ema_averages:
                result = appendData(result,ta.EMA(result, i))
            result['Target'] = result['Close'].shift(-2) #predicting 10 days out
            #result = result[result['Target'].notnull()]
            result['pct_target'] = ((result['Target'] - result['Close'])/result['Close'])* 100
            result['class_buy'] = result['pct_target'].apply(lambda x: 1 if x > 1 else 0)
            result['class_hold'] = result['pct_target'].apply(lambda x: 1 if x <= 1 and x > 0 else 0)
            result['class_sell'] = result['pct_target'].apply(lambda x: 1 if x <=0 else 0)
        #    result = result.drop('Dividends', axis=1)
        #    result = result.drop('Stock Splits', axis=1)
            result['date_field'] = result.index
            #result['Date'] = pd.to_datetime(result['date_field'])
        #    result = result.drop('Close', axis=1)
            #result['date_field'] = result['date_field'].dt.date
        #    print (final_result.shape)
            final_result = result
        #    print (final_result.shape)
            
            fng_df = get_fng_df()
            fng_df['x'] = fng_df['x'].dt.date
            final_result= pd.merge(final_result, fng_df, left_on = 'date_field', right_on = 'x', how = 'left')
        #    final_result = final_result.drop('date_field', axis=1)
            final_result = final_result.drop('x', axis=1)
            final_result = final_result.drop('rating', axis=1)
            final_result['fng'] = final_result['y']
            final_result = final_result.drop('y', axis=1)

            final_result['fng_prior'] = final_result['fng'].shift(5) #10 days prior
            final_result['fng_diff'] = final_result['fng'] - final_result['fng_prior']
            final_result['fng_uptrend'] = final_result['fng_diff'].apply(lambda x: 1 if x > 5 else 0)
            final_result['fng_downtrend'] = final_result['fng_diff'].apply(lambda x: 1 if x < -5 else 0)
            final_result['fng_high'] = final_result['fng'].apply(lambda x: 0 if x > 70 else 1)
            final_result['fng_low'] = final_result['fng'].apply(lambda x: 0 if x < 30 else 1)
            final_result['fng'] = final_result['fng'].apply(lambda x: 0 if x > 50 else 1)
            final_result['DI+_prior'] = final_result['DI+'].shift(5) #10 days prior
            final_result['DI-_prior'] = final_result['DI-'].shift(5) #10 days prior
            final_result['DI_diff_prior'] = final_result['DI+_prior'] - final_result['DI-_prior']
            final_result['DI_diff'] = final_result['DI+'] - final_result['DI-']
            final_result['DI_crossover'] = final_result.apply(lambda x: 1 if x.DI_diff_prior < 0 and x.DI_diff > 1 else 0, axis=1)
            final_result['DI_uptrend'] = final_result.apply(lambda x: 1 if x['DI+_prior'] < x['DI+'] else 0, axis=1)
            final_result['di_uptrend_ADX'] = final_result.apply(lambda row: 1 if  row['DI_uptrend'] == 1 and row['14 period ADX.'] > 20 else 0, axis=1)
            final_result['SAR_level'] = final_result['SAR']
            final_result['next_support'] = final_result['Close'].apply(lambda x: next_buy_level(x, levels_lists))
            final_result['pct_to_SAR_support'] = (final_result['Close'] - final_result['SAR_level'])/final_result['Close'] * 100
            final_result['pct_to_other_support'] = (final_result['Close'] - final_result['next_support'])/final_result['Close'] * 100
        #    final_result = final_result.drop('Capital Gains', axis=1)
        #    final_result = final_result.dropna()
            #final_result = final_result.drop('pct_target', axis=1)
            final_result['fng'] = final_result['fng'].apply(lambda x: 0 if x > 50 else 1)
        #    final_result['BB_breakout'] = final_result['BB_UPPER'].apply(lambda x: 1 if x < 0 else 0)
            final_result['ree_flag'] = final_result.apply(lambda row: -1 if  row['8 period EMA'] > row['21 period EMA'] and row['21 period EMA'] > row['34 period EMA'] and row['34 period EMA'] > row['55 period EMA'] and row['55 period EMA'] > row['89 period EMA'] and row['14 period ADX.'] > 20 and row['14 period STOCH %K'] < 40 else 0, axis=1)
            final_result['ree_flag2'] = final_result.apply(lambda row: -1 if  row['21 period EMA'] > row['34 period EMA'] and row['34 period EMA'] > row['55 period EMA'] and row['55 period EMA'] > row['89 period EMA'] and row['14 period ADX.'] > 20 and row['14 period STOCH %K'] < 50 else 0, axis=1)
            final_result['BB_lower_hold'] = final_result.apply(lambda row: 3 if row['BB_LOWER'] > 0 and row['BB_LOWER'] < .01 and row['8 period EMA'] > row['BB_LOWER_PRICE'] and row['21 period EMA'] < row['34 period EMA'] and row['34 period EMA'] < row['55 period EMA'] and row['55 period EMA'] < row['89 period EMA'] and row['14 period STOCH %K'] < 30 else 0, axis=1)
        #    final_result['stoch_low'] = final_result.apply(lambda row: 1 if  row['14 period STOCH %K'] < 40 else 0, axis=1)
        #    final_result['stoch_really_low'] = final_result.apply(lambda row: 1 if  row['14 period STOCH %K'] < 30 else 0, axis=1)
            final_result['rsi_low'] = final_result.apply(lambda row: 1 if  row['14 period RSI'] < 30 else 0, axis=1)
            final_result['rsi_lower_25'] = final_result.apply(lambda row: 1 if  row['14 period RSI'] < 25 and row['14 period RSI'] > 1 else 0, axis=1)
            final_result['rsi_lower_25_30'] = final_result.apply(lambda row: 1 if  row['14 period RSI'] > 25 and row['14 period RSI'] < 30 else 0, axis=1)
            final_result['rsi_lower_30_40'] = final_result.apply(lambda row: 1 if  row['14 period RSI'] > 30 and row['14 period RSI'] < 40 else 0, axis=1)
            final_result['rsi_lower_70_80'] = final_result.apply(lambda row: 1 if  row['14 period RSI'] > 70 and row['14 period RSI'] < 80 else 0, axis=1)
            final_result['rsi_lower_80'] = final_result.apply(lambda row: 1 if  row['14 period RSI'] > 80 else 0, axis=1)
            final_result['not_macd'] = final_result.apply(lambda row: 1 if  row['8 period EMA'] > row['21 period EMA'] and row['21 period EMA'] < row['34 period EMA'] else 0, axis=1)
            
            final_result['ema_downtrend_lt'] = final_result.apply(lambda row: 1 if row['8 period EMA'] < row['21 period EMA'] and row['21 period EMA'] < row['34 period EMA'] and row['34 period EMA'] < row['55 period EMA'] else 0, axis=1)
            final_result['ema_downtrend_st'] = final_result.apply(lambda row: 1 if row['8 period EMA'] < row['21 period EMA'] and row['21 period EMA'] < row['34 period EMA'] else 0, axis=1)

            final_result = macd_crossover(final_result)
            final_result['SAR_level'] = final_result['SAR']
            final_result['SAR'] = final_result.apply(lambda row: 1 if  row['Close'] > row['SAR'] else 0, axis=1)
        #    final_result['pivot_check'] = final_result.apply(lambda row: 1 if  row['Open'] > row['pivot'] and (row['Open'] - row['pivot'])/ row['pivot'] > .0025 else 0, axis=1)
        #    final_result['ADX_CHECK1'] = final_result.apply(lambda row: 1 if  row['8 period EMA'] > row['34 period EMA'] and row['Open'] > row['SAR'] and row['14 period ADX.'] > 40 else 0, axis=1)
        #    final_result['ADX_CHECK2'] = final_result.apply(lambda row: 1 if row['BEARISH_MACD_CROSSOVER'] == 1 and row['14 period ADX.'] > 50 and row['14 period RSI'] < 60 else 0, axis=1)
        #    final_result['ADX_CHECK3'] = final_result.apply(lambda row: 1 if row['14 period ADX.'] > 50 and row['14 period RSI'] < 60 else 0, axis=1)
        #    final_result['MFI_high'] = final_result.apply(lambda row: 1 if row['14 period MFI'] > 50 else 0, axis=1)
            final_result['MFI_low'] = final_result.apply(lambda row: 1 if row['14 period MFI'] < 30 else 0, axis=1)
            final_result['BullishFractal'] = final_result['BullishFractal'].shift(2) #predicting 10 days out
            final_result['BearishFractal'] = final_result['BearishFractal'].shift(2) #predicting 10 days out
            final_result['stoch_low'] = final_result.apply(lambda row: 1 if  row['14 period STOCH %K'] < 40 else 0, axis=1)
            final_result['stoch_really_low'] = final_result.apply(lambda row: 1 if  row['14 period STOCH %K'] < 30 else 0, axis=1)

            final_result['ticker'] = ticker
            final_result['Total'] = 0
            final_result['Total_overfit'] = 0
            final_result['Total_kmeans'] = 0.00
            final_result['Total_kmeans_st'] = 0.00
            final_result = final_result.tail(1)
#            column_list = ['ticker', 'date_field', 'Close','BB_BUCKET_1', 'BB_BUCKET_2', 'BB_BUCKET_3', 'BB_BUCKET_4', 'rsi_lower_25', 'rsi_lower_30_40', 'rsi_lower_25_30', 'rsi_lower_70_80', 'rsi_lower_80', 'ree_flag', 'ree_flag2', 'ema_downtrend_lt', 'ema_downtrend_st', 'di_uptrend_ADX', 'SAR', 'BearishFractal', 'BullishFractal', 'Total']
#            final_result = final_result[column_list].tail(1)
            final_result_df = pd.concat([final_result_df, final_result])       
            print(ticker)


        except Exception as e:
            print("oops error in check_indicators_dailu() function:  ", e)   
            traceback.print_exc() 
    return final_result_df

def check_indicators_fifteen_min(ticker):
    ticker_history = get_ticker_history(ticker, '60d', '15m')
    result = explore_indicators(ticker_history)
    levels = get_fractals_levels(ticker_history)
    fib_levels = fib_retrace(ticker_history)
    levels_lists = fib_levels + levels
    result['Target'] = result['Close'].shift(-2) #predicting 30 mins out
    result['Target_4hours'] = result['Close'].shift(-20) #predicting 30 mins out
    result = result[result['Target'].notnull()]
    result['pct_target'] = ((result['Target'] - result['Close'])/result['Close'])* 100
    result['pct_target_4hours'] = ((result['Target_4hours'] - result['Close'])/result['Close'])* 100
    result['pct_change_underlying'] = ((result['Close'] - result['Open'])/result['Open'])* 100
    result['pct_to_50ema'] = (result['50 period EMA'] - result['Close'])/result['Close']
    sma_ema_averages = [5, 10, 30, 60]
    for i in sma_ema_averages:
        result = appendData(result,ta.EMA(result, i))

    result['pct_to_5ema'] = (result['5 period EMA'] - result['Close'])/result['Close'] * 100
    result['pct_to_10ema'] = (result['10 period EMA'] - result['Close'])/result['Close'] * 100
    result['pct_to_30ema'] = (result['30 period EMA'] - result['Close'])/result['Close'] * 100
    result['pct_to_60ema'] = (result['60 period EMA'] - result['Close'])/result['Close'] * 100
    final_result = result
    final_result['datetime_field'] = final_result.index
    final_result['datetime_field_copy'] = final_result.index
    final_result['datetime_field'] = final_result['datetime_field'].dt.time
    final_result['ticker'] = ticker
    # final_result = final_result.drop('Dividends', axis=1)
    # final_result = final_result.drop('Stock Splits', axis=1)
    # final_result = final_result.drop('Open', axis=1)
    # final_result = final_result.drop('Close', axis=1)
    # final_result = final_result.drop('High', axis=1)
    print(final_result['Volume'])
    final_result['Volume'] = (final_result['Volume']-final_result['Volume'].min())/(final_result['Volume'].max()-final_result['Volume'].min())
    print(final_result['Volume'])
    continuous_column_list = ['datetime_field', 'Close', 'Volume', 'pct_to_10ema', 'pct_to_30ema', 'pct_target', 'pct_target_4hours']
    final_result = final_result[continuous_column_list]
    return final_result


def get_fifteen_min_data(ticker):
    ticker_history = get_ticker_history(ticker, '60d', '15m')
    print(ticker_history)
    result = ticker_history
    result['Target'] = result['Close'].shift(-2) #predicting 30 mins out
    result['Target_4hours'] = result['Close'].shift(-20) #predicting 30 mins out
    result = result[result['Target'].notnull()]
    result['pct_target'] = ((result['Target'] - result['Close'])/result['Close'])* 100
    result['pct_target_4hours'] = ((result['Target_4hours'] - result['Close'])/result['Close'])* 100
    result['pct_change_underlying'] = ((result['Close'] - result['Open'])/result['Open'])* 100
    final_result = result
    final_result['datetime_field'] = final_result.index
    final_result['datetime_field_copy'] = final_result.index
#    final_result['datetime_field'] = final_result['datetime_field'].dt.time
    final_result['ticker'] = ticker
    return final_result



def check_indicators_daily_nextday(ticker):
    #try:
        ticker_history = get_ticker_history(ticker, '1y', '1d')
        result = explore_indicators(ticker_history)
        levels = get_fractals_levels(ticker_history)
        fib_levels = fib_retrace(ticker_history)
        levels_lists = fib_levels + levels
        result['Target'] = result['Close'].shift(-1) #predicting 10 days out
        result = result[result['Target'].notnull()]
        result['pct_target'] = ((result['Target'] - result['Close'])/result['Close'])* 100
        result['pct_change_underlying'] = ((result['Close'] - result['Open'])/result['Open'])* 100
        result['pct_to_50ema'] = (result['50 period EMA'] - result['Close'])/result['Close']
        result['BB_UPPER_PRICE'] = result['BB_UPPER']
        result['BB_UPPER'] = (result['BB_UPPER'] - result['Close'])/result['Close']
        result['BB_LOWER_PRICE'] = result['BB_LOWER']
        result['BB_LOWER'] = (result['BB_LOWER'] - result['Close'])/result['Close']
        result['BB_MIDDLE'] = result['BB_UPPER_PRICE'] - ((result['BB_UPPER_PRICE'] - result['BB_LOWER_PRICE'])/2)

        #result = result.drop('Close', axis=1)
        #result = result.drop('Adj Close', axis=1)
        sma_ema_averages = [5, 10, 30, 60]
        for i in sma_ema_averages:
            result = appendData(result,ta.EMA(result, i))

        result['pct_to_5ema'] = (result['5 period EMA'] - result['Close'])/result['Close'] * 100
        result['pct_to_10ema'] = (result['10 period EMA'] - result['Close'])/result['Close'] * 100
        result['pct_to_30ema'] = (result['30 period EMA'] - result['Close'])/result['Close'] * 100
        result['pct_to_60ema'] = (result['60 period EMA'] - result['Close'])/result['Close'] * 100

        #result['date_field'] = result.index
        #result['date_field'] = result['date_field'].dt.date
        final_result = result

        final_result['DI+_prior'] = final_result['DI+'].shift(5) #10 days prior
        final_result['DI-_prior'] = final_result['DI-'].shift(5) #10 days prior
        final_result['DI_diff_prior'] = final_result['DI+_prior'] - final_result['DI-_prior']
        final_result['DI_diff'] = final_result['DI+'] - final_result['DI-']
        final_result['DI_crossover'] = final_result.apply(lambda x: 1 if x.DI_diff_prior < 0 and x.DI_diff > 1 else 0, axis=1)
        final_result['DI_uptrend'] = final_result.apply(lambda x: 1 if x['DI+_prior'] < x['DI+'] else 0, axis=1)
        final_result['di_uptrend_ADX'] = final_result.apply(lambda row: 1 if  row['DI_uptrend'] == 1 and row['14 period ADX.'] > 20 else 0, axis=1)
        final_result['SAR_level'] = final_result['SAR']
        final_result['next_support'] = final_result['Close'].apply(lambda x: next_buy_level(x, levels_lists))
        final_result['pct_to_SAR_support'] = (final_result['Close'] - final_result['SAR_level'])/final_result['Close'] * 100
        final_result['pct_to_other_support'] = (final_result['Close'] - final_result['next_support'])/final_result['Close'] * 100
        final_result['SAR_level'] = final_result['SAR']
        final_result['SAR'] = final_result.apply(lambda row: 1 if  row['Close'] > row['SAR'] else 0, axis=1)

        final_result['BullishFractal'] = final_result['BullishFractal'].shift(2) #predicting 10 days out
        final_result['BearishFractal'] = final_result['BearishFractal'].shift(2) #predicting 10 days out

        final_result['ticker'] = ticker
        final_result = final_result.drop('Dividends', axis=1)
        final_result = final_result.drop('Stock Splits', axis=1)
        final_result = final_result.drop('Open', axis=1)
        final_result = final_result.drop('Close', axis=1)
        final_result = final_result.drop('High', axis=1)
        #minmax_scaler = MinMaxScaler()
        print(final_result['Volume'])
        final_result['Volume'] = (final_result['Volume']-final_result['Volume'].min())/(final_result['Volume'].max()-final_result['Volume'].min())
        #final_result['Volume'] = minmax_scaler.fit_transform([final_result['Volume']])[0]
        print(final_result['Volume'])
        continuous_column_list = ['Volume', 'pct_to_5ema', 'pct_to_10ema', 'pct_to_30ema', 'pct_to_60ema', 'BB_UPPER', 'BB_LOWER', 'pct_to_SAR_support', 'pct_to_other_support', '14 period ADX.', '14 period RSI', '14 period MFI', 'DI+', 'DI-', '14 period STOCH %K', 'BearishFractal', 'BullishFractal']
        final_result = final_result[continuous_column_list]
        transform_1 = ['14 period ADX.', '14 period RSI', '14 period MFI', 'DI+', 'DI-', '14 period STOCH %K']
        for key_name in transform_1:
            final_result[key_name] = final_result[key_name] / 100
        for key_name in continuous_column_list:
            final_result[key_name] = round(final_result[key_name], 2)
        final_result['tmp_join'] = 1
    
        #final_result = final_result.tail(1)
    #except Exception as e:
    #    print("oops:  ", e)   
        #final_result = pd.DataFrame()
        return final_result

def get_weekly_atm_options_data(symbol):
    # Get today's date
    today = datetime.date.today()
    # Find the number of days until next Friday
    days_until_friday = (4 - today.weekday()) % 7
    days_until_friday = 7 if days_until_friday == 0 else days_until_friday
    # Add the number of days to today's date
    next_friday = today + datetime.timedelta(days=days_until_friday)
    next_friday = next_friday.strftime("%Y-%m-%d")  
    # Print the date
    the_ticker = yf.Ticker(symbol)
    #current_price_underlying = the_ticker.info['currentPrice']
    call_options = pd.DataFrame(the_ticker.option_chain(next_friday).calls)
    itm_call_options = call_options[call_options['inTheMoney'] == False]
    #columns = itm_call_options.columns
    #new_columns = [x + "_" + str(i) + "dte" for x in columns]
    #itm_call_options.columns = new_columns
    new_df = itm_call_options.head(1)
    new_df = new_df.reset_index(drop = True)

    current_time = datetime.datetime.now()
    date_time = current_time.strftime("%Y-%m-%d %R")  
    new_df['date_field'] = date_time
    new_df['tmp_join'] = 1
    return new_df

def get_weekly_greeks(symbol, strike):
    # Get today's date
    today = datetime.date.today()
    # Find the number of days until next Friday
    days_until_friday = (4 - today.weekday()) % 7
    days_until_friday = 7 if days_until_friday == 0 else days_until_friday

    # Add the number of days to today's date
    next_friday = today + datetime.timedelta(days=days_until_friday)
    next_friday = next_friday.strftime("%Y-%m-%d")  

    url = f"https://api.nasdaq.com/api/quote/{symbol}/option-chain/greeks?assetclass=stocks&date={next_friday}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"
    }
    response = requests.get(url, headers=headers).json()

    df2 = pd.DataFrame(response['data']['table']['rows'])
    current_time = datetime.datetime.now()
    date_time = current_time.strftime("%Y-%m-%d %R")  
    df2['date_field'] = date_time
    df2['tmp_join'] = 1
    df2 = df2[df2['strike'] == strike]

    df2 = df2.drop('url', axis=1)
    return(df2)

def merge_fifteen_min_data(ticker, df):
    fifteen_min_data = check_indicators_fifteen_min(ticker).tail(1)
    #print(fifteen_min_data.to_string())
    #fifteen_min_data['open_session'] = 1 if datetime.datetime.now().hour < 9 else 0
    #fifteen_min_data['close_session'] = 1 if datetime.datetime.now().hour > 14 and datetime.datetime.now().minute > 30 else 0
    #fifteen_min_data['lunch_session'] = 1 if datetime.datetime.now().hour > 12 and datetime.datetime.now().hour < 13 else 0
    #fifteen_min_data = fifteen_min_data.drop('ticker', axis=1)
#    continuous_column_list =['pct_change_underlying', 'Volume', '5 period EMA', '10 period EMA', '30 period EMA', '60 period EMA', 'BB_UPPER', 'BB_LOWER', 'pct_to_SAR_support', 'pct_to_other_support', '14 period ADX.', '14 period RSI', '14 period MFI', 'DI+', 'DI-', '14 period STOCH %K', 'BearishFractal', 'BullishFractal']
    #continuous_column_list =['pct_change_underlying', 'Volume', 'pct_to_5ema', 'pct_to_10ema', 'pct_to_30ema', 'pct_to_60ema', 'BB_UPPER', 'BB_LOWER', 'pct_to_SAR_support', 'pct_to_other_support', '14 period ADX.', '14 period RSI', '14 period MFI', 'DI+', 'DI-', '14 period STOCH %K', 'BearishFractal', 'BullishFractal']
    continuous_column_list = ['pct_to_10ema', 'pct_to_30ema']
    limited_list = ['pct_to_10ema', 'pct_to_30ema']
    fifteen_min_data = fifteen_min_data[limited_list]

    #update columsn mames with list comprehension
    columns = fifteen_min_data.columns
    new_columns = [ticker + "_fifteenmin_" + x for x in columns]
    fifteen_min_data.columns = new_columns
    fifteen_min_data = fifteen_min_data.tail(1)
    fifteen_min_data['tmp_join'] = 1
    print('...test debug test...')
    print(fifteen_min_data.shape)
    print(df.shape)
    new_df = pd.merge(df, fifteen_min_data, left_on='tmp_join', right_on='tmp_join')
    #new_df = new_df.drop('tmp_join', axis=1)
    print('...test debug test...')
    print(new_df.shape)
    return new_df

def to_datetime(x):
  try:
    # Your logic to convert various valid date formats to datetime objects
    return pd.to_datetime(x)  # Assuming successful conversion
  except:
    return pd.NA  # Or another appropriate value for missing/invalid entries


def merge_fifteen_min_comp_data_full(ticker, df):
    fifteen_min_data = check_indicators_fifteen_min(ticker)
    #continuous_column_list = ['pct_change_underlying', 'Volume', 'pct_to_5ema', 'pct_to_10ema', 'pct_to_30ema', 'pct_to_60ema', 'BB_UPPER', 'BB_LOWER', 'pct_to_SAR_support', 'pct_to_other_support', '14 period ADX.', '14 period RSI', '14 period MFI', 'DI+', 'DI-', '14 period STOCH %K', 'BearishFractal', 'BullishFractal']
    continuous_column_list = ['Close', 'pct_to_10ema', 'pct_to_30ema']
    limited_list = ['Close', 'pct_to_10ema', 'pct_to_30ema']
    fifteen_min_data = fifteen_min_data[limited_list]
    fifteen_min_data['date_field_copy'] = fifteen_min_data.index
    #fifteen_min_data['datetime_field'] = fifteen_min_data['datetime_field'].dt.time

    print(fifteen_min_data)
    #fifteen_min_data = fifteen_min_data[continuous_column_list]
    #update columsn mames with list comprehension
    new_columns = [ticker + "_dailynextday_" + x for x in continuous_column_list]
    #new_columns.insert('datetime_field', 0)
    new_columns = new_columns + ['date_field_copy']
    #print(fifteen_min_data.head(1))
    #print("is the error with 15 min data??????????????????")
    #print(df)
    print(fifteen_min_data)
    #fifteen_min_data['date_field_copy'] = pd.to_datetime(fifteen_min_data['date_field_copy'], format='%Y%m%d')
    fifteen_min_data['date_field_copy'] = fifteen_min_data['date_field_copy'].apply(to_datetime)

    fifteen_min_data.columns = new_columns
    print("is the error with 15 min data??????????????????")
    print(type(fifteen_min_data['date_field_copy'].iloc[0]))
    print(fifteen_min_data['date_field_copy'].iloc[10])
    print("is the error with df data??????????????????")
    print(type(df['date_field_copy'].iloc[0]))
    print(df['date_field_copy'].iloc[0])

    #new_df = pd.merge(df, fifteen_min_data, left_on='Datetime', right_on='Datetime')
    #new_df = pd.merge(df, fifteen_min_data, left_index=True, right_index=True)
    new_df = pd.merge(df, fifteen_min_data, left_on='date_field_copy', right_on='date_field_copy', how = 'left')
    #new_df = new_df.drop('tmp_join', axis=1)
    return new_df

def merge_daily_comp_full(ticker, df):
    data = check_indicators_daily_nextday(ticker)
    continuous_column_list =['pct_change_underlying', 'Volume', 'pct_to_5ema', 'pct_to_10ema', 'pct_to_30ema', 'pct_to_60ema', 'BB_UPPER', 'BB_LOWER', 'pct_to_SAR_support', 'pct_to_other_support', '14 period ADX.', '14 period RSI', '14 period MFI', 'DI+', 'DI-', '14 period STOCH %K', 'BearishFractal', 'BullishFractal']

    #fifteen_min_data = fifteen_min_data[continuous_column_list]
    #update columsn mames with list comprehension
    columns = data.columns
    new_columns = [ticker + "_dailynextday_" + x for x in columns]
    data.columns = new_columns

    new_df = pd.merge(df, data, left_on='Datetime', right_on='Datetime')
    #new_df = new_df.drop('tmp_join', axis=1)
    return new_df

def add_day(string_date):
    date_format = "%Y-%m-%d"
    try:
        # Parse the string date into a datetime object
        date_obj = datetime.datetime.strptime(string_date, date_format)
    except ValueError:
        print(f"Invalid date format. Please use YYYY-MM-DD format for '{string_date}'.")
        return None
    date_with_added_day = date_obj + timedelta(days = 1)
    return date_with_added_day.strftime("%Y-%m-%d")

def add_weekday(string_date):
    date_format = "%Y-%m-%d"
    try:
        date_obj = datetime.datetime.strptime(string_date, date_format)
    except ValueError:
        print(f"Invalid date format. Please use YYYY-MM-DD format for '{string_date}'.")
        return None

    # Determine the weekday of the current date
    weekday = date_obj.weekday()

    # Calculate days to add, skipping weekends
    days_to_add = 1
    if weekday == 4:  # Friday
        days_to_add = 3  # Skip to Monday

    # Add the calculated days and return the new formatted date
    new_date = date_obj + datetime.timedelta(days=days_to_add)
    return new_date.strftime(date_format)

def get_my_ticker_list():
    #my_ticker_list = ['GATX', 'LULU', 'DTO', 'BHP','GS','BKNG','BMY','COIN','LVS','EXR','EXPE','BGNE','GEN','ELF','JEF','ASND','SKM','PAC','BZ','ADC','PHI','ACT','GATX','ALKS','FRHC','INSM','NMIH','FCPT','WB', 'AFRM', 'SOUN', 'GCT','CRNC','GB','GEN','EEFT','CCSI','FOUR','tsla', 'fmc', 'meli', 'nu', 'aapl', 'stm', 'qs', 'zeta', 'arry', 'maxn', 'hum', 'erii', 'pii', 'ISRG', 'AMZN', 'NVDA', 'TSM', 'ASX', 'STM', 'CSTL', 'ENVX', 'NGG', 'APP', 'SLDP', 'NGG', 'CCOI','CSIQ', 'LUNR', 'ROIV', 'INSP', 'ENVX', 'MTLS', 'NEE', 'PDD', 'ALB', 'GH', 'ROIV', 'PYPL', 'OPRA', 'BABA', 'LI', 'IMAX','ADBE', 'GOOG', 'STNE','NVEI', 'INTU', 'NU', 'HIMS', 'FTNT', 'V', 'TGT', 'INTC', 'NEE', 'USB', 'OTEX','VEEV', 'DOCN', 'SQ','PAYC','DOCN','USB','MTB','FITB','TEX','OTEX','BILL','YOU','PDD','PCOR','PCTY','PAYO','NVEI','SAP','NICE','VEEV','ZETA','GB','PATH','OKTA','HUBS','YMM','TDUP','SHLS','CORT','HRMY','NVO','FOLD','MDXG','MNKD', 'DCBO', 'HROW','ALKS']
    my_ticker_list = ['LULU', 'BHP','GS','BKNG','BMY','COIN','LVS','EXR','EXPE','SKM','PAC','PHI','ALKS','INSM', 'CRNC','GB','GEN','EEFT','CCSI','FOUR','fmc', 'meli', 'nu', 'aapl', 'stm', 'qs', 'zeta', 'arry', 'maxn', 'hum', 'erii', 'pii', 'ISRG', 'AMZN', 'NVDA', 'TSM', 'ASX', 'STM', 'CSTL', 'ENVX', 'NGG', 'APP', 'SLDP', 'NGG', 'CCOI','CSIQ', 'ROIV', 'INSP', 'ENVX', 'MTLS', 'NEE', 'PDD', 'ALB', 'GH', 'ROIV', 'PYPL', 'OPRA', 'BABA', 'LI', 'IMAX','ADBE', 'GOOG', 'STNE','NVEI', 'INTU', 'NU', 'HIMS', 'FTNT', 'V', 'TGT', 'INTC', 'NEE', 'USB', 'OTEX','VEEV', 'DOCN', 'SQ','PAYC','DOCN','USB','MTB','FITB','TEX','OTEX','BILL','YOU','PDD','PCOR','PCTY','PAYO','NVEI','SAP','NICE','VEEV','ZETA','GB','OKTA','HUBS','YMM','TDUP','SHLS','CORT','HRMY','NVO','FOLD','MDXG','MNKD','HROW','ALKS']
    my_ticker_list = [x.upper() for x in my_ticker_list]
    return my_ticker_list


def get_citrini_us_raw():
    pd.set_option("display.max_colwidth", 10000)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'data', 'citrini_csv.csv')#.csv
    df = pd.read_csv(filepath, encoding='iso-8859-1')
    # Filter for US country
    df_filter = df[df['country'] == 'US']
    # Get unique tickers as a list
    return df_filter

def get_citrini_us_tickers():
    pd.set_option("display.max_colwidth", 10000)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'data', 'citrini_csv.csv')#.csv
    df = pd.read_csv(filepath, encoding='iso-8859-1')
    # Filter for US country
    df_filter = df[df['country'] == 'US']
    # Get unique tickers as a list
    tickers = df_filter['Ticker.2'].unique().tolist()
    return tickers

def get_citrini_us_bio_tickers():
    pd.set_option("display.max_colwidth", 10000)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'data', 'citrini_csv.csv')#.csv
    df = pd.read_csv(filepath, encoding='iso-8859-1')
    # Filter for US country
    df_filter = df[df['country'] == 'US']
    df_filter = df[df['Portfolio Level 1'] == 'BIO 2025 TRADES']
    # Get unique tickers as a list
    tickers = df_filter['Ticker.2'].unique().tolist()
    return tickers

def get_citrini_us_ai_tickers():
    pd.set_option("display.max_colwidth", 10000)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'data', 'citrini_csv.csv')#.csv
    df = pd.read_csv(filepath, encoding='iso-8859-1')
    # Filter for US country
    df_filter = df[df['country'] == 'US']
    df_filter = df[df['Portfolio Level 1'] == 'DYNAMIC AI BASKET']
    # Get unique tickers as a list
    tickers = df_filter['Ticker.2'].unique().tolist()
    return tickers


def get_citrini_us_hc_tickers():
    pd.set_option("display.max_colwidth", 10000)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'data', 'citrini_csv.csv')#.csv
    df = pd.read_csv(filepath, encoding='iso-8859-1')
    # Filter for US country
    df_filter = df[df['country'] == 'US']
    df_filter = df[df['Portfolio Level 1'] == 'MEDTECH & HEALTHCARE INNOVATI']
    # Get unique tickers as a list
    tickers = df_filter['Ticker.2'].unique().tolist()
    return tickers

def get_citrini_us_ng_tickers():
    pd.set_option("display.max_colwidth", 10000)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'data', 'citrini_csv.csv')#.csv
    df = pd.read_csv(filepath, encoding='iso-8859-1')
    # Filter for US country
    df_filter = df[df['country'] == 'US']
    df_filter = df[df['Portfolio Level 1'] == 'NAT GAS']
    # Get unique tickers as a list
    tickers = df_filter['Ticker.2'].unique().tolist()
    return tickers

def get_citrini_us_robots_tickers():
    pd.set_option("display.max_colwidth", 10000)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'data', 'citrini_csv.csv')#.csv
    df = pd.read_csv(filepath, encoding='iso-8859-1')
    # Filter for US country
    df_filter = df[df['country'] == 'US']
    df_filter = df[df['Portfolio Level 1'] == 'ROBOTS NARROWED']
    # Get unique tickers as a list
    tickers = df_filter['Ticker.2'].unique().tolist()
    return tickers

def get_my_basket_viz_val1():
    viz_val1 = ['BILL', 'EL', 'BL', 'PYPL', 'SOFI', 'BRZE', 'NXT', 'DOCU', 'TOST', 'SLDP', 'MDXG', 'NTRA', 'ANSS', 'LYFT', 'ZM', 'MLM', 'FOUR', 'SJM', 'CSIQ', 'VLO', 'ACHR', 'DBX', 'CXM', 'CNP', 'EBAY', 'MA', 'PAYC', 'YOU', 'TBLA', 'HRMY', 'ASML', 'SO', 'ETR','SPG', 'FROG', 'UTHR', 'OKTA', 'FTNT', 'AZN', 'MTLS', 'NVDA', 'DH', 'ALKS', 'IRDM', 'EXPE', 'SWI']
    return viz_val1

def get_my_basket_viz_val2():
    viz_val2 = ['GPRE', 'ALB','MU','BPMC','CLCO','BG','NE','CNMD','ROIV','AIR','EXAS','APA','INCY','EXEL', 'HST', 'CMCSA','SQM','BAX','NEE','KALU','REGN','LYB', 'INSP', 'O', 'CAH', 'VICI', 'FE', 'ESNT', 'ACCD', 'PNW', 'HPQ', 'HZO', 'PHI', 'E', 'UMC', 'STLA', 'LULU', 'AMGN', 'EXC', 'NVS', 'CCOI', 'NEM', 'CMPS', 'DV', 'OPRA', 'CORT','PINS']
    return viz_val2

def get_my_basket_large_cap():
    viz_val_lrg_cap = ['FMC', 'MRK','CE','TGT','PEP','MSFT','INTU','AMZN','SHY','IEF','TLT','VZ','BABA','BHP', 'JPM', 'ADBE','NVS','LI','NVDA','MA','V','KO']
    return viz_val_lrg_cap

def get_my_viz_value_ticker_list():
    #my_ticker_list = ['GATX', 'LULU', 'DTO', 'BHP','GS','BKNG','BMY','COIN','LVS','EXR','EXPE','BGNE','GEN','ELF','JEF','ASND','SKM','PAC','BZ','ADC','PHI','ACT','GATX','ALKS','FRHC','INSM','NMIH','FCPT','WB', 'AFRM', 'SOUN', 'GCT','CRNC','GB','GEN','EEFT','CCSI','FOUR','tsla', 'fmc', 'meli', 'nu', 'aapl', 'stm', 'qs', 'zeta', 'arry', 'maxn', 'hum', 'erii', 'pii', 'ISRG', 'AMZN', 'NVDA', 'TSM', 'ASX', 'STM', 'CSTL', 'ENVX', 'NGG', 'APP', 'SLDP', 'NGG', 'CCOI','CSIQ', 'LUNR', 'ROIV', 'INSP', 'ENVX', 'MTLS', 'NEE', 'PDD', 'ALB', 'GH', 'ROIV', 'PYPL', 'OPRA', 'BABA', 'LI', 'IMAX','ADBE', 'GOOG', 'STNE','NVEI', 'INTU', 'NU', 'HIMS', 'FTNT', 'V', 'TGT', 'INTC', 'NEE', 'USB', 'OTEX','VEEV', 'DOCN', 'SQ','PAYC','DOCN','USB','MTB','FITB','TEX','OTEX','BILL','YOU','PDD','PCOR','PCTY','PAYO','NVEI','SAP','NICE','VEEV','ZETA','GB','PATH','OKTA','HUBS','YMM','TDUP','SHLS','CORT','HRMY','NVO','FOLD','MDXG','MNKD','HROW','ALKS']
    my_ticker_list = ['SOFI', 'HOOD', 'OKTA', 'AMGN', 'INSP', 'VLO', 'FROG', 'ADSK', 'MLM', 'CLSK', 'TBLA', 'CMCSA', 'BRZE', 'ETR', 'LYB', 'AIR', 'TOST', 'DOCU', 'ABBV', 'SO', 'IRDM', 'PNW', 'RAMP', 'MDXG', 'DV', 'INTU', 'ETSY', 'DBX', 'ATEN', 'KVUE', 'BL', 'MARA', 'PATH']
    my_ticker_list = [x.upper() for x in my_ticker_list]
    return my_ticker_list

def get_my_ticker_list_daily_manual():
    #my_ticker_list = ['GATX', 'LULU', 'DTO', 'BHP','GS','BKNG','BMY','COIN','LVS','EXR','EXPE','BGNE','GEN','ELF','JEF','ASND','SKM','PAC','BZ','ADC','PHI','ACT','GATX','ALKS','FRHC','INSM','NMIH','FCPT','WB', 'AFRM', 'SOUN', 'GCT','CRNC','GB','GEN','EEFT','CCSI','FOUR','tsla', 'fmc', 'meli', 'nu', 'aapl', 'stm', 'qs', 'zeta', 'arry', 'maxn', 'hum', 'erii', 'pii', 'ISRG', 'AMZN', 'NVDA', 'TSM', 'ASX', 'STM', 'CSTL', 'ENVX', 'NGG', 'APP', 'SLDP', 'NGG', 'CCOI','CSIQ', 'LUNR', 'ROIV', 'INSP', 'ENVX', 'MTLS', 'NEE', 'PDD', 'ALB', 'GH', 'ROIV', 'PYPL', 'OPRA', 'BABA', 'LI', 'IMAX','ADBE', 'GOOG', 'STNE','NVEI', 'INTU', 'NU', 'HIMS', 'FTNT', 'V', 'TGT', 'INTC', 'NEE', 'USB', 'OTEX','VEEV', 'DOCN', 'SQ','PAYC','DOCN','USB','MTB','FITB','TEX','OTEX','BILL','YOU','PDD','PCOR','PCTY','PAYO','NVEI','SAP','NICE','VEEV','ZETA','GB','PATH','OKTA','HUBS','YMM','TDUP','SHLS','CORT','HRMY','NVO','FOLD','MDXG','MNKD','HROW','ALKS']
    my_ticker_list = []
    my_ticker_list = [x.upper() for x in my_ticker_list]
    return my_ticker_list

def get_fifteen_full_run(ticker_list, daily_info):
    final_result_df = pd.DataFrame()
    for ticker in ticker_list:
        try:
            print (ticker)
            print ("test1")
            result = check_indicators_fifteen_min(ticker)
            print(result)
                #try:
                    #STEP 2 - run ticker 3d 15m.  Same for VXX, VVIX, SPY, TLT, GLD, OIL, JPY IWM, QQQ.  This isn't going to work unless I tail 1
            result['datetime_field'] = result.index
            print (result['datetime_field'][0])
            print (type(result['datetime_field'][0]))
            result['datetime_field'] = result['datetime_field'].dt.time
            result['open_session'] = result['datetime_field'].apply(lambda x: 1 if x.hour < 10 else 0)
            #result['open_session'] = 1 if result['datetime_field'].hour < 9 else 0
            #result['close_session'] = 1 if result['datetime_field'].hour > 14 and result['datetime_field'].minute > 30 else 0
            result['close_session'] = result['datetime_field'].apply(lambda x: 1 if x.hour == 15 and x.minute >= 30 else 0)
            result['lunch_session'] = result['datetime_field'].apply(lambda x: 1 if x.hour >= 12 and x.hour < 13 else 0)
            #result['lunch_session'] = 1 if result['datetime_field'].hour > 12 and result['datetime_field'].hour < 13 else 0
            #result = result.drop('datetime_field', axis=1)
            

            earnings_dates = get_earnings_dates(ticker)
            #earnings_dates_last_date = earnings_dates[earnings_dates['Reported EPS'].notnull()].index[0].to_pydatetime()#.strftime('%Y-%m-%d')
            surprise = earnings_dates[earnings_dates['Reported EPS'].notnull()]['Surprise(%)'][0]
            result['Surprise(%)'] = round(surprise, 2)
            print(result)
            ##add surprise, days until fri, days until earnings, and perhaps other k means from daily to continuous data in input and algo
            daily_TA_ticker = daily_info[(daily_info['ticker'] == ticker)]
            print(daily_TA_ticker)
            daily_TA_ticker = daily_TA_ticker.drop('ticker', axis=1)
            print(daily_TA_ticker)
            result['date_field'] = result.index
            result['date_field_copy'] = result.index
            result['date_field'] = result['date_field'].dt.date
            #result['date_field'] = result['date_field'].strftime("%Y-%m-%d")
            #date_string = date_x.strftime("%Y-%m-%d")  # Assuming desired format is YYYY-MM-DD


            result = get_days_to_earnings_in_df(ticker, result)
            print (result.shape)
            print (daily_TA_ticker.shape)
            result['days_until_earnings'] = result['days_until_earnings']/80 #normalize
            result['days_until_friday'] = result['date_field'].map(lambda x: get_days_to_friday_given_date_normalized(x))

            result['date_field'] = pd.to_datetime(result['date_field'])
            result['date_field'] = result['date_field'].dt.strftime('%Y-%m-%d')  # Assuming desired format is YYYY-MM-DD
            print (result.shape)
            print("is the error with 15 min data??????????????????")
            print(type(result['date_field'].iloc[0]))
            print(result['date_field'].tail(10))
            print("is the error with df data??????????????????")
            print(daily_TA_ticker['date_field'].tail(10))
            print(type(daily_TA_ticker['date_field'].iloc[0]))

            result = pd.merge(result, daily_TA_ticker, left_on =  'date_field', right_on = 'date_field', how = 'left')
            result = result.drop('date_field', axis=1)
            print (result.shape)

            print (final_result_df.shape)
            final_result_df = pd.concat([final_result_df, result])
            print (final_result_df.shape)
            print (final_result_df)
        except Exception as e:
            print("oops:  ", e)   
        
    print(final_result_df.shape)
    ###STEP 2 - GET 15 MIN DATA FOR COMPARISONS AND MERGE BY DATETIME

    list_of_comps = ['VXX', 'UUP', 'SPY', 'IEF', 'TLT', 'GLD', 'USO', 'IWM', 'QQQ']
    #VIX, dollar, SPY, 7-1o year, 20 year, gold, oil, smalls, tech.  Trying to predict all stocks (not particular ones) based on this.  remove QQQ and IWM
    list_of_comps = ['VXX', 'UUP', 'SPY', 'IEF', 'TLT', 'GLD', 'USO']
    #continuous_column_list =['pct_change_underlying', 'Volume', 'pct_to_5ema', 'pct_to_10ema', 'pct_to_30ema', 'pct_to_60ema', 'BB_UPPER', 'BB_LOWER', 'pct_to_SAR_support', 'pct_to_other_support', '14 period ADX.', '14 period RSI', '14 period MFI', 'DI+', 'DI-', '14 period STOCH %K', 'BearishFractal', 'BullishFractal']
    #each one has 18 indicators.  eek
    #7 x 3 = 21
    #9 x 18 = 140 something.  reduced dimensionality by A LOT!
    #####reduce to ['Volume', 'pct_to_10ema', 'pct_to_30ema']
    #will encoder work on such large volume?
    #list_of_comps = ['VXX', 'UUP', 'SPY', 'IEF', 'TLT', 'GLD', 'USO', 'FXY', 'IWM', 'QQQ']
    print ("test2")
    for ticker in list_of_comps:
        print ("test3")
        final_result_df = merge_fifteen_min_comp_data_full(ticker, final_result_df)
        print ("test4")
        print(final_result_df.shape)

        
    print(final_result_df.shape)


    final_result_df = final_result_df.dropna() 
    final_result_df.round(1) 

    print (final_result_df.shape)
    return final_result_df


def get_fifteen_full_run_SPY():
    final_result_df = pd.DataFrame()
    ticker = 'SPY'
    print (ticker)
    result = check_indicators_fifteen_min(ticker)
    print ("LOOK HERE")
    print(result.tail(34))

    result['datetime_field'] = result.index
    print (result['datetime_field'][0])
    print (type(result['datetime_field'][0]))
    result['datetime_field'] = result['datetime_field'].dt.time
    result['open_session'] = result['datetime_field'].apply(lambda x: 1 if x.hour < 10 else 0)
    result['close_session'] = result['datetime_field'].apply(lambda x: 1 if x.hour == 15 and x.minute >= 30 else 0)
    result['lunch_session'] = result['datetime_field'].apply(lambda x: 1 if x.hour >= 12 and x.hour < 13 else 0)
    print(result)

    result['date_field'] = result.index
    result['date_field_copy'] = result.index
    result['date_field'] = result['date_field'].dt.date
    print (result.shape)
    result['days_until_friday'] = result['date_field'].map(lambda x: get_days_to_friday_given_date_normalized(x))

    result['date_field'] = pd.to_datetime(result['date_field'])
    result['date_field'] = result['date_field'].dt.strftime('%Y-%m-%d')  # Assuming desired format is YYYY-MM-DD
    print (result.shape)
    print(type(result['date_field'].iloc[0]))
    print(result['date_field'].tail(10))

    result = result.drop('date_field', axis=1)
    print (result.shape)
    print (final_result_df.shape)
    final_result_df = pd.concat([final_result_df, result])
    print (final_result_df.shape)
    print (final_result_df)

    print(final_result_df.shape)
    ###STEP 2 - GET 15 MIN DATA FOR COMPARISONS AND MERGE BY DATETIME
    list_of_comps = ['VXX', '^VVIX']
    print ("test2")
    for ticker in list_of_comps:
        print ("test3")
        final_result_df = merge_fifteen_min_comp_data_full(ticker, final_result_df)
        print ("test4")
        print(final_result_df.shape)
        
    #final_result_df = final_result_df.dropna() 
    final_result_df.round(1) 
    print (final_result_df.shape)
    return final_result_df


def get_fifteen_predict_run_with_earnings(ticker_list, daily_info):
    final_result_df = pd.DataFrame()
    for ticker in ticker_list:
        try:
            #print (ticker)
            #print ("test1")
            result = check_indicators_fifteen_min(ticker)
            #result.to_csv("test.csv")
            #print(result)
                #try:
                    #STEP 2 - run ticker 3d 15m.  Same for VXX, VVIX, SPY, TLT, GLD, OIL, JPY IWM, QQQ.  This isn't going to work unless I tail 1
            result['datetime_field'] = result.index
            #print (result['datetime_field'][0])
            #print (type(result['datetime_field'][0]))
            result['datetime_field'] = result['datetime_field'].dt.time
            result['open_session'] = result['datetime_field'].apply(lambda x: 1 if x.hour < 10 else 0)
            result['close_session'] = result['datetime_field'].apply(lambda x: 1 if x.hour == 15 and x.minute >= 30 else 0)
            result['lunch_session'] = result['datetime_field'].apply(lambda x: 1 if x.hour >= 12 and x.hour < 13 else 0)

            # earnings_dates = get_earnings_dates(ticker)
            # print("this is earnings DF")
            # print(earnings_dates)
            # #earnings_dates_last_date = earnings_dates[earnings_dates['Reported EPS'].notnull()].index[0].to_pydatetime()#.strftime('%Y-%m-%d')
            # surprise = earnings_dates[earnings_dates['Reported EPS'].notnull()]['Surprise(%)'][0]
            # result['Surprise(%)'] = round(surprise, 2)
            #print(result)
            ##add surprise, days until fri, days until earnings, and perhaps other k means from daily to continuous data in input and algo
            #print("debug message 9888888")
            #print(daily_info.shape)
            daily_TA_ticker = daily_info[(daily_info['ticker'] == ticker)]
            #print("debug message 9999999")
            #print(daily_TA_ticker.shape)
            daily_TA_ticker = daily_TA_ticker.drop('ticker', axis=1)
            #print(daily_TA_ticker)
            result['date_field'] = result.index
            result['date_field_copy'] = result.index
            result['date_field'] = result['date_field'].dt.date
            #result['date_field'] = result['date_field'].strftime("%Y-%m-%d")
            #date_string = date_x.strftime("%Y-%m-%d")  # Assuming desired format is YYYY-MM-DD


            # result = get_days_to_earnings_in_df(ticker, result)
            #print (result.shape)
            #print (daily_TA_ticker.shape)
            # result['days_until_earnings'] = result['days_until_earnings']/80 #normalize
            result['days_until_friday'] = result['date_field'].map(lambda x: get_days_to_friday_given_date_normalized(x))

            result['date_field'] = pd.to_datetime(result['date_field'])
            result['date_field'] = result['date_field'].dt.strftime('%Y-%m-%d')  # Assuming desired format is YYYY-MM-DD
            #print (result.shape)
            #print("is the error with 15 min data??????????????????")
            #print(type(result['date_field'].iloc[0]))
            #print(result['date_field'].tail(10))
            #print("is the error with df data??????????????????")
            #print(daily_TA_ticker['date_field'].tail(10))
            #print(type(daily_TA_ticker['date_field'].iloc[0]))
            #print ("rrrrrrrrrrrrrrrrrr")

            result = pd.merge(result, daily_TA_ticker, left_on =  'date_field', right_on = 'date_field', how = 'left')
            #print ("xxxxxxx")
            result = result.drop('date_field', axis=1)
            result['ticker'] = ticker
            #print (result.shape)
            result = result.tail(1)
            #print (final_result_df.shape)
            #print ("ffffffff")
            final_result_df = pd.concat([final_result_df, result])
            final_result_df['tmp_join'] = 1

            print (final_result_df.shape)
            print (final_result_df)
        except Exception as e:
            print("oops:  ", e)   
        
    print(final_result_df.shape)
    ###STEP 2 - GET 15 MIN DATA FOR COMPARISONS AND MERGE BY DATETIME

    #list_of_comps = ['VXX', 'UUP', 'SPY', 'IEF', 'TLT', 'GLD', 'USO', 'IWM', 'QQQ']
    #VIX, dollar, SPY, 7-1o year, 20 year, gold, oil, smalls, tech.  Trying to predict all stocks (not particular ones) based on this.  remove QQQ and IWM
    #list_of_comps = ['VXX', 'UUP', 'SPY', 'IEF', 'TLT', 'GLD', 'USO']
    list_of_comps = ['SPY','TLT', 'VXX']
    #continuous_column_list =['pct_change_underlying', 'Volume', 'pct_to_5ema', 'pct_to_10ema', 'pct_to_30ema', 'pct_to_60ema', 'BB_UPPER', 'BB_LOWER', 'pct_to_SAR_support', 'pct_to_other_support', '14 period ADX.', '14 period RSI', '14 period MFI', 'DI+', 'DI-', '14 period STOCH %K', 'BearishFractal', 'BullishFractal']
    #each one has 18 indicators.  eek
    #7 x 3 = 21
    #9 x 18 = 140 something.  reduced dimensionality by A LOT!
    #####reduce to ['Volume', 'pct_to_10ema', 'pct_to_30ema']
    #will encoder work on such large volume?
    #list_of_comps = ['VXX', 'UUP', 'SPY', 'IEF', 'TLT', 'GLD', 'USO', 'FXY', 'IWM', 'QQQ']
    #print ("test2")
    # for ticker in list_of_comps:
    #     print ("test3")
    #     final_result_df = merge_fifteen_min_data(ticker, final_result_df)
    #     print ("test4")
    #     print(final_result_df.shape)

        
    #print(final_result_df.shape)


    #print(final_result_df)
    #final_result_df.to_csv('test_zero_df.csv')
    #final_result_df = final_result_df.dropna() 
    final_result_df.round(1) 

    #print (final_result_df.shape)
    return final_result_df

def get_fifteen_predict_run(ticker_list, daily_info):
    final_result_df = pd.DataFrame()
    for ticker in ticker_list:
        try:
            result = check_indicators_fifteen_min(ticker)
            result['datetime_field'] = result.index
            result['datetime_field'] = result['datetime_field'].dt.time
            result['open_session'] = result['datetime_field'].apply(lambda x: 1 if x.hour < 10 else 0)
            result['close_session'] = result['datetime_field'].apply(lambda x: 1 if x.hour == 15 and x.minute >= 30 else 0)
            result['lunch_session'] = result['datetime_field'].apply(lambda x: 1 if x.hour >= 12 and x.hour < 13 else 0)
            daily_TA_ticker = daily_info[(daily_info['ticker'] == ticker)]
            daily_TA_ticker = daily_TA_ticker.drop('ticker', axis=1)
            result['date_field'] = result.index
            result['date_field_copy'] = result.index
            result['date_field'] = result['date_field'].dt.date
            result['days_until_friday'] = result['date_field'].map(lambda x: get_days_to_friday_given_date_normalized(x))
            result['date_field'] = pd.to_datetime(result['date_field'])
            result['date_field'] = result['date_field'].dt.strftime('%Y-%m-%d')  # Assuming desired format is YYYY-MM-DD
            result = pd.merge(result, daily_TA_ticker, left_on =  'date_field', right_on = 'date_field', how = 'left')
            result = result.drop('date_field', axis=1)
            result['ticker'] = ticker
            result = result.tail(1)
            final_result_df = pd.concat([final_result_df, result])
            final_result_df['tmp_join'] = 1
        except Exception as e:
            print("oops get_fifteen_predict_run failed:  ", e)   
    print(final_result_df.shape)
    final_result_df.round(1) 
    return final_result_df

def get_put_options_data_atm_price(symbol, exp_date):
    the_ticker = yf.Ticker(symbol)
    current_price_underlying = the_ticker.info['currentPrice']
    beg_price = the_ticker.history('1y', '1d').tail(1)['Close'].values[0].item()
    rate_return = (current_price_underlying - beg_price)/beg_price
    put_options = pd.DataFrame(the_ticker.option_chain(exp_date).puts)
    itm_call_options = put_options[put_options['inTheMoney'] == True]
    #avg_atm_price = round(((itm_call_options.head(1)['bid'].values[0] + itm_call_options.head(1)['ask'].values[0])/2), 1)
    avg_atm_price = itm_call_options.tail(1)['lastPrice'].values[0]
    atm_price_pct_of_underlying = avg_atm_price/current_price_underlying
    iv = itm_call_options.head(1)['impliedVolatility'].values[0]
    openInterest = itm_call_options.head(1)['openInterest'].values[0]
    return [symbol, atm_price_pct_of_underlying, iv, rate_return, openInterest, 'put']


def get_call_options_data_atm_price(symbol, exp_date):
    the_ticker = yf.Ticker(symbol)
    current_price_underlying = the_ticker.info['currentPrice']
    beg_price = the_ticker.history('1y', '1d').tail(1)['Close'].values[0].item()
    rate_return = (current_price_underlying - beg_price)/beg_price
    call_options = pd.DataFrame(the_ticker.option_chain(exp_date).calls)
    itm_call_options = call_options[call_options['inTheMoney'] == False]
    #avg_atm_price = round(((itm_call_options.head(1)['bid'].values[0] + itm_call_options.head(1)['ask'].values[0])/2), 1)
    avg_atm_price = itm_call_options.head(1)['lastPrice'].values[0]
    print(symbol)
    print(itm_call_options)
    print(itm_call_options.tail(1))
    print(avg_atm_price)
    print(current_price_underlying)
    atm_price_pct_of_underlying = avg_atm_price/current_price_underlying
    iv = itm_call_options.tail(1)['impliedVolatility'].values[0]
    openInterest = itm_call_options.tail(1)['openInterest'].values[0]
    return [symbol, atm_price_pct_of_underlying, iv, rate_return, openInterest, 'call']

def read_spotgamma_web_token():
    secrets = get_secrets() 
#    with open('spotgamma_login_results.pickle', 'rb') as handle:
#        response = pickle.load(handle)
    return secrets['SPOTGAMMA_WEB_TOKEN']


def get_spotgamma_token():
    print("getting new sg token to get hiro data")
    secrets = get_secrets() 
    url = "https://api.spotgamma.com/v1/login"
    jwt = read_spotgamma_web_token()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
        "access-control-allow-credentials": True,
        "access-control-allow-origin": "*",
        "app-type": "web",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "Content-Type": "application/json",
        "Referer": "https://dashboard.spotgamma.com/",
        "Version": "1728",
        "X-Json-Web-Token": jwt,

        ":authority": "api.spotgamma.com",
        ":method": "POST",
        ":path": "/v1/login",
        ":scheme": "https",
    }
    headers = {

        "accept": "*/*",
        "accept-encoding": "gzip, deflate, bt, zstd",
        "accept-language": "en-US,en;q=0.9",
        "app-type": "web",
        "Content-Type": "application/json",
        "origin": "https://dashboard.spotgamma.com/",
        "Priority": "u=1,i",
        "Referer": "https://dashboard.spotgamma.com/",
        "Sec-CH-UA": '"Chromium";v="128", "Not)A;Brand";v="24", "Google Chrome";v="128"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": "Windows",
        "sec-Fetch-Dest": "",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
        "Version": "1728",
        "X-Json-Web-Token": jwt,
    }
    data = {"username": secrets['SPOTGAMMA_USERNAME'], "password": secrets['SPOTGAMMA_PWD']}
    print(data)
    print(type(data))
    print("posting to url to get new hiro token")
    response = requests.post(url, headers=headers, json=data)
    print(response.status_code)
    print(response)
    response.raise_for_status()  # raises exception when not a 2xx response
    if response.status_code != 204:
        response_data = response.json()
    print(response_data)
    bearer_token = response_data.get('sgToken')
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'spotgamma_login_results.pickle')#.csv
    with open(filepath, 'wb') as handle:
        pickle.dump(bearer_token, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return bearer_token

def read_spotgamma_token():
    secrets = get_secrets() 
#    with open('spotgamma_login_results.pickle', 'rb') as handle:
#        response = pickle.load(handle)
    return secrets['SPOTGAMMA_TOKEN']

def read_spotgamma_token_only():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir_path, 'spotgamma_login_results.pickle')#.csv
    with open(filepath, 'rb') as handle:
        response = pickle.load(handle)
    return response


    secrets = get_secrets() 

#    with open('spotgamma_login_results.pickle', 'rb') as handle:
#        response = pickle.load(handle)
    return secrets['SPOTGAMMA_TOKEN']


def get_spotgamma_hiro_data(filtered):
    #bearer_token = read_spotgamma_token()
    #bearer_token = get_spotgamma_token()
    #bearer_token = "Bearer " + bearer_token
    print("getting hiro data")
    jwt = read_spotgamma_web_token()
    url = "https://api.spotgamma.com/v6/running_hiro"
    try:
        print("trying to get hiro with old SG token")
        bearer_token = read_spotgamma_token_only()
        bearer_token = "Bearer " + bearer_token
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
        "Content-Type": "application/json",
        "Referer": "https://dashboard.spotgamma.com/",
        "Version": "1681",
        "Authorization": bearer_token,
        "X-Json-Web-Token": jwt,
        }
        hiro_response = requests.get(url, headers=headers)
        if hiro_response.status_code == 403:
            print("trying to get hiro with new SG token")
            bearer_token = get_spotgamma_token()
            bearer_token = "Bearer " + bearer_token
            headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
            "Content-Type": "application/json",
            "Referer": "https://dashboard.spotgamma.com/",
            "Version": "1681",
            "Authorization": bearer_token,
            "X-Json-Web-Token": jwt,
            }
            hiro_response = requests.get(url, headers=headers)
        else:
            print("OK, the stored bearer token was good")
        hiro_data = hiro_response.json()

    except Exception as e:
        print(f"error getting spotgamma token during hiro get: {e}")
        traceback.print_exc()
    #hiro_data = requests.get(url, headers=headers).json()
    if filtered == 1:
        for d in hiro_data:
            for k, v in d.items():
                if k == "currentDaySignal":
                    d[k] = float(v)
        hiro_data = [item for item in hiro_data if "currentDaySignal" in item and item["currentDaySignal"] > 0]
    elif filtered == 0:
        for d in hiro_data:
            for k, v in d.items():
                if k == "currentDaySignal":
                    d[k] = float(v)
        hiro_data = [item for item in hiro_data]
    else:
        print("not sure what to do")
    return hiro_data

# def get_spotgamma_hiro_data_best():
#     bearer_token = read_spotgamma_token()
#     #bearer_token = get_spotgamma_token()

#     print(bearer_token)
#     url = "https://api.spotgamma.com/v6/running_hiro"
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
#         "Authorization": f"""Bearer {bearer_token}"""
#     }
#     hiro_data = requests.get(url, headers=headers).json()
#     for d in hiro_data:
#         for k, v in d.items():
#             if k == "currentDaySignal":
#                 d[k] = float(v)
#             if k == "low1":
#                 d[k] = float(v)
#             if k == "high1":
#                 d[k] = float(v)
#             if k == "currentDaySignal":
#                 d[k] = float(v)



#     hiro_data = [item for item in hiro_data if "currentDaySignal" in item and item["currentDaySignal"] > 0]
#     hiro_data_df = pd.DataFrame(hiro_data)
#     hiro_data_df['buy_rank'] = hiro_data_df['currentDaySignal'] / hiro_data_df['high20']

#     return hiro_data

def get_spotgamma_equityhub_data(ticker):
    jwt = read_spotgamma_web_token()
    url = f"""https://api.spotgamma.com/v3/equitiesBySyms?syms={ticker}"""
    try:
        bearer_token = read_spotgamma_token_only()
        bearer_token = "Bearer " + bearer_token
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
        "Content-Type": "application/json",
        "Referer": "https://dashboard.spotgamma.com/",
        "Version": "1681",
        "Authorization": bearer_token,
        "X-Json-Web-Token": jwt,
        }
        hiro_response = requests.get(url, headers=headers)
        if hiro_response.status_code == 403:
            bearer_token = get_spotgamma_token()
            bearer_token = "Bearer " + bearer_token
            headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
            "Content-Type": "application/json",
            "Referer": "https://dashboard.spotgamma.com/",
            "Version": "1681",
            "Authorization": bearer_token,
            "X-Json-Web-Token": jwt,
            }
            hiro_response = requests.get(url, headers=headers)
        else:
            print("OK, the stored bearer token was good")
        hiro_data = hiro_response.json()
    except Exception as e:
        print(f"error getting spotgamma token during equityhub get: {e}")
        traceback.print_exc()
    return hiro_data

def expand_history(df, x_days):
    new_df = pd.DataFrame()
    for idx, row in df.iterrows():
        try:
            ticker = row['ticker']
            #the_history = get_ticker_history_offset_x_days(ticker, '1d', start = row['date_field'], x_days = x_days)
            the_history = get_daily_alpaca_data_as_df(ticker, row['date_field'])
            the_history = the_history.iloc[0:x_days+1]
            the_history['ticker'] = ticker
            print(ticker)
            print("below is the history which should be x days")
            print(the_history)
            the_history['PriorClose'] = the_history['Close'].shift(1)
            print(the_history)
            new_df = pd.concat([new_df, the_history], axis=0)
        except Exception as e:
            print(f"error getting ticker data: {e}")
            traceback.print_exc()
    return new_df

def expand_history_to_tgt(df, x_days, target_pct):
    new_df = pd.DataFrame()
    for idx, row in df.iterrows():
        ticker = row['ticker']
        the_history = get_ticker_history_offset_x_days(ticker, '1d', start = row['date_field'], x_days = x_days)
        the_history['ticker'] = ticker

        try:
            the_entry_price = the_history['Open'].iloc[0]
        except:
            print ("price error - stock likely delissted?????????????????")
            the_entry_price = 2
        condition_met = False
        rows_to_keep = []
        for idx, row in the_history.iterrows():
            if condition_met:
                continue  
            if row['High'] > round((the_entry_price*(1 + target_pct)),2):
                the_history.at[idx, 'Close'] = round(the_entry_price*1.02,2)
                condition_met = True
            rows_to_keep.append(idx)
        the_history = the_history.loc[rows_to_keep]

        print("-------------------------")
        print(ticker)
        the_history['PriorClose'] = the_history['Close'].shift(1)
        print(the_history)
        new_df = pd.concat([new_df, the_history], axis=0)
    return new_df


def expand_history_with_stop_only_day1dip(df, x_days, target_limit):
    new_df = pd.DataFrame()
    for idx, row in df.iterrows():
        ticker = row['ticker']
        the_history = get_ticker_history_offset_x_days(ticker, '1d', start = row['date_field'], x_days = x_days)
        the_history['ticker'] = ticker
        the_history['PriorClose'] = the_history['Close'].shift(1)
        the_history = the_history[(the_history['PriorClose'].notna())]
        try:
            if the_history['Open'].iloc[0] < the_history['PriorClose'].iloc[0]:
                #print(the_history['Open'].iloc[0])
                #print(the_history['PriorClose'].iloc[0])
                pass
            else:
                #print(the_history['Open'].iloc[0])
                #print(the_history['PriorClose'].iloc[0])
                try:
                    the_entry_price = the_history['Open'].iloc[0]
                    the_entry_price = the_entry_price * 1.001 #not likely to get at open price exactly
                except:
                    print ("price error - stock likely delissted?????????????????")
                    the_entry_price = 2
                condition_met = False
                rows_to_keep = []
                for idx, row in the_history.iterrows():
                    if condition_met:
                        continue  
                    if row['Low'] < round((the_entry_price*(1 + target_limit)),2):
                        the_history.at[idx, 'Close'] = round((the_entry_price*(1 + target_limit)),2)
                        the_history.loc[0, 'PriorClose'] = the_entry_price
                        condition_met = True
                    rows_to_keep.append(idx)
                the_history = the_history.loc[rows_to_keep]

                print("-------------------------")
                print(ticker)
                print(the_history)
                new_df = pd.concat([new_df, the_history], axis=0)
        except Exception as E:
            print(E)
    return new_df


def expand_history_to_tgt_only_day1dip(df, x_days, target_pct):
    new_df = pd.DataFrame()
    for idx, row in df.iterrows():
        ticker = row['ticker']
        the_history = get_ticker_history_offset_x_days(ticker, '1d', start = row['date_field'], x_days = x_days)
        the_history['ticker'] = ticker
        the_history['PriorClose'] = the_history['Close'].shift(1)
        the_history = the_history[(the_history['PriorClose'].notna())]
        try:
            if the_history['Open'].iloc[0] < the_history['PriorClose'].iloc[0]:
                #print(the_history['Open'].iloc[0])
                #print(the_history['PriorClose'].iloc[0])
                pass
            else:
                #print(the_history['Open'].iloc[0])
                #print(the_history['PriorClose'].iloc[0])
                try:
                    the_entry_price = the_history['Open'].iloc[0]
                except:
                    print ("price error - stock likely delissted?????????????????")
                    the_entry_price = 2
                condition_met = False
                rows_to_keep = []
                for idx, row in the_history.iterrows():
                    if condition_met:
                        continue  
                    if row['High'] > round((the_entry_price*(1 + target_pct)),2):
                        the_history.at[idx, 'Close'] = round((the_entry_price*(1 + target_pct)),2)
                        the_history.loc[0, 'PriorClose'] = the_entry_price
                        condition_met = True
                    rows_to_keep.append(idx)
                the_history = the_history.loc[rows_to_keep]

                print("-------------------------")
                print(ticker)
                print(the_history)
                new_df = pd.concat([new_df, the_history], axis=0)
        except Exception as E:
            print(E)
    return new_df


def expand_history_to_tgt_only_day1dip_random(df, x_days, target_pct):
    new_df = pd.DataFrame()
    for idx, row in df.iterrows():
        ticker = get_random_ticker()
#        ticker = row['ticker']
        the_history = get_ticker_history_offset_x_days(ticker, '1d', start = row['date_field'], x_days = x_days)
        the_history['ticker'] = ticker
        the_history['PriorClose'] = the_history['Close'].shift(1)
        the_history = the_history[(the_history['PriorClose'].notna())]
        try:
            if the_history['Open'].iloc[0] < the_history['PriorClose'].iloc[0]:
                #print(the_history['Open'].iloc[0])
                #print(the_history['PriorClose'].iloc[0])
                pass
            else:
                #print(the_history['Open'].iloc[0])
                #print(the_history['PriorClose'].iloc[0])
                try:
                    the_entry_price = the_history['Open'].iloc[0]
                except:
                    print ("price error - stock likely delissted?????????????????")
                    the_entry_price = 2
                condition_met = False
                rows_to_keep = []
                for idx, row in the_history.iterrows():
                    if condition_met:
                        continue  
                    if row['High'] > round((the_entry_price*(1 + target_pct)),2):
                        the_history.at[idx, 'Close'] = round((the_entry_price*(1 + target_pct)),2)
                        the_history.loc[0, 'PriorClose'] = the_entry_price
                        condition_met = True
                    rows_to_keep.append(idx)
                the_history = the_history.loc[rows_to_keep]

                print("-------------------------")
                print(ticker)
                print(the_history)
                new_df = pd.concat([new_df, the_history], axis=0)
        except Exception as E:
            print(E)
    return new_df


def expand_history_random(df, x_days):
    new_df = pd.DataFrame()
    for idx, row in df.iterrows():
        try:
            ticker = get_random_ticker()
            #the_history = get_ticker_history_offset_x_days(ticker, '1d', start = row['date_field'], x_days = x_days)
            the_history = get_daily_alpaca_data_as_df(ticker, row['date_field'])
            the_history = the_history.iloc[0:x_days+1]
            the_history['ticker'] = ticker
            print(ticker)
            print("below is the history which should be x days")
            print(the_history)
            the_history['PriorClose'] = the_history['Close'].shift(1)
            print(the_history)
            new_df = pd.concat([new_df, the_history], axis=0)
        except Exception as e:
            print(f"error getting ticker data: {e}")
            traceback.print_exc()
    return new_df

#replaced with alpaca
# def expand_history_random(df, x_days):
#     new_df = pd.DataFrame()
#     for idx, row in df.iterrows():
#         ticker = get_random_ticker()
#         print(f"random ticker this time is {ticker} - not {idx}.  A diff random is {get_random_ticker()}")
#         the_history = get_ticker_history_offset_x_days(ticker, '1d', start = row['date_field'], x_days = x_days)
#         the_history['ticker'] = ticker
#         print(ticker)
#         the_history['PriorClose'] = the_history['Close'].shift(1)
#         print(the_history)
#         new_df = pd.concat([new_df, the_history], axis=0)
#     return new_df
    

def expand_history_spy(df, x_days):
    new_df = pd.DataFrame()
    for idx, row in df.iterrows():
        ticker = 'SPY'
        the_history = get_ticker_history_offset_x_days(ticker, '1d', start = row['date_field'], x_days = x_days)
        the_history['ticker'] = ticker
        print(ticker)
        the_history['PriorClose'] = the_history['Close'].shift(1)
        print(the_history)
        new_df = pd.concat([new_df, the_history], axis=0)
    return new_df

def create_weekly_historical_analysis(filepath, plot_filename, benchmark_ticker, start_date, x_days, label):
    ## get my stocks 
    current_time = datetime.datetime.now()
    pd.set_option("display.max_colwidth", 10000)
    data = pd.read_csv(filepath, encoding='iso-8859-1')
    #yday = current_time - timedelta(days=10)
    #yday = yday.strftime("%Y-%m-%d")
    #start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    data = data.drop_duplicates()
    data.to_csv(filepath,index = False)
    #data = data[(data['date_field'] >= start_date)]
    #data = data[data['date_field'] >= start_date]
    print(data)
    ## get benchmark returns
    print("got to SPY get ticker thing")
    #benchmark_data = get_ticker_history_offset('SPY', '10y', '1d', start = start_date)###change this to remove start and remove _offset
    #benchmark_data = get_daily_alpaca_data_as_df_all('SPY', start_date)
    #benchmark_data.to_csv("check_benchmarks_data.csv")
    #print("done with SPY get ticker thing")
    #benchmark_data['PriorClose'] = benchmark_data['Close'].shift(1)
    #benchmark_data['MyReturn'] = ((benchmark_data['Close'] - benchmark_data['PriorClose']) / benchmark_data['PriorClose']) * 100
    #benchmark_data = benchmark_data[(benchmark_data['PriorClose'].notna())]
    #benchmark_returns_df = benchmark_data.groupby('Date').mean()['MyReturn']

    ## get data returns
    data = data[['ticker', 'date_field']].drop_duplicates()
    #data = data.groupby('ticker').agg(date_field_min= ('date_field', 'min')) 
    data = data.sort_values(by=['date_field'], ascending=True)
    #random_data = data.copy()
    #spy_data = data.copy()

    ##prepare my data
    print("got to MY get ticker thing")
    my_data = expand_history(data, x_days)
    my_data.to_csv("my_data_check.csv")
    print("done with  MY get ticker thing")
    
    my_data = my_data[(my_data['PriorClose'].notna())]
    my_data = my_data[my_data['PriorClose'] > 2]

    #calc my returns multi_day_high
    my_data['MyReturn'] = ((my_data['Close'] - my_data['PriorClose']) / my_data['PriorClose']) * 100
    my_data['MyReturn_overnight'] = ((my_data['Open'] - my_data['PriorClose']) / my_data['PriorClose']) * 100
    my_data['MyReturn_daytrade'] = ((my_data['Close'] - my_data['Open']) / my_data['Open']) * 100
    my_data.to_csv("my_data_check2.csv")
    #focus just on my returns
    my_data_overnight = my_data['MyReturn_overnight']
    my_data_daytrade = my_data['MyReturn_daytrade']
    my_data = my_data['MyReturn']
    print (my_data)
    #calculate mean
    my_data = my_data.groupby('Date').mean()
    print("grouped by date")
    print(my_data)
    my_data_overnight = my_data_overnight.groupby('Date').mean()
    print(my_data_overnight)
    my_data_daytrade = my_data_daytrade.groupby('Date').mean()
    print(my_data_daytrade)

    ##prepare random data
    # random_data = expand_history_random(random_data, x_days)
    # random_data = random_data[(random_data['PriorClose'].notna())]
    # random_data['MyReturn'] = ((random_data['Close'] - random_data['PriorClose']) / random_data['PriorClose']) * 100
    # random_data['MyReturn_overnight'] = ((random_data['Open'] - random_data['PriorClose']) / random_data['PriorClose']) * 100
    # random_data['MyReturn_daytrade'] = ((random_data['Close'] - random_data['Open']) / random_data['Open']) * 100

    # random_data_overnight = random_data['MyReturn_overnight']
    # random_data_daytrade = random_data['MyReturn_daytrade']
    # random_data = random_data['MyReturn']

    # random_data = random_data.groupby('Date').mean()
    # random_data_overnight = random_data_overnight.groupby('Date').mean()
    # random_data_daytrade = random_data_daytrade.groupby('Date').mean()

    ##prepare spy data
    # spy_data = expand_history_spy(spy_data, x_days)
    # spy_data = spy_data[(spy_data['PriorClose'].notna())]
    # #spy_data['MyReturn'] = ((spy_data['Close'] - spy_data['Open']) / spy_data['Open']) * 100
    # spy_data['MyReturn_overnight'] = ((spy_data['Open'] - spy_data['PriorClose']) / spy_data['PriorClose']) * 100
    # #spy_data = spy_data['MyReturn']
    # spy_data = spy_data['MyReturn_overnight']
    # spy_data = spy_data.groupby('Date').mean()

    #plot
    my_data = my_data.cumsum()
    my_data_overnight = my_data_overnight.cumsum()
    my_data_daytrade = my_data_daytrade.cumsum()
    # random_data = random_data.cumsum()
    # random_data_daytrade = random_data_daytrade.cumsum()
    # random_data_overnight = random_data_overnight.cumsum()
    # spy_data_overnight = spy_data.cumsum()
    print("my_data")
    print(my_data)
    print("my_data_overnight")
    print(my_data_overnight)
    print("my_data_daytrade")
    print(my_data_daytrade)
    # print("random_data")
    # print(random_data)
    #benchmark_returns_df = benchmark_returns_df.cumsum()
    #print(benchmark_returns_df)
    plot_performance_1line(my_data, my_data_daytrade, plot_filename, label)
    plot_performance_1line_plotly(my_data, f"plotly_{plot_filename}", label)
#    plot_performance(my_data, benchmark_returns_df, plot_filename, label, 'Benchmark (SPY)')
    #plot_performance_with_random(my_data, random_data, random_data_overnight, random_data_daytrade, my_data_overnight, my_data_daytrade, benchmark_returns_df, spy_data_overnight, plot_filename, label, 'Random Returns', 'Overnight', 'Daytrade only', f'Benchmark ({benchmark_ticker})')
    return None


def create_weekly_historical_analysis_full(filepath, plot_filename, benchmark_ticker, start_date, x_days, label):
    ## get my stocks 
    current_time = datetime.datetime.now()
    pd.set_option("display.max_colwidth", 10000)
    data = pd.read_csv(filepath, encoding='iso-8859-1')
    #yday = current_time - timedelta(days=10)
    #yday = yday.strftime("%Y-%m-%d")
    #start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    data = data.drop_duplicates()
    data.to_csv(filepath,index = False)
    #data = data[(data['date_field'] >= start_date)]
    #data = data[data['date_field'] >= start_date]
    print(data)
    ## get benchmark returns
    print("got to SPY get ticker thing")
    benchmark_data = get_ticker_history_offset('SPY', '10y', '1d', start = start_date)###change this to remove start and remove _offset
    benchmark_data = get_daily_alpaca_data_as_df_all('SPY', start_date)
    benchmark_data.to_csv("check_benchmarks_data.csv")
    print("done with SPY get ticker thing")
    benchmark_data['PriorClose'] = benchmark_data['Close'].shift(1)
    benchmark_data['MyReturn'] = ((benchmark_data['Close'] - benchmark_data['PriorClose']) / benchmark_data['PriorClose']) * 100
    benchmark_data = benchmark_data[(benchmark_data['PriorClose'].notna())]
    benchmark_returns_df = benchmark_data.groupby('Date').mean()['MyReturn']

    ## get data returns
    data = data[['ticker', 'date_field']].drop_duplicates()
    #data = data.groupby('ticker').agg(date_field_min= ('date_field', 'min')) 
    data = data.sort_values(by=['date_field'], ascending=True)
    random_data = data.copy()
    spy_data = data.copy()

    ##prepare my data
    print("got to MY get ticker thing")
    my_data = expand_history(data, x_days)
    my_data.to_csv("my_data_check.csv")
    print("done with  MY get ticker thing")
    
    my_data = my_data[(my_data['PriorClose'].notna())]
    my_data = my_data[my_data['PriorClose'] > 2]

    #calc my returns multi_day_high
    my_data['MyReturn'] = ((my_data['Close'] - my_data['PriorClose']) / my_data['PriorClose']) * 100
    my_data['MyReturn_overnight'] = ((my_data['Open'] - my_data['PriorClose']) / my_data['PriorClose']) * 100
    my_data['MyReturn_daytrade'] = ((my_data['Close'] - my_data['Open']) / my_data['Open']) * 100
    my_data.to_csv("my_data_check2.csv")
    #focus just on my returns
    my_data_overnight = my_data['MyReturn_overnight']
    my_data_daytrade = my_data['MyReturn_daytrade']
    my_data = my_data['MyReturn']
    print (my_data)
    #calculate mean
    my_data = my_data.groupby('Date').mean()
    print("grouped by date")
    print(my_data)
    my_data_overnight = my_data_overnight.groupby('Date').mean()
    print(my_data_overnight)
    my_data_daytrade = my_data_daytrade.groupby('Date').mean()
    print(my_data_daytrade)

    ##prepare random data
    random_data = expand_history_random(random_data, x_days)
    random_data = random_data[(random_data['PriorClose'].notna())]
    random_data['MyReturn'] = ((random_data['Close'] - random_data['PriorClose']) / random_data['PriorClose']) * 100
    random_data['MyReturn_overnight'] = ((random_data['Open'] - random_data['PriorClose']) / random_data['PriorClose']) * 100
    random_data['MyReturn_daytrade'] = ((random_data['Close'] - random_data['Open']) / random_data['Open']) * 100

    random_data_overnight = random_data['MyReturn_overnight']
    random_data_daytrade = random_data['MyReturn_daytrade']
    random_data = random_data['MyReturn']

    random_data = random_data.groupby('Date').mean()
    random_data_overnight = random_data_overnight.groupby('Date').mean()
    random_data_daytrade = random_data_daytrade.groupby('Date').mean()

    ##prepare spy data
    spy_data = expand_history_spy(spy_data, x_days)
    spy_data = spy_data[(spy_data['PriorClose'].notna())]
    spy_data['MyReturn'] = ((spy_data['Close'] - spy_data['Open']) / spy_data['Open']) * 100
    #spy_data['MyReturn_overnight'] = ((spy_data['Open'] - spy_data['PriorClose']) / spy_data['PriorClose']) * 100
    spy_data = spy_data['MyReturn']
    #spy_data = spy_data['MyReturn_overnight']
    spy_data = spy_data.groupby('Date').mean()

    #plot
    my_data = my_data.cumsum()
    my_data_overnight = my_data_overnight.cumsum()
    my_data_daytrade = my_data_daytrade.cumsum()
    random_data = random_data.cumsum()
    random_data_daytrade = random_data_daytrade.cumsum()
    random_data_overnight = random_data_overnight.cumsum()
    spy_data = spy_data.cumsum()
    print("my_data")
    print(my_data)
    print("my_data_overnight")
    print(my_data_overnight)
    print("my_data_daytrade")
    print(my_data_daytrade)
    # print("random_data")
    # print(random_data)
    benchmark_returns_df = benchmark_returns_df.cumsum()
    #print(benchmark_returns_df)
    #plot_performance_1line(my_data, my_data_daytrade, plot_filename, label)
    #plot_performance_1line_plotly(my_data, f"plotly_{plot_filename}", label)
#    plot_performance(my_data, benchmark_returns_df, plot_filename, label, 'Benchmark (SPY)')
    plot_performance_with_random(my_data, random_data, random_data_overnight, random_data_daytrade, my_data_overnight, my_data_daytrade, benchmark_returns_df, spy_data, plot_filename, label, 'Random Returns', 'Overnight', 'Daytrade only', f'Benchmark ({benchmark_ticker})')
    return None


def create_weekly_historical_analysis_overfit(filepath, plot_filename, benchmark_ticker, start_date, x_days, label):
    ## get my stocks 
    current_time = datetime.datetime.now()
    pd.set_option("display.max_colwidth", 10000)
    data = pd.read_csv(filepath, encoding='iso-8859-1')
    #yday = current_time - timedelta(days=10)
    #yday = yday.strftime("%Y-%m-%d")
    #start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    data = data.drop_duplicates()
    data.to_csv(filepath,index = False)
    #data = data[(data['date_field'] >= start_date)]
    #data = data[data['date_field'] >= start_date]
    data = data[data['Total_overfit'] >= 2]
    data = data[data['Total_overfit_30'] >= 2]
    print(data)
    ## get benchmark returns
    print("got to SPY get ticker thing")
    #benchmark_data = get_ticker_history_offset('SPY', '10y', '1d', start = start_date)###change this to remove start and remove _offset
    #benchmark_data = get_daily_alpaca_data_as_df_all('SPY', start_date)
    #benchmark_data.to_csv("check_benchmarks_data.csv")
    #print("done with SPY get ticker thing")
    #benchmark_data['PriorClose'] = benchmark_data['Close'].shift(1)
    #benchmark_data['MyReturn'] = ((benchmark_data['Close'] - benchmark_data['PriorClose']) / benchmark_data['PriorClose']) * 100
    #benchmark_data = benchmark_data[(benchmark_data['PriorClose'].notna())]
    #benchmark_returns_df = benchmark_data.groupby('Date').mean()['MyReturn']

    ## get data returns
    data = data[['ticker', 'date_field']].drop_duplicates()
    #data = data.groupby('ticker').agg(date_field_min= ('date_field', 'min')) 
    data = data.sort_values(by=['date_field'], ascending=True)
    #random_data = data.copy()
    #spy_data = data.copy()

    ##prepare my data
    print("got to MY get ticker thing")
    my_data = expand_history(data, x_days)
    my_data.to_csv("my_data_check.csv")
    print("done with  MY get ticker thing")
    
    my_data = my_data[(my_data['PriorClose'].notna())]
    #calc my returns multi_day_high
    my_data['MyReturn'] = ((my_data['Close'] - my_data['PriorClose']) / my_data['PriorClose']) * 100
    my_data['MyReturn_overnight'] = ((my_data['Open'] - my_data['PriorClose']) / my_data['PriorClose']) * 100
    my_data['MyReturn_daytrade'] = ((my_data['Close'] - my_data['Open']) / my_data['Open']) * 100
    my_data.to_csv("my_data_check2.csv")
    #focus just on my returns
    my_data_overnight = my_data['MyReturn_overnight']
    my_data_daytrade = my_data['MyReturn_daytrade']
    my_data = my_data['MyReturn']
    print (my_data)
    #calculate mean
    my_data = my_data.groupby('Date').mean()
    print("grouped by date")
    print(my_data)
    my_data_overnight = my_data_overnight.groupby('Date').mean()
    print(my_data_overnight)
    my_data_daytrade = my_data_daytrade.groupby('Date').mean()
    print(my_data_daytrade)

    ##prepare random data
    # random_data = expand_history_random(random_data, x_days)
    # random_data = random_data[(random_data['PriorClose'].notna())]
    # random_data['MyReturn'] = ((random_data['Close'] - random_data['PriorClose']) / random_data['PriorClose']) * 100
    # random_data['MyReturn_overnight'] = ((random_data['Open'] - random_data['PriorClose']) / random_data['PriorClose']) * 100
    # random_data['MyReturn_daytrade'] = ((random_data['Close'] - random_data['Open']) / random_data['Open']) * 100

    # random_data_overnight = random_data['MyReturn_overnight']
    # random_data_daytrade = random_data['MyReturn_daytrade']
    # random_data = random_data['MyReturn']

    # random_data = random_data.groupby('Date').mean()
    # random_data_overnight = random_data_overnight.groupby('Date').mean()
    # random_data_daytrade = random_data_daytrade.groupby('Date').mean()

    ##prepare spy data
    # spy_data = expand_history_spy(spy_data, x_days)
    # spy_data = spy_data[(spy_data['PriorClose'].notna())]
    # #spy_data['MyReturn'] = ((spy_data['Close'] - spy_data['Open']) / spy_data['Open']) * 100
    # spy_data['MyReturn_overnight'] = ((spy_data['Open'] - spy_data['PriorClose']) / spy_data['PriorClose']) * 100
    # #spy_data = spy_data['MyReturn']
    # spy_data = spy_data['MyReturn_overnight']
    # spy_data = spy_data.groupby('Date').mean()

    #plot
    my_data = my_data.cumsum()
    my_data_overnight = my_data_overnight.cumsum()
    my_data_daytrade = my_data_daytrade.cumsum()
    # random_data = random_data.cumsum()
    # random_data_daytrade = random_data_daytrade.cumsum()
    # random_data_overnight = random_data_overnight.cumsum()
    # spy_data_overnight = spy_data.cumsum()
    print("my_data")
    print(my_data)
    print("my_data_overnight")
    print(my_data_overnight)
    print("my_data_daytrade")
    print(my_data_daytrade)
    # print("random_data")
    # print(random_data)
    #benchmark_returns_df = benchmark_returns_df.cumsum()
    #print(benchmark_returns_df)
    plot_performance_1line(my_data, my_data_daytrade, plot_filename, label)
    plot_performance_1line_plotly(my_data, f"plotly_{plot_filename}", label)
#    plot_performance(my_data, benchmark_returns_df, plot_filename, label, 'Benchmark (SPY)')
    #plot_performance_with_random(my_data, random_data, random_data_overnight, random_data_daytrade, my_data_overnight, my_data_daytrade, benchmark_returns_df, spy_data_overnight, plot_filename, label, 'Random Returns', 'Overnight', 'Daytrade only', f'Benchmark ({benchmark_ticker})')
    return None



def create_weekly_historical_analysis_new(filepath, plot_filename, benchmark_ticker, start_date, x_days, label):
    ## get my stocks 
    pd.set_option("display.max_colwidth", 10000)
    data = pd.read_csv(filepath, encoding='iso-8859-1')
    #yday = current_time - timedelta(days=10)
    #yday = yday.strftime("%Y-%m-%d")
    #start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    data = data.drop_duplicates()
    data.to_csv(filepath,index = False)
    #data = data[(data['date_field'] >= start_date)]
    #data = data[data['date_field'] >= start_date]
    print(data)
    ## get benchmark returns
    print("got to SPY get ticker thing")
    #benchmark_data = get_ticker_history_offset_new('SPY', '10y', '1d', start = start_date)###change this to remove start and remove _offset
    benchmark_data = get_ticker_history_offset('SPY', '10y', '1d', start = start_date)###change this to remove start and remove _offset
    print("done with SPY get ticker thing")
    benchmark_data['PriorClose'] = benchmark_data['Close'].shift(1)
    benchmark_data['MyReturn'] = ((benchmark_data['Close'] - benchmark_data['PriorClose']) / benchmark_data['PriorClose']) * 100
    benchmark_data = benchmark_data[(benchmark_data['PriorClose'].notna())]
    benchmark_returns_df = benchmark_data.groupby('Date').mean()['MyReturn']

    ## get data returns
    data = data[['ticker', 'date_field']].drop_duplicates()
    #data = data.groupby('ticker').agg(date_field_min= ('date_field', 'min')) 
    data = data.sort_values(by=['date_field'], ascending=True)
    random_data = data.copy()
    spy_data = data.copy()

    ##prepare my data
    print("got to MY get ticker thing")
    my_data = expand_history(data, x_days)
    my_data.to_csv("my_data_check.csv")
    print("done with  MY get ticker thing")
    
    my_data = my_data[(my_data['PriorClose'].notna())]
    #calc my returns multi_day_high
    my_data['MyReturn'] = ((my_data['Close'] - my_data['PriorClose']) / my_data['PriorClose']) * 100
    my_data['MyReturn_overnight'] = ((my_data['Open'] - my_data['PriorClose']) / my_data['PriorClose']) * 100
    my_data['MyReturn_daytrade'] = ((my_data['Close'] - my_data['Open']) / my_data['Open']) * 100
    my_data.to_csv("my_data_check2.csv")
    #focus just on my returns
    my_data_overnight = my_data['MyReturn_overnight']
    my_data_daytrade = my_data['MyReturn_daytrade']
    my_data = my_data['MyReturn']
    print (my_data)
    #calculate mean
    my_data = my_data.groupby('Date').mean()
    print("grouped by date")
    print(my_data)
    my_data_overnight = my_data_overnight.groupby('Date').mean()
    print(my_data_overnight)
    my_data_daytrade = my_data_daytrade.groupby('Date').mean()
    print(my_data_daytrade)

    ##prepare random data
    random_data = expand_history_random(random_data, x_days)
    random_data = random_data[(random_data['PriorClose'].notna())]
    random_data['MyReturn'] = ((random_data['Close'] - random_data['PriorClose']) / random_data['PriorClose']) * 100
    random_data['MyReturn_overnight'] = ((random_data['Open'] - random_data['PriorClose']) / random_data['PriorClose']) * 100
    random_data['MyReturn_daytrade'] = ((random_data['Close'] - random_data['Open']) / random_data['Open']) * 100

    random_data_overnight = random_data['MyReturn_overnight']
    random_data_daytrade = random_data['MyReturn_daytrade']
    random_data = random_data['MyReturn']

    random_data = random_data.groupby('Date').mean()
    random_data_overnight = random_data_overnight.groupby('Date').mean()
    random_data_daytrade = random_data_daytrade.groupby('Date').mean()

    ##prepare spy data
    spy_data = expand_history_spy(spy_data, x_days)
    spy_data = spy_data[(spy_data['PriorClose'].notna())]
    #spy_data['MyReturn'] = ((spy_data['Close'] - spy_data['Open']) / spy_data['Open']) * 100
    spy_data['MyReturn_overnight'] = ((spy_data['Open'] - spy_data['PriorClose']) / spy_data['PriorClose']) * 100
    #spy_data = spy_data['MyReturn']
    spy_data = spy_data['MyReturn_overnight']
    spy_data = spy_data.groupby('Date').mean()

    #plot
    my_data = my_data.cumsum()
    my_data_overnight = my_data_overnight.cumsum()
    my_data_daytrade = my_data_daytrade.cumsum()
    random_data = random_data.cumsum()
    random_data_daytrade = random_data_daytrade.cumsum()
    random_data_overnight = random_data_overnight.cumsum()
    spy_data_overnight = spy_data.cumsum()
    print("my_data")
    print(my_data)
    print("my_data_overnight")
    print(my_data_overnight)
    print("my_data_daytrade")
    print(my_data_daytrade)
    print("random_data")
    print(random_data)
    benchmark_returns_df = benchmark_returns_df.cumsum()
    print(benchmark_returns_df)
    plot_performance(my_data, benchmark_returns_df, plot_filename, label, 'Benchmark (SPY)')
    #plot_performance_with_random(my_data, random_data, random_data_overnight, random_data_daytrade, my_data_overnight, my_data_daytrade, benchmark_returns_df, spy_data_overnight, plot_filename, label, 'Random Returns', 'Overnight', 'Daytrade only', f'Benchmark ({benchmark_ticker})')
    return None



def create_weekly_historical_analysis_max(filepath, plot_filename, benchmark_ticker, start_date, x_days, label, stop_pct):
    ## get my stocks 
    current_time = datetime.datetime.now()
    pd.set_option("display.max_colwidth", 10000)
    data = pd.read_csv(filepath, encoding='iso-8859-1')
    #yday = current_time - timedelta(days=10)
    #yday = yday.strftime("%Y-%m-%d")
    #start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    data = data.drop_duplicates()
    data.to_csv(filepath,index = False)
    #data = data[(data['date_field'] >= start_date)]
    #data = data[data['date_field'] >= start_date]
    print(data)
    ## get benchmark returns
    print("got to SPY get ticker thing")
    benchmark_data = get_ticker_history_offset('SPY', '10y', '1d', start = start_date)###change this to remove start and remove _offset
    print("done with SPY get ticker thing")
    benchmark_data['PriorClose'] = benchmark_data['Close'].shift(1)
    benchmark_data['MyReturn'] = ((benchmark_data['Close'] - benchmark_data['PriorClose']) / benchmark_data['PriorClose']) * 100
    benchmark_data = benchmark_data[(benchmark_data['PriorClose'].notna())]
    benchmark_returns_df = benchmark_data.groupby('Date').mean()['MyReturn']

    ## get data returns
    data = data[['ticker', 'date_field']].drop_duplicates()
    #data = data.groupby('ticker').agg(date_field_min= ('date_field', 'min')) 
    data = data.sort_values(by=['date_field'], ascending=True)
    random_data = data.copy()
    spy_data = data.copy()

    ##prepare my data
    print("got to MY get ticker thing")
#    my_data = expand_history_to_tgt_only_day1dip(data, x_days, .05)
    my_data = expand_history_with_stop_only_day1dip(data, x_days, stop_pct)
    print("done with  MY get ticker thing")
    print(my_data)
    
    #my_data = my_data[(my_data['PriorClose'].notna())] #moved to function
    #calc my returns
    my_data['MyReturn'] = ((my_data['Close'] - my_data['PriorClose']) / my_data['PriorClose']) * 100
    #my_data['MyReturn'] = ((my_data['Close'] - my_data['Open']) / my_data['Open']) * 100
    #my_data['MyReturn'] = ((my_data['multi_day_high'] - my_data['PriorClose']) / my_data['PriorClose']) * 100
    #my_data['MyReturn'] = ((my_data['multi_day_high'] - my_data['Open']) / my_data['Open']) * 100
#    my_data = my_data[my_data['Open'] < my_data['PriorClose']] #not doing what I thought it was.  Need it to only do this for first in ticker set
    #['MyReturn_overnight'] = ((my_data['Open'] - my_data['PriorClose']) / my_data['PriorClose']) * 100
    #my_data['MyReturn_daytrade'] = ((my_data['Close'] - my_data['Open']) / my_data['Open']) * 100
    my_data['MyReturn_overnight'] = ((my_data['Close'] - my_data['PriorClose']) / my_data['PriorClose']) * 100
    my_data['MyReturn_daytrade'] = ((my_data['Close'] - my_data['PriorClose']) / my_data['PriorClose']) * 100

    #focus just on my returns
    my_data_overnight = my_data['MyReturn_overnight']
    my_data_daytrade = my_data['MyReturn_daytrade']
    my_data = my_data['MyReturn']
    print ("loook here-----------------------------------")
    print (my_data)
    #calculate mean
    my_data = my_data.groupby('Date').mean()
    print("grouped by date")
    print(my_data)
    my_data_overnight = my_data_overnight.groupby('Date').mean()
    print(my_data_overnight)
    my_data_daytrade = my_data_daytrade.groupby('Date').mean()
    print(my_data_daytrade)

    ##prepare random data
    random_data = expand_history_random(random_data, x_days)
    random_data = random_data[(random_data['PriorClose'].notna())]
    random_data['MyReturn'] = ((random_data['Close'] - random_data['PriorClose']) / random_data['PriorClose']) * 100
    random_data['MyReturn_overnight'] = random_data['MyReturn']
    random_data['MyReturn_daytrade'] = random_data['MyReturn']


    random_data_overnight = random_data['MyReturn_overnight']
    random_data_daytrade = random_data['MyReturn_daytrade']
    random_data = random_data['MyReturn']

    random_data = random_data.groupby('Date').mean()
    random_data_overnight = random_data_overnight.groupby('Date').mean()
    random_data_daytrade = random_data_daytrade.groupby('Date').mean()

    ##prepare spy data
    spy_data = expand_history_spy(spy_data, x_days)
    spy_data = spy_data[(spy_data['PriorClose'].notna())]
    #spy_data['MyReturn'] = ((spy_data['Close'] - spy_data['Open']) / spy_data['Open']) * 100
    spy_data['MyReturn_overnight'] = ((spy_data['Open'] - spy_data['PriorClose']) / spy_data['PriorClose']) * 100
    #spy_data = spy_data['MyReturn']
    spy_data = spy_data['MyReturn_overnight']
    spy_data = spy_data.groupby('Date').mean()

    #plot
    my_data = my_data.cumsum()
    my_data_overnight = my_data_overnight.cumsum()
    my_data_daytrade = my_data_daytrade.cumsum()
    random_data = random_data.cumsum()
    random_data_daytrade = random_data_daytrade.cumsum()
    random_data_overnight = random_data_overnight.cumsum()
    spy_data_overnight = spy_data.cumsum()
    print("my_data")
    print(my_data)
    print("my_data_overnight")
    print(my_data_overnight)
    print("my_data_daytrade")
    print(my_data_daytrade)
    print("random_data")
    print(random_data)
    benchmark_returns_df = benchmark_returns_df.cumsum()
    print(benchmark_returns_df)
    #plot_performance(my_data, benchmark_returns_df, plot_filename, label, f'Benchmark ({benchmark_ticker})')
    plot_performance_with_random(my_data, random_data, random_data_overnight, random_data_daytrade, my_data_overnight, my_data_daytrade, benchmark_returns_df, spy_data_overnight, plot_filename, label, 'Random Returns', 'Overnight', 'Daytrade only', f'Benchmark ({benchmark_ticker})')
    return None



def create_weekly_historical_analysis_total_ta_experiments(filepath, plot_filename, benchmark_ticker, start_date, x_days, label):
    ## get my stocks 
    current_time = datetime.datetime.now()
    pd.set_option("display.max_colwidth", 10000)
    data = pd.read_csv(filepath, encoding='iso-8859-1')
    data = data.drop_duplicates()
    data.to_csv(filepath,index = False)
    ## get benchmark returns
    benchmark_data = get_ticker_history_offset('SPY', '10y', '1d', start = start_date)###change this to remove start and remove _offset
    benchmark_data['PriorClose'] = benchmark_data['Close'].shift(1)
    benchmark_data['MyReturn'] = ((benchmark_data['Close'] - benchmark_data['PriorClose']) / benchmark_data['PriorClose']) * 100
    benchmark_data = benchmark_data[(benchmark_data['PriorClose'].notna())]
    benchmark_returns_df = benchmark_data.groupby('Date').mean()['MyReturn']

    ## get data returns
    data = data[['ticker', 'date_field']].drop_duplicates()
    data = data.sort_values(by=['date_field'], ascending=True)
    spy_data = data.copy()

    ##prepare my data
    my_data = expand_history_to_tgt_only_day1dip(data, x_days, .1)
    my_data['MyReturn'] = ((my_data['Close'] - my_data['PriorClose']) / my_data['PriorClose']) * 100
    my_data = my_data['MyReturn']
    #calculate mean
    my_data = my_data.groupby('Date').mean()
    print("grouped by date")
    print(my_data)

    ##prepare spy data
    spy_data = expand_history_spy(spy_data, x_days)
    spy_data = spy_data[(spy_data['PriorClose'].notna())]
    spy_data = spy_data.groupby('Date').mean()

    #plot
    my_data = my_data.cumsum()
    benchmark_returns_df = benchmark_returns_df.cumsum()
    print(benchmark_returns_df)
    plot_performance(my_data, benchmark_returns_df, plot_filename, label, f'Benchmark ({benchmark_ticker})')
    return None

def create_weekly_historical_analysis_short(filepath, plot_filename, benchmark_ticker, start_date, x_days, label):
    ## get my stocks 
    current_time = datetime.datetime.now()
    pd.set_option("display.max_colwidth", 10000)
    data = pd.read_csv(filepath, encoding='iso-8859-1')
    #data = data[data['date_field'] >= start_date]
    data = data.drop_duplicates()
    data.to_csv(filepath,index = False)
    print(data)
    ## get benchmark returns
#    benchmark_data = get_ticker_history_offset('SPY', '10y', '1d', start = start_date)###change this to remove start and remove _offset
    benchmark_data = get_daily_alpaca_data_as_df_all('SPY', start_date)
    benchmark_data['PriorClose'] = benchmark_data['Close'].shift(1)
    benchmark_data['MyReturn'] = -((benchmark_data['Close'] - benchmark_data['PriorClose']) / benchmark_data['PriorClose']) * 100
    benchmark_data = benchmark_data[(benchmark_data['PriorClose'].notna())]
    benchmark_returns_df = benchmark_data.groupby('Date').mean()['MyReturn']

    ## get data returns
    data = data[['ticker', 'date_field']].drop_duplicates()
    #data = data.groupby('ticker').agg(date_field_min= ('date_field', 'min')) 
    data = data.sort_values(by=['date_field'], ascending=True)
    random_data = data.copy()
    spy_data = data.copy()

    ##prepare my data
    my_data = expand_history(data, x_days)
    my_data = my_data[(my_data['PriorClose'].notna())]
    #calc my returns
    my_data['MyReturn'] = -((my_data['Close'] - my_data['PriorClose']) / my_data['PriorClose']) * 100
    my_data['MyReturn_overnight'] = -((my_data['Open'] - my_data['PriorClose']) / my_data['PriorClose']) * 100
    my_data['MyReturn_daytrade'] = -((my_data['Close'] - my_data['Open']) / my_data['Open']) * 100
    #focus just on my returns
    my_data_overnight = my_data['MyReturn_overnight']
    my_data_daytrade = my_data['MyReturn_daytrade']
    my_data = my_data['MyReturn']

    #calculate mean
    my_data = my_data.groupby('Date').mean()
    print("grouped by date")
    print(my_data)
    my_data_overnight = my_data_overnight.groupby('Date').mean()
    print(my_data_overnight)
    my_data_daytrade = my_data_daytrade.groupby('Date').mean()
    print(my_data_daytrade)

    ##prepare random data
    random_data = expand_history_random(random_data, x_days)
    random_data = random_data[(random_data['PriorClose'].notna())]
    random_data['MyReturn'] = -((random_data['Close'] - random_data['PriorClose']) / random_data['PriorClose']) * 100
    random_data['MyReturn_overnight'] = -((random_data['Open'] - random_data['PriorClose']) / random_data['PriorClose']) * 100
    random_data['MyReturn_daytrade'] = -((random_data['Close'] - random_data['Open']) / random_data['Open']) * 100

    random_data_overnight = random_data['MyReturn_overnight']
    random_data_daytrade = random_data['MyReturn_daytrade']
    random_data = random_data['MyReturn']

    random_data = random_data.groupby('Date').mean()
    random_data_overnight = random_data_overnight.groupby('Date').mean()
    random_data_daytrade = random_data_daytrade.groupby('Date').mean()

    ##prepare spy data
    spy_data = expand_history_spy(spy_data, x_days)
    spy_data = spy_data[(spy_data['PriorClose'].notna())]
    #spy_data['MyReturn'] = ((spy_data['Close'] - spy_data['Open']) / spy_data['Open']) * 100
    spy_data['MyReturn_overnight'] = -((spy_data['Open'] - spy_data['PriorClose']) / spy_data['PriorClose']) * 100
    #spy_data = spy_data['MyReturn']
    spy_data = spy_data['MyReturn_overnight']
    spy_data = spy_data.groupby('Date').mean()

    #plot
    my_data = my_data.cumsum()
    my_data_overnight = my_data_overnight.cumsum()
    my_data_daytrade = my_data_daytrade.cumsum()
    random_data = random_data.cumsum()
    random_data_daytrade = random_data_daytrade.cumsum()
    random_data_overnight = random_data_overnight.cumsum()
    spy_data_overnight = spy_data.cumsum()
    print("my_data")
    print(my_data)
    print("my_data_overnight")
    print(my_data_overnight)
    print("my_data_daytrade")
    print(my_data_daytrade)
    print("random_data")
    print(random_data)
    benchmark_returns_df = benchmark_returns_df.cumsum()
    print(benchmark_returns_df)
    #plot_performance(my_data, benchmark_returns_df, 'top10_technicals_analysis_historical_weekly3.png', 'Stratify Technicals 3', 'Benchmark (SPY)')
#    plot_performance_with_random(my_data, random_data, random_data_overnight, random_data_daytrade, my_data_overnight, my_data_daytrade, benchmark_returns_df, spy_data_overnight, plot_filename, label, 'Random Returns', 'Overnight', 'Daytrade only', f'Benchmark ({benchmark_ticker})')
    plot_performance_with_random(my_data, random_data, random_data_overnight, random_data_daytrade, my_data_overnight, my_data_daytrade, benchmark_returns_df, spy_data_overnight, plot_filename, label, 'Random Returns', 'Overnight', 'Daytrade only', f'Benchmark ({benchmark_ticker})')
    return None


def email_alert_boto3(subject_content, body_content, notifications_to, cc_recipient = "messages@stratifydataconsulting.com"):

    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.s
    SENDER = "Eric <eric@stratifydataconsulting.com>"
    RECIPIENT_CC = cc_recipient
    # Replace recipient@example.com with a "To" address. If your account 
    # is still in the sandbox, this address must be verified.
    RECIPIENT = notifications_to

    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the 
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    #CONFIGURATION_SET = "test"

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "us-west-2"

    # The subject line for the email.
    SUBJECT = subject_content

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = ("Amazon SES Test (Python)\r\n"
                "This email was sent with Amazon SES using the "
                "AWS SDK for Python (Boto)."
                )
                
    # The HTML body of the email.
    BODY_HTML = f"""<html>
    <head></head>
    <body>
    {body_content}
    </body>
    </html>
                """            

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=AWS_REGION)

    # Try to send the email.
    #try:
        #Provide the contents of the email.
    response = client.send_email(
        Destination={
            'ToAddresses': [
                RECIPIENT,
            ],
            'CcAddresses': [
                RECIPIENT_CC,
            ]
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': CHARSET,
                    'Data': BODY_HTML,
                },
                'Text': {
                    'Charset': CHARSET,
                    'Data': BODY_TEXT,
                },
            },
            'Subject': {
                'Charset': CHARSET,
                'Data': SUBJECT,
            },
        },
        Source=SENDER,
        # If you are not using a configuration set, comment or delete the
        # following line
#        ConfigurationSetName=CONFIGURATION_SET,
    )
    # Display an error if something goes wrong.	
    #except ClientError as e:
    #    print(e.response['Error']['Message'])
    #    traceback.print_exc()

    #else:
    #    print("Email sent! Message ID:"),
    #    print(response['MessageId'])
    return None

def higher_volume_list():
    the_list = ['ULTA', 'AA', 'AAL', 'AAPL', 'ASML', 'ADBE', 'ABBV', 'ABEV', 'ABNB', 'ABR', 'ABT', 'ACHR', 'ACN', 'ADI', 'ADM', 'ADMA', 'ADT', 'AEO', 'AES', 'AFRM', 'AG', 'AGL', 'AGNC', 'AIG', 'ALB', 'ALIT', 'ALK', 'AM', 'AMAT', 'AMC', 'AMCR', 'AMD', 'AMH', 'AMZN', 'APA', 'APH', 'APLD', 'APLE', 'APLM', 'APO', 'APP', 'APPS', 'APTV', 'AQN', 'ARCC', 'ARDX', 'ARQT', 'ARRY', 'ASTS', 'ASX', 'AUR', 'AVGO', 'AVTR', 'AXP', 'AZN', 'BA', 'BABA', 'BAC', 'BAX', 'BB', 'BBD', 'BBWI', 'BBY', 'BCS', 'BE', 'BEKE', 'BEN', 'BHP', 'BIDU', 'BILI', 'BITF', 'BK', 'BKR', 'BLUE', 'BMBL', 'BMY', 'BP', 'BRFS', 'BROS', 'BRX', 'BSX', 'BTDR', 'BTE', 'BTG', 'BTI', 'BTU', 'BX', 'BYND', 'BZ', 'C', 'CAG', 'CAN', 'CARR', 'CAT', 'CCCS', 'CCI', 'CCJ', 'CCL', 'CDE', 'CEG', 'CELH', 'CFG', 'CFLT', 'CGC', 'CHGG', 'CHPT', 'CHWY', 'CIFR', 'CL', 'CLF', 'CLOV', 'CLSK', 'CLVT', 'CMCSA', 'CMG', 'CMS', 'CNC', 'CNP', 'CNQ', 'COF', 'COHR', 'COIN', 'COMM', 'COMP', 'COP', 'COTY', 'CPB', 'CPNG', 'CPRT', 'CRBG', 'CRGY', 'CRH', 'CRK', 'CRM', 'CRWD', 'CSCO', 'CSGP', 'CSX', 'CTRA', 'CTSH', 'CTVA', 'CUK', 'CVE', 'CVNA', 'CVS', 'CVX', 'CX', 'CZR', 'D', 'DAL', 'DAR', 'DASH', 'DBX', 'DDOG', 'DELL', 'DG', 'DHI', 'DHR', 'DIS', 'DKNG', 'DLTR', 'DNA', 'DNN', 'DOC', 'DOW', 'DT', 'DUK', 'DVN', 'DXCM', 'EB', 'EBAY', 'EL', 'ELAN', 'EMR', 'ENB', 'ENLC', 'ENPH', 'ENVX', 'EOG', 'EOSE', 'EPD', 'EQNR', 'EQT', 'EQX', 'ERIC', 'ET', 'ETRN', 'EVGO', 'EVH', 'EW', 'EXC', 'EXK', 'F', 'FAST', 'FCEL', 'FCX', 'FE', 'FHN', 'FIGS', 'FIS', 'FITB', 'FLEX', 'FOLD', 'FOXA', 'FSLR', 'FSLY', 'FSM', 'FTNT', 'FTV', 'FUBO', 'GE', 'GEHC', 'GEN', 'GERN', 'GEVO', 'GGB', 'GH', 'GILD', 'GIS', 'GLW', 'GM', 'GME', 'GOEV', 'GOLD', 'GOOG', 'GOOGL', 'GPS', 'GRAB', 'GSAT', 'GSK', 'GT', 'GTES', 'HAL', 'HBAN', 'HBI', 'HBM', 'HCP', 'HD', 'HDB', 'HE', 'HIMS', 'HL', 'HLN', 'HMY', 'HON', 'HOOD', 'HPE', 'HPP', 'HPQ', 'HR', 'HRL', 'HST', 'HTZ', 'HUMA', 'HUT', 'HWM', 'IAG', 'IAUX', 'IBM', 'IBN', 'IBRX', 'ICE', 'INCY', 'INDI', 'INFN', 'INFY', 'INSM', 'INTC', 'INVH', 'IONQ', 'IOT', 'IOVA', 'IP', 'IPG', 'IQ', 'IVZ', 'JBLU', 'JCI', 'JD', 'JNJ', 'JOBY', 'JPM', 'K', 'KDP', 'KEY', 'KGC', 'KHC', 'KIM', 'KKR', 'KMB', 'KMI', 'KO', 'KOS', 'KR', 'KSS', 'KVUE', 'LAC', 'LAZR', 'LCID', 'LEN', 'LESL', 'LI', 'LOW', 'LUMN', 'LUNR', 'LUV', 'LVS', 'LXRX', 'LYFT', 'LYG', 'LZ', 'M', 'MARA', 'MAXN', 'MBLY', 'MCD', 'MCHP', 'MCW', 'MDLZ', 'MDT', 'MET', 'META', 'MGM', 'MLCO', 'MMM', 'MNST', 'MO', 'MODG', 'MOS', 'MPW', 'MQ', 'MRK', 'MRNA', 'MRO', 'MRVI', 'MRVL', 'MS', 'MSTR', 'MTCH', 'MU', 'MUFG', 'NAT', 'NCLH', 'NDAQ', 'NEE', 'NEM', 'NEXT', 'NFE', 'NFLX', 'NGD', 'NI', 'NIO', 'NKE', 'NKLA', 'NLY', 'NOK', 'NOVA', 'NRDY', 'NU', 'NVAX', 'NVDA', 'NVO', 'NWG', 'NWL', 'NWSA', 'NXE', 'NXT', 'NYCB', 'O', 'OBDC', 'OLPX', 'OM', 'ON', 'ONON', 'OPEN', 'ORCL', 'OSCR', 'OTIS', 'OVV', 'OWL', 'OXY', 'PAAS', 'PACB', 'PAGS', 'PANW', 'PARA', 'PATH', 'PAYO', 'PBI', 'PBR', 'PCAR', 'PCG', 'PDD', 'PEG', 'PENN', 'PEP', 'PFE', 'PG', 'PGR', 'PHM', 'PINS', 'PLD', 'PLTR', 'PLUG', 'PM', 'PPL', 'PR', 'PSEC', 'PSNY', 'PSTG', 'PTEN', 'PTON', 'PYPL', 'QCOM', 'QS', 'RBLX', 'RCM', 'RDFN', 'RF', 'RIG', 'RIOT', 'RIVN', 'RKLB', 'ROIV', 'ROKU', 'RPRX', 'RTX', 'RUN', 'RVNC', 'RXRX', 'S', 'SABR', 'SAVA', 'SAVE', 'SBSW', 'SBUX', 'SCHW', 'SE', 'SEDG', 'SG', 'SHEL', 'SHLS', 'SHO', 'SHOP', 'SIRI', 'SLB', 'SLCA', 'SMCI', 'SMR', 'SNAP', 'SNDL', 'SNOW', 'SNY', 'SO', 'SOFI', 'SONO', 'SOUN', 'SPCE', 'SPWR', 'SQ', 'SRE', 'SSRM', 'STEM', 'STLA', 'STM', 'STNE', 'STT', 'SU', 'SWKS', 'SWN', 'SYF', 'SYY', 'T', 'TAL', 'TDOC', 'TELL', 'TEVA', 'TFC', 'TGB', 'TGT', 'TGTX', 'TJX', 'TLRY', 'TME', 'TMUS', 'TOST', 'TPR', 'TRIP', 'TSM', 'TTD', 'TXN', 'U', 'UA', 'UAA', 'UAL', 'UBER', 'UEC', 'UL', 'UMC', 'UPS', 'UPST', 'UPWK', 'URG', 'USB', 'V', 'VFC', 'VICI', 'VIPS', 'VLO', 'VLY', 'VOD', 'VRT', 'VSAT', 'VSCO', 'VST', 'VTR', 'VTRS', 'VZ', 'W', 'WBA', 'WBD', 'WDC', 'WELL', 'WEN', 'WFC', 'WIT', 'WMB', 'WY', 'XEL', 'XP', 'YUMC', 'Z']
    return the_list

def viz_value_list():
    the_list = []
    return the_list


def get_holdings(etf):
    # Specify the URL of the webpage containing the table
    url = f"https://stockanalysis.com/etf/{etf}/holdings/"

    # Send an HTTP request to the webpage and get the HTML content
    response = requests.get(url)
    html_content = response.content

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the table you want to scrape
    table = soup.find('table')  # Find the first table in the HTML
    # Or, if you need to be more specific:
    # table = soup.find('table', {'id': 'my-table'})  # Find table by ID
    # table = soup.find('table', {'class': 'my-table-class'})  # Find table by class

    # Convert the table to a Pandas DataFrame
    df = pd.read_html(str(table))[0]

    # Print the DataFrame
    return df