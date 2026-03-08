"""
Anonymous session analytics via Google Sheets.
"""

import datetime
import hashlib
import json

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

from config import SHEET_ID

HEADER_ROW = [
    "timestamp", "anon_id", "zip", "device_type",
    "session_duration_seconds", "tabs_visited", "max_tab_reached",
    "monte_carlo_run", "quiz_score", "pdf_downloaded",
    "bounced", "error_event",
]


@st.cache_resource
def get_gsheet():
    """Return a gspread worksheet or None on failure."""
    try:
        raw = st.secrets["gcp_service_account"]
        creds_dict = json.loads(raw) if isinstance(raw, str) else dict(raw)
        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID).sheet1
        if sheet.row_count == 0 or sheet.cell(1, 1).value != "timestamp":
            sheet.append_row(HEADER_ROW)
        return sheet
    except Exception:
        return None


def get_anon_id() -> str:
    try:
        ua = st.context.headers.get("User-Agent", "")
        raw = ua + st.context.headers.get("Accept-Language", "")
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
    except Exception:
        return "unknown"


def get_device_type() -> str:
    try:
        ua = st.context.headers.get("User-Agent", "").lower()
        if any(x in ua for x in ["iphone", "android", "mobile", "ipad"]):
            return "mobile"
        return "desktop"
    except Exception:
        return "unknown"


def log_session():
    """Write one row of anonymous analytics to the Google Sheet."""
    try:
        sheet = get_gsheet()
        if sheet is None:
            return
        ss = st.session_state
        elapsed = (datetime.datetime.now() - ss.session_start).seconds
        bounced = 1 if (elapsed < 60 and ss.max_tab_reached <= 1) else 0
        sheet.append_row([
            datetime.datetime.now().isoformat(),
            ss.anon_id,
            ss.tracked_zip,
            ss.device_type,
            elapsed,
            len(ss.tabs_visited),
            ss.max_tab_reached,
            1 if ss.monte_carlo_run else 0,
            ss.quiz_score,
            1 if ss.pdf_downloaded else 0,
            bounced,
            ss.last_error or "",
        ])
    except Exception:
        pass


def log_error(error_msg: str):
    st.session_state.last_error = str(error_msg)[:200]
