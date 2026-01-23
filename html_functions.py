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
from finta import TA as ta
import plotly.graph_objects as go
import matplotlib.pyplot as plt 
import mplfinance as mpf 
import requests
from datetime import timedelta
import pickle
import boto3


def generate_card_html(row):
    #print ({row['CompanyName']})
    #CompanyName = "Unknown"

    try:
        proxy_exp_date = row['exp_date']
    except:
        proxy_exp_date = 0

    try:
        proxy_options_value = row['options_value']
    except:
        proxy_options_value = 0

    try:
        proxy_total_30min = row['Total_30min']
    except:
        proxy_total_30min = 0

    try:
        proxy_total_4h = row['Total_4h']
    except:
        proxy_total_4h = 0

    try:
        CompanyName = row['CompanyName']
    except:
        CompanyName = "Unknown"
    try:
        currentRatio = row['currentRatio']
    except:
        currentRatio = "Unknown"
    try:
        quickRatio = row['quickRatio']
    except:
        quickRatio = "Unknown"
    
    html_card = f"""
    <div class="card", style = "display: block">
        <center>
        <span class="tooltip" style="font-weight:bold;align:center;">{row['ticker']} 
            <span class="tooltiptext">{row['longBusinessSummary']}</span>
        </span>
        <br>
        <a href='https://www.google.com/search?q={CompanyName}' target="_blank">{CompanyName}</a>
        </center>
        <hr>
        <center>
        <!--
        <span style="font-weight:bold;">TA 1: </span>
        <span style="font-weight:normal;">{row['Total']}</span>
        <span style="font-weight:bold;">Overfit 10 day (TA 2b): </span>
        <span style="font-weight:normal;">{row['Total_overfit']}</span>
        <span style="font-weight:bold;">Overfit 5 day (TA 2): </span>
        <span style="font-weight:normal;">{row['Total_overfit']}</span>
        <br>
        <span style="font-weight:bold;">K Means 10 day (TA 3): </span>
        <span style="font-weight:normal;">{row['Total_kmeans']}</span>
        <span style="font-weight:bold;">K Means 5 day (TA 4): </span>
        <span style="font-weight:normal;">{row['Total_kmeans_st']}</span>
        -->
        <span style="font-weight:bold;">Technical Score: </span>
        <span style="font-weight:normal;">{row['Total_TA']}</span>
        <br>
        <a href='./{row['ticker']}_plot.png'>
        <img src='./{row['ticker']}_plot.png' width="600" height="330" title = "Daily candles, 50d-ema, 200d-ema, and fibonacci lines"></a>
        </center>
        <br>
        <br>
        <hr>
        <center>
        <span class="tooltip" style="font-weight:bold;align:center;">Fundamentals: 
            <span class="tooltiptext">This is a dynamic score between 0 and 20 using a proprietary blend of PE, PS, Revenue Growth, Gross Margin % and Earnings Growth potential. The intent is to considers both growth and value in the fundamentals. </span>
        </span> 
            <span style="font-weight:normal;">{row['score']}
            </span>       
        </center>
        <br>
        <center>
        <span><span style="font-weight:bold;">PE (TTM): </span>   <span style="font-weight:normal;">{round(row['trailingPE'], 2)}</span>
        <a> | </a>
        <span><span style="font-weight:bold;">PE (Fwd): </span>   <span style="font-weight:normal;">{round(row['forwardPE'], 2)}</span>
        <a> | </a>
        <!--<span><span style="font-weight:bold;">PEG: </span>   <span style="font-weight:normal;">{round(row['pegRatio'],2)}</span>
        <a> | </a>-->
        <span><span style="font-weight:bold;">Div: </span>   <span style="font-weight:normal;">{round(row['dividendYield'], 2)}%</span>
        <br>
        <span><span style="font-weight:bold;">Earnings Growth: </span>   <span style="font-weight:normal;">{round(row['earningsGrowth'], 2)}%</span>
        <a> | </a>
        <span><span style="font-weight:bold;">Revenue Growth: </span>   <span style="font-weight:normal;">{round(row['revenueGrowth'], 2)}%</span>
        <a> | </a>
        <br>
        <span><span style="font-weight:bold;">PS: </span>   <span style="font-weight:normal;">{round(row['priceToSalesTrailing12Months'], 2)}</span>
        <a> | </a>
        <span><span style="font-weight:bold;">Gross Margin: </span>   <span style="font-weight:normal;">{round(row['grossMargins'], 0)}%</span>
        <a> | </a>
        <span class="tooltip" style="font-weight:bold;">PS(adj):    
            <span class="tooltiptext"> PS(adj) is Price to Sales adjusted to account multiplying affect on earnings if there is continued growth based on top line and gross margin.</span>
        </span>
        <span style="font-weight:normal;">{round(row['PS_adj'], 2)}</span>
        <br>
        <span><span style="font-weight:bold;">Current Ratio: </span>   <span style="font-weight:normal;">{round(currentRatio, 2)}</span>
        <a> | </a>
        <span><span style="font-weight:bold;">Quick Ratio: </span>   <span style="font-weight:normal;">{round(quickRatio, 2)}</span>
        <br>
        </center>
        <hr>
        <center>
        <div class="grid">
            <button onclick="window.open('https://www.macrotrends.net/stocks/charts/{row['ticker']}/{CompanyName}/revenue');" style = "font-weight: normal;font-size : 12px;height:40px; width:170px;">Research</button>
            <button onclick="window.open('https://news.google.com/search?q={row['ticker']}%20{CompanyName}');" style = "font-weight: normal;font-size : 12px;height:40px; width:170px;">News</button>
            <button onclick="window.open('https://twitter.com/search?q=%24{row['ticker']}');" style = "font-weight: normal;font-size : 12px;height:40px; width:170px;">Twitter</button>
            <button onclick="window.open('https://www.google.com/search?q={row['ticker']}+stock');" style = "font-weight: normal;font-size : 12px;height:40px; width:170px;">Chart</button>
            <button onclick="window.open('https://finance.yahoo.com/chart/{row['ticker']}/');" style = "font-weight: normal;font-size : 12px;height:40px; width:170px;">Interactive</button>
            <button onclick="window.open('https://finance.yahoo.com/quote/{row['ticker']}/options/');" style = "font-weight: normal;font-size : 12px;height:40px; width:170px;">Options Chain</button>
        </div>
        </center> 
    </div>
"""
    return html_card


