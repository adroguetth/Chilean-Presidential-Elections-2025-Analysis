# Chilean Presidential Elections 2025 — Dashboard

Interactive Streamlit dashboard for the 2025 Chilean presidential election results.

## Features

- **Summary**: Static overview with key metrics and results
- **First Round**: Dynamic analysis with filters
  - Summary, Zones, Communal, Null/Blank, Transfers
- **Second Round**: Dynamic analysis with filters
  - Summary, Zones, Communal, Null/Blank, Transfers
- **Language toggle**: ES / EN

## Data Source

SQLite database loaded from:
`https://raw.githubusercontent.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/main/raw/database/chile_elections.db`

## Installation

```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
