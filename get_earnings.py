from datetime import datetime, timedelta
import os
import pickle
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent
DATA_DIR = REPO_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_secrets():
    api_key = os.getenv("FINANCIALMODELINGPREP_API_KEY")
    if api_key:
        return {"FINANCIALMODELINGPREP_API_KEY": api_key}

    fallback_pickle = os.getenv(
        "STOCK_SCREENER_SECRETS_PICKLE",
        str(REPO_ROOT / "secret_stock_analysis_app.pickle"),
    )
    if os.path.exists(fallback_pickle):
        with open(fallback_pickle, "rb") as handle:
            return pickle.load(handle)

    return {}


def get_recent_earnings(days_back: int = 14) -> pd.DataFrame:
    """Fetches stock earnings results from the updated FMP stable API."""

    secrets = get_secrets()
    api_key = secrets.get("FINANCIALMODELINGPREP_API_KEY")
    if not api_key:
        print("No FMP API key found; writing an empty earnings file for this run.")
        return pd.DataFrame()

    end_date_str = datetime.today().strftime("%Y-%m-%d")
    start_date_str = (datetime.today() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    url = "https://financialmodelingprep.com/stable/earnings-calendar"
    params = {
        "from": start_date_str,
        "to": end_date_str,
        "apikey": api_key,
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        print(url)
        print(params)

        data = response.json()
        if not data:
            print(f"No earnings data found between {start_date_str} and {end_date_str}.")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        columns_to_keep = [
            "date",
            "symbol",
            "epsActual",
            "epsEstimated",
            "revenueActual",
            "revenueEstimated",
        ]
        available_cols = [col for col in columns_to_keep if col in df.columns]

        df_cleaned = df[available_cols].copy()
        df_cleaned = df_cleaned.sort_values(by="date", ascending=False)
        return df_cleaned

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while connecting to FMP: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    earnings_df = get_recent_earnings(days_back=14)

    if not earnings_df.empty:
        print(f"\n--- Successfully Retrieved {len(earnings_df)} Earnings Reports ---")
        print(earnings_df.head(15).to_string(index=False))

    output_filepath = DATA_DIR / "recent_earnings.csv"
    earnings_df.to_csv(output_filepath, index=False)
    print(f"✓ Saved {output_filepath}")
