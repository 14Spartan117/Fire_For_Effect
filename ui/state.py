"""
Initialise all persistent session-state keys.
"""

import datetime
import streamlit as st

from analytics import get_anon_id, get_device_type


def init_session_state():
    """Call once at app start to guarantee every key exists."""

    # ── Financial state ───────────────────────────────────────────────────────
    _defaults = {
        "tab1_rank": "E-5",
        "tab1_tis": 4.0,
        "base_pay": 0.0,
        "bah_amt": 0.0,
        "bas_amt": 0.0,
        "pmt_target": 0.0,
        "savings_rate_pct": 0.0,
        "nest_egg_target": 0.0,
        "est_pension": 0.0,
        "mc_success_rate": None,
        "tab3_take_home": 0.0,
        "tab3_fixed": 0.0,
        "tab3_invested": 0.0,
        "tab3_guilt_free": 0.0,
        "bah_manual": False,
        "les_tsp_actual": 0.0,
        "special_pay": 0.0,
        # Monte Carlo simulation results (populated in tab_retirement)
        "sim_results": None,
        "sim_savings_pct": 0.0,
        "sim_current_age": 0,
        "sim_age_at_retire": 0,
        "sim_target": 0.0,
        "sim_data_source": None,
    }

    # ── Analytics state ───────────────────────────────────────────────────────
    _analytics = {
        "consent_given": False,
        "session_start": datetime.datetime.now(),
        "anon_id": get_anon_id(),
        "device_type": get_device_type(),
        "tabs_visited": set(),
        "max_tab_reached": 0,
        "tracked_zip": "",
        "monte_carlo_run": False,
        "quiz_score": None,
        "pdf_downloaded": False,
        "last_error": "",
        "session_logged": False,
    }

    for k, v in {**_defaults, **_analytics}.items():
        if k not in st.session_state:
            st.session_state[k] = v
