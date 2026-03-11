"""
Tab 8 -- Rent vs. Buy Calculator
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config import RANKS
from data import get_military_pay


def render_tab_rent_vs_buy(container):
    with container:
        ss = st.session_state
        ss.tabs_visited.add(8)
        ss.max_tab_reached = max(ss.max_tab_reached, 8)

        st.header("Should You Rent or Buy?")
        st.caption(
            "This calculator is built around your BAH. It tells you the true cost of buying vs. renting, "
            "what equity you actually build, and -- if you plan to rent it out later -- what your real return looks like."
        )

        # ── SECTION 1: BAH LOOKUP ────────────────────────────────────────
        st.subheader("Step 1: Your BAH")
        col_r1, col_r2, col_r3, col_r4 = st.columns(4)
        with col_r1:
            default_rank_idx = RANKS.index(ss.get("tab1_rank", "O-3")) if ss.get("tab1_rank", "O-3") in RANKS else 14
            rvb_rank = st.selectbox("Rank", RANKS, index=default_rank_idx, key="rvb_rank")
        with col_r2:
            rvb_zip = st.text_input("Duty Station ZIP", value=ss.get("tracked_zip", ""), key="rvb_zip")
        with col_r3:
            rvb_dep = st.radio("Dependents", ["With", "Without"], horizontal=True, key="rvb_dep")
        with col_r4:
            rvb_tis = st.number_input("Years of Service", min_value=0, max_value=30, value=4, key="rvb_tis")

        rvb_has_dep = (rvb_dep == "With")
        _, _, rvb_bah_auto = get_military_pay(rvb_rank, rvb_tis, rvb_zip, rvb_has_dep)

        if rvb_bah_auto > 0:
            st.success(
                f"BAH for **{rvb_rank}** at ZIP **{rvb_zip}** "
                f"({'w/' if rvb_has_dep else 'w/o'} dependents): **${rvb_bah_auto:,.0f}/month**"
            )
            rvb_bah = rvb_bah_auto
        else:
            st.warning(f"ZIP **{rvb_zip}** not found -- enter BAH manually.")
            rvb_bah = st.number_input(
                "Your Monthly BAH ($/month)", min_value=0.0, step=50.0,
                value=2000.0, key="rvb_bah_manual",
            )

        st.divider()

        # ── SECTION 2: PROPERTY & LOAN INPUTS ────────────────────────────
        st.subheader("Step 2: The Property & Loan")
        col_p1, col_p2 = st.columns(2)

        with col_p1:
            rvb_home_price = st.number_input(
                "Home Price ($)", min_value=50_000, max_value=2_000_000,
                value=350_000, step=5_000, key="rvb_price",
            )
            rvb_market_rent = st.number_input(
                "Market Rent for Comparable Home ($/month)",
                min_value=500, max_value=10_000,
                value=int(rvb_bah * 0.95) if rvb_bah > 0 else 2000,
                step=50, key="rvb_mkt_rent",
            )
            rvb_years_stay = st.slider(
                "How Long Do You Plan to Stay? (years)", 1, 15, 3, key="rvb_stay",
            )

        with col_p2:
            rvb_va_loan = st.toggle("VA Loan (0% down, no PMI)", value=True, key="rvb_va")
            if rvb_va_loan:
                rvb_down_pct = 0.0
                st.caption(
                    "VA loan: no down payment, no PMI. A 2.15% funding fee is "
                    "rolled into the loan (first use, not disabled)."
                )
                rvb_funding_fee_pct = 0.0215
            else:
                rvb_down_pct = st.slider("Down Payment (%)", 3, 25, 10, key="rvb_down") / 100
                rvb_funding_fee_pct = 0.0

            rvb_rate = st.number_input(
                "Interest Rate (%)", min_value=2.0, max_value=12.0,
                value=6.75, step=0.05, format="%.2f", key="rvb_rate",
            ) / 100

        st.divider()

        # ── SECTION 3: ADJUSTABLE ASSUMPTIONS ────────────────────────────
        with st.expander("Adjust Assumptions (click to customize -- defaults are conservative baselines)"):
            col_a1, col_a2, col_a3 = st.columns(3)
            with col_a1:
                rvb_appreciation = st.slider(
                    "Annual Home Appreciation (%)", 0.0, 8.0, 3.0, 0.25, key="rvb_appr",
                ) / 100
                rvb_prop_tax_rate = st.slider(
                    "Property Tax Rate (% of value/yr)", 0.5, 3.0, 1.1, 0.05, key="rvb_ptax",
                ) / 100
                rvb_maint_rate = st.slider(
                    "Maintenance (% of value/yr)", 0.5, 2.0, 1.0, 0.1, key="rvb_maint",
                ) / 100
            with col_a2:
                rvb_insurance_mo = st.number_input(
                    "Home Insurance ($/month)", 50, 500, 120, 10, key="rvb_ins",
                )
                rvb_hoa_mo = st.number_input(
                    "HOA ($/month, 0 if none)", 0, 1000, 0, 25, key="rvb_hoa",
                )
                rvb_pmi_rate = 0.0 if rvb_va_loan else (
                    st.slider("PMI Rate (% of loan/yr)", 0.2, 1.5, 0.5, 0.05, key="rvb_pmi") / 100
                    if rvb_down_pct < 0.20 else 0.0
                )
            with col_a3:
                rvb_buy_closing = st.slider(
                    "Buying Closing Costs (%)", 1.0, 5.0, 3.0, 0.25, key="rvb_bclose",
                ) / 100
                rvb_sell_closing = st.slider(
                    "Selling Closing Costs (%)", 4.0, 8.0, 6.0, 0.25, key="rvb_sclose",
                ) / 100
                rvb_rent_increase = st.slider(
                    "Annual Rent Increase (%)", 0.0, 6.0, 3.0, 0.25, key="rvb_renti",
                ) / 100
                rvb_invest_return = st.slider(
                    "Investment Return on Down Payment if Renting (%)",
                    3.0, 10.0, 7.0, 0.25, key="rvb_inv",
                ) / 100

        # ── CALCULATIONS ─────────────────────────────────────────────────
        rvb_down_amt = rvb_home_price * rvb_down_pct
        rvb_funding_fee = (rvb_home_price * rvb_funding_fee_pct) if rvb_va_loan else 0.0
        rvb_loan_amt = rvb_home_price - rvb_down_amt + rvb_funding_fee
        rvb_monthly_rate = rvb_rate / 12
        rvb_n_payments = 360  # 30-year

        if rvb_monthly_rate > 0:
            rvb_mortgage_pi = rvb_loan_amt * (
                rvb_monthly_rate * (1 + rvb_monthly_rate) ** rvb_n_payments
            ) / ((1 + rvb_monthly_rate) ** rvb_n_payments - 1)
        else:
            rvb_mortgage_pi = rvb_loan_amt / rvb_n_payments

        rvb_prop_tax_mo = (rvb_home_price * rvb_prop_tax_rate) / 12
        rvb_maint_mo = (rvb_home_price * rvb_maint_rate) / 12
        rvb_pmi_mo = (rvb_loan_amt * rvb_pmi_rate) / 12
        rvb_total_own_mo = (
            rvb_mortgage_pi + rvb_prop_tax_mo + float(rvb_insurance_mo)
            + rvb_maint_mo + float(rvb_hoa_mo) + rvb_pmi_mo
        )
        rvb_buy_closing_cost = rvb_home_price * rvb_buy_closing

        # Month-by-month simulation
        n_months = rvb_years_stay * 12
        balance = rvb_loan_amt
        total_interest = 0.0
        total_principal = 0.0
        total_buy_costs = rvb_buy_closing_cost + rvb_down_amt

        rent_mo = float(rvb_market_rent)
        total_rent_paid = 0.0
        invest_balance = rvb_down_amt + rvb_buy_closing_cost

        monthly_costs_buy = []
        monthly_costs_rent = []

        for m in range(n_months):
            interest_portion = balance * rvb_monthly_rate
            principal_portion = rvb_mortgage_pi - interest_portion
            balance -= principal_portion
            total_interest += interest_portion
            total_principal += principal_portion

            total_rent_paid += rent_mo
            invest_balance *= (1 + rvb_invest_return / 12)
            if m % 12 == 11:
                rent_mo *= (1 + rvb_rent_increase)

            monthly_costs_buy.append(rvb_total_own_mo)
            monthly_costs_rent.append(rent_mo)

        # End-of-stay values
        rvb_home_value_end = rvb_home_price * (1 + rvb_appreciation) ** rvb_years_stay
        rvb_equity_end = rvb_home_value_end - balance
        rvb_sell_cost = rvb_home_value_end * rvb_sell_closing
        rvb_net_proceeds = rvb_equity_end - rvb_sell_cost

        total_buy_out = (
            rvb_total_own_mo * n_months + rvb_buy_closing_cost
            + rvb_down_amt + rvb_funding_fee
        )
        total_rent_out = total_rent_paid
        buy_net_cost = total_buy_out - rvb_net_proceeds
        rent_net_cost = total_rent_out - (invest_balance - (rvb_down_amt + rvb_buy_closing_cost))

        net_delta = rent_net_cost - buy_net_cost
        bah_coverage_buy = rvb_bah - rvb_total_own_mo
        bah_coverage_rent = rvb_bah - rvb_market_rent

        # ── SECTION 4: OUTPUT ────────────────────────────────────────────
        st.subheader("Step 3: The Numbers")

        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("Monthly Mortgage (P&I)", f"${rvb_mortgage_pi:,.0f}")
        mc2.metric(
            "Total Monthly Own Cost", f"${rvb_total_own_mo:,.0f}",
            delta=f"${rvb_total_own_mo - rvb_market_rent:+,.0f} vs renting",
            delta_color="inverse",
        )
        mc3.metric("Market Rent", f"${rvb_market_rent:,.0f}")
        mc4.metric("Your BAH", f"${rvb_bah:,.0f}")

        mc5, mc6, mc7, mc8 = st.columns(4)
        mc5.metric(
            "BAH vs Own Cost", f"${bah_coverage_buy:+,.0f}/mo",
            delta="surplus" if bah_coverage_buy >= 0 else "shortfall",
            delta_color="normal" if bah_coverage_buy >= 0 else "inverse",
        )
        mc6.metric(
            "BAH vs Rent", f"${bah_coverage_rent:+,.0f}/mo",
            delta="surplus" if bah_coverage_rent >= 0 else "shortfall",
            delta_color="normal" if bah_coverage_rent >= 0 else "inverse",
        )
        mc7.metric("Equity Built (Paydown)", f"${total_principal:,.0f}")
        mc8.metric("Est. Home Value at Sale", f"${rvb_home_value_end:,.0f}")

        st.divider()

        # Monthly cost breakdown
        with st.expander("Monthly Cost Breakdown -- Buying"):
            rows = {
                "Principal & Interest": rvb_mortgage_pi,
                "Property Tax": rvb_prop_tax_mo,
                "Home Insurance": float(rvb_insurance_mo),
                "Maintenance (est.)": rvb_maint_mo,
                "HOA": float(rvb_hoa_mo),
                "PMI": rvb_pmi_mo,
            }
            if rvb_va_loan:
                rows[f"VA Funding Fee (rolled in, {rvb_funding_fee_pct*100:.2f}%)"] = rvb_funding_fee / 360
            df_breakdown = pd.DataFrame({"Monthly Cost": rows})
            df_breakdown["Monthly Cost"] = df_breakdown["Monthly Cost"].map(lambda x: f"${x:,.0f}")
            st.dataframe(df_breakdown, use_container_width=True)

        # True cost comparison
        st.subheader(f"Over {rvb_years_stay} Year{'s' if rvb_years_stay != 1 else ''}: True Cost After Selling")

        tc1, tc2, tc3 = st.columns(3)
        tc1.metric(
            "Net Cost of Buying", f"${buy_net_cost:,.0f}",
            help="All payments + closing costs + selling costs - net sale proceeds",
        )
        tc2.metric(
            "Net Cost of Renting", f"${rent_net_cost:,.0f}",
            help="Total rent paid - investment gains on down payment opportunity cost",
        )
        tc3.metric(
            "Buying Advantage" if net_delta > 0 else "Renting Advantage",
            f"${abs(net_delta):,.0f}",
            delta="Buying wins" if net_delta > 0 else "Renting wins",
            delta_color="normal" if net_delta > 0 else "inverse",
        )

        if net_delta > 0:
            st.success(
                f"Over {rvb_years_stay} years, **buying saves you approximately "
                f"${net_delta:,.0f}** compared to renting -- after accounting for "
                "selling costs and the investment return you'd earn on the down payment "
                "if you rented instead."
            )
        else:
            st.info(
                f"Over {rvb_years_stay} years, **renting saves you approximately "
                f"${abs(net_delta):,.0f}** compared to buying at this price. "
                "Try increasing the stay duration or adjusting appreciation -- "
                "time in the home is usually the biggest lever."
            )

        # Cumulative cost chart
        cum_buy = []
        cum_rent = []
        running_buy = rvb_buy_closing_cost + rvb_down_amt + rvb_funding_fee
        running_rent = 0.0
        invest_val = rvb_down_amt + rvb_buy_closing_cost
        bal_chart = rvb_loan_amt

        for m in range(n_months):
            running_buy += rvb_total_own_mo
            running_rent += monthly_costs_rent[m]
            invest_val *= (1 + rvb_invest_return / 12)
            i_p = bal_chart * rvb_monthly_rate
            p_p = rvb_mortgage_pi - i_p
            bal_chart -= p_p
            hv = rvb_home_price * (1 + rvb_appreciation) ** ((m + 1) / 12)
            equity = hv - bal_chart
            net_buy_cumulative = running_buy - (equity - hv * rvb_sell_closing)
            net_rent_cumulative = running_rent - (invest_val - (rvb_down_amt + rvb_buy_closing_cost))
            cum_buy.append(net_buy_cumulative)
            cum_rent.append(net_rent_cumulative)

        months_axis = list(range(1, n_months + 1))
        fig_rvb = go.Figure()
        fig_rvb.add_trace(go.Scatter(
            x=months_axis, y=cum_buy, name="Buying (net true cost)",
            line=dict(color="#00aaff", width=2),
        ))
        fig_rvb.add_trace(go.Scatter(
            x=months_axis, y=cum_rent, name="Renting (net true cost)",
            line=dict(color="#ff8844", width=2),
        ))

        # Crossover point
        crossover = None
        for i in range(1, len(cum_buy)):
            if (cum_buy[i - 1] > cum_rent[i - 1]) != (cum_buy[i] > cum_rent[i]):
                crossover = i
                break
        if crossover:
            fig_rvb.add_vline(
                x=crossover, line_dash="dot", line_color="#00ff88",
                annotation_text=f"Break-even: month {crossover} ({crossover // 12}y {crossover % 12}m)",
                annotation_position="top right", annotation_font_color="#00ff88",
            )

        fig_rvb.update_layout(
            title="Cumulative Net Cost: Buying vs. Renting",
            xaxis_title="Month", yaxis_title="Net True Cost ($)",
            yaxis_tickformat="$,.0f",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            template="plotly_dark", height=380,
            margin=dict(t=60, b=40),
        )
        st.plotly_chart(fig_rvb, use_container_width=True)
        st.caption(
            "Net true cost = total cash out - equity recovered (buy) or total rent - investment gains "
            "on down payment (rent). Lower is better. The crossover is your break-even point."
        )

        # ── SECTION 5: RENTAL SCENARIO ───────────────────────────────────
        st.divider()
        st.subheader("What If I Rent It Out After I'm Done Living There?")
        st.caption(
            "This section assumes you stop living in the home and convert it to a rental property. "
            "It calculates your return three ways -- each adds one more layer of value."
        )

        with st.expander("Rental Scenario Inputs & Assumptions", expanded=True):
            rc1, rc2, rc3 = st.columns(3)
            with rc1:
                rvb_rental_income = st.number_input(
                    "Expected Monthly Rent ($/month)", min_value=500, max_value=10_000,
                    value=int(rvb_market_rent * 1.05), step=50, key="rvb_rental_income",
                )
                rvb_vacancy_rate = st.slider(
                    "Vacancy Rate (%)", 0, 20, 8, 1, key="rvb_vacancy",
                ) / 100
                rvb_mgmt_rate = st.slider(
                    "Property Management Fee (% of rent)", 0, 15, 8, 1, key="rvb_mgmt",
                ) / 100
            with rc2:
                rvb_capex_rate = st.slider(
                    "CapEx / Major Repairs Reserve (% of rent)", 0, 15, 8, 1, key="rvb_capex",
                ) / 100
                rvb_rental_ins_mo = st.number_input(
                    "Landlord Insurance ($/month)", 50, 400, 150, 10, key="rvb_rins",
                )
                rvb_rental_prop_tax_same = st.checkbox(
                    "Use same property tax as above", value=True, key="rvb_rptax_same",
                )
            with rc3:
                rvb_rental_years = st.slider(
                    "How Long Do You Plan to Rent It Out? (years)", 1, 20, 5, key="rvb_ryears",
                )
                rvb_rental_appr = st.slider(
                    "Appreciation During Rental Period (%/yr)", 0.0, 8.0, 3.0, 0.25, key="rvb_rappr",
                ) / 100
                rvb_rental_income_growth = st.slider(
                    "Annual Rent Increase (%/yr)", 0.0, 6.0, 2.0, 0.25, key="rvb_rgrowth",
                ) / 100

        # Rental calculations
        rvb_rental_start_balance = balance
        rvb_rental_start_home_val = rvb_home_value_end
        rvb_rental_n_months = rvb_rental_years * 12
        rvb_rental_prop_tax_mo = rvb_prop_tax_mo

        rent_income_mo = float(rvb_rental_income)
        r_balance = rvb_rental_start_balance
        r_home_val = rvb_rental_start_home_val

        total_gross_rent = 0.0
        total_mortgage_paid_r = 0.0
        total_principal_r = 0.0
        total_expenses_r = 0.0

        for m in range(rvb_rental_n_months):
            effective_rent = rent_income_mo * (1 - rvb_vacancy_rate)
            total_gross_rent += effective_rent

            i_r = r_balance * rvb_monthly_rate
            p_r = rvb_mortgage_pi - i_r
            r_balance -= p_r
            total_mortgage_paid_r += rvb_mortgage_pi
            total_principal_r += p_r

            mgmt = effective_rent * rvb_mgmt_rate
            capex = effective_rent * rvb_capex_rate
            expenses = mgmt + capex + rvb_rental_ins_mo + rvb_rental_prop_tax_mo + rvb_maint_mo
            total_expenses_r += expenses

            if m % 12 == 11:
                rent_income_mo *= (1 + rvb_rental_income_growth)

        r_home_val_end = rvb_rental_start_home_val * (1 + rvb_rental_appr) ** rvb_rental_years
        r_equity_end = r_home_val_end - max(r_balance, 0)
        r_sell_cost = r_home_val_end * rvb_sell_closing

        net_cash_flow = total_gross_rent - total_expenses_r - total_mortgage_paid_r
        total_cash_invested = rvb_down_amt + rvb_buy_closing_cost + rvb_funding_fee

        if total_cash_invested > 0:
            roi_cashflow = (net_cash_flow / total_cash_invested) / rvb_rental_years * 100
            roi_paydown = ((net_cash_flow + total_principal_r) / total_cash_invested) / rvb_rental_years * 100
        else:
            roi_cashflow = 0.0
            roi_paydown = 0.0

        appreciation_gain = r_home_val_end - rvb_rental_start_home_val
        roi_total = (
            ((net_cash_flow + total_principal_r + appreciation_gain) / total_cash_invested)
            / rvb_rental_years * 100
            if total_cash_invested > 0 else 0.0
        )

        annual_noi = (total_gross_rent - total_expenses_r) / rvb_rental_years
        cap_rate = (annual_noi / rvb_rental_start_home_val) * 100 if rvb_rental_start_home_val > 0 else 0.0
        avg_monthly_cashflow = net_cash_flow / rvb_rental_n_months

        # Display rental results
        r1, r2, r3, r4 = st.columns(4)
        r1.metric(
            "Avg Monthly Cash Flow", f"${avg_monthly_cashflow:,.0f}/mo",
            delta="positive" if avg_monthly_cashflow >= 0 else "negative cash flow",
            delta_color="normal" if avg_monthly_cashflow >= 0 else "inverse",
        )
        r2.metric(
            "Cap Rate", f"{cap_rate:.1f}%",
            help="Net Operating Income / property value. 5-8% is typically considered healthy.",
        )
        r3.metric(
            "Est. Equity at Exit", f"${r_equity_end - r_sell_cost:,.0f}",
            help="Home value minus remaining mortgage minus selling costs",
        )
        r4.metric(
            "Tenant Paydown (principal)", f"${total_principal_r:,.0f}",
            help="How much of your mortgage balance your tenants pay down",
        )

        st.divider()
        st.subheader("Return on Investment -- Three Ways to Look at It")
        st.caption(
            "Each row adds one more source of return. The first row is the most "
            "conservative -- only counting cash you actually receive."
        )

        roi_data = {
            "What's Included": [
                "Cash flow only",
                "Cash flow + tenant mortgage paydown",
                "Cash flow + paydown + appreciation",
            ],
            "Annual ROI": [
                f"{roi_cashflow:.1f}%",
                f"{roi_paydown:.1f}%",
                f"{roi_total:.1f}%",
            ],
            "Description": [
                "Only passive income after all expenses & mortgage. The floor.",
                "Adds principal reduction by tenants -- real wealth even if you break even on cash.",
                "Adds speculative appreciation. The ceiling -- not guaranteed, but historically likely.",
            ],
        }
        st.dataframe(pd.DataFrame(roi_data), use_container_width=True, hide_index=True)

        with st.expander("Rental P&L Summary"):
            pnl_data = {
                "Item": [
                    "Gross Rent Collected (adj. for vacancy)",
                    "- Property Management",
                    "- CapEx / Repairs Reserve",
                    "- Landlord Insurance",
                    "- Property Tax",
                    "- Maintenance",
                    "= Net Operating Income (NOI)",
                    "- Mortgage Payments (P&I)",
                    "= Net Cash Flow",
                    "  + Tenant Principal Paydown",
                    "  + Appreciation Gain (est.)",
                    "= Total Wealth Created",
                ],
                "Total over Period": [
                    f"${total_gross_rent:,.0f}",
                    f"-${total_gross_rent * rvb_mgmt_rate:,.0f}",
                    f"-${total_gross_rent * rvb_capex_rate:,.0f}",
                    f"-${rvb_rental_ins_mo * rvb_rental_n_months:,.0f}",
                    f"-${rvb_rental_prop_tax_mo * rvb_rental_n_months:,.0f}",
                    f"-${rvb_maint_mo * rvb_rental_n_months:,.0f}",
                    f"${annual_noi * rvb_rental_years:,.0f}",
                    f"-${total_mortgage_paid_r:,.0f}",
                    f"${net_cash_flow:,.0f}",
                    f"+${total_principal_r:,.0f}",
                    f"+${appreciation_gain:,.0f}",
                    f"${net_cash_flow + total_principal_r + appreciation_gain:,.0f}",
                ],
            }
            st.dataframe(pd.DataFrame(pnl_data), use_container_width=True, hide_index=True)

        st.caption(
            "**Assumptions:** 30-year fixed mortgage. Appreciation compounds annually. "
            "Vacancy and CapEx are estimated percentages of gross rent. "
            "ROI is annualized over the rental hold period and uses original cash invested "
            "(down payment + closing costs + VA funding fee if applicable). "
            "Tax implications of rental income not modeled -- consult a CPA."
        )
