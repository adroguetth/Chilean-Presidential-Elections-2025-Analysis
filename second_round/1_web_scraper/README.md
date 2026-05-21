# 🌐 Web Scraper - Chilean Second Round Election 2025

![MIT License](https://img.shields.io/badge/license-MIT-9ecae1?style=flat-square&logo=open-source-initiative&logoColor=white) ![Web Scraping](https://img.shields.io/badge/Web-Scraping-orange?style=flat-square) ![ETL](https://img.shields.io/badge/ETL-9ecae1?style=flat-square)

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white) [![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=flat-square&logo=selenium&logoColor=white)](https://selenium.dev) ![Firefox](https://img.shields.io/badge/Firefox-FF7139?style=flat-square&logo=firefox&logoColor=white)

## 📥 Quick Downloads

| Document | Format |
| :------- | :----- |
| **🇬🇧 English Documentation** | [Markdown](https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/blob/main/second_round/1_web_scraper/README.md) |
| **🇪🇸 Spanish Documentation** | [Markdown](https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/blob/main/second_round/1_web_scraper/README_ES.md) |
| **📊 Raw Data (CSV)** | [Download](https://raw.githubusercontent.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/refs/heads/main/raw/chile_2025_second_round.csv) |

## 📋 General Description

This script is the **second component** of the Chilean Presidential Elections 2025 intelligence system. It automates the extraction of second-round electoral results from the official SERVEL website, processing all communes in Chile and generating structured CSV outputs optimized for data analysis.

The script uses **Selenium** with Firefox WebDriver for browser automation, implements **name normalization** (converting 'ARICA' to 'Arica'), includes **automatic backup** before overwriting results, and provides **partial progress saving** every 10 communes to prevent data loss during long executions.

### Key Features

- **Complete Extraction**: Processes all 346 communes across 16 regions of Chile
- **Second Round Specific**: Optimized for JARA vs KAST presidential candidates
- **Name Normalization**: Converts uppercase names to title format (Arica vs ARICA)
- **Tidy Data Output**: Columns optimized for SQL (`snake_case`), Python, and DAX
- **Automatic Backup**: Creates backup before overwriting `latest_results.csv`
- **Partial Progress**: Saves intermediate results every 10 communes
- **Multi-format Export**: Generates CSV (primary) and Excel (secondary)
- **Metadata Generation**: Automatic documentation of dataset structure
- **Headless Mode**: Support for server/CI/CD environments

## 📊 Process Flow Diagram

### **Legend**

| Color        | Type          | Description                                           |
| :----------- | :------------ | :---------------------------------------------------- |
| 🔵 Blue       | Input / Start | SERVEL website, configuration, CLI arguments          |
| 🟠 Orange     | Process       | Browser automation, data extraction, file operations  |
| 🔴 Red        | Decision      | Conditional branching (selector works?, file exists?) |
| 🟢 Green      | Storage       | CSV outputs, backups, metadata, logs                  |
| 🟣 Purple     | External      | Firefox browser, GeckoDriver                          |
| 🟢 Dark Green | Output        | Final CSV, summary report                             |

