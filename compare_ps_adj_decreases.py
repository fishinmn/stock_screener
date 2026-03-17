import json
import pandas as pd
from pathlib import Path

# Paths
base_path = Path(__file__).parent
old_json_path = base_path / "docs" / "holds_json_data_all.json"
csv_path = base_path / "data" / "algo10_data_all.csv"

# Load old data
with open(old_json_path, 'r') as f:
    old_data = json.load(f)

# Create dict keyed by Symbol
old_dict = {item['Symbol']: item for item in old_data}

# Load CSV
df = pd.read_csv(csv_path)

# Add new columns
df['PS_adj_prior_run'] = None
df['change_in_PS_adj'] = None

for idx, row in df.iterrows():
    symbol = row['Symbol']
    if symbol in old_dict:
        old_ps = old_dict[symbol].get('PS_adj')
        new_ps = row['PS_adj']
        if old_ps is not None and new_ps is not None:
            df.at[idx, 'PS_adj_prior_run'] = old_ps
            df.at[idx, 'change_in_PS_adj'] = new_ps - old_ps

# Save updated CSV
df.to_csv(csv_path, index=False)

print(f"Updated {csv_path} with PS_adj_prior_run and change_in_PS_adj columns")