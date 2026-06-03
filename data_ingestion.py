"""
=============================================================
  Mutual Fund Analytics — Day 1: Data Ingestion
  File   : data_ingestion.py
  Author : Intern
  Date   : 2026-06-01
=============================================================
Tasks covered:
  3. Load all CSV datasets — print shape, dtypes, head, anomalies
  6. Explore fund_master — unique fund houses, categories, etc.
  7. Validate AMFI codes — data quality summary
=============================================================
"""

import os
import pandas as pd
import numpy as np

# ─────────────────────────────────────────────────────────────
# 0.  PATHS
# ─────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
RAW_DIR   = os.path.join(BASE_DIR, "data", "raw")
PROC_DIR  = os.path.join(BASE_DIR, "data", "processed")

os.makedirs(RAW_DIR,  exist_ok=True)
os.makedirs(PROC_DIR, exist_ok=True)


# ─────────────────────────────────────────────────────────────
# 1.  HELPER — inspect a dataframe
# ─────────────────────────────────────────────────────────────
def inspect_df(name: str, df: pd.DataFrame) -> None:
    """Print shape, dtypes, head(5) and flag anomalies."""
    print("\n" + "═" * 60)
    print(f"  DATASET : {name}")
    print("═" * 60)
    print(f"  Shape   : {df.shape[0]} rows × {df.shape[1]} columns")
    print("\n── dtypes ──────────────────────────────────────────────")
    print(df.dtypes.to_string())
    print("\n── head(5) ─────────────────────────────────────────────")
    print(df.head(5).to_string(index=False))
    _flag_anomalies(df)


def _flag_anomalies(df: pd.DataFrame) -> None:
    """Check for nulls, duplicates, negative values, mixed types."""
    issues = []

    # Missing values
    null_counts = df.isnull().sum()
    cols_with_nulls = null_counts[null_counts > 0]
    if not cols_with_nulls.empty:
        for col, cnt in cols_with_nulls.items():
            pct = 100 * cnt / len(df)
            issues.append(f"  ⚠  Nulls in '{col}': {cnt} ({pct:.1f}%)")

    # Duplicate rows
    dup_count = df.duplicated().sum()
    if dup_count:
        issues.append(f"  ⚠  {dup_count} duplicate row(s) detected")

    # Negative values in numeric columns
    num_cols = df.select_dtypes(include=[np.number]).columns
    for col in num_cols:
        neg = (df[col] < 0).sum()
        if neg:
            issues.append(f"  ⚠  Negative values in '{col}': {neg} row(s)")

    if issues:
        print("\n── anomalies ───────────────────────────────────────────")
        for msg in issues:
            print(msg)
    else:
        print("\n  ✔  No anomalies detected")


# ─────────────────────────────────────────────────────────────
# 2.  LOAD DATASETS
#     Simulated 10-dataset structure; adapt paths as needed.
# ─────────────────────────────────────────────────────────────

# Map of logical name → expected filename in data/raw/
DATASETS = {
    "fund_master"       : "fund_master.csv",
    "nav_history"       : "nav_history.csv",
    "portfolio_holdings": "portfolio_holdings.csv",
    "sip_transactions"  : "sip_transactions.csv",
    "benchmark_returns" : "benchmark_returns.csv",
    "expense_ratios"    : "expense_ratios.csv",
    "fund_returns"      : "fund_returns.csv",
    "risk_metrics"      : "risk_metrics.csv",
    "aum_data"          : "aum_data.csv",
    "investor_profiles" : "investor_profiles.csv",
}

# For Day 1 we load the single provided CSV as fund_master
# and copy it to data/raw/ if not already there.
PROVIDED_CSV = os.path.join(BASE_DIR, "1.csv")
FUND_MASTER_PATH = os.path.join(RAW_DIR, "fund_master.csv")

if os.path.exists(PROVIDED_CSV) and not os.path.exists(FUND_MASTER_PATH):
    import shutil
    shutil.copy(PROVIDED_CSV, FUND_MASTER_PATH)
    print(f"[INFO] Copied provided CSV → {FUND_MASTER_PATH}")


def load_all_datasets() -> dict[str, pd.DataFrame]:
    """Load each dataset, inspect it, return dict of DataFrames."""
    loaded: dict[str, pd.DataFrame] = {}

    for name, filename in DATASETS.items():
        fpath = os.path.join(RAW_DIR, filename)

        if not os.path.exists(fpath):
            print(f"\n[SKIP] '{filename}' not found in data/raw/ — skipping.")
            continue

        try:
            df = pd.read_csv(fpath, low_memory=False)
            inspect_df(name, df)
            loaded[name] = df
        except Exception as exc:
            print(f"\n[ERROR] Failed to load '{filename}': {exc}")

    return loaded


# ─────────────────────────────────────────────────────────────
# 3.  EXPLORE FUND MASTER
# ─────────────────────────────────────────────────────────────