def get_html_end():

    html_end = """
                                    <div>
                                    <center>
                                    <p style="margin:0"><span>© 2024 Stratify Data Consulting LLC DBA Algo10</span></p>
                                    <br>
                                    <p>All Stratify Data Consulting LLC DBA Algo10 materials, information, and presentations are for educational purposes only and is not specific investment advice nor recommendations. Day trading, algorithmic trading, and options trading is risky and should not be conducted based on this material alone.  Past performance is not necessarily indicative of future results. 
                                    </p>
                                    <br>
                                    <p><a href="./disclosures.html">Full Disclosure</a></a></p>
                                    <br>
                                    </center>
                                    </div>
    
    </body>
    </html>
    """
    return html_end

def get_html_header():
    html_headers = """
    <html>
    <head>
    <title>Stratify Data Consulting</title>
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    </head>

    <style>

    .body {
        background-color:#7bceeb;
        margin-left: 100px;
        margin-right: 100px;  
        box-sizing: border-box;
    }

    .myDiv {
    padding-top: 2px;
    padding-right: 2px;
    padding-bottom: 20px;
    padding-left: 20px;
    margin-bottom: 16px;
    margin-bottom: 16px;
    background-color: rgba(225, 251, 212, 0.8);
    text-align: center;
    justify-content: center;
    width: 100%;
    }

    .section {
    display: grid;
    grid-template-columns: var(--page-margin) [center-start] 1fr [center-end] var(--page-margin);
    
    & > * {
        grid-column: center;
    }
    }

    .cards-wrapper {
    grid-column: center-start / -1;
    display: grid;
    grid-auto-flow: column;
    gap: 1rem;
    overflow: auto;
    padding-bottom: 1rem;
    padding-right: var(--page-margin);
        }
    .card {
        box-shadow: rgba(0, 0, 0, 0.05) 0px 0px 0px 1px, rgb(209, 213, 219) 0px 0px 0px 1px inset;    transition: 0.3s;
        min-width: 60 rem;
        background: transparent;
        border-style: solid;
        border-width: 2px 2px 2px 2px;
        border-color: black;
        border-radius: 0.2rem;
    }
    <!-- HTML !-->
    <button class="button-19" role="button">Button 19</button>

    /* CSS */
    .button-19 {
    appearance: button;
    background-color: #1899D6;
    border: solid transparent;
    border-radius: 16px;
    border-width: 0 0 4px;
    box-sizing: border-box;
    color: #FFFFFF;
    cursor: pointer;
    display: inline-block;
    font-family: din-round,sans-serif;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: .8px;
    line-height: 20px;
    margin: 0;
    outline: none;
    overflow: visible;
    padding: 13px 16px;
    text-align: center;
    text-transform: uppercase;
    touch-action: manipulation;
    transform: translateZ(0);
    transition: filter .2s;
    user-select: none;
    -webkit-user-select: none;
    vertical-align: middle;
    white-space: nowrap;
    width: 100%;
    }

    .button-19:after {
    background-clip: padding-box;
    background-color: #355E3B;
    border: solid transparent;
    border-radius: 16px;
    border-width: 0 0 4px;
    bottom: 1px;
    content: "";
    left: 1;
    position: absolute;
    right: 1;
    top: 1;
    z-index: -1;
    }

    .button-19:main,
    .button-19:focus {
    user-select: auto;
    }

    .button-19:hover:not(:disabled) {
    filter: brightness(1.1);
    -webkit-filter: brightness(1.1);
    }

    .button-19:disabled {
    cursor: auto;
    }

    .h2 {
        -webkit-text-size-adjust: 100%;
    -webkit-tap-highlight-color: rgba(0,0,0,0);
    -webkit-font-smoothing: antialiased;
    direction: ltr;
    text-align: center;
    box-sizing: inherit;
    text-transform: none;
    width: 100%;
    position: relative;
    margin-left: auto;
    margin-right: auto;
    max-width: 100%;
    display: inline-block;
    font-family: 'Playfair Display', Georgia, serif;
    overflow-wrap: break-word;
    margin-top: 0;
    line-height: 1.2;
    letter-spacing: 0.023em;
    margin-bottom: 16px;
    white-space: pre-line;
    color: rgb(21, 21, 21);
    font-weight: 400;
    font-size: 44px;

    .p {
        -webkit-text-size-adjust: 100%;
    -webkit-tap-highlight-color: rgba(0,0,0,0);
    -webkit-font-smoothing: antialiased;
    direction: ltr;
    text-align: center;
    overflow-wrap: break-word;
    font-weight: 400;
    line-height: 1.5;
    color: rgb(87, 87, 87);
    box-sizing: inherit;
    font-family: 'Open Sans', arial, sans-serif;
    letter-spacing: unset;
    text-transform: unset;
    font-size: 16px;
    }
    }

    
    .tooltip {
    position: relative;
    display: inline-block;
    border-bottom: 1px dotted black;
    }

    .tooltip .tooltiptext {
    visibility: hidden;
    width: 240px;
    background-color: gray;
    color: #fff;
    text-align: center;
    border-radius: 6px;
    padding: 5px 0;

    /* Position the tooltip */
    position: absolute;
    z-index: 1;
    }

    .tooltip:hover .tooltiptext {
    visibility: visible;
    }

        .overlay {
    position: absolute; 
    bottom: 0; 
    background: rgb(0, 0, 0);
    background: rgba(0, 0, 0, 0.5); /* Black see-through */
    color: #f1f1f1; 
    width: 100%;
    transition: .5s ease;
    opacity:0;
    color: white;
    font-size: 20px;
    padding: 20px;
    text-align: center;
    }

    }
    </style>
    <body>
    <center>
    <a href='https://stratifydataconsulting.com/' ><img src='/logo16.png'  width="100" height="100" align="center"></a>
    </center>
    <br>




    """
    return html_headers

