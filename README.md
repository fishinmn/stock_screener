# Stock Screener Repository

## Overview
This repository contains the core pipeline for generating stock screening data and publishing it to a JSON format for web consumption.

## Main Pipeline (`run_merge_and_publish.bat`)

The main workflow consists of 7 steps:

1. **fundamentals_screener_mega_caps.py** - Screens mega-cap stocks for fundamental metrics
2. **fundamentals_screener_large_caps.py** - Screens large-cap stocks for fundamental metrics
3. **fundamentals_screener_mid_caps.py** - Screens mid-cap stocks for fundamental metrics
4. **fundamentals_screener_small_caps.py** - Screens small-cap stocks for fundamental metrics
5. **merge_fundamentals_only.py** - Merges all cap-size fundamentals into a single file
6. **algo10_data_all.py** - Processes and enriches the merged data with additional metrics
7. **publish_json_holds_all.py** - Publishes the final data as JSON for web consumption

## Key Files

### Python Scripts (Root Directory)
- **fundamentals_screener_*.py** - Screeners for different market cap sizes
- **merge_fundamentals_only.py** - Merges screener outputs
- **algo10_data_all.py** - Main data processing and enrichment
- **publish_json_holds_all.py** - JSON publisher
- **investing_functions.py** - Utility functions for data processing

### Web Files (html/)
- **welcome.html** - Main stock screener interface (loads holds_json_data_all.json)
- **index.html** - Homepage/landing page
- **full-disclosure.html** - Legal disclosure page
- **terms-conditions.html** - Terms and conditions
- **privacy-policy.html** - Privacy policy
- **favicon.ico** - Site favicon

### Data Files (data/)

#### Input Files (Required - Not in Repo)
These CSV files are sourced from NASDAQ and need to be obtained separately:
- **nasdaq_screener_megacap.csv**
- **nasdaq_screener_lrgcap.csv**
- **nasdaq_screener_midap.csv**
- **nasdaq_screener_smallcap_with_coverage.csv**

#### Intermediate Files (Generated)
- **fundamentals_screener_mega_caps.csv**
- **fundamentals_screener_large.csv**
- **fundamentals_screener_mid_caps.csv**
- **fundamentals_screener_small_cap.csv**
- **all_caps_fundamentals.csv**
- **algo10_data_all.csv**

#### Output Files (Published)
- **holds_json_data_all.json** - JSON data consumed by welcome.html
- **holds_json_data_all.html** - HTML version of the data

## Data Flow

```
NASDAQ CSV files (input)
    ↓
fundamentals_screener_*.py (4 parallel processes)
    ↓
merge_fundamentals_only.py
    ↓
algo10_data_all.py (enrichment)
    ↓
publish_json_holds_all.py
    ↓
holds_json_data_all.json → welcome.html (web display)
```

## Dependencies

See `requirements.txt` for Python package dependencies. Key dependencies include:
- pandas
- yfinance
- yahooquery
- boto3
- Various other data processing and visualization libraries

## Notes

- The batch file references `C:\git\stock_analysis_app\` but the actual scripts should be run from this repository
- The NASDAQ screener CSV files must be obtained and placed in the `data/` directory before running the pipeline
- All image assets (favicon, logos) should be placed in the root web directory when deploying
