# --- TAB 5: ACTION PLAN ---
with tab5:
    st.header("Step 5: Your Custom Action Plan (The Flowchart)")
    st.write("We merged the legendary personal finance flowchart with military-specific 'cheat codes'. Knock these out in order from top to bottom!")
    
    # Grab the numbers generated in Tabs 2 & 3
    pmt = st.session_state.pmt_target
    f_total = fixed_total if 'fixed_total' in locals() else 0.0
    g_free = fun_total if 'fun_total' in locals() else 0.0

    st.subheader("Phase 0: The Baseline")
    st.checkbox(f"1. Create a Budget: You already did this in Step 3! Your fixed costs are **\\${f_total:,.2f}** and guilt-free spending is **\\${g_free:,.2f}**.", value=True, key="step1")
    st.checkbox("2. The SCRA Check: Call lenders for any debt you had BEFORE joining and legally cap your interest rate at 6%.", key="step2")
    st.checkbox("3. Starter Emergency Fund: Stash \\$1,000 to 1 month of living expenses in a High-Yield Savings Account (HYSA).", key="step3")

    st.subheader("Phase 1: The Match & Toxic Debt")
    st.checkbox("4. Get Your Free Money (BRS Match): Log into MyPay and ensure your TSP is set to at least 5%. Never leave this money on the table.", key="step4")
    st.checkbox("5. Nuke High-Interest Debt: Aggressively pay off credit cards and high-rate car loans (over 8%). Use the [Avalanche](https://www.investopedia.com/terms/d/debt-avalanche.asp) or [Snowball](https://www.investopedia.com/articles/personal-finance/080716/debt-avalanche-vs-debt-snowball-which-best-you.asp) method.", key="step5")

    st.subheader("Phase 2: Financial Armor")
    st.checkbox("6. Fully Funded Emergency Fund: Build that HYSA up to cover 3 to 6 months of essential living expenses.", key="step6")
    st.checkbox("7. Deployment Hack (If Applicable): If deploying to a combat zone, max out the Savings Deposit Program (SDP) for a guaranteed 10% return before investing elsewhere.", key="step7")

    st.subheader("Phase 3: Retirement & Wealth Building")
    st.checkbox("8. Evaluate Roth vs. Traditional: For most junior/mid-grade military, Roth TSP/IRA wins because your allowances (BAH/BAS) aren't taxed.", key="step8")
    st.checkbox(f"9. Bridge the Retirement Gap: Set up an allotment or auto-transfer of **\\${pmt:,.2f} / month** to hit your specific retirement goal.", key="step9")
    st.checkbox("10. Push for 15%+: Increase your TSP contributions until you are saving at least 15% of your total pay for retirement.", key="step10")

    st.subheader("Phase 4: Advanced Goals")
    st.checkbox("11. Education & Kids: Use Tuition Assistance (TA) for yourself, and transfer the Post-9/11 GI Bill to dependents BEFORE funding a 529 college savings plan.", key="step11")
    st.checkbox("12. Immediate Goals & Real Estate: Save cash for upcoming PCS expenses, a reliable vehicle, or a house (Even with the 0% down VA Loan, you still need cash for closing costs!).", key="step12")

    # --- PROGRESS BAR LOGIC ---
    st.divider()
    
    # Count how many checkboxes are True in the session state
    steps_completed = sum([st.session_state.get(f"step{i}", False) for i in range(1, 13)])
    progress_pct = int((steps_completed / 12.0) * 100)
    
    col_pct, col_bar = st.columns([1, 4])
    with col_pct:
        st.metric("Flowchart Completion", f"{progress_pct}%")
    with col_bar:
        st.write("") # Spacing to align with metric
        st.write("")
        st.progress(progress_pct / 100.0)
    
    if progress_pct == 100:
        st.balloons()
        st.success("🎉 Outstanding! You have conquered the flowchart, paid off your toxic debt, and set your investments on autopilot.")
