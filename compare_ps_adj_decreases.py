import json
from pathlib import Path

# Paths
base_path = Path(__file__).parent
new_json_path = base_path / "data" / "holds_json_data_all.json"
old_json_path = base_path / "docs" / "holds_json_data_all.json"
output_path = base_path / "data" / "top_ps_adj_decreases.json"

# Load new data
with open(new_json_path, 'r') as f:
    new_data = json.load(f)

# Load old data
with open(old_json_path, 'r') as f:
    old_data = json.load(f)

# Create dicts keyed by Symbol
new_dict = {item['Symbol']: item for item in new_data}
old_dict = {item['Symbol']: item for item in old_data}

# Collect decreases
decreases = []
for symbol, new_item in new_dict.items():
    if symbol in old_dict:
        new_ps = new_item.get('PS_adj')
        old_ps = old_dict[symbol].get('PS_adj')
        if new_ps is not None and old_ps is not None and new_ps < 1:
            decrease = old_ps - new_ps
            if decrease > 0:
                decreases.append({
                    'Symbol': symbol,
                    'old_PS_adj': old_ps,
                    'new_PS_adj': new_ps,
                    'decrease': decrease
                })

# Sort by decrease descending
decreases.sort(key=lambda x: x['decrease'], reverse=True)

# Take top 20
top_20 = decreases[:20]

# Save to JSON
with open(output_path, 'w') as f:
    json.dump(top_20, f, indent=4)

print(f"Top 20 PS_adj decreases saved to {output_path}")