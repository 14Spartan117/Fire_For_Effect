"""
Tab 5 -- Way Ahead: Financial Order of Operations
"""

import streamlit as st


def render_tab_action(container):
    with container:
        ss = st.session_state
        ss.tabs_visited.add(5)
        ss.max_tab_reached = max(ss.max_tab_reached, 5)
        st.header("Way Ahead: Your Financial Order of Operations")
        st.write("Gamifying the classic financial order of operations. Expand each step, execute the mission, and check it off.")

        total_steps = 9
        steps_completed = sum(ss.get(f"step_{i}", False) for i in range(1, total_steps + 1))
        progress_pct = int((steps_completed / total_steps) * 100)

        col_pct, col_bar = st.columns([1, 4])
        with col_pct:
            st.metric("Mission Completion", f"{progress_pct}%", f"{steps_completed}/{total_steps} Steps")
        with col_bar:
            st.write("")
            st.write("")
            st.progress(steps_completed / total_steps)

        if steps_completed == total_steps:
            st.balloons()
            st.success(
                "\U0001F389 Outstanding! You have executed the order of operations, "
                "killed your toxic debt, and set your wealth generation on autopilot."
            )

        st.divider()

        # ── Phase 1 ──────────────────────────────────────────────────────────
        st.subheader("Phase 1: Stop the Bleeding (Immediate Action)")
        with st.expander("1. Secure the BRS Match (Free Money)"):
            st.markdown("""
* **The Mission:** If you are in the Blended Retirement System (BRS), the DoD matches up to 5% of your base pay. If you contribute 4%, you are taking a voluntary pay cut.
* **Action Steps:** Log into MyPay. Navigate to the "Traditional/Roth TSP" section. Set your contribution to a minimum of 5% (Roth is usually best for junior/mid-grade ranks due to tax-free allowances).
            """)
            st.checkbox("\u2705 I have secured my 5% BRS Match", key="step_1")

        with st.expander("2. The SCRA Debt Hack"):
            st.markdown("""
* **The Mission:** The Servicemembers Civil Relief Act (SCRA) legally caps interest rates at 6% for any debt you acquired *before* entering active duty.
* **Action Steps:** Identify pre-military credit cards, auto loans, or student loans. Call your lender's specific SCRA department. Submit a copy of your active-duty orders.
            """)
            st.checkbox("\u2705 I have verified my SCRA eligibility and contacted lenders", key="step_2")

        with st.expander("3. Nuke Toxic Debt (The 24% APR Trap)"):
            st.markdown("""
* **The Mission:** You cannot out-invest a 20% credit card or a predatory car loan from outside the gate.
* **Action Steps:** Take the "Surplus" from your Tab 3 budget and route 100% of it toward your highest-interest debt. Use the Avalanche Method (mathematically optimal) or Snowball Method (psychological wins).
            """)
            st.checkbox("\u2705 I have a plan in place to eliminate all debt over 8% APR", key="step_3")

        # ── Phase 2 ──────────────────────────────────────────────────────────
        st.subheader("Phase 2: Build Financial Armor")
        with st.expander("4. Escape the 0.01% Checking Account (HYSA)"):
            st.markdown("""
* **The Mission:** Traditional banks pay you pennies while inflation eats your money. Keep your Emergency Fund in a Higher Yield Option for maximum accessibility *and* high interest (typically 4-5%).
* **Action Steps:** Open a High-Yield Savings Account (HYSA). Set up an auto-transfer. Aim for 3-6 months of your Fixed Costs.
            """)
            st.checkbox("\u2705 My emergency fund is sitting in an HYSA", key="step_4")

        # ── Phase 3 ──────────────────────────────────────────────────────────
        st.subheader("Phase 3: The Engine (Wealth Generation)")
        with st.expander("5. Escape the G-Fund Trap"):
            st.markdown("""
* **The Mission:** If you joined before 2018, your TSP defaulted into the G-Fund (Government Securities). It barely beats inflation.
* **Action Steps:** Move your investments into the C-Fund, S-Fund, I-Fund, or an L-Fund (Lifecycle) that matches your expected retirement year.
            """)
            st.checkbox("\u2705 My TSP is out of the G-Fund and properly invested", key="step_5")

        with st.expander("6. Automate the 'Retirement Gap'"):
            st.markdown("""
* **The Mission:** Tab 2 showed you exactly how much extra you need to invest monthly to hit your FIRE number. Willpower fails; automation doesn't.
* **Action Steps:** 1. Increase your TSP contributions to the percentage that will meet your monthly retirement goals.
    2. **Crucial TSP Step:** Log into TSP.gov. Change your **Contribution Allocation** AND conduct an **Interfund Transfer**.
    3. Alternatively, open a Roth IRA. Set up an auto-draft on the 1st of every month.
            """)
            st.checkbox("\u2705 My required monthly investments are fully automated", key="step_6")

        # ── Phase 4 ──────────────────────────────────────────────────────────
        st.subheader("Phase 4: Military Cheat Codes")
        with st.expander("7. The GI Bill Transfer Trap"):
            st.markdown("""
* **The Mission:** You cannot transfer the Post-9/11 GI Bill as a retirement gift. You must have at least 6 years of service AND commit to serving 4 more years from the date of transfer. You must also have 100% GI Bill eligibility.
* **Action Steps:** The exact day you meet both requirements, log into MilConnect and initiate the transfer.
            """)
            st.checkbox("\u2705 I have transferred my GI Bill (Or decided not to)", key="step_7")

        with st.expander("8. The Deployment Multiplier (SDP)"):
            st.markdown("""
* **The Mission:** If you deploy to a combat zone, the military offers the Savings Deposit Program (SDP), which guarantees a 10% annual return on up to $10,000.
* **Action Steps:** Once you are in theater for 30 days, go to the local finance office and max this out.
            """)
            st.checkbox("\u2705 I am aware of the SDP and will use it if deployed", key="step_8")

        with st.expander("9. VA Loan & The 'Funding Fee' Waiver"):
            st.markdown("""
* **The Mission:** The VA loan allows 0% down, but charges a "Funding Fee" (up to 3.3%). If you have a service-connected disability rating of just **10%**, that fee is completely waived.
* **Action Steps:** Go to medical. Document your back, your knees, and your tinnitus *now*. File your BDD claim 180 days out.
            """)
            st.checkbox("\u2705 I am documenting my medical records for my BDD claim", key="step_9")
