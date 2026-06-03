"""
=============================================================
  Mutual Fund Analytics — Day 1: Live NAV Fetch
  File   : live_nav_fetch.py
  Author : Intern
  Date   : 2026-06-01
=============================================================
Tasks covered:
  4. Fetch live NAV — HDFC Top 100 Direct (125497)
  5. Fetch NAV for 5 key schemes:
       SBI Bluechip      119551
       ICICI Bluechip    120503
       Nippon Large Cap  118632
       Axis Bluechip     119092
       Kotak Bluechip    120841
=============================================================
"""

import os
import json
import time
import requests
import pandas as pd
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# 0.  PATHS
# ─────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR  = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

API_BASE  = "https://api.mfapi.in/mf"
TIMEOUT   = 10          # seconds per request
RETRY_MAX = 3           # retry attempts on failure
SLEEP_SEC = 0.5         # polite delay between requests


# ─────────────────────────────────────────────────────────────
# 1.  SCHEME REGISTRY
# ─────────────────────────────────────────────────────────────

SCHEMES = {
    125497: "HDFC Top 100 Fund - Direct Plan - Growth",
    119551: "SBI Bluechip Fund - Regular Plan - Growth",
    120503: "ICICI Pru Bluechip Fund - Regular - Growth",
    118632: "Nippon India Large Cap Fund - Regular - Growth",
    119092: "Axis Bluechip Fund - Regular - Growth",
    120841: "Kotak Bluechip Fund - Regular - Growth",
}


# ─────────────────────────────────────────────────────────────
# 2.  FETCH HELPER
# ─────────────────────────────────────────────────────────────

