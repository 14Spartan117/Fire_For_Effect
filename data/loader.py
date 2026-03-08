"""
Load and query military_data.json for base pay, BAH, and BAS.
"""

import json
from pathlib import Path
import streamlit as st

from config import BAS_OFFICER, BAS_ENLISTED

_DATA_FILE = Path(__file__).resolve().parent.parent / "military_data.json"


@st.cache_data
def load_military_data() -> dict:
    """Load the JSON pay tables. Returns empty structure on failure."""
    try:
        with open(_DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Data file missing: {_DATA_FILE}")
        return {"base_pay": {}, "zip_to_mha": {}, "bah_rates": {}}


# Module-level singleton loaded once on import
DATA = load_military_data()


def get_base_pay(rank: str, tis: float) -> float:
    """Look up base pay for *rank* at *tis* years of service."""
    rank_data = DATA.get("base_pay", {}).get(rank, {})
    if not rank_data:
        return 0.0
    available = sorted(int(k) for k in rank_data.keys())
    snapped = available[0]
    for b in available:
        if tis >= b:
            snapped = b
        else:
            break
    return float(rank_data.get(str(snapped), 0.0))


def get_military_pay(rank: str, tis: float, zip_code: str, has_dep: bool):
    """Return (base, bas, bah) for the given inputs."""
    base = get_base_pay(rank, tis)
    bas = BAS_OFFICER if ("O" in rank or "W" in rank) else BAS_ENLISTED
    zip_info = DATA.get("zip_to_mha", {}).get(zip_code)
    bah = 0.0
    if zip_info:
        mha_code = zip_info["mha"]
        dep_key = "with" if has_dep else "without"
        bah = DATA.get("bah_rates", {}).get(mha_code, {}).get(rank, {}).get(dep_key, 0.0)
    return float(base), float(bas), float(bah)
