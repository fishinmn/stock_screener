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
    lambda row: f"https://www.google.com/search?q=For%20${row['Symbol']}%20({row['longName']})%20I%20want%20it%20to%20format%20the%20output%20with%208%20basic%20checks.%201)%20Green%20check%20mark%20if%20PS_adj%20({row['PS_adj']})%20is%20valid%202)%20verify%20EV/Sales%20does%20show%20issue%203)%20Verify%20good%20time%20to%20buy%20based%20on%20the%20RSI%20technical%20indicator%20only.%204)%20consistent%20revenue%20growth%20QoQ%20and%20YoY%205)%20Analyze%20Gross%20Margin%20Stability.%20Compare%20Revenue%20growth%20vs.%20Gross%20Margin%20percentage%20over%20the%20last%204%20quarters.%20Specifically%2C%20check%20if%20Gross%20Margin%20is%20declining%20while%20Revenue%20is%20increasing%20(a%20sign%20of%20buying%20revenue%20via%20price%20cuts).%20Also%2C%20verify%20if%20Adjusted%20EBITDA%20is%20growing%20in%20line%20with%20Revenue%20to%20ensure%20operational%20efficiency.%206)%20Interest%20Coverage%3A%20Calculate%20EBIT%20/%20Interest%20Expense.%20Give%20a%20Pass%20if%20the%20ratio%20is%20above%203.0x%2C%20ensuring%20debt%20is%20manageable.%207)%20Insider%20Alignment%3A%20Verify%20the%20percentage%20of%20Insider%20Ownership.%20Give%20a%20Pass%20if%20it%20is%20above%205%25.%208)%20Recent%20Insider%20Buys%20or%20Sales%3A%20Track%20recent%20insider%20transactions%20over%20the%20last%203%20months.%20Bullish%20signal%20if%20insiders%20are%20buying%2C%20bearish%20if%20insiders%20are%20selling.%20Then%20show%20the%20revenue%20YoY%20and%20the%20PS%20ratio%20and%20GM%20percentage%20then%20multiply%20PS%20x%201%20minus%20RevYoYPct%20x%201%20minus%20GM_percent%20and%20call%20it%20PS_adj.%20Also%20calculate%20and%20compare%20Price%20to%20Sales%20ratio%20to%20EV%20to%20sales%20ratio%20and%20show%20red%20flag%20if%20too%20much%20debt.%20Also%20check%20technical%20levels%20using%20RSI%20and%20if%20price%20is%20down%20for%20good%20buying%20opportunity.%20Also%20verify%20revenue%20growth%20is%20solid%20trend%20over%20past%20quarters%20and%20years.",
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
output_columns = columns + ['PS_ratio','company', 'view_x', 'share_x', 'margin exp.', 'earnings', 'rating', 'rating_sortable', 'ask_grok', 'stock_analysis_link']

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
