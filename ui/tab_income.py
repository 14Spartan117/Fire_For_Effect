"""
Tab 1 -- What Do You Make?
"""

import streamlit as st

from config import RANKS
from data import get_military_pay, DATA


def render_tab_income(container):
    with container:
        ss = st.session_state
        ss.tabs_visited.add(1)
        ss.max_tab_reached = max(ss.max_tab_reached, 1)
        st.header("Step 1: What You Make")

        col1, col2 = st.columns(2)
        with col1:
            rank = st.selectbox("Current Rank", RANKS, index=4, key="tab1_rank_widget")
            tis = st.number_input("Years of Service (TIS)", 0, 40, 4)
        with col2:
            zip_code = st.text_input("Duty Station Zip Code", "92136")
            dep = st.checkbox("With Dependents?", value=True)
            ss.tracked_zip = zip_code

        # ── Optional special / incentive pays ─────────────────────────────────
        with st.expander("\U0001F396\uFE0F Optional Special / Incentive Pays (Monthly)"):
            sp1, sp2 = st.columns(2)
            with sp1:
                hdip_static = st.checkbox("HDIP: Parachute (Static Line) (+$150)")
                hdip_mff = st.checkbox("HDIP: Military Free Fall / HALO (+$225)")
                hdip_demo = st.checkbox("HDIP: Demolition (+$150)")
            with sp2:
                hfp_idp = st.checkbox("Hostile Fire / Imminent Danger Pay (up to +$225)")
                flpb_on = st.checkbox("Foreign Language Proficiency Bonus (FLPB)")
                avip_on = st.checkbox("Aviation Incentive Pay (Army Officer AvIP)")

            flpb_amt = 0
            if flpb_on:
                flpb_amt = st.number_input(
                    "FLPB monthly amount (enter your known amount from orders/LES)",
                    min_value=0, max_value=1000, value=0, step=50,
                )

            avip_amt = 0
            if avip_on:
                yas = st.number_input(
                    "Years of Aviation Service (YAS)",
                    min_value=0.0, max_value=40.0, value=2.0, step=0.5,
                )
                if yas <= 2:
                    avip_amt = 125
                elif yas <= 6:
                    avip_amt = 200
                elif yas <= 10:
                    avip_amt = 700
                elif yas <= 22:
                    avip_amt = 1000
                elif yas <= 24:
                    avip_amt = 700
                else:
                    avip_amt = 400

            dive_on = st.checkbox("Diving Duty Pay")
            dive_amt = 0
            if dive_on:
                dive_category = st.selectbox("Dive category (Army)", [
                    "Under instruction at approved dive school ($110)",
                    "Combat Diver ($215)",
                    "Diver Second Class ($150)",
                    "Salvage Diver ($175)",
                    "Diver First Class ($215)",
                    "Master Diver ($340)",
                    "Officer: Marine Diving Officer ($240)",
                    "Officer: Diving Medical Officer ($215)",
                ])
                dive_map = {
                    "Under instruction at approved dive school ($110)": 110,
                    "Combat Diver ($215)": 215,
                    "Diver Second Class ($150)": 150,
                    "Salvage Diver ($175)": 175,
                    "Diver First Class ($215)": 215,
                    "Master Diver ($340)": 340,
                    "Officer: Marine Diving Officer ($240)": 240,
                    "Officer: Diving Medical Officer ($215)": 215,
                }
                dive_amt = dive_map.get(dive_category, 0)

            sdap_on = st.checkbox("Special Duty Assignment Pay (SDAP) (Recruiter/Drill/etc.)")
            sdap_amt = 0
            if sdap_on:
                sdap_amt = st.number_input(
                    "SDAP monthly amount", min_value=0, max_value=1000, value=0, step=25,
                )

        special_pay = 0
        if hdip_static:
            special_pay += 150
        if hdip_mff:
            special_pay += 225
        if hdip_demo:
            special_pay += 150
        if hfp_idp:
            special_pay += 225
        special_pay += flpb_amt
        special_pay += avip_amt
        special_pay += dive_amt
        special_pay += sdap_amt

        st.divider()

        # ── Calculate pay ─────────────────────────────────────────────────────
        zip_found = DATA.get("zip_to_mha", {}).get(zip_code) is not None

        if zip_found:
            base, bas, bah = get_military_pay(rank, tis, zip_code, dep)
            ss.bah_manual = False
        else:
            base, bas, _ = get_military_pay(rank, tis, "92136", dep)
            st.warning(
                f"\u26A0\uFE0F Zip code **{zip_code}** was not found in the BAH database. "
                "Make sure you're entering your **duty station** zip code, not your home address. "
                "If your zip is correct and still not found, enter your BAH manually below."
            )
            bah = st.number_input(
                "Manual BAH Entry ($/month)", min_value=0.0, step=50.0, key="manual_bah_input"
            )
            ss.bah_manual = True

        ss.base_pay = base
        ss.bas_amt = bas
        ss.bah_amt = bah
        ss.special_pay = special_pay
        ss.tab1_rank = rank
        ss.tab1_tis = tis

        gross = base + bas + bah + special_pay
        annual_gross = gross * 12

        col_monthly, col_annual = st.columns(2)
        with col_monthly:
            st.info(f"### \U0001F5D3\uFE0F Monthly Gross\n# ${gross:,.2f}")
        with col_annual:
            st.success(f"### \U0001F4B0 Annual Gross\n# ${annual_gross:,.2f}")

        st.write("")
        c_a, c_b, c_c, c_d = st.columns(4)
        c_a.metric("Base Pay", f"${base:,.2f}")
        c_b.metric("BAH (Tax-Free)", f"${bah:,.2f}")
        c_c.metric("BAS (Tax-Free)", f"${bas:,.2f}")
        c_d.metric("Special Pays", f"${special_pay:,.2f}")
