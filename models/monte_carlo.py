"""
TSP historical-return scraper and Monte Carlo retirement simulator.
"""

import io
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import streamlit as st
import yfinance as yf

from models.allocations import get_lifecycle_allocation


# ── ETF proxies for TSP funds ─────────────────────────────────────────────────
# C: SPY  (SPDR S&P 500)           → C Fund tracks S&P 500
# S: VXF  (Vanguard Extended Mkt)  → S Fund tracks DJ US Completion TSM
# I: EFA  (iShares MSCI EAFE)      → I Fund tracks MSCI EAFE
# F: AGG  (iShares US Agg Bond)    → F Fund tracks Bloomberg US Agg Bond
# G: SHY  (iShares 1-3yr Treasury) → G Fund proxy (no market equivalent)
_FUND_TICKERS = {"C": "SPY", "S": "VXF", "I": "EFA", "F": "AGG", "G": "SHY"}
_ETF_START = "2003-11-01"  # AGG launch date — earliest common history

# ── CSV fallback folder ───────────────────────────────────────────────────────
# Reads real TSP fund data from data/TSP_data/ when TSP.gov and yfinance fail.
#
# Expected filename pattern (already present in the folder):
#   tsp_c_fund_monthly_returns.csv
#   tsp_s_fund_monthly_returns.csv
#   tsp_I_fund_monthly_returns.csv   ← capital I is fine, matched case-insensitively
#   tsp_g_fund_monthly_returns.csv
#   tsp_f_fund_monthly_returns.csv   ← add if available; F fund is optional
#
# Required columns: month_end (date), monthly_return (decimal, e.g. 0.0178)
# Optional columns: month_end_price, monthly_return_pct  (ignored)
#
# If F fund data is absent, the G fund is used as its proxy for any
# allocation that references F (conservative bond-like behaviour).
_CSV_DIR = Path(__file__).resolve().parent.parent / "data" / "TSP_data"
_FUNDS = ["C", "S", "I", "F", "G"]

# Filename pattern: tsp_{fund}_fund_monthly_returns.csv  (case-insensitive match)
_CSV_PATTERN = "tsp_{fund}_fund_monthly_returns.csv"


def _csv_returns() -> pd.DataFrame:
    """
    Load monthly returns from TSP CSV files in data/TSP_data/.

    Columns used: month_end (date index), monthly_return (decimal return).
    If the F fund file is missing, G fund returns are substituted for F so
    allocations that reference F still work.
    Raises ValueError if no files are found at all.
    """
    series = {}
    for fund in _FUNDS:
        # Match case-insensitively (e.g. tsp_I_fund... or tsp_i_fund...)
        candidates = list(_CSV_DIR.glob(f"tsp_{fund}_fund_monthly_returns.csv")) + \
                     list(_CSV_DIR.glob(f"tsp_{fund.lower()}_fund_monthly_returns.csv")) + \
                     list(_CSV_DIR.glob(f"tsp_{fund.upper()}_fund_monthly_returns.csv"))
        # Deduplicate
        seen, unique = set(), []
        for p in candidates:
            if p.name not in seen:
                seen.add(p.name)
                unique.append(p)
        if not unique:
            continue

        raw = pd.read_csv(unique[0])
        raw.columns = raw.columns.str.strip().str.lower()

        # Date column
        date_col = next((c for c in raw.columns if "month" in c and "end" in c), None) \
                   or next((c for c in raw.columns if "date" in c), None)
        if date_col is None:
            continue
        raw[date_col] = pd.to_datetime(raw[date_col], format="mixed")
        raw = raw.set_index(date_col).sort_index()

        # Return column: prefer monthly_return (decimal) over pct column
        ret_col = next((c for c in raw.columns if c == "monthly_return"), None) \
                  or next((c for c in raw.columns
                           if "return" in c and "pct" not in c), None) \
                  or next((c for c in raw.columns if "return" in c), None)
        if ret_col is None:
            # Fall back to price column and compute returns
            price_col = next((c for c in raw.columns if "price" in c), raw.columns[0])
            s = pd.to_numeric(raw[price_col], errors="coerce").resample("ME").last()
            s = s.pct_change()
        else:
            s = pd.to_numeric(raw[ret_col], errors="coerce").resample("ME").last()
            # If values look like percentages (median > 0.5) scale to decimal
            if s.dropna().median() > 0.5:
                s = s / 100.0

        series[fund] = s

    if not series:
        raise ValueError(
            f"No TSP CSV files found in {_CSV_DIR}.\n"
            "Expected filenames like: tsp_c_fund_monthly_returns.csv"
        )

    df = pd.DataFrame(series).replace([np.inf, -np.inf], np.nan).dropna()

    # If F fund is missing, substitute G as a conservative bond proxy
    if "F" not in df.columns and "G" in df.columns:
        df["F"] = df["G"]

    return df


