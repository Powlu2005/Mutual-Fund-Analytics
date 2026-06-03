# Mutual-Fund-Analytics
# 📊 Mutual Fund Analytics — Capstone Project I

> **Internship Capstone | Start Date: 01 Jun 2026 | Status: IN PROGRESS**

---

## 🗂️ Project Structure

```
mutual_fund_analytics/
├── data/
│   ├── raw/            ← original CSVs & live API JSON files
│   └── processed/      ← cleaned, transformed datasets
├── notebooks/          ← Jupyter exploratory notebooks
├── sql/                ← SQL queries & schema scripts
├── dashboard/          ← Plotly / Dash dashboard code
├── reports/            ← generated PDF / HTML reports
├── data_ingestion.py   ← Day 1: load & inspect all datasets
├── live_nav_fetch.py   ← Day 1: fetch real-time NAV from mfapi.in
├── requirements.txt    ← all Python dependencies
└── README.md
```

---

## ⚙️ Setup

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/mutual-fund-analytics.git
cd mutual-fund-analytics

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Day 1 — Data Ingestion

### Step 1: Load & inspect all datasets
```bash
python data_ingestion.py
```
Output:
- Shape, dtypes, head(5) for every CSV
- Anomaly flags (nulls, duplicates, negatives)
- Fund master exploration (fund houses, categories, risk grades)
- AMFI code validation summary

### Step 2: Fetch live NAV data
```bash
python live_nav_fetch.py
```
Output:
- `data/raw/nav_raw_<code>.json`  — raw API response
- `data/raw/nav_<code>.csv`       — parsed NAV history
- `data/raw/nav_combined_all_schemes.csv` — all schemes stacked
- `data/raw/live_nav_snapshot.csv`        — latest NAV table

---

## 📡 Schemes Tracked

| AMFI Code | Scheme                                    | Fund House     |
|-----------|-------------------------------------------|----------------|
| 125497    | HDFC Top 100 Fund - Direct Plan - Growth  | HDFC MF        |
| 119551    | SBI Bluechip Fund - Regular - Growth      | SBI MF         |
| 120503    | ICICI Pru Bluechip Fund - Regular         | ICICI Pru MF   |
| 118632    | Nippon India Large Cap Fund               | Nippon India MF|
| 119092    | Axis Bluechip Fund - Regular              | Axis MF        |
| 120841    | Kotak Bluechip Fund - Regular             | Kotak MF       |

---

## 📅 Progress Log

| Day | Date       | Task                              | Status     |
|-----|------------|-----------------------------------|------------|
| 1   | 2026-06-01 | Data Ingestion + Live NAV Fetch   | ✅ Complete |
| 2   | TBD        | EDA + Data Cleaning               | ⏳ Planned  |
| 3   | TBD        | SQL Schema + Queries              | ⏳ Planned  |
| 4   | TBD        | Returns & Risk Metrics            | ⏳ Planned  |
| 5   | TBD        | Dashboard                         | ⏳ Planned  |

---

## 🙏 Data Sources
- **AMFI India** — [mfapi.in](https://mfapi.in/) (free, open NAV API)
- Fund master CSV provided by internship supervisor