def fetch_nav(amfi_code: int) -> dict | None:
    """
    Fetch NAV data from mfapi.in for a given AMFI code.
    Returns the parsed JSON dict, or None on failure.
    """
    url = f"{API_BASE}/{amfi_code}"

    for attempt in range(1, RETRY_MAX + 1):
        try:
            resp = requests.get(url, timeout=TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            return data
        except requests.exceptions.Timeout:
            print(f"  [WARN] Timeout on {amfi_code} (attempt {attempt}/{RETRY_MAX})")
        except requests.exceptions.HTTPError as e:
            print(f"  [ERROR] HTTP {e.response.status_code} for {amfi_code}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] Request failed for {amfi_code}: {e}")
            return None
        except json.JSONDecodeError:
            print(f"  [ERROR] Invalid JSON for {amfi_code}")
            return None

        time.sleep(SLEEP_SEC)

    print(f"  [FAIL] All {RETRY_MAX} attempts exhausted for {amfi_code}")
    return None


# ─────────────────────────────────────────────────────────────
# 3.  PARSE RESPONSE
# ─────────────────────────────────────────────────────────────

def parse_nav_response(amfi_code: int, raw: dict) -> pd.DataFrame:
    """
    Parse mfapi.in JSON into a tidy DataFrame.

    Response structure:
    {
      "meta": { "scheme_name": ..., "fund_house": ..., "scheme_type": ...,
                "scheme_category": ..., "scheme_code": ... },
      "data": [ { "date": "DD-MM-YYYY", "nav": "123.4567" }, ... ],
      "status": "SUCCESS"
    }
    """
    meta   = raw.get("meta", {})
    rows   = raw.get("data", [])
    status = raw.get("status", "UNKNOWN")

    if status != "SUCCESS" or not rows:
        print(f"  [WARN] Unexpected status '{status}' for {amfi_code}")
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df["amfi_code"]    = amfi_code
    df["scheme_name"]  = meta.get("scheme_name", SCHEMES.get(amfi_code, "Unknown"))
    df["fund_house"]   = meta.get("fund_house", "Unknown")
    df["scheme_type"]  = meta.get("scheme_type", "")
    df["category"]     = meta.get("scheme_category", "")

    # Parse dates and NAV
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
    df["nav"]  = pd.to_numeric(df["nav"], errors="coerce")

    # Sort newest first
    df.sort_values("date", ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df


# ─────────────────────────────────────────────────────────────
# 4.  FETCH & SAVE  — single scheme
# ─────────────────────────────────────────────────────────────

def fetch_and_save_single(amfi_code: int) -> pd.DataFrame | None:
    """Fetch one scheme, parse, save raw CSV, return DataFrame."""
    name = SCHEMES.get(amfi_code, str(amfi_code))
    print(f"\n  Fetching [{amfi_code}] {name} …")

    raw = fetch_nav(amfi_code)
    if raw is None:
        return None

    df = parse_nav_response(amfi_code, raw)
    if df.empty:
        return None

    # Save raw JSON
    json_path = os.path.join(RAW_DIR, f"nav_raw_{amfi_code}.json")
    with open(json_path, "w") as f:
        json.dump(raw, f, indent=2)

    # Save parsed CSV
    csv_path = os.path.join(RAW_DIR, f"nav_{amfi_code}.csv")
    df.to_csv(csv_path, index=False)

    # Preview
    latest = df.iloc[0]
    print(f"  ✔  {len(df):,} records | Latest NAV: ₹{latest['nav']:.4f} on {latest['date'].date()}")
    print(f"     Saved → {csv_path}")

    return df


# ─────────────────────────────────────────────────────────────
# 5.  COMBINED HISTORY  — all 5 schemes
# ─────────────────────────────────────────────────────────────

def build_combined_nav(all_dfs: list[pd.DataFrame]) -> pd.DataFrame:
    """Stack all individual NAV DataFrames into one combined file."""
    valid = [df for df in all_dfs if not df.empty]
    if not valid:
        return pd.DataFrame()

    combined = pd.concat(valid, ignore_index=True)
    combined.sort_values(["amfi_code", "date"], ascending=[True, False], inplace=True)
    combined.reset_index(drop=True, inplace=True)

    out_path = os.path.join(RAW_DIR, "nav_combined_all_schemes.csv")
    combined.to_csv(out_path, index=False)
    print(f"\n  ✔  Combined NAV saved → {out_path}")
    print(f"     Total records: {len(combined):,}")
    return combined


# ─────────────────────────────────────────────────────────────
# 6.  PRINT LIVE SNAPSHOT
# ─────────────────────────────────────────────────────────────

def print_live_snapshot(all_dfs: list[pd.DataFrame]) -> None:
    """Print a formatted table of the latest NAV for each scheme."""
    rows = []
    for df in all_dfs:
        if df.empty:
            continue
        r = df.iloc[0]
        rows.append({
            "AMFI Code"   : int(r["amfi_code"]),
            "Scheme"      : r["scheme_name"][:45],
            "Latest NAV"  : f"₹{r['nav']:.4f}",
            "As of Date"  : str(r["date"].date()),
        })

    if not rows:
        return

    snap_df = pd.DataFrame(rows)

    print("\n" + "═" * 80)
    print("  LIVE NAV SNAPSHOT  —  " + datetime.now().strftime("%d %b %Y %H:%M:%S"))
    print("═" * 80)
    print(snap_df.to_string(index=False))
    print("═" * 80)

    # Save snapshot
    snap_path = os.path.join(RAW_DIR, "live_nav_snapshot.csv")
    snap_df.to_csv(snap_path, index=False)
    print(f"\n  Snapshot saved → {snap_path}")


# ─────────────────────────────────────────────────────────────
# 7.  MAIN
# ─────────────────────────────────────────────────────────────

def main():
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║   MUTUAL FUND ANALYTICS — Day 1: Live NAV Fetch          ║")
    print("╚" + "═" * 58 + "╝")
    print(f"\n  Base URL  : {API_BASE}")
    print(f"  Schemes   : {len(SCHEMES)}")
    print(f"  Timestamp : {datetime.now().strftime('%d %b %Y %H:%M:%S')}")

    all_dfs: list[pd.DataFrame] = []

    # ── Task 4: HDFC Top 100 Direct first ──────────────────────
    print("\n── TASK 4 : HDFC Top 100 Direct (125497) ───────────────────")
    hdfc_df = fetch_and_save_single(125497)
    if hdfc_df is not None:
        all_dfs.append(hdfc_df)
    time.sleep(SLEEP_SEC)

    # ── Task 5: remaining 5 key schemes ────────────────────────
    print("\n── TASK 5 : 5 Key Schemes ───────────────────────────────────")
    remaining = [code for code in SCHEMES if code != 125497]
    for code in remaining:
        df = fetch_and_save_single(code)
        if df is not None:
            all_dfs.append(df)
        time.sleep(SLEEP_SEC)

    # ── Combine & snapshot ─────────────────────────────────────
    combined = build_combined_nav(all_dfs)
    print_live_snapshot(all_dfs)

    print("\n" + "─" * 60)
    print(f"  Fetched {len(all_dfs)}/{len(SCHEMES)} schemes successfully.")
    print("  All raw JSON and parsed CSVs saved to data/raw/")
    print("─" * 60 + "\n")


if __name__ == "__main__":
    main()
