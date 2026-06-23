import pandas as pd
#from investing_functions import spotgamma_hiro_tickers, higher_volume_list, get_citrini_us_raw, get_citrini_us_tickers, get_company_name, get_summary,get_my_ticker_list , get_my_basket_viz_val1, get_my_basket_viz_val2, get_my_basket_large_cap, get_my_viz_value_ticker_list
import datetime
import os
import urllib.parse

###get my stocks caps
current_time = datetime.datetime.now()
pd.set_option("display.max_colwidth", 10000)
dir_path = os.path.dirname(os.path.realpath(__file__))
filepath = os.path.join(dir_path, 'data', 'fundamentals_screener_recent_earnings.csv')
data = pd.read_csv(filepath, encoding='iso-8859-1')
print(data.shape)


df = data
df['company'] = df['longName']
#df['summary'] = df['Symbol'].apply(lambda x: get_summary(x))

df['ask_grok'] = df.apply(
    lambda row: "https://www.google.com/search?q=" + urllib.parse.quote(
        f"For ${row['Symbol']} ({row['longName']}) I want to verify the most recent earnings which just happened "
        f"1) Verify PS_adj ({row['PS_adj']}) is correct by checking Revenue Growth ({row['revenueGrowth']}%), "
        f"Gross Margin % ({row['grossMargins']}%), and Price to Sales ({row['priceToSalesTrailing12Months']}). "
        f"Note that PS_adj = PS * (1 - GM%) * (1 - YoYRev%growth). "
        f"2) Check if their PS_adj is better pre earnings or post earnings. "
        ),
    axis=1
)
df['stock_analysis_link'] = df.apply(
    lambda row: f"https://stockanalysis.com/stocks/{row['Symbol']}/revenue",
    axis=1
)


try:
    df['HoodChart'] = df['Symbol'].map(lambda x: f'<a href="https://robinhood.com/us/en/stocks/{x}/">Chart</a>')
except Exception as error:
    print("An exception occurred with hood chart:", error)

# try:
#     df['YahooChart'] = df['Symbol'].map(lambda x: f'<a href="https://finance.yahoo.com/chart/{x}/">Chart</a>')
# except Exception as error:
#     print("An exception occurred with ycharts:", error)

df = df.drop_duplicates(subset=['Symbol'])
# Combine all columns from the original 'columns' list and the newly created columns
output_columns = list(df.columns) + ['PS_ratio','company', 'ask_grok', 'stock_analysis_link']

#remove rows where "company" == asdfsdfsdfsdf   
df = df[df['company'] != 'asdfsdfsdfsdf']

df['PS_ratio'] = df['priceToSalesTrailing12Months'] / df['PS_adj']

# List of columns to round
round_cols = [
    'revenueGrowth', 'grossMargins', 'trailingPE', 'forwardPE',
    'PS_adj', 'priceToSalesTrailing12Months', 'PS_ratio', 'dividendYield', 'earningsGrowth'
]

# Round specified columns to 2 decimal places if they exist in the DataFrame
for col in round_cols:
    if col in df.columns:
        df[col] = df[col].round(2)


file_name = "recent_earnings_data.csv"
dir_path = os.path.dirname(os.path.realpath(__file__))
filepath = os.path.join(dir_path, 'data', file_name)
df[output_columns].to_csv(filepath, index=False)
