from datetime import datetime, timedelta
import os
import requests
import pandas as pd
import pickle

def get_secrets():
    with open('C:/git/secret_stock_analysis_app.pickle', 'rb') as handle:
        response = pickle.load(handle)
    # print(response['SPOTGAMMA_USERNAME'])
    # print(response['SPOTGAMMA_PWD'])
    # print(response['ALPACA_PAPER_GMAIL_KEY'])
    # print(response['ALPACA_PAPER_GMAIL_SECRET_KEY'])
    return response


def get_recent_earnings(days_back: int = 14) -> pd.DataFrame:
    """Fetches stock earnings results from the updated FMP stable API."""
    
    # 1. Dynamically calculate the historical date range (last 1-2 weeks)
    end_date_str = datetime.today().strftime('%Y-%m-%d')
    start_date_str = (datetime.today() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    # 2. Construct the CORRECT stable URL path as per documentation
    url = "https://financialmodelingprep.com/stable/earnings-calendar"
    
    # 3. Supply parameters including the target date windows
    params = {
        "from": start_date_str,
        "to": end_date_str,
        "apikey": get_secrets()['FINANCIALMODELINGPREP_API_KEY']
    }
    
    try:
        # 4. Execute the API request
        response = requests.get(url, params=params)
        response.raise_for_status() 
        
        data = response.json()
        if not data:
            print(f"No earnings data found between {start_date_str} and {end_date_str}.")
            return pd.DataFrame()
            
        # 5. Load into a Pandas DataFrame
        df = pd.DataFrame(data)
        
        # 6. Filter for historical results that actually have reported metrics
        if 'eps' in df.columns:
            df = df[df['eps'].notna()]
            
        # 7. Reorganize columns for clear data mapping
        columns_to_keep = ['date', 'symbol', 'epsActual', 'epsEstimated', 'revenueActual', 'revenueEstimated']
        available_cols = [col for col in columns_to_keep if col in df.columns]
        
        df_cleaned = df[available_cols].copy()
        df_cleaned = df_cleaned.sort_values(by='date', ascending=False)
        
        return df_cleaned

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while connecting to FMP: {e}")
        return pd.DataFrame()

# --- Execution Example ---
if __name__ == "__main__":
    # Fetch earnings from the last 14 days
    earnings_df = get_recent_earnings(days_back=14)
    
    if not earnings_df.empty:
        print(f"\n--- Successfully Retrieved {len(earnings_df)} Earnings Reports ---")
        print(earnings_df.head(15).to_string(index=False))

        dir_path = os.path.dirname(os.path.realpath(__file__))
        output_filepath = os.path.join(dir_path, 'data', "recent_earnings.csv")
        earnings_df.to_csv(output_filepath, index=False)
