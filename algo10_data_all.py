import pandas as pd
#from investing_functions import spotgamma_hiro_tickers, higher_volume_list, get_citrini_us_raw, get_citrini_us_tickers, get_company_name, get_summary,get_my_ticker_list , get_my_basket_viz_val1, get_my_basket_viz_val2, get_my_basket_large_cap, get_my_viz_value_ticker_list
import datetime
import os
import urllib.parse

###get my stocks caps
current_time = datetime.datetime.now()
pd.set_option("display.max_colwidth", 10000)
dir_path = os.path.dirname(os.path.realpath(__file__))
filepath = os.path.join(dir_path, 'data', 'all_caps_fundamentals.csv')
data = pd.read_csv(filepath, encoding='iso-8859-1')
print(data.shape)


# print(get_my_ticker_list())
# print(get_my_basket_viz_val1())
# print(get_my_basket_viz_val2())
# print(get_my_basket_large_cap())
# print(get_my_viz_value_ticker_list())
#my_ticker_list = get_my_ticker_list() + get_my_basket_viz_val1() + get_my_basket_viz_val2() + get_my_basket_large_cap() + get_my_viz_value_ticker_list()

#my_ticker_list = my_ticker_list + higher_volume_list() + spotgamma_hiro_tickers()

#print(my_ticker_list)
#print(len(my_ticker_list))


#df = data[data['Symbol'].isin(my_ticker_list)]
#print(df.shape)

columns = ['Symbol','longName', 'industryKey','marketCap','priceToSalesTrailing12Months','currentRatio','quickRatio','revenueGrowth','grossMargins','trailingPE','forwardPE','PS_adj','pegRatio','dividendYield','earningsGrowth','profitMargins','shortPercentOfFloat']
df = data[columns]
#data = data.sort_values('Total_TA', ascending=False)
#data.reset_index(drop=True, inplace=True)

print(df.shape)

# Load SP500 data
sp500_filepath = os.path.join(dir_path, 'data', 'sp500.csv')
sp500_df = pd.read_csv(sp500_filepath)
sp500_tickers = set(sp500_df['Ticker'].str.strip('"'))

# Add SP500 column
df['SP500'] = df['Symbol'].apply(lambda x: 'Yes' if x in sp500_tickers else 'No')

def margin_exp(PS_adj, PS=None, revenueGrowth=None):
    if pd.isna(PS_adj) or pd.isna(PS) or pd.isna(revenueGrowth):
        return ''
    if PS_adj < 0.5 and PS_adj != 0.0 and (PS_adj <= PS) and (revenueGrowth > 0):
        return '🚀🚀🚀'
    elif PS_adj < 1 and PS_adj != 0.0 and (PS_adj <= PS) and (revenueGrowth > 0):
        return '🚀🚀'
    elif PS_adj < 1.5 and PS_adj != 0.0 and (PS_adj <= PS) and (revenueGrowth > 0):
        return '🚀'
    else:
        return ''

def earnings(trailingPE, forwardPE):
    pes = [pe for pe in [trailingPE, forwardPE] if not pd.isna(pe)]
    if not pes:
        return ''
    pe = min(pes)
    if pe > 0 and pe < 20:
        return '💵💵💵'
    if pe > 0 and pe < 50:
        return '💵💵'
    if pe > 0 and pe < 99:
        return '💵'
    return ''

for idx, row in df.iterrows():
    print(row['Symbol'])
    df.at[idx, 'margin exp.'] = margin_exp(row['PS_adj'], row['priceToSalesTrailing12Months'], row['revenueGrowth'])
    print(row['Symbol'])
    df.at[idx, 'earnings'] = earnings(row['trailingPE'], row['forwardPE'])



df['company'] = df['longName']
#df['summary'] = df['Symbol'].apply(lambda x: get_summary(x))

df['ask_grok'] = df.apply(
    lambda row: "https://www.google.com/search?q=" + urllib.parse.quote(
        f"For ${row['Symbol']} ({row['longName']}) I want it to format the output with 6 basic checks. "
        f"1) Verify PS_adj ({row['PS_adj']}) is correct by checking Revenue Growth ({row['revenueGrowth']}%), "
        f"Gross Margin % ({row['grossMargins']}%), and Price to Sales ({row['priceToSalesTrailing12Months']}). "
        f"Note that PS_adj = PS * (1 - GM%) * (1 - YoYRev%growth). "
        f"2) Check sequential Quarter over Quarter growth to see if there is any slippage occurring in the near term. "
        f"3) Check the Rule of 40: Revenue Growth + Operating Margin should be above 40. "
        f"4) Check P/FCF (Price to Free Cash Flow) and compare to others in its peer group in the {row['industryKey']} industry. "
        f"5) Check Insider Sales or Purchases: are insiders buying or selling? "
        f"6) Check EV/Sales ratio and compare to Price to Sales ratio ({row['priceToSalesTrailing12Months']}) to see if massively different, which could indicate high debt."
    ),
    axis=1
)
df['stock_analysis_link'] = df.apply(
    lambda row: f"https://stockanalysis.com/stocks/{row['Symbol']}/revenue",
    axis=1
)
df['rating'] = df['margin exp.'] + df['earnings']
df['rating_sortable'] = df['rating'].apply(lambda x: len(str(x)))
df['view_x'] = df['Symbol'].apply(lambda x: f"https://x.com/search?q=%24{x}&src=typed_query&f=top")
df['share_x'] = df.apply(
    lambda row: "https://x.com/intent/post?text=" +
    urllib.parse.quote(
        f"Check out ${row['Symbol']} {row['company']} (Rating: {row['rating']}) @ https://algo10.com/"
    ),
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

print (df['rating'])
df = df.drop_duplicates(subset=['Symbol'])
# Combine all columns from the original 'columns' list and the newly created columns
output_columns = columns + ['PS_ratio','company', 'SP500', 'view_x', 'share_x', 'margin exp.', 'earnings', 'rating', 'rating_sortable', 'ask_grok', 'stock_analysis_link']

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


file_name = "algo10_data_all.csv"
dir_path = os.path.dirname(os.path.realpath(__file__))
filepath = os.path.join(dir_path, 'data', file_name)
df[output_columns].to_csv(filepath, index=False)