def explore_fund_master(df: pd.DataFrame) -> None:
    """Print unique fund houses, categories, sub-categories, risk grades."""
    print("\n" + "═" * 60)
    print("  FUND MASTER — Exploration")
    print("═" * 60)

    # Unique fund houses
    if "fund_house" in df.columns:
        fh = df["fund_house"].unique()
        print(f"\n  Fund Houses ({len(fh)}):")
        for h in sorted(fh):
            count = (df["fund_house"] == h).sum()
            print(f"    • {h:35s}  {count:3d} schemes")

    # Unique categories
    if "category" in df.columns:
        cats = df["category"].value_counts()
        print(f"\n  Categories ({len(cats)}):")
        for cat, cnt in cats.items():
            print(f"    • {cat:20s}  {cnt:3d} schemes")

    # Unique sub-categories
    if "sub_category" in df.columns:
        sub = df["sub_category"].value_counts()
        print(f"\n  Sub-Categories ({len(sub)}):")
        for s, cnt in sub.items():
            print(f"    • {s:25s}  {cnt:3d} schemes")

    # Risk grades
    if "risk_category" in df.columns:
        risk = df["risk_category"].value_counts()
        print(f"\n  Risk Grades ({len(risk)}):")
        for r, cnt in risk.items():
            print(f"    • {r:20s}  {cnt:3d} schemes")

    # AMFI scheme code structure
    if "amfi_code" in df.columns:
        codes = df["amfi_code"].dropna().astype(str)
        lengths = codes.str.len().value_counts()
        print(f"\n  AMFI Code Lengths:")
        for length, cnt in lengths.items():
            print(f"    • {length}-digit codes: {cnt}")
        print(f"  Range: {codes.min()} → {codes.max()}")


# ─────────────────────────────────────────────────────────────
# 4.  VALIDATE AMFI CODES
# ─────────────────────────────────────────────────────────────

def validate_amfi_codes(
    fund_master: pd.DataFrame,
    nav_history: pd.DataFrame | None
) -> None:
    """Check every fund_master AMFI code exists in nav_history."""
    print("\n" + "═" * 60)
    print("  DATA QUALITY SUMMARY — AMFI Code Validation")
    print("═" * 60)

    fm_codes  = set(fund_master["amfi_code"].dropna().astype(str).str.strip())
    total_fm  = len(fm_codes)

    print(f"\n  Total schemes in fund_master : {total_fm}")

    if nav_history is None or "amfi_code" not in nav_history.columns:
        print("  [WARN] nav_history not available — skipping cross-check.")
        print("  Action: Place nav_history.csv in data/raw/ and re-run.")
        _quality_summary_standalone(fund_master)
        return

    nav_codes     = set(nav_history["amfi_code"].dropna().astype(str).str.strip())
    matched       = fm_codes & nav_codes
    missing_in_nav = fm_codes - nav_codes
    extra_in_nav  = nav_codes - fm_codes

    print(f"  Total codes in nav_history   : {len(nav_codes)}")
    print(f"  Matched (both datasets)      : {len(matched)}")
    print(f"  ──────────────────────────────────────────")
    print(f"  ⚠  In fund_master but NOT nav_history : {len(missing_in_nav)}")
    if missing_in_nav:
        for code in sorted(missing_in_nav):
            name = fund_master.loc[
                fund_master["amfi_code"].astype(str).str.strip() == code,
                "scheme_name"
            ].values
            label = name[0] if len(name) else "Unknown"
            print(f"      {code} — {label}")

    print(f"  ⚠  In nav_history but NOT fund_master : {len(extra_in_nav)}")
    if extra_in_nav:
        for code in sorted(list(extra_in_nav)[:10]):   # print max 10
            print(f"      {code}")

    coverage = 100 * len(matched) / total_fm if total_fm else 0
    print(f"\n  Coverage score : {coverage:.1f}%")
    print(f"  Quality grade  : {'✔ PASS' if coverage >= 95 else '✘ REVIEW NEEDED'}")


def _quality_summary_standalone(df: pd.DataFrame) -> None:
    """Quality check on fund_master alone."""
    print("\n  — Standalone fund_master quality check —")
    total     = len(df)
    nulls     = df.isnull().sum().sum()
    dups      = df.duplicated(subset=["amfi_code"]).sum() if "amfi_code" in df.columns else 0
    neg_exp   = (df["expense_ratio_pct"] < 0).sum() if "expense_ratio_pct" in df.columns else 0

    print(f"  Total records          : {total}")
    print(f"  Total null cells       : {nulls}")
    print(f"  Duplicate AMFI codes   : {dups}")
    print(f"  Negative expense ratios: {neg_exp}")
    grade = "✔ GOOD" if nulls == 0 and dups == 0 and neg_exp == 0 else "⚠ CHECK"
    print(f"  Quality assessment     : {grade}")


# ─────────────────────────────────────────────────────────────
# 5.  MAIN
# ─────────────────────────────────────────────────────────────

def main():
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║   MUTUAL FUND ANALYTICS — Day 1: Data Ingestion          ║")
    print("╚" + "═" * 58 + "╝")

    datasets = load_all_datasets()

    # Explore fund_master if loaded
    if "fund_master" in datasets:
        explore_fund_master(datasets["fund_master"])

        # Validate AMFI codes
        nav_hist = datasets.get("nav_history")   # None if not loaded yet
        validate_amfi_codes(datasets["fund_master"], nav_hist)
    else:
        print("\n[WARN] fund_master not loaded. Place fund_master.csv in data/raw/")

    print("\n" + "─" * 60)
    print("  Day 1 ingestion complete.")
    print("  Next: run live_nav_fetch.py to pull real-time NAV data.")
    print("─" * 60 + "\n")


if __name__ == "__main__":
    main()