def _yfinance_returns() -> pd.DataFrame:
    """Download real ETF monthly returns as TSP fund proxies."""
    tickers = list(_FUND_TICKERS.values())
    raw = yf.download(tickers, start=_ETF_START, auto_adjust=True, progress=False)
    prices = raw["Close"].rename(columns={v: k for k, v in _FUND_TICKERS.items()})
    monthly = prices.resample("ME").last()
    returns = monthly.pct_change()
    returns.replace([np.inf, -np.inf], np.nan, inplace=True)
    returns = returns.dropna()
    return returns[["C", "S", "I", "F", "G"]]


# ── Data loader ───────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False, ttl=86400)
def scrape_and_prep_tsp_data():
    """
    Fetch real TSP fund return data.  Tries TSP.gov first; falls back to
    yfinance ETF proxies (real historical data).  Returns
    (monthly_returns_df, source_label).  Raises on total failure.
    """
    # ── 1. Try TSP.gov direct ─────────────────────────────────────────────────
    url = "https://www.tsp.gov/data/fund-price-history.csv"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "text/csv,application/csv",
        "Referer": "https://www.tsp.gov/",
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        if "<html" in response.text.lower() or "<!doctype html" in response.text.lower():
            raise ValueError("TSP.gov returned HTML (blocked).")

        df = pd.read_csv(io.StringIO(response.text))
        df.columns = df.columns.str.strip().str.lower()
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").set_index("date")

        core = []
        for fund in ["c", "s", "i", "f", "g"]:
            if fund in df.columns:
                core.append(fund)
            elif f"{fund} fund" in df.columns:
                df.rename(columns={f"{fund} fund": fund}, inplace=True)
                core.append(fund)

        for col in core:
            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.replace(",", "").astype(float)

        monthly = df[core].resample("ME").last().pct_change()
        monthly.replace([np.inf, -np.inf], np.nan, inplace=True)
        monthly = monthly.dropna()
        monthly.columns = ["C", "S", "I", "F", "G"]
        return monthly, "TSP.gov (Live)"

    except Exception:
        pass

    # ── 2. Fall back to real ETF proxies via yfinance ─────────────────────────
    try:
        returns = _yfinance_returns()
        if returns.empty:
            raise ValueError("yfinance returned no data.")
        return returns, "ETF Proxy (Real)"
    except Exception:
        pass

    # ── 3. Fall back to local CSV files in data/tsp_csvs/ ─────────────────────
    try:
        returns = _csv_returns()
        if returns.empty:
            raise ValueError("CSV files produced no usable rows.")
        funds_loaded = ", ".join(returns.columns.tolist())
        return returns, f"CSV (Manual) — funds: {funds_loaded}"
    except Exception as exc:
        raise RuntimeError(
            "Could not load TSP data from any source.\n\n"
            "To use offline CSV data, place files in:\n"
            f"  {_CSV_DIR}\n\n"
            "Option A — combined file: tsp_funds.csv\n"
            "  Columns: Date, C, S, I, F, G  (prices or monthly returns)\n\n"
            "Option B — per-fund files: C.csv  S.csv  I.csv  F.csv  G.csv\n"
            "  Columns: Date, Price  (or Close / Value / Return)\n\n"
            "Then restart the app."
        ) from exc


# ── Monte Carlo engine ───────────────────────────────────────────────────────

def run_real_monte_carlo(
    current_age: int,
    retire_age: int,
    initial_bal: float,
    monthly_contrib,
    hist_returns: pd.DataFrame,
    use_lc: bool,
    manual_alloc: dict,
    inflation_rate: float = 0.025,
    trials: int = 1000,
) -> np.ndarray:
    """
    Run *trials* bootstrap Monte Carlo simulations.

    monthly_contrib can be a scalar (fixed $) or list/array of length *months*.
    Returns an (trials x months+1) numpy array of portfolio paths.
    """
    months = (retire_age - current_age) * 12
    monthly_inflation = (1 + inflation_rate) ** (1 / 12) - 1

    if np.isscalar(monthly_contrib):
        contrib_schedule = np.full(months, monthly_contrib)
    else:
        contrib_schedule = np.array(monthly_contrib)
        if len(contrib_schedule) < months:
            contrib_schedule = np.pad(
                contrib_schedule, (0, months - len(contrib_schedule)), "edge"
            )
        else:
            contrib_schedule = contrib_schedule[:months]

    results = []
    for _ in range(trials):
        balance = initial_bal
        path = [balance]
        samples = hist_returns.sample(months, replace=True)

        for i in range(months):
            if use_lc:
                years_left = (months - i) / 12
                alloc = get_lifecycle_allocation(years_left)
            else:
                alloc = manual_alloc

            nom_ret = sum(samples.iloc[i][f] * alloc.get(f, 0) for f in alloc)
            real_ret = (1 + nom_ret) / (1 + monthly_inflation) - 1
            balance = (balance * (1 + real_ret)) + contrib_schedule[i]
            path.append(balance)

        results.append(path)
    return np.array(results)
