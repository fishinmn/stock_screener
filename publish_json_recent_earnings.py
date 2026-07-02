# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 08:36:15 2016

@author: efischer
"""
import json
import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd

current_time = datetime.now()
pd.set_option("display.max_colwidth", 10000)

repo_root = Path(__file__).resolve().parent
data_dir = repo_root / "data"
docs_dir = repo_root / "docs"
data_dir.mkdir(parents=True, exist_ok=True)
docs_dir.mkdir(parents=True, exist_ok=True)

filepath = data_dir / "recent_earnings_data.csv"
data = pd.read_csv(filepath, encoding="utf-8")
data = data.where(pd.notnull(data), None)
export_json = data.to_dict(orient="records")

file_name = "json_data_recent_earnings.json"
filepath_data_json = data_dir / file_name
with open(filepath_data_json, "w", encoding="utf-8") as f:
    json.dump(export_json, f, indent=4, sort_keys=True, default=str)
print(f"✓ Created {filepath_data_json}")

filepath_docs_json = docs_dir / file_name
shutil.copy2(filepath_data_json, filepath_docs_json)
print(f"✓ Copied to {filepath_docs_json}")

recommendation_list_string = json.dumps(
    data.to_dict(orient="records"), indent=4, sort_keys=True, default=str
)
recommendation_list = json.loads(recommendation_list_string)

file_name_html = "json_data_recent_earnings.html"
filepath_data_html = data_dir / file_name_html
with open(filepath_data_html, "w", encoding="utf-8") as file_html:
    file_html.write(json.dumps(recommendation_list))
print(f"✓ Created {filepath_data_html}")

filepath_docs_html = docs_dir / file_name_html
shutil.copy2(filepath_data_html, filepath_docs_html)
print(f"✓ Copied to {filepath_docs_html}")

print("\n✅ All files published to docs/ folder for GitHub Pages deployment")