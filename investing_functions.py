# -*- coding: utf-8 -*-
"""
Minimal investing_functions.py - Contains only functions used by the codebase
Created for stock_screener project
"""
import pandas as pd
import numpy as np
import time
import yfinance as yf
import traceback


# ==================== Functions used by fundamentals_screener_*.py ====================

def get_roe(symbol):
    """
    Calculate Return on Equity (ROE) for a given stock symbol.
    Used by: df_filter_fundamentals()
    """
    try:
        ticker = yf.Ticker(symbol)
        
        # Get financial statements
        income_statement = ticker.income_stmt
        balance_sheet = ticker.balance_sheet
        
        # Extract Net Income and Shareholder's Equity
        net_income = income_statement.loc['Net Income', :].iloc[0]
        shareholders_equity = balance_sheet.loc['Common Stock Equity', :].iloc[0]
        
        # Calculate ROE
        roe = (net_income / shareholders_equity) * 100
        return roe
    except Exception as e:
        print("oops roe:  ", e)
        traceback.print_exc() 
        return 0


def df_filter_fundamentals(df):
    """
    Main function to filter and score stocks based on fundamental metrics.
    Used by: all fundamentals_screener_*.py files
    
    Input: DataFrame with 'Symbol' column
    Output: DataFrame with scored fundamental metrics
    """
    # Initialize all columns with default values
    df['previousClose'] = np.nan
    df['fullTimeEmployees'] = np.nan
    df['website'] = 'blah'
    df['longBusinessSummary'] = 'blah'
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

    # Fetch data for each stock
    for idx, row in df.iterrows():
        try:
            time.sleep(1)  # To avoid hitting API rate limits
            stock_ticker = row['Symbol']
            print(stock_ticker)
            yf_data = yf.Ticker(stock_ticker)
            info = yf_data.info
            
            # Extract all available metrics with error handling
            try:
                df.at[idx, 'longName'] = info['longName']
            except Exception as e:
                print("oops longName:  ", e)
                
            try:
                df.at[idx, 'marketCap'] = info['marketCap']
            except Exception as e:
                print("oops marketCap:  ", e)
                
            try:
                df.at[idx, 'industryKey'] = info['industryKey']
            except Exception as e:
                print("oops industryKey:  ", e)
                
            try:
                df.at[idx, 'sector'] = info['sector']
            except Exception as e:
                print("oops sector:  ", e)
                
            try:
                df.at[idx, 'previousClose'] = info['previousClose']
            except Exception as e:
                print("oops previousClose:  ", e)
                
            try:
                df.at[idx, 'lastDividendValue'] = info['lastDividendValue']
            except Exception as e:
                print("oops lastDividendValue:  ", e)
                
            try:
                df.at[idx, 'currency'] = info['currency']
            except Exception as e:
                print("oops currency:  ", e)
                
            try:
                df.at[idx, 'dividendYield'] = info['dividendYield']
            except Exception as e:
                print("oops dividendYield:  ", e)
                
            try:
                df.at[idx, 'dividendRate'] = info['dividendRate']
            except Exception as e:
                print("oops dividendRate:  ", e)
                
            try:
                df.at[idx, 'industry'] = info['industry']
            except Exception as e:
                print("oops industry:  ", e)

            try:
                df.at[idx, 'roe'] = get_roe(stock_ticker)
            except Exception as e:
                print("oops roe:  ", e)

            try:
                df.at[idx, 'enterpriseValue'] = info['enterpriseValue']
            except Exception as e:
                print("oops enterpriseValue:  ", e)
                
            try:
                df.at[idx, 'floatShares'] = info['floatShares']
            except Exception as e:
                print("oops floatShares:  ", e)
                
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

            # Calculate PS_adj
            try:
                if info['revenueGrowth'] > 0:
                    test = info['priceToSalesTrailing12Months'] * (1-(info['revenueGrowth'])) * (1-info['grossMargins'])
                else:
                    test = info['priceToSalesTrailing12Months'] * (1-(info['revenueGrowth'])) 
                df.at[idx, 'PS_adj'] = test
            except Exception as e:
                print("oops PS_adj:  ", e)

            try:
                df.at[idx, 'enterpriseToRevenue'] = info['enterpriseToRevenue']
            except Exception as e:
                print("oops enterpriseToRevenue:  ", e)

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
                
        except Exception as e:
            print("oops - iteration:  ", e)

    # Calculate derived metric
    df['Growth to High'] = df['fiftyTwoWeekHigh'] - df['previousClose']/df['previousClose']

    # Calculate scoring
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

            if row['pegRatio'] < 1:
                score = score + 2

            df.at[idx, 'score'] = score
        except Exception as e:
            print("oops - score:  ", e)
            
    # Type conversions
    df['priceToSalesTrailing12Months'].astype(float)
    df['revenueGrowth'].astype(float)
    df['grossMargins'].astype(float)
    df['trailingPE'].astype(float)
    df['forwardPE'].astype(float)
    df['PS_adj'].astype(float)
    df['roe'].astype(float)
    df['earningsGrowth'].astype(float)
    df['profitMargins'].astype(float)
    df['shortPercentOfFloat'].astype(float)
    df['dividendYield'].astype(float)
    df['currentRatio'].astype(float)
    df['quickRatio'].astype(float)

    # Formatting and rounding
    df['priceToSalesTrailing12Months'] = df['priceToSalesTrailing12Months'].map(lambda x: round(x, 2) if isinstance(x, float) else 0)
    df['revenueGrowth'] = round(df['revenueGrowth'], 4)*100
    df['grossMargins'] = round(df['grossMargins'], 4)*100
    df['trailingPE'] = df['trailingPE'].map(lambda x: round(x, 2) if isinstance(x, float) else 0)
    df['forwardPE'] = df['forwardPE'].map(lambda x: round(x, 2) if isinstance(x, float) else 0)
    df['PS_adj'] = df['PS_adj'].map(lambda x: round(x, 2) if isinstance(x, float) else 0)
    df['roe'] = round(df['roe'], 2)
    df['earningsGrowth'] = round(df['earningsGrowth'], 4)*100
    df['profitMargins'] = round(df['profitMargins'], 4)*100
    df['shortPercentOfFloat'] = round(df['shortPercentOfFloat'], 4)*100
    df['dividendYield'] = round(df['dividendYield'], 2)
    
    df = df[['Symbol', 'longName', 'sector','industry','industryKey', 'marketCap', 'priceToSalesTrailing12Months', 'currentRatio', 'quickRatio', 'revenueGrowth', 'grossMargins', 'trailingPE', 'forwardPE', 'PS_adj', 'pegRatio', 'dividendYield', 'earningsGrowth', 'profitMargins',  'shortPercentOfFloat', 'roe', 'score']]
    return df
