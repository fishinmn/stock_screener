# -*- coding: utf-8 -*-
"""
Publishes upcoming earnings data as JSON/HTML in data/ and docs/.
"""
import json
import shutil
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError

repo_root = Path(__file__).resolve().parent
data_dir = repo_root / "data"
docs_dir = repo_root / "docs"
data_dir.mkdir(parents=True, exist_ok=True)
docs_dir.mkdir(parents=True, exist_ok=True)

filepath = data_dir / "upcoming_earnings.csv"
if filepath.exists() and filepath.stat().st_size > 0:
    try:
        data = pd.read_csv(filepath, encoding="utf-8")
    except EmptyDataError:
        data = pd.DataFrame()
else:
    data = pd.DataFrame()
data = data.where(pd.notnull(data), None)
export_json = data.to_dict(orient="records")

file_name = "json_data_upcoming_earnings.json"
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

file_name_html = "json_data_upcoming_earnings.html"
filepath_data_html = data_dir / file_name_html
with open(filepath_data_html, "w", encoding="utf-8") as file_html:
    file_html.write(json.dumps(recommendation_list))
print(f"✓ Created {filepath_data_html}")

filepath_docs_html = docs_dir / file_name_html
shutil.copy2(filepath_data_html, filepath_docs_html)
print(f"✓ Copied to {filepath_docs_html}")

print("\n✅ Upcoming earnings published to docs/ folder")
