import json
import math
import pandas as pd
from pathlib import Path

# Paths
base_path = Path(__file__).parent
old_json_path = base_path / "docs" / "holds_json_data_all.json"
csv_path = base_path / "data" / "algo10_data_all.csv"

# ---- CONFIG ----

# Columns that should never be "backfilled" from the prior run - identifiers
# and columns that are freshly computed further down in this script.
EXCLUDE_FROM_BACKFILL = {"Symbol", "PS_adj_prior_run", "change_in_PS_adj"}

# Columns where 0 is a legitimate value and should NOT be treated as missing/bad.
# Add column names here as you discover fields where 0 is a real, meaningful
# reading (e.g. a YoY figure that's genuinely flat).
ZERO_IS_VALID = {
    # "RevYoY",
}

# Text values (case-insensitive, whitespace-trimmed) treated as "missing" placeholders.
BAD_TEXT_VALUES = {"unknown", "n/a", "na", "none", "null", "-", ""}


def is_bad_value(value, column):
    """Return True if `value` looks missing/low-quality for the given column."""
    if value is None:
        return True
    try:
        if pd.isna(value):
            return True
    except (TypeError, ValueError):
        pass
    if isinstance(value, str):
        return value.strip().lower() in BAD_TEXT_VALUES
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return True
        if value == 0 and column not in ZERO_IS_VALID:
            return True
    return False


# Load old data
with open(old_json_path, 'r') as f:
    old_data = json.load(f)

# Create dict keyed by Symbol
old_dict = {item['Symbol']: item for item in old_data}

# Load CSV
df = pd.read_csv(csv_path)

# ---- Backfill any new-run values that regressed vs. the prior run ----
backfill_log = []

for idx, row in df.iterrows():
    symbol = row['Symbol']
    old_row = old_dict.get(symbol)
    if not old_row:
        continue

    for col in df.columns:
        if col in EXCLUDE_FROM_BACKFILL:
            continue
        if col not in old_row:
            continue

        new_val = row[col]
        old_val = old_row.get(col)

        if is_bad_value(new_val, col) and not is_bad_value(old_val, col):
            df.at[idx, col] = old_val
            backfill_log.append((symbol, col, new_val, old_val))

# ---- PS_adj comparison (uses the possibly-backfilled PS_adj) ----
df['PS_adj_prior_run'] = None
df['change_in_PS_adj'] = None

for idx, row in df.iterrows():
    symbol = row['Symbol']
    if symbol in old_dict:
        old_ps = old_dict[symbol].get('PS_adj')
        new_ps = row['PS_adj']
        if old_ps is not None and new_ps is not None and not pd.isna(new_ps):
            df.at[idx, 'PS_adj_prior_run'] = old_ps
            df.at[idx, 'change_in_PS_adj'] = new_ps - old_ps

# Save updated CSV
df.to_csv(csv_path, index=False)

print(f"Updated {csv_path} with PS_adj_prior_run and change_in_PS_adj columns")
if backfill_log:
    print(f"\nBackfilled {len(backfill_log)} value(s) from the prior run where new data looked worse:")
    for symbol, col, new_val, old_val in backfill_log:
        print(f"  {symbol}.{col}: {new_val!r} -> {old_val!r}")
else:
    print("No fields needed backfilling from the prior run.")
