# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 08:36:15 2016

@author: efischer
"""
import pandas as pd
import numpy as np
import os
import json
import shutil
from datetime import datetime

###get my stocks caps
current_time = datetime.now()
pd.set_option("display.max_colwidth", 10000)


dir_path = os.path.dirname(os.path.realpath(__file__))
filepath = os.path.join(dir_path, 'data', 'algo10_data_all.csv')
data = pd.read_csv(filepath, encoding='utf-8')
data = data.where(pd.notnull(data), None)  # <-- This line converts NaN to None (which becomes null in JSON)
# Convert DataFrame to list of dicts for JSON export
export_json = data.to_dict(orient='records')

#writing data data frame to json file
file_name = "holds_json_data_all.json"
filepath_data_json = os.path.join(dir_path, 'data', file_name)            
with open(filepath_data_json, 'w') as f:
    json.dump(export_json, f, indent=4, sort_keys=True, default=str)

print(f"✓ Created {filepath_data_json}")

# Copy JSON to docs folder for GitHub Pages
filepath_docs_json = os.path.join(dir_path, 'docs', file_name)
shutil.copy2(filepath_data_json, filepath_docs_json)
print(f"✓ Copied to {filepath_docs_json}")

##################
# Create HTML version
recommendation_list_string = json.dumps(data.to_dict(orient='records'), indent=4, sort_keys=True, default=str)
recommendation_list = json.loads(recommendation_list_string)

file_name_html = "holds_json_data_all.html"
filepath_data_html = os.path.join(dir_path, 'data', file_name_html)

with open(filepath_data_html, 'w') as file_html:
    file_html.write(json.dumps(recommendation_list))

print(f"✓ Created {filepath_data_html}")

# Copy HTML to docs folder for GitHub Pages
filepath_docs_html = os.path.join(dir_path, 'docs', file_name_html)
shutil.copy2(filepath_data_html, filepath_docs_html)
print(f"✓ Copied to {filepath_docs_html}")

print("\n✅ All files published to docs/ folder for GitHub Pages deployment")