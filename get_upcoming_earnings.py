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


def get_upcoming_earnings(days_ahead: int = 5) -> pd.DataFrame:
    """Fetch upcoming earnings for the next 5 business days from FMP."""
    secrets = get_secrets()
    api_key = secrets.get("FINANCIALMODELINGPREP_API_KEY")
    if not api_key:
        print("No FMP API key found; writing an empty upcoming earnings file for this run.")
        return pd.DataFrame()

    today = datetime.today()
    end_date = today + timedelta(days=days_ahead * 2)
    start_date = today

    url = "https://financialmodelingprep.com/stable/earnings-calendar"
    params = {
        "from": start_date.strftime("%Y-%m-%d"),
        "to": end_date.strftime("%Y-%m-%d"),
        "apikey": api_key,
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        if not data:
            print("No upcoming earnings data found.")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        columns_to_keep = [
            "date",
            "symbol",
            "epsEstimated",
            "revenueEstimated",
            "epsActual",
            "revenueActual",
            "hour",
            "exchange",
            "fiscalDateEnding",
            "updatedFromDate",
        ]
        available_cols = [col for col in columns_to_keep if col in df.columns]
        df_cleaned = df[available_cols].copy()
        df_cleaned = df_cleaned.sort_values(by="date", ascending=True)
        return df_cleaned
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while connecting to FMP: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    earnings_df = get_upcoming_earnings(days_ahead=5)

    if not earnings_df.empty:
        print(f"\n--- Successfully Retrieved {len(earnings_df)} Upcoming Earnings Reports ---")
        print(earnings_df.head(15).to_string(index=False))

    output_filepath = DATA_DIR / "upcoming_earnings.csv"
    earnings_df.to_csv(output_filepath, index=False)
    print(f"✓ Saved {output_filepath}")