def get_html_header_algoten():
    html_headers = """
    <html>
    <head>
    <title>AlgoTen</title>
    <link rel="icon" type="image/x-icon" href="/favicon2.ico">
    </head>

    <style>

    .body {
        background-color:#7bceeb;
        margin-left: 100px;
        margin-right: 100px;  
        box-sizing: border-box;
    }

    .myDiv {
    padding-top: 2px;
    padding-right: 2px;
    padding-bottom: 20px;
    padding-left: 20px;
    margin-bottom: 16px;
    margin-bottom: 16px;
    background-color: rgba(225, 251, 212, 0.8);
    text-align: center;
    justify-content: center;
    width: 100%;
    }

    .section {
    display: grid;
    grid-template-columns: var(--page-margin) [center-start] 1fr [center-end] var(--page-margin);
    
    & > * {
        grid-column: center;
    }
    }

    .cards-wrapper {
    grid-column: center-start / -1;
    display: grid;
    grid-auto-flow: column;
    gap: 1rem;
    overflow: auto;
    padding-bottom: 1rem;
    padding-right: var(--page-margin);
        }
    .card {
        box-shadow: rgba(0, 0, 0, 0.05) 0px 0px 0px 1px, rgb(209, 213, 219) 0px 0px 0px 1px inset;    transition: 0.3s;
        min-width: 60 rem;
        background: transparent;
        border-style: solid;
        border-width: 2px 2px 2px 2px;
        border-color: black;
        border-radius: 0.2rem;
    }
    <!-- HTML !-->
    <button class="button-19" role="button">Button 19</button>

    /* CSS */
    .button-19 {
    appearance: button;
    background-color: #1899D6;
    border: solid transparent;
    border-radius: 16px;
    border-width: 0 0 4px;
    box-sizing: border-box;
    color: #FFFFFF;
    cursor: pointer;
    display: inline-block;
    font-family: din-round,sans-serif;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: .8px;
    line-height: 20px;
    margin: 0;
    outline: none;
    overflow: visible;
    padding: 13px 16px;
    text-align: center;
    text-transform: uppercase;
    touch-action: manipulation;
    transform: translateZ(0);
    transition: filter .2s;
    user-select: none;
    -webkit-user-select: none;
    vertical-align: middle;
    white-space: nowrap;
    width: 100%;
    }

    .button-19:after {
    background-clip: padding-box;
    background-color: #355E3B;
    border: solid transparent;
    border-radius: 16px;
    border-width: 0 0 4px;
    bottom: 1px;
    content: "";
    left: 1;
    position: absolute;
    right: 1;
    top: 1;
    z-index: -1;
    }

    .button-19:main,
    .button-19:focus {
    user-select: auto;
    }

    .button-19:hover:not(:disabled) {
    filter: brightness(1.1);
    -webkit-filter: brightness(1.1);
    }

    .button-19:disabled {
    cursor: auto;
    }

    .h2 {
        -webkit-text-size-adjust: 100%;
    -webkit-tap-highlight-color: rgba(0,0,0,0);
    -webkit-font-smoothing: antialiased;
    direction: ltr;
    text-align: center;
    box-sizing: inherit;
    text-transform: none;
    width: 100%;
    position: relative;
    margin-left: auto;
    margin-right: auto;
    max-width: 100%;
    display: inline-block;
    font-family: 'Playfair Display', Georgia, serif;
    overflow-wrap: break-word;
    margin-top: 0;
    line-height: 1.2;
    letter-spacing: 0.023em;
    margin-bottom: 16px;
    white-space: pre-line;
    color: rgb(21, 21, 21);
    font-weight: 400;
    font-size: 44px;

    .p {
        -webkit-text-size-adjust: 100%;
    -webkit-tap-highlight-color: rgba(0,0,0,0);
    -webkit-font-smoothing: antialiased;
    direction: ltr;
    text-align: center;
    overflow-wrap: break-word;
    font-weight: 400;
    line-height: 1.5;
    color: rgb(87, 87, 87);
    box-sizing: inherit;
    font-family: 'Open Sans', arial, sans-serif;
    letter-spacing: unset;
    text-transform: unset;
    font-size: 16px;
    }
    }

    
    .tooltip {
    position: relative;
    display: inline-block;
    border-bottom: 1px dotted black;
    }

    .tooltip .tooltiptext {
    visibility: hidden;
    width: 240px;
    background-color: gray;
    color: #fff;
    text-align: center;
    border-radius: 6px;
    padding: 5px 0;

    /* Position the tooltip */
    position: absolute;
    z-index: 1;
    }

    .tooltip:hover .tooltiptext {
    visibility: visible;
    }

        .overlay {
    position: absolute; 
    bottom: 0; 
    background: rgb(0, 0, 0);
    background: rgba(0, 0, 0, 0.5); /* Black see-through */
    color: #f1f1f1; 
    width: 100%;
    transition: .5s ease;
    opacity:0;
    color: white;
    font-size: 20px;
    padding: 20px;
    text-align: center;
    }

    }
    </style>
    <body>
    <center>
    <a href='./welcome.html' ><img src='/algoten_logo.png'  width="100" height="100" align="center"></a>
    </center>
    <br>




    """
    return html_headers

#def make_card_as_full_page():
#    card = generate_card_html(row)
#    get_html_end()