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
        st.write(
            "Gamifying the classic financial order of operations. "
            "Expand each step, execute the mission, and check it off."
        )

        total_steps = 11
        steps_completed = sum(
            ss.get(f"step_{i}", False) for i in range(1, total_steps + 1)
        )
        progress_pct = int((steps_completed / total_steps) * 100)

        col_pct, col_bar = st.columns([1, 4])
        with col_pct:
            st.metric(
                "Mission Completion",
                f"{progress_pct}%",
                f"{steps_completed}/{total_steps} Steps",
            )
        with col_bar:
            st.write("")
            st.write("")
            st.progress(steps_completed / total_steps)

        if steps_completed == total_steps:
            st.balloons()
            st.success(
                "Outstanding! You have executed the order of operations, "
                "killed your toxic debt, and set your wealth generation on autopilot."
            )

        st.divider()

        # ── CRAWL (Do simultaneously) ──────────────────────────────────
        st.subheader("CRAWL: Stop the Bleeding (Do Simultaneously)")

        with st.expander("1. Get Access to Your Money & Secure the BRS Match"):
            st.markdown("""
* **The Mission:** If you are in the Blended Retirement System (BRS), the DoD matches up to 5% of your base pay. If you contribute 4%, you are taking a voluntary pay cut.
* **Action Steps:**
    1. Log into [MyPay](https://mypay.dfas.mil). Navigate to the "Traditional/Roth TSP" section.
    2. Set your contribution to a **minimum of 5%** (Roth is usually best for junior/mid-grade ranks due to tax-free allowances).
    3. Set up a [TSP.gov](https://www.tsp.gov) account if you haven't already.
            """)
            st.checkbox("I have secured my 5% BRS Match", key="step_1")

        with st.expander("2. Open a High-Yield Savings Account (HYSA) & Get to $1,000"):
            st.markdown("""
* **The Mission:** Traditional banks pay you pennies while inflation eats your money. A HYSA gives you 4-5% APY with full accessibility.
* **Action Steps:**
    1. Open a HYSA (SoFi, Marcus, Ally, etc.)
    2. Set up an auto-transfer from your checking on every payday.
    3. Get to $1,000 as fast as possible -- this is your starter emergency fund.
            """)
            st.checkbox("My emergency fund is in an HYSA with at least $1,000", key="step_2")

        with st.expander("3. The SCRA Debt Hack"):
            st.markdown("""
* **The Mission:** The Servicemembers Civil Relief Act (SCRA) legally caps interest rates at **6%** for any debt you acquired *before* entering active duty.
* **Action Steps:**
    1. Identify pre-military credit cards, auto loans, or student loans.
    2. Call your lender's specific SCRA department.
    3. Submit a copy of your active-duty orders.
* Not all lenders are proactive about this -- you may need to push. Some will even **refund** interest already charged above 6%.
            """)
            st.checkbox("I have verified my SCRA eligibility and contacted lenders", key="step_3")

        with st.expander("4. Nuke Toxic Debt (The 24% APR Trap)"):
            st.markdown("""
* **The Mission:** You cannot out-invest a 20% credit card or a predatory car loan from outside the gate.
* **Action Steps:**
    1. Take the "Surplus" from your Tab 3 budget and route **100%** of it toward your highest-interest debt.
    2. Use the **Avalanche Method** (mathematically optimal) or **Snowball Method** (psychological wins).
    3. Once all debt above 8% is gone, redirect that cash flow to investments.
            """)
            st.checkbox("I have a plan to eliminate all debt over 8% APR", key="step_4")

        # ── WALK (In order) ────────────────────────────────────────────
        st.subheader("WALK: Build the Foundation (In Order)")

        with st.expander("5. Full Emergency Fund (3-6 Months of Fixed Costs)"):
            st.markdown("""
* **The Mission:** $1,000 was the starter -- now build the real thing. Target 3-6 months of your fixed costs from Tab 3.
* **Action Steps:**
    1. Keep it in your HYSA.
    2. Auto-transfer every month until you hit target.
    3. Do NOT invest this money -- it's insurance, not an investment.
            """)
            st.checkbox("My emergency fund covers 3-6 months of fixed costs", key="step_5")

        with st.expander("6. Escape the G-Fund Trap & Set Your Allocation"):
            st.markdown("""
* **The Mission:** If you joined before 2018, your TSP defaulted into the **G-Fund** (Government Securities). It barely beats inflation.
* **Action Steps:**
    1. Log into [TSP.gov](https://www.tsp.gov).
    2. Change your **Contribution Allocation** (where new money goes).
    3. Conduct an **Interfund Transfer** (moves existing balance).
    4. Target C/S/I-Fund mix or an L-Fund matching your expected retirement year.
            """)
            st.checkbox("My TSP is out of the G-Fund and properly invested", key="step_6")

        with st.expander("7. Automate Your Savings Rate in MyPay"):
            st.markdown("""
* **The Mission:** Tab 2 showed you exactly how much extra you need to invest monthly to hit your FIRE number. Willpower fails; automation doesn't.
* **Action Steps:**
    1. Increase your TSP contributions to the percentage from Tab 2.
    2. If TSP is maxed, open a Roth IRA and auto-draft on the 1st of every month.
    3. After every promotion -- increase savings rate, not spending.
            """)
            st.checkbox("My required monthly investments are fully automated", key="step_7")

        # ── RUN (After Walk is solid) ──────────────────────────────────
        st.subheader("RUN: Military Cheat Codes (After Walk Is Solid)")

        with st.expander("8. Paperwork: Will, POA, SGLI, TSP Beneficiary"):
            st.markdown("""
* **The Mission:** Nobody wants to think about this, but if something happens, your family needs to be protected.
* **Action Steps:**
    1. **JAG Will:** Visit your installation's legal office. Free for all service members.
    2. **Power of Attorney:** Designate someone to handle your finances if you're incapacitated.
    3. **SGLI Beneficiary:** Verify at [milConnect](https://milconnect.dmdc.osd.mil).
    4. **TSP Beneficiary:** Verify at [TSP.gov](https://www.tsp.gov) -- this is separate from SGLI.
            """)
            st.checkbox("My will, POA, SGLI, and TSP beneficiaries are current", key="step_8")

        with st.expander("9. The GI Bill Transfer Window"):
            st.markdown("""
* **The Mission:** You cannot transfer the Post-9/11 GI Bill as a retirement gift. You must have at least **6 years of service** AND commit to serving **4 more years** from the date of transfer.
* **Action Steps:**
    1. The exact day you meet both requirements, log into [MilConnect](https://milconnect.dmdc.osd.mil) and initiate the transfer.
    2. If you wait until year 18, you'll be obligated until year 22 -- plan accordingly.
    3. ROTC and academy service obligations can complicate eligibility -- check with your education center.
            """)
            st.checkbox("I have transferred my GI Bill (or have a date planned)", key="step_9")

        with st.expander("10. VA Benefits & BDD Claim Before Separation"):
            st.markdown("""
* **The Mission:** The VA provides healthcare, disability compensation, education, home loans, and more -- but you need to document and file *before* you separate.
* **Action Steps:**
    1. **Document everything now.** Go to sick call for your back, knees, hearing, mental health -- all of it.
    2. **File a BDD (Benefits Delivery at Discharge) claim** 180 days before your separation date.
    3. A **10%+ disability rating** waives the VA loan funding fee (saves thousands).
    4. Review the full VA benefits catalog at [va.gov](https://www.va.gov).
            """)
            st.checkbox("I am documenting medical records and plan to file BDD", key="step_10")

        with st.expander("11. Build Beyond: FIRE, Real Estate, & Goal-Based Saving"):
            st.markdown("""
* **The Mission:** If you've made it here, you are ahead of 95% of your peers. Now it's time to think bigger.
* **Explore:**
    1. **FIRE (Financial Independence, Retire Early):** Your military pension is a head start most civilians would kill for. [r/financialindependence](https://www.reddit.com/r/financialindependence/)
    2. **Real Estate:** The VA loan lets you buy with 0% down. Live in it, PCS, rent it out. Repeat. Check the Rent vs. Buy tab. [BiggerPockets](https://www.biggerpockets.com/)
    3. **SBA Boots to Business:** Free entrepreneurship training for transitioning service members. [sba.gov/bootstobusiness](https://www.sba.gov/bootstobusiness)
    4. **The Deployment Multiplier (SDP):** If deployed to a combat zone, the Savings Deposit Program guarantees **10% annual return** on up to $10,000. Max it out at your local finance office after 30 days in theater.
            """)
            st.checkbox("I am actively building beyond the basics", key="step_11")
