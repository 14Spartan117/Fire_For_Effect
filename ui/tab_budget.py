"""
Tab 3 -- Where Does It Go?  (Conscious spending / budget)
"""

import datetime

import plotly.graph_objects as go
import streamlit as st


def render_tab_budget(container):
    with container:
        ss = st.session_state
        ss.tabs_visited.add(3)
        ss.max_tab_reached = max(ss.max_tab_reached, 3)
        st.header("Step 3: Where Does It Go?")

        special_pay = ss.get("special_pay", 0.0)

        pay_mode = st.radio(
            "Income Mode",
            [
                "\U0001F4CB Using my LES values below",
                (
                    "\U0001F3B2 I'll skip the LES and let an algorithm guess my take-home pay"
                    "--even though it knows nothing about my deductions, allotments, or tax "
                    "situation. Honestly, it'll fit right in with the rest of my planning: "
                    "assumptions, hopes, and vibes."
                ),
            ],
            key="pay_mode_radio",
        )

        st.divider()

        # ── LES Form ─────────────────────────────────────────────────────────
        if "\U0001F4CB" in pay_mode:
            st.subheader("\U0001F5C2\uFE0F Leave & Earnings Statement")
            st.caption(
                "Enter the values directly from your LES. Pull up your LES at "
                "[myPay](https://mypay.dfas.mil) and follow along line by line."
            )

        les_col1, les_col2, les_col3 = st.columns(3)

        with les_col1:
            st.markdown("**ENTITLEMENTS**")
            tab1_base = float(ss.get("base_pay", 0.0))
            tab1_bah = float(ss.get("bah_amt", 0.0))
            tab1_bas = float(ss.get("bas_amt", 0.0))

            if "les_base" not in ss:
                ss["les_base"] = 0.0
            if "les_bah" not in ss:
                ss["les_bah"] = 0.0
            if "les_bas" not in ss:
                ss["les_bas"] = 0.0

            if st.button("\u2B07\uFE0F Import Base Pay / BAH / BAS from Tab 1", key="import_tab1_pay"):
                ss["les_base"] = tab1_base
                ss["les_bah"] = tab1_bah
                ss["les_bas"] = tab1_bas
                st.rerun()

            les_base = st.number_input("Base Pay", min_value=0.0, step=10.0, key="les_base")
            les_bah = st.number_input("BAH", min_value=0.0, step=10.0, key="les_bah")
            les_bas = st.number_input("BAS", min_value=0.0, step=10.0, key="les_bas")

            mismatch_fields = []
            if tab1_base > 0 and abs(les_base - tab1_base) > 1.0:
                mismatch_fields.append(f"Base Pay (calculator: ${tab1_base:,.2f})")
            if tab1_bah > 0 and abs(les_bah - tab1_bah) > 1.0:
                mismatch_fields.append(f"BAH (calculator: ${tab1_bah:,.2f})")
            if tab1_bas > 0 and abs(les_bas - tab1_bas) > 1.0:
                mismatch_fields.append(f"BAS (calculator: ${tab1_bas:,.2f})")

            if mismatch_fields:
                field_names = ", ".join([f.split(" (")[0] for f in mismatch_fields])
                calc_values = ", ".join([f.split("calculator: ")[1].rstrip(")") for f in mismatch_fields])
                st.warning(
                    f"\u26A0\uFE0F The value you entered for **{field_names}** does not match "
                    f"the calculated value ({calc_values}). Check with your S1 if needed."
                )

            if "les_ent_rows" not in ss:
                ss.les_ent_rows = 0
            les_extra_ent = 0.0
            for i in range(ss.les_ent_rows):
                ec1, ec2 = st.columns([2, 1])
                ec1.text_input("Pay Type", key=f"les_ent_name_{i}", placeholder="e.g. Flight Pay")
                les_extra_ent += ec2.number_input("Amount", min_value=0.0, step=10.0, key=f"les_ent_amt_{i}")
            if st.button("\uFF0B Add Entitlement", key="les_add_ent"):
                ss.les_ent_rows += 1
                st.rerun()

            les_tot_ent = les_base + les_bah + les_bas + les_extra_ent
            st.metric("TOT ENT", f"${les_tot_ent:,.2f}")

        with les_col2:
            st.markdown("**DEDUCTIONS**")
            les_fed_tax = st.number_input("Federal Taxes", min_value=0.0, value=0.0, step=10.0, key="les_fed")
            les_fica_ss = st.number_input("FICA - Soc Security", min_value=0.0, value=0.0, step=10.0, key="les_ss")
            les_fica_med = st.number_input("FICA - Medicare", min_value=0.0, value=0.0, step=10.0, key="les_med")
            les_state = st.number_input(
                "State Taxes", min_value=0.0, value=0.0, step=10.0, key="les_state",
                help="Enter 0 if you live in a state with no income tax.",
            )
            les_sgli = st.number_input("SGLI", min_value=0.0, value=0.0, step=1.0, key="les_sgli")
            les_sgli_fam = st.number_input("SGLI Fam/Spouse", min_value=0.0, value=0.0, step=1.0, key="les_sgli_fam")
            les_tsp = st.number_input(
                "TSP Contribution\n(Roth or Traditional)", min_value=0.0, value=0.0, step=10.0, key="les_tsp_input",
                help="Enter your total TSP deduction -- Roth, Traditional, or both combined.",
            )
            les_midmonth = st.number_input(
                "Mid-Month Pay", min_value=0.0, value=0.0, step=10.0, key="les_mid",
                help="Already received on the 15th -- offsets your EOM deposit.",
            )

            if "les_ded_rows" not in ss:
                ss.les_ded_rows = 0
            les_extra_ded = 0.0
            for i in range(ss.les_ded_rows):
                dc1, dc2 = st.columns([2, 1])
                dc1.text_input("Deduction Type", key=f"les_ded_name_{i}", placeholder="e.g. Dental")
                les_extra_ded += dc2.number_input("Amount", min_value=0.0, step=10.0, key=f"les_ded_amt_{i}")
            if st.button("\uFF0B Add Deduction", key="les_add_ded"):
                ss.les_ded_rows += 1
                st.rerun()

            les_tot_ded = (
                les_fed_tax + les_fica_ss + les_fica_med + les_state
                + les_sgli + les_sgli_fam + les_tsp + les_midmonth + les_extra_ded
            )
            st.metric("TOT DED", f"${les_tot_ded:,.2f}")
            ss.les_tsp_actual = les_tsp

        with les_col3:
            st.markdown("**ALLOTMENTS**")
            st.caption("Recurring autopays -- insurance, savings allotments, etc.")

            if "les_almt_rows" not in ss:
                ss.les_almt_rows = 1
            les_tot_almt = 0.0
            for i in range(ss.les_almt_rows):
                ac1, ac2 = st.columns([2, 1])
                ac1.text_input("Allotment", key=f"les_almt_name_{i}", placeholder="e.g. TRICARE Dental")
                les_tot_almt += ac2.number_input("Amount", min_value=0.0, step=10.0, key=f"les_almt_amt_{i}")
            if st.button("\uFF0B Add Allotment", key="les_add_almt"):
                ss.les_almt_rows += 1
                st.rerun()

            st.metric("TOT ALMT", f"${les_tot_almt:,.2f}")
            st.divider()
            st.markdown("**SUMMARY**")
            eom_pay = les_tot_ent - les_tot_ded - les_tot_almt
            mil_takehome = les_midmonth + max(0.0, eom_pay)

            st.metric("TOT ENT", f"${les_tot_ent:,.2f}")
            st.metric("- TOT DED", f"${les_tot_ded:,.2f}")
            st.metric("- TOT ALMT", f"${les_tot_almt:,.2f}")
            st.metric("= EOM PAY", f"${max(0.0, eom_pay):,.2f}")

        if "\U0001F4CB" in pay_mode:
            st.info(
                f"**Mid-Month Pay (${les_midmonth:,.2f}) + EOM Pay (${max(0.0, eom_pay):,.2f}) "
                f"= Total Military Take-Home: ${mil_takehome:,.2f}/month.**"
            )
        else:
            les_midmonth = 0.0
            eom_pay = 0.0
            mil_takehome = 0.0
            les_fed_tax = 0.0
            les_fica_ss = 0.0
            les_fica_med = 0.0
            les_state = 0.0
            les_tot_ent = 0.0

        st.divider()

        # ── Additional Income ─────────────────────────────────────────────────
        st.subheader("\u2795 Additional Income")
        st.write(
            "Add any other income streams below. **All amounts must be after-tax** "
            "-- enter what actually hits your account, not gross."
        )

        if "extra_income_rows" not in ss:
            ss.extra_income_rows = 0
        if st.button("Add Income Stream"):
            ss.extra_income_rows += 1

        total_extra_income = 0.0
        for i in range(ss.extra_income_rows):
            c_name, c_amt, c_freq = st.columns([2, 1, 1])
            with c_name:
                st.text_input("Source Name", key=f"ei_name_{i}", placeholder="e.g. Spouse's Job")
            with c_amt:
                amt = st.number_input("Amount ($)", key=f"ei_amt_{i}", min_value=0.0, step=100.0)
            with c_freq:
                freq = st.selectbox("Frequency", ["Monthly", "Bi-weekly", "Annually"], key=f"ei_freq_{i}")

            if freq == "Monthly":
                monthly_amt = amt
            elif freq == "Bi-weekly":
                monthly_amt = (amt * 26) / 12
            else:
                monthly_amt = amt / 12
            total_extra_income += monthly_amt

        if ss.extra_income_rows > 0:
            if st.button("Clear Extra Income", type="secondary"):
                ss.extra_income_rows = 0
                st.rerun()

        st.divider()

        # ── Take-Home Anchor ──────────────────────────────────────────────────
        if "\U0001F3B2" in pay_mode:
            mil_taxable = ss.base_pay + special_pay
            mil_nontaxable = ss.bah_amt + ss.bas_amt
            # Extra income is entered after-tax, so only mil_taxable drives the tax estimate
            taxable_monthly = mil_taxable
            annual_taxable = taxable_monthly * 12
            std_deduction = 15000
            tax_base = max(0, annual_taxable - std_deduction)
            tax = 0
            if tax_base > 100525:
                tax += (tax_base - 100525) * 0.24
                tax_base = 100525
            if tax_base > 47150:
                tax += (tax_base - 47150) * 0.22
                tax_base = 47150
            if tax_base > 11600:
                tax += (tax_base - 11600) * 0.12
                tax_base = 11600
            if tax_base > 0:
                tax += tax_base * 0.10
            monthly_fed_tax = tax / 12
            monthly_fica = taxable_monthly * 0.0765
            take_home = (
                taxable_monthly - monthly_fed_tax - monthly_fica
                + mil_nontaxable + total_extra_income
            )
            st.caption(
                f"*Estimated Taxes: Federal **${monthly_fed_tax:,.0f}** | "
                f"FICA **${monthly_fica:,.0f}** -- BAH/BAS excluded from tax.*"
            )
        else:
            take_home = mil_takehome + total_extra_income
            monthly_fed_tax = les_fed_tax
            monthly_fica = les_fica_ss + les_fica_med

        st.info(f"\U0001F4B0 Total Combined Monthly Take-Home: **${take_home:,.2f}**")
        st.divider()

        col_a, col_b, col_c = st.columns(3)
        bp = ss.base_pay if ss.base_pay > 0 else (take_home * 0.6)

        with col_a:
            st.subheader("\U0001F6D1 Fixed Costs")
            housing = st.number_input("Housing + Utilities", value=float(ss.bah_amt))
            trans = st.number_input("Car/Insurance/Fuel", value=bp * 0.15)
            health = st.number_input("Healthcare", value=bp * 0.08)
            groceries = st.number_input("Groceries", value=bp * 0.13)
            fixed_total = housing + trans + health + groceries
            fixed_pct = (fixed_total / take_home * 100) if take_home > 0 else 0
            st.metric("Total Fixed", f"${fixed_total:,.2f}", f"{fixed_pct:.1f}%")

        with col_b:
            st.subheader("\U0001F680 Invest/Save")
            retirement = st.number_input("Retirement (TSP/IRA)", value=float(ss.pmt_target))
            emergency = st.number_input("Emergency Savings", value=take_home * 0.05)
            save_invest_total = retirement + emergency
            save_pct = (save_invest_total / take_home * 100) if take_home > 0 else 0
            st.metric("Total Invested", f"${save_invest_total:,.2f}", f"{save_pct:.1f}%")

        with col_c:
            st.subheader("\U0001F379 Guilt-Free")
            available_for_fun = max(0.0, take_home - fixed_total - save_invest_total)

            experiences = st.number_input("Experiences (Travel, Events)", min_value=0.0, value=0.0, step=50.0)
            convenience = st.number_input("Convenience (Delivery, Time-savers)", min_value=0.0, value=0.0, step=50.0)
            hobbies = st.number_input("Hobbies (Gear, Gym, Gaming)", min_value=0.0, value=0.0, step=50.0)
            personal = st.number_input("Personal (Clothes, Grooming)", min_value=0.0, value=0.0, step=50.0)
            entertainment = st.number_input("Entertainment (Dining Out, Bars)", min_value=0.0, value=0.0, step=50.0)
            generosity = st.number_input("Generosity (Gifts, Donations)", min_value=0.0, value=0.0, step=50.0)

            fun_total = experiences + convenience + hobbies + personal + entertainment + generosity
            fun_pct = (fun_total / take_home * 100) if take_home > 0 else 0
            remaining = available_for_fun - fun_total

            st.divider()
            if remaining > 0.005:
                st.success(f"**Remaining to allocate: ${remaining:,.2f}**")
            elif remaining >= -0.005:
                st.success("**Fully allocated. Nothing left on the table. \u2705**")
            else:
                st.error(f"**Over-allocated by ${abs(remaining):,.2f} -- trim a category above.**")

            st.metric("Guilt-Free Total", f"${fun_total:,.2f}", f"{fun_pct:.1f}% of take-home")

        # ── Sankey ────────────────────────────────────────────────────────────
        if "\U0001F3B2" in pay_mode:
            sankey_tax = monthly_fed_tax + monthly_fica
            sankey_gross = mil_taxable + mil_nontaxable + total_extra_income
        else:
            sankey_tax = les_fed_tax + les_fica_ss + les_fica_med + les_state
            sankey_gross = les_tot_ent + total_extra_income

        invest_total = save_invest_total
        guilt_free_total = fun_total
        surplus_amt = take_home - (fixed_total + invest_total + guilt_free_total)

        ss.tab3_take_home = take_home
        ss.tab3_fixed = fixed_total
        ss.tab3_invested = invest_total
        ss.tab3_guilt_free = guilt_free_total

        st.divider()
        st.subheader(f"\U0001F4CA Your {datetime.date.today().year} Monthly Cash Flow Architecture")

        nodes = ["Gross Income", "Taxes", "Take-Home Pay", "Fixed Costs",
                 "Investments", "Guilt-Free", "Surplus"]
        links = {
            "source": [0, 0, 2, 2, 2, 2],
            "target": [1, 2, 3, 4, 5, 6],
            "value": [
                max(0.1, sankey_tax), max(0.1, take_home), max(0.1, fixed_total),
                max(0.1, invest_total), max(0.1, guilt_free_total), max(0.1, surplus_amt),
            ],
            "color": [
                "rgba(200,200,200,0.4)", "rgba(0,212,255,0.4)", "rgba(255,99,132,0.5)",
                "rgba(75,192,192,0.5)", "rgba(255,206,86,0.5)", "rgba(0,255,127,0.7)",
            ],
        }

        fig = go.Figure(data=[go.Sankey(
            node=dict(pad=15, thickness=20, label=nodes, color="#00D4FF"),
            link=links,
        )])
        fig.update_layout(
            font=dict(color="white", size=12), paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", template="plotly_dark", height=600,
            margin=dict(l=10, r=10, t=40, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

        if surplus_amt < -5:
            st.error(f"\u26A0\uFE0F **Budget Deficit:** Over-allocated by **${abs(surplus_amt):,.2f}**.")
        elif surplus_amt > 5:
            st.success(f"\u2705 **Budget Surplus:** You have **${surplus_amt:,.2f}** unallocated.")
