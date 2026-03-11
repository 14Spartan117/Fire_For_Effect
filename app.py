"""
F.I.R.E. for Effect -- main Streamlit entry point.

Run with:  streamlit run app.py
"""

import streamlit as st

from config import PAGE_CONFIG
from analytics import log_session
from ui import (
    init_session_state,
    render_consent_screen,
    render_tab_income,
    render_tab_retirement,
    render_tab_budget,
    render_tab_quiz,
    render_tab_action,
    render_tab_feedback,
    render_tab_plan,
    render_tab_rent_vs_buy,
)

# --- Page config (must be first Streamlit call) ---
st.set_page_config(**PAGE_CONFIG)

# --- Session state ---
init_session_state()

# --- Consent gate ---
render_consent_screen()

# --- App shell ---
st.title("\U0001F396\uFE0F F.I.R.E. for Effect: Financial Planning for Soldiers")
st.caption("Finance is boring. Do it once, get it right, and move on.")
st.markdown("---")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "\U0001F4B0 What Do You Make?",
    "\U0001F4C8 How Much Do You Need to Save?",
    "\U0001F4B8 Where Does It Go?",
    "\U0001F3AF Know the Game",
    "\u2705 The Way Ahead",
    "\U0001F4C4 Your Plan",
    "\U0001F4EC Feedback",
    "\U0001F3E0 Rent vs. Buy",
])

render_tab_income(tab1)
render_tab_retirement(tab2)
render_tab_budget(tab3)
render_tab_quiz(tab4)
render_tab_action(tab5)
render_tab_plan(tab6)
render_tab_feedback(tab7)
render_tab_rent_vs_buy(tab8)

# --- Log session on exit (if not already logged via PDF download) ---
if not st.session_state.session_logged:
    st.session_state.session_logged = True
    log_session()

# --- Global footer ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; font-size: 0.85em; color: gray;'>
<b>Disclaimer:</b> This tool is for educational purposes only. I am not a financial advisor --
but financial literacy isn't reserved for people with CFP after their name. Purposeful scrolling
through r/personalfinance and r/MilitaryFinance, clicking some links, and reading for a weekend
will get you further than you can possibly imagine. Where applicable, model assumptions are
documented in the expandable sections throughout the app. Take charge of your money and own your
future -- the return on investment is 100%. Oh, and I'll take a smash burger with sauteed jalapenos
and a cup that's 90% seltzer water with a splash of Coke.
</div>
""", unsafe_allow_html=True)
