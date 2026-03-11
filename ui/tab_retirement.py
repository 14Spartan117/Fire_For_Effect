"""
Tab 2 -- How Much Do You Need to Save?
"""

import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import streamlit as st

from config import RANKS
from data import get_base_pay, get_military_pay
from models import (
    get_lifecycle_allocation,
    get_blended_nominal_return,
    get_time_weighted_blended_return,
    build_monthly_base_pay_schedule,
    solve_savings_rate,
    calc_high3_pension,
    calc_pension_apv,
    scrape_and_prep_tsp_data,
    run_real_monte_carlo,
)


def render_tab_retirement(container):
    with container:
        ss = st.session_state
        ss.tabs_visited.add(2)
        ss.max_tab_reached = max(ss.max_tab_reached, 2)
        st.header("Step 2: Retirement & Pension Target")
        st.info(
            "\U0001F4A1 **Reality Check:** We'll calculate the single savings rate "
            "-- as a % of your base pay -- that you can plug directly into MyPay "
            "and stay on track for your entire career."
        )

        # ── Row 1: Career inputs ──────────────────────────────────────────────
        col_l, col_r = st.columns(2)
        with col_l:
            st.subheader("Career Timeline")
            retire_system = st.radio(
                "Retirement System",
                ["BRS (2.0%)", "Legacy / High-3 (2.5%)"],
                horizontal=True,
            )
            multiplier = 0.02 if "BRS" in retire_system else 0.025

            # Seed widget keys from Tab 1 defaults on first load
            if "tab2_rank_widget" not in ss:
                ss["tab2_rank_widget"] = ss.get("tab1_rank", RANKS[4])
            if "tab2_tis_widget" not in ss:
                ss["tab2_tis_widget"] = float(ss.get("tab1_tis", 4.0))

            if st.button("\u2B07\uFE0F Import Rank / TIS from Tab 1", key="import_tab1_rank"):
                t1_rank = ss.get("tab1_rank")
                t1_tis = ss.get("tab1_tis", 4.0)
                if t1_rank and t1_rank in RANKS:
                    ss["tab2_rank_widget"] = t1_rank
                ss["tab2_tis_widget"] = float(t1_tis)
                st.rerun()

            start_rank = st.selectbox(
                "Current Rank", RANKS,
                key="tab2_rank_widget",
            )
            start_tis = st.number_input(
                "Current Years of Service",
                min_value=0.0, max_value=40.0, step=0.5,
                key="tab2_tis_widget",
            )
            retire_rank = st.selectbox("Expected Rank at Retirement", RANKS, index=20)
            yrs_at_retire = st.slider("Total Years of Service at Retirement", 20, 40, 20)
            current_age = st.slider("Current Age", 18, 60, 27)
            age_at_retire = st.slider("Age When You Stop Working Entirely", 38, 75, 60)

        with col_r:
            st.subheader("Assets & Goals")
            current_tsp = st.number_input(
                "Current TSP / IRA Balance ($)", value=10000, step=1000
            )
            monthly_goal = st.number_input(
                "Desired Monthly Income in Retirement ($)", value=8000, step=500
            )

            retire_base, _, _ = get_military_pay(retire_rank, yrs_at_retire, "92136", False)
            no_mil_retirement = st.checkbox(
                "I don't plan to retire from the military",
                value=False,
                help="Check this if you plan to separate before 20 years. "
                     "Sets pension to $0 and removes the pension floor.",
            )
            sex_for_apv = st.radio(
                "Sex (only used for actuarial life expectancy)",
                ["Male", "Female"], horizontal=True,
                help="Used only for the actuarial pension value calculation.",
            )

            est_pension = calc_high3_pension(retire_rank, yrs_at_retire, multiplier)
            annual_pension = est_pension * 12
            retire_at_age = current_age + max(0, yrs_at_retire - start_tis)
            swr_value = annual_pension / 0.04
            apv_value = calc_pension_apv(
                annual_pension, int(retire_at_age),
                discount_rate=0.025, sex=sex_for_apv.lower(),
            )

            if no_mil_retirement:
                st.caption("...and it's gone.")
                est_pension = 0.0
            else:
                pa, pb, pc = st.columns(3)
                pa.metric("Monthly Pension", f"${est_pension:,.0f}/mo")
                pb.metric("Annual Pension", f"${annual_pension:,.0f}/yr")
                pc.metric(
                    "Expected Years of Pension Payments",
                    f"~{int(apv_value / annual_pension * (1 + 0.025)):.0f} yrs",
                    help="Actuarially expected payment duration based on SSA mortality tables.",
                )

                pd2, pe = st.columns(2)
                pd2.metric(
                    "Pension Value (SWR Estimate)",
                    f"${swr_value:,.0f}",
                    help="How much you'd need in savings to replace this pension at a 4% withdrawal rate.",
                )
                pe.metric(
                    "Pension Value (Life Expectancy Estimate)",
                    f"${apv_value:,.0f}",
                    delta=f"${swr_value - apv_value:+,.0f} vs SWR",
                    delta_color="inverse",
                    help="Based on SSA 2022 life tables, 2.5% discount rate.",
                )
                st.caption(
                    "[4% Rule / SWR](https://www.investopedia.com/terms/f/four-percent-rule.asp) · "
                    "[SSA 2022 Actuarial Life Tables](https://www.ssa.gov/oact/STATS/table4c6.html)"
                )

            st.subheader("Post-Military Civilian Salary")
            civilian_monthly = st.number_input(
                "Expected Monthly Civilian Salary ($)",
                min_value=0.0, value=0.0, step=100.0,
            )
            total_monthly_civ = civilian_monthly + est_pension
            c1, c2 = st.columns(2)
            c1.metric("Civilian + Pension / Month", f"${total_monthly_civ:,.0f}")
            c2.metric("Civilian + Pension / Year", f"${total_monthly_civ * 12:,.0f}")

        mil_years = max(0, yrs_at_retire - start_tis)
        mil_months = int(mil_years * 12)
        years_to_grow = age_at_retire - current_age
        total_months = max(1, years_to_grow * 12)

        # ── Row 2: Fund allocation ────────────────────────────────────────────
        st.divider()
        st.subheader("\U0001F4CA TSP Fund Allocation")
        st.caption(
            "By default, 100% goes to the L-Fund -- TSP's automatic lifecycle strategy "
            "that shifts to bonds as you approach retirement. To customize, move the sliders below. "
            "The L-Fund percentage updates automatically to show what's left over."
        )

        alloc_col, inf_col = st.columns([5, 1])
        with inf_col:
            inflation_input = st.slider(
                "Inflation Rate (%)", 0.0, 10.0, 2.5, 0.1,
                help="Adjusts returns into today's purchasing power.",
            )
            inflation_rate = inflation_input / 100.0

        def real(nominal):
            return round(((1 + nominal) / (1 + inflation_rate) - 1) * 100, 1)

        rc = real(0.113)
        rs = real(0.094)
        ri = real(0.063)
        rf = real(0.054)
        rg = real(0.047)

        with alloc_col:
            fc1, fc2, fc3, fc4, fc5, fc6 = st.columns(6)
            pct_c = fc1.slider(f"C-Fund (S&P 500)\n{rc:+.1f}% real +/-18%/yr", 0, 100, 0, 5,
                               help="Large-cap U.S. stocks.")
            pct_s = fc2.slider(f"S-Fund (Small Cap)\n{rs:+.1f}% real +/-22%/yr", 0, 100, 0, 5,
                               help="Small/mid-cap U.S. stocks.")
            pct_i = fc3.slider(f"I-Fund (Intl)\n{ri:+.1f}% real +/-19%/yr", 0, 100, 0, 5,
                               help="International stocks.")
            pct_f = fc4.slider(f"F-Fund (Bonds)\n{rf:+.1f}% real +/-4%/yr", 0, 100, 0, 5,
                               help="U.S. bond index.")
            pct_g = fc5.slider(f"G-Fund (Govt)\n{rg:+.1f}% real +/-0%/yr", 0, 100, 0, 5,
                               help="Government securities.")
            manual_sum = pct_c + pct_s + pct_i + pct_f + pct_g
            pct_l = max(0, 100 - manual_sum)
            fc6.metric(
                "L-Fund (Auto)\nLifecycle blend",
                f"{pct_l}%",
                delta="Remainder" if pct_l > 0 else "None",
                delta_color="normal" if pct_l > 0 else "off",
                help="Whatever you don't manually allocate goes here.",
            )

        if manual_sum > 100:
            st.error(
                f"\u26A0\uFE0F Over-allocated by {manual_sum - 100}% -- "
                "reduce your fund allocations. Total must be <= 100%."
            )
            allocation_valid = False
        else:
            alloc_display = (
                f"C:{pct_c}% | S:{pct_s}% | I:{pct_i}% | F:{pct_f}% | G:{pct_g}% "
                f"| L-Fund (auto): {pct_l}%"
            )
            st.success(f"\u2705 Allocation: {alloc_display}")
            allocation_valid = True

        alloc_dict = {
            "C": pct_c / 100, "S": pct_s / 100, "I": pct_i / 100,
            "F": pct_f / 100, "G": pct_g / 100, "L": pct_l / 100,
        }
        mc_manual_alloc = {k: v for k, v in alloc_dict.items() if k != "L"}
        use_lc = pct_l > 0

        expected_nom = get_blended_nominal_return(alloc_dict, years_to_grow)
        expected_real_rate = ((1 + get_time_weighted_blended_return(alloc_dict, total_months)) / (1 + inflation_rate)) - 1

        # ── Solver & results ──────────────────────────────────────────────────
        if years_to_grow > 0 and allocation_valid:
            monthly_income_gap = max(0, monthly_goal - est_pension)
            total_nest_egg_needed = (monthly_income_gap * 12) / 0.04

            base_pay_schedule = build_monthly_base_pay_schedule(
                start_rank, start_tis, min(mil_months, total_months)
            )

            savings_pct, contrib_schedule = solve_savings_rate(
                total_nest_egg_needed, current_tsp,
                base_pay_schedule, civilian_monthly,
                mil_months, total_months,
                expected_real_rate, inflation_rate,
            )

            current_base = get_base_pay(start_rank, start_tis)
            ss.pmt_target = savings_pct * current_base
            ss.savings_rate_pct = savings_pct
            ss.nest_egg_target = total_nest_egg_needed
            ss.est_pension = est_pension

            avg_mil_income = (
                np.mean(base_pay_schedule) if len(base_pay_schedule) > 0 else current_base
            )
            civ_pct = (
                savings_pct * (avg_mil_income / civilian_monthly)
                if civilian_monthly > 0
                else None
            )
            monthly_dollar_equiv = savings_pct * current_base

            st.divider()
            r1, r2, r3 = st.columns(3)
            r1.metric("Target Nest Egg (Real $)", f"${total_nest_egg_needed:,.0f}")
            r2.metric("Blended Nominal Return", f"{expected_nom * 100:.2f}%")
            r3.metric("Real Return (After Inflation)", f"{expected_real_rate * 100:.2f}%")

            st.divider()
            m1, m2, m3 = st.columns(3)
            m1.metric(
                "\U0001F4CC Military Savings Rate",
                f"{savings_pct * 100:.1f}% of Base Pay",
                delta="This percentage is adjusted in MyPay",
                delta_color="off",
            )
            if civ_pct is not None:
                m2.metric(
                    "\U0001F4CC Civilian Savings Rate",
                    f"{civ_pct * 100:.1f}% of Civilian Salary",
                    delta="Set this up in your 401k or IRA after separation",
                    delta_color="off",
                )
            else:
                m2.metric(
                    "\U0001F4CC Civilian Savings Rate",
                    "Enter civilian salary above",
                    delta="Required to calculate post-military rate",
                    delta_color="off",
                )
            m3.metric(
                "Today's Military Dollar Equivalent",
                f"${monthly_dollar_equiv:,.2f} / month",
                delta="Starting point only -- see note below",
                delta_color="off",
            )

            # ── TSP Gap Callout ───────────────────────────────────────────────
            les_tsp = ss.get("les_tsp_actual", 0.0)
            if les_tsp > 0 and current_base > 0:
                current_tsp_pct = (les_tsp / current_base) * 100
                gap_pct = savings_pct * 100 - current_tsp_pct
                gap_dollars = monthly_dollar_equiv - les_tsp
                if gap_pct > 0.5:
                    st.warning(
                        f"**You are currently saving {current_tsp_pct:.1f}% of your base pay "
                        f"(${les_tsp:,.2f}/month) toward TSP.** "
                        f"To meet your financial goals, you need to increase your contributions to "
                        f"**{savings_pct * 100:.1f}%** -- an increase of **{gap_pct:.1f} percentage points "
                        f"(${gap_dollars:,.2f}/month)**. You can make this adjustment now in "
                        f"[MyPay](https://mypay.dfas.mil)."
                    )
                elif gap_pct < -0.5:
                    st.success(
                        f"**You are currently saving {current_tsp_pct:.1f}% of your base pay "
                        f"(${les_tsp:,.2f}/month) toward TSP** -- "
                        f"**${abs(gap_dollars):,.2f}/month more than your goal requires.** "
                        "That surplus increases the odds of hitting your goal. Congrats! \U0001F389"
                    )
                else:
                    st.success(
                        f"**You are currently saving {current_tsp_pct:.1f}% of your base pay "
                        f"(${les_tsp:,.2f}/month) toward TSP** -- right on target."
                    )
            elif les_tsp == 0.0:
                st.caption(
                    "\U0001F4A1 *Enter your current TSP contribution from your LES in the "
                    "Budget tab to see how your current savings compares to your goal.*"
                )

            civ_rate_line = (
                f"After separation, target **{civ_pct * 100:.1f}% of your civilian salary** -- "
                "set this up in your employer's 401k or IRA. These two rates work together to get you to your goal."
                if civ_pct is not None
                else "Enter your expected civilian salary above to calculate your post-military savings rate."
            )

            st.info(
                f"**Why the percentage matters more than the dollar amount.**\n\n"
                f"A fixed ${monthly_dollar_equiv:,.0f}/month sounds simple -- but inflation erodes its purchasing power every year. "
                "A percentage of base pay scales automatically with every promotion and raise, keeping your contributions "
                "aligned with what your future actually costs. Set it once, let your career do the rest.\n\n"
                f"**Military phase:** Save **{savings_pct * 100:.1f}% of base pay** -- set this in MyPay. "
                f"{civ_rate_line}\n\n"
                "More on why this works: [Time Value of Money](https://www.investopedia.com/terms/t/timevalueofmoney.asp)."
            )

            # ── Savings Rate Explorer ─────────────────────────────────────────
            st.divider()
            st.subheader("\U0001F3AF Savings Rate Explorer")
            st.caption(
                "Drag the slider to see how your savings rate affects your portfolio growth "
                "and the age at which you hit your goal."
            )
            st.info(
                "\U0001F4A1 **This is a what-if explorer.** Adjusting the slider here does not "
                "change your plan -- it lets you explore tradeoffs between savings rate and retirement age "
                "before you commit."
            )

            explore_pct = st.slider(
                "Savings Rate (% of Base Pay)",
                min_value=0.0, max_value=60.0,
                value=float(round(savings_pct * 100, 1)),
                step=0.5, key="explorer_slider",
            )

            explore_rate = explore_pct / 100.0
            monthly_real = (1 + expected_real_rate) ** (1 / 12) - 1

            full_income = list(base_pay_schedule)
            for _ in range(total_months - len(base_pay_schedule)):
                full_income.append(civilian_monthly)
            full_income = full_income[:total_months]

            balance = float(current_tsp)
            ages, balances = [], []
            goal_age = None

            for m in range(total_months):
                age_now = current_age + m / 12.0
                contrib = explore_rate * full_income[m] if m < len(full_income) else 0.0
                balance = balance * (1 + monthly_real) + contrib
                ages.append(age_now)
                balances.append(balance)
                if goal_age is None and balance >= total_nest_egg_needed:
                    goal_age = age_now

            fig_exp = go.Figure()
            fig_exp.add_trace(go.Scatter(
                x=ages, y=balances, mode="lines", name="Portfolio Growth",
                line=dict(color="#00b4d8", width=2.5),
                hovertemplate="Age %{x:.1f}: $%{y:,.0f}<extra></extra>",
            ))
            fig_exp.add_hline(
                y=total_nest_egg_needed, line_dash="dash", line_color="#ef476f",
                line_width=1.5,
                annotation_text=f"Target: ${total_nest_egg_needed:,.0f}",
                annotation_position="top left",
                annotation_font_color="#ef476f",
            )
            if goal_age is not None and goal_age <= age_at_retire:
                fig_exp.add_vline(x=goal_age, line_dash="dash", line_color="#06d6a0", line_width=1.5)
                fig_exp.add_annotation(
                    x=goal_age, y=total_nest_egg_needed,
                    text=f"  Goal met at age {goal_age:.1f}",
                    showarrow=True, arrowhead=2, arrowcolor="#06d6a0",
                    font=dict(color="#06d6a0", size=12),
                    bgcolor="rgba(0,0,0,0.6)", bordercolor="#06d6a0", borderwidth=1,
                    ax=40, ay=-40,
                )
            else:
                fig_exp.add_annotation(
                    x=ages[len(ages) // 2], y=max(balances) * 0.5,
                    text="Goal not reached within timeframe -- increase savings rate",
                    showarrow=False, font=dict(color="#ef476f", size=12),
                    bgcolor="rgba(0,0,0,0.6)",
                )

            fig_exp.update_layout(
                plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                font=dict(color="#fafafa"), height=350,
                margin=dict(l=60, r=30, t=30, b=50),
                xaxis=dict(title="Age", gridcolor="#2a2a3e", zerolinecolor="#2a2a3e"),
                yaxis=dict(title="Portfolio Value ($)", gridcolor="#2a2a3e",
                           zerolinecolor="#2a2a3e", tickformat="$,.0f"),
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#fafafa")),
                showlegend=True,
            )
            st.plotly_chart(fig_exp, use_container_width=True)

            # ── Monte Carlo ───────────────────────────────────────────────────
            st.divider()
            st.subheader("\U0001F3B2 Monte Carlo Projection (1,000 Trials)")
            st.markdown("""
You've done the work. You know what you make, what you need, what you need to save, and how you want
it invested. The graph above gives you the answer -- if I do this, when will I meet my goal? It's
clean, smooth, predictable.

**But it's a lie.**

Real markets don't move in straight lines. They crash the second you buy in. They go sideways for a
decade while you wonder if you made a mistake. They drop 40% and every instinct you have screams
*sell*. The average return is a number drawn through decades of panic, euphoria, and everything in
between -- and the average hides all of it.

**Know that this is what you're actually signing up for.**

Every gray line below is a real possible future. Two soldiers, same plan, same rate, same fund --
completely different outcomes based on nothing but luck and timing. That's the game. There will be
years that feel like you're losing. Stay in. Don't touch it. You made a plan -- execute it like your
financial future depends on it, because it does.

And if anyone ever tells you they have a guaranteed return, a cheat code, or a hot tip -- run. People
brag about wins. They never mention the losses. The market has no shortcuts: there is only time,
consistency, and discipline.

*May the odds be ever in your favor.*
            """)

            if st.button("Run Simulation", type="primary"):
                ss.monte_carlo_run = True
                with st.spinner("Running 1,000 trials..."):
                    fund_params, data_source = scrape_and_prep_tsp_data()
                    l_fund_weight = pct_l / 100.0
                    explore_contrib_schedule = [explore_rate * inc for inc in full_income]
                    sim_results = run_real_monte_carlo(
                        current_age, age_at_retire, current_tsp,
                        explore_contrib_schedule, fund_params,
                        l_fund_weight, mc_manual_alloc,
                        inflation_rate=inflation_rate, trials=1000,
                    )

                fig, ax = plt.subplots(figsize=(12, 6), facecolor="#0e1117")
                ax.set_facecolor("#0e1117")
                time_axis = np.linspace(current_age, age_at_retire, sim_results.shape[1])

                p10 = np.percentile(sim_results, 10, axis=0)
                p50 = np.percentile(sim_results, 50, axis=0)
                p90 = np.percentile(sim_results, 90, axis=0)
                success_rate = np.mean(sim_results[:, -1] >= total_nest_egg_needed) * 100
                ss.mc_success_rate = success_rate

                # Store for PDF generation in tab_plan
                ss.sim_results = sim_results
                ss.sim_savings_pct = explore_rate
                ss.sim_current_age = current_age
                ss.sim_age_at_retire = age_at_retire
                ss.sim_target = total_nest_egg_needed
                ss.sim_data_source = data_source

                final_vals = sim_results[:, -1]
                sorted_idx = np.argsort(final_vals)
                # Sample from 5th–95th percentile to keep extreme outliers off the chart
                p05_idx = int(0.05 * (1000 - 1))
                p95_idx = int(0.95 * (1000 - 1))
                sample_idx = [sorted_idx[p05_idx + int(i * (p95_idx - p05_idx) / 19)] for i in range(20)]

                for k, idx in enumerate(sample_idx):
                    label = (
                        f"Based on {explore_pct:.1f}% military savings rate "
                        f"-- Probability of Success: {success_rate:.1f}%"
                        if k == 0 else ""
                    )
                    ax.plot(time_axis, sim_results[idx], color="#b4b4c8", lw=0.9,
                            alpha=0.35, label=label)

                ax.fill_between(time_axis, p10, p90, color="#00b4d8", alpha=0.15)
                ax.plot(time_axis, p90, color="#00b4d8", lw=1.2, linestyle="dashed",
                        label=f"90th Percentile: ${p90[-1]:,.0f} at age {age_at_retire}")
                ax.plot(time_axis, p50, color="#00b4d8", lw=2.5,
                        label=f"Median: ${p50[-1]:,.0f} at age {age_at_retire}")
                ax.plot(time_axis, p10, color="#00b4d8", lw=1, linestyle="dotted",
                        label=f"10th Percentile: ${p10[-1]:,.0f} at age {age_at_retire}")
                ax.axhline(y=total_nest_egg_needed, color="#ef476f", linestyle="--", lw=1.5,
                           label=f"Target: ${total_nest_egg_needed:,.0f}")

                y_ceil = max(p90[-1] * 1.5, total_nest_egg_needed * 1.5)
                ax.set_ylim(bottom=0, top=y_ceil)
                ax.set_ylabel("Portfolio Value ($)", fontsize=11, color="#fafafa")
                ax.set_xlabel("Age", fontsize=11, color="#fafafa")
                ax.tick_params(colors="#fafafa")
                ax.spines["bottom"].set_color("#2a2a3e")
                ax.spines["left"].set_color("#2a2a3e")
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)
                ax.grid(True, linestyle="--", alpha=0.2, color="#2a2a3e")
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${int(x):,}"))
                ax.legend(
                    loc="upper left", fontsize=9,
                    facecolor="#14141f", edgecolor="#00b4d8",
                    labelcolor="#fafafa", framealpha=0.85,
                )
                st.pyplot(fig)

                st.caption(
                    "**A note on probability of success:** A result of 50-60% is intentional and appropriate. "
                    "Targeting 80-90% means planning to survive the worst historical market sequences -- "
                    "which results in significant over-saving in most scenarios. With a military pension as a floor, "
                    "a 50-60% Monte Carlo success rate reflects a realistic, balanced plan."
                )

        # ── Assumptions expander ──────────────────────────────────────────────
        st.divider()
        with st.expander("\U0001F4CB Model Assumptions"):
            st.markdown("""
**Promotion Timeline (Primary Zone -- Army)**

| Community | Progression |
|---|---|
| **Officers** | O-1 -> O-2 at 2 yrs - O-3 at 4 - O-4 at 11 - O-5 at 17 - O-6 at 23 |
| **Warrant Officers** | W-1 -> CW2 at 3 yrs - CW3 at 8 - CW4 at 14 - CW5 at 20 |
| **Enlisted** | E-1 -> E-2 at 6 mo - E-3 at 18 mo - E-4 at 2 yrs - E-5 at 4 - E-6 at 8 - E-7 at 14 - E-8 at 18 - E-9 at 23 |

> Promotion lag: Timelines reflect when pay actually changes -- approximately 12 months after board selection.

**Pension (High-3 Average)** -- Averages base pay across the 3 years immediately before retirement.

**Savings Rate Solver** -- Binary-searches for the constant percentage of income that grows your current TSP balance to your target nest egg.

**Fund Return Assumptions** *(inception-to-date, tspfolio.com)*

| Fund | Nominal CAGR | Std Dev |
|---|---|---|
| C-Fund (S&P 500) | 11.3% | +/-18%/yr |
| S-Fund (Small Cap) | 9.4% | +/-22%/yr |
| I-Fund (International) | 6.3% | +/-19%/yr |
| F-Fund (Bonds) | 5.4% | +/-4%/yr |
| G-Fund (Govt Securities) | 4.7% | +/-0%/yr |
| L-Fund | Dynamic blend based on years to retirement |

Real returns shown in sliders use the Fisher equation: `(1 + nominal) / (1 + inflation) - 1`.

**Monte Carlo** -- 1,000 trials using parametric Normal distribution draws calibrated to each fund's historical mean and standard deviation. Monthly parameters are derived using variance drag correction: `mu_annual = geo_mean + sigma^2/2`. Success = portfolio >= target nest egg at your stop-working age.

**Pension Valuation** -- Actuarial Present Value (APV) uses SSA 2022 Period Life Tables with Gompertz extrapolation for ages 79+. Discount rate: 2.5% real. SWR estimate uses the standard 4% safe withdrawal rule.

**Other:** Nest egg target uses the 4% safe withdrawal rule. Civilian salary is a major unknown -- be conservative.
            """)
