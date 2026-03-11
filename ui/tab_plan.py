"""
Tab 6 -- Your Plan (2-page PDF snapshot with charts + checklist)
"""

import datetime
import io

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import streamlit as st

from analytics import log_session


def render_tab_plan(container):
    with container:
        ss = st.session_state
        ss.tabs_visited.add(6)
        ss.max_tab_reached = max(ss.max_tab_reached, 6)
        st.header("\U0001F4C4 Your Plan")
        st.caption(
            "Your numbers and your checklist -- one PDF. Download it, share it, "
            "or just keep it somewhere you'll look at it."
        )

        # ── Check data readiness ─────────────────────────────────────────────
        missing = []
        if ss.get("base_pay", 0.0) == 0.0:
            missing.append("**Tab 1** -- complete your rank, TIS, and zip code")
        if ss.get("pmt_target", 0.0) == 0.0:
            missing.append("**Tab 2** -- complete your career inputs and fund allocation")
        if ss.get("tab3_take_home", 0.0) == 0.0:
            missing.append("**Tab 3** -- enter your take-home pay and budget")

        if missing:
            st.warning(
                "Complete the following before generating your plan:\n\n"
                + "\n".join(f"- {m}" for m in missing)
            )
            return

        # ── Pull data ─────────────────────────────────────────────────────────
        base_pay = ss.get("base_pay", 0.0)
        bah_amt = ss.get("bah_amt", 0.0)
        bas_amt = ss.get("bas_amt", 0.0)
        special_pay = ss.get("special_pay", 0.0)
        gross_monthly = base_pay + bah_amt + bas_amt + special_pay

        savings_rate = ss.get("savings_rate_pct", 0.0)
        nest_egg = ss.get("nest_egg_target", 0.0)
        est_pension = ss.get("est_pension", 0.0)
        pmt_target = ss.get("pmt_target", 0.0)

        take_home = ss.get("tab3_take_home", 0.0)
        fixed_costs = ss.get("tab3_fixed", 0.0)
        invested = ss.get("tab3_invested", 0.0)
        guilt_free = ss.get("tab3_guilt_free", 0.0)
        surplus = take_home - fixed_costs - invested - guilt_free

        mc_results = ss.get("sim_results", None)
        mc_age_start = ss.get("sim_current_age", 0)
        mc_age_end = ss.get("sim_age_at_retire", 0)
        mc_target = ss.get("sim_target", 0.0)
        mc_rate = ss.get("sim_savings_pct", 0.0)

        on_track = surplus >= 0 and invested >= pmt_target * 0.9

        # ── On-screen preview ────────────────────────────────────────────────
        st.subheader("Snapshot")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown("**Income**")
            st.metric("Monthly Gross", f"${gross_monthly:,.0f}")
            st.metric("Base Pay", f"${base_pay:,.0f}")
            st.metric("BAH", f"${bah_amt:,.0f}")
            st.metric("BAS", f"${bas_amt:,.0f}")
        with col_b:
            st.markdown("**Retirement**")
            st.metric("Est. Monthly Pension", f"${est_pension:,.0f}")
            st.metric("Target Nest Egg", f"${nest_egg:,.0f}")
            st.metric(
                "Required Savings Rate",
                f"{savings_rate * 100:.1f}% of Base Pay" if savings_rate else "--",
            )
            if mc_results is not None:
                mc_success = ss.get("mc_success_rate", None)
                if mc_success is not None:
                    st.metric("Simulation Success Rate", f"{mc_success:.0f}%")
        with col_c:
            st.markdown("**Budget**")
            st.metric("Take-Home", f"${take_home:,.0f}")
            st.metric("Fixed Costs", f"${fixed_costs:,.0f}")
            st.metric("Invested", f"${invested:,.0f}")
            delta_color = "normal" if surplus >= 0 else "inverse"
            st.metric(
                "Surplus / Deficit",
                f"${surplus:,.0f}",
                delta="On track" if surplus >= 0 else "Needs attention",
                delta_color=delta_color,
            )

        st.divider()

        # ── PDF generation ───────────────────────────────────────────────────
        if st.button("\U0001F4E5 Generate & Download PDF", type="primary"):
            ss.pdf_downloaded = True
            if not ss.session_logged:
                ss.session_logged = True
                log_session()

            from fpdf import FPDF

            pdf = FPDF()
            pdf.set_margins(15, 15, 15)

            def safe(text):
                return (
                    str(text)
                    .replace("\u2014", "-").replace("\u2013", "-")
                    .replace("\u2190", "<-").replace("\u2192", "->")
                    .replace("\u2019", "'").replace("\u2018", "'")
                    .replace("\u201c", '"').replace("\u201d", '"')
                    .replace("\u2026", "...")
                )

            def page_header():
                pdf.set_font("Helvetica", "B", 14)
                pdf.set_fill_color(30, 60, 114)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 10, safe("F.I.R.E. for Effect  --  Financial Plan"),
                         fill=True, ln=True, align="C")
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Helvetica", "", 8)
                pdf.cell(0, 5, safe(
                    f"Generated {datetime.date.today().strftime('%B %d, %Y')}  |  "
                    "For planning purposes only -- not financial advice."
                ), ln=True, align="C")
                pdf.ln(3)

            def section_header(title):
                pdf.set_font("Helvetica", "B", 10)
                pdf.set_fill_color(220, 230, 245)
                pdf.set_text_color(30, 60, 114)
                pdf.cell(0, 6, safe(f"  {title}"), fill=True, ln=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)

            def row(label, value):
                pdf.set_font("Helvetica", "B", 9)
                pdf.cell(90, 5, safe(f"    {label}"), ln=False)
                pdf.set_font("Helvetica", "", 9)
                pdf.cell(0, 5, safe(value), ln=True)

            # ── PAGE 1 ──────────────────────────────────────────────────────
            pdf.add_page()
            page_header()

            # Income
            section_header("INCOME SNAPSHOT")
            row("Monthly Gross Pay:", f"${gross_monthly:,.0f}")
            row("Base Pay:", f"${base_pay:,.0f}")
            row("BAH (Tax-Free):", f"${bah_amt:,.0f}")
            row("BAS (Tax-Free):", f"${bas_amt:,.0f}")
            row("Special Pays:", f"${special_pay:,.0f}")
            pdf.ln(3)

            # Retirement
            section_header("RETIREMENT TARGETS")
            row("Estimated Monthly Pension:", f"${est_pension:,.0f}  (High-3 Average)")
            row("Target Nest Egg:", f"${nest_egg:,.0f}")
            row("Required Savings Rate:",
                f"{savings_rate * 100:.1f}% of base pay  --  set in MyPay (mypay.dfas.mil)"
                if savings_rate else "N/A")
            pdf.ln(3)

            # Monte Carlo chart (if simulation was run)
            if mc_results is not None and mc_age_end > mc_age_start:
                _time = np.linspace(mc_age_start, mc_age_end, mc_results.shape[1])
                _p10 = np.percentile(mc_results, 10, axis=0)
                _p50 = np.percentile(mc_results, 50, axis=0)
                _p90 = np.percentile(mc_results, 90, axis=0)

                _mc_fig, _mc_ax = plt.subplots(figsize=(7.2, 2.8))
                _mc_fig.patch.set_facecolor("white")
                _mc_ax.set_facecolor("white")
                _mc_ax.fill_between(
                    _time, _p10, _p90,
                    color="#00b4d8", alpha=0.15, label="10th-90th percentile",
                )
                _mc_ax.plot(
                    _time, _p50,
                    color="#00b4d8", lw=2,
                    label=f"Median  (saving {mc_rate * 100:.1f}% of base pay)",
                )
                _mc_ax.axhline(
                    y=mc_target, color="#ef476f", linestyle="--", lw=1.5,
                    label=f"Target: ${mc_target:,.0f}",
                )
                _mc_ax.set_xlabel("Age", fontsize=8)
                _mc_ax.set_ylabel("Portfolio Value", fontsize=8)
                _mc_ax.yaxis.set_major_formatter(
                    plt.FuncFormatter(
                        lambda x, _: f"${x / 1e6:.1f}M" if x >= 1e6 else f"${int(x):,}"
                    )
                )
                _mc_ax.tick_params(labelsize=7)
                _mc_ax.legend(fontsize=7, loc="upper left")
                _mc_ax.spines["top"].set_visible(False)
                _mc_ax.spines["right"].set_visible(False)
                _mc_ax.grid(True, linestyle="--", alpha=0.3)
                _mc_fig.tight_layout()

                _mc_buf = io.BytesIO()
                _mc_fig.savefig(_mc_buf, format="png", dpi=150, bbox_inches="tight")
                plt.close(_mc_fig)
                _mc_buf.seek(0)

                pdf.set_font("Helvetica", "I", 8)
                pdf.set_text_color(80, 80, 80)
                pdf.cell(0, 5, "Luck & Timing Roulette -- 1,000 simulated market scenarios",
                         ln=True)
                pdf.set_text_color(0, 0, 0)
                pdf.image(_mc_buf, x=15, w=180)
                pdf.ln(2)

            # Budget summary
            section_header("MONTHLY BUDGET SUMMARY")
            row("Take-Home Pay:", f"${take_home:,.0f}")
            row("Fixed Costs:", f"${fixed_costs:,.0f}")
            row("Investments / Savings:", f"${invested:,.0f}")
            row("Guilt-Free Spending:", f"${guilt_free:,.0f}")
            _status = "SURPLUS" if surplus >= 0 else "DEFICIT"
            row(f"Budget {_status}:", f"${abs(surplus):,.0f} / month")
            pdf.ln(3)

            # Budget bar chart
            if take_home > 0:
                _surplus_plot = max(0.0, surplus)
                _vals = [fixed_costs, invested, guilt_free, _surplus_plot]
                _labels = ["Fixed", "Invested", "Guilt-Free", "Surplus"]
                _colors = ["#ef476f", "#00b4d8", "#ffd166", "#06d6a0"]
                _total = sum(_vals) if sum(_vals) > 0 else 1

                _bar_fig, _bar_ax = plt.subplots(figsize=(7.2, 0.9))
                _bar_fig.patch.set_facecolor("white")
                _bar_ax.set_facecolor("white")
                _left = 0
                for _v, _lbl, _c in zip(_vals, _labels, _colors):
                    if _v > 0:
                        _bar_ax.barh(
                            0, _v / _total, left=_left / _total,
                            color=_c, height=0.5,
                            label=f"{_lbl} ${_v:,.0f}",
                        )
                        _left += _v
                _bar_ax.set_xlim(0, 1)
                _bar_ax.axis("off")
                _bar_ax.legend(
                    loc="upper center", bbox_to_anchor=(0.5, -0.05),
                    ncol=4, fontsize=7, frameon=False,
                )
                if surplus < 0:
                    _bar_ax.set_title(
                        f"Budget deficit: ${abs(surplus):,.0f}/month",
                        fontsize=8, color="#ef476f",
                    )
                _bar_fig.tight_layout()

                _bar_buf = io.BytesIO()
                _bar_fig.savefig(_bar_buf, format="png", dpi=150, bbox_inches="tight")
                plt.close(_bar_fig)
                _bar_buf.seek(0)
                pdf.image(_bar_buf, x=15, w=180)
                pdf.ln(2)

            # Disclaimer bottom of page 1
            pdf.set_font("Helvetica", "I", 7)
            pdf.set_text_color(140, 140, 140)
            pdf.multi_cell(180, 4, safe(
                "Projections use primary-zone promotion timelines, historical TSP fund "
                "return averages, and a 4% safe withdrawal rate. Actual results will vary. "
                "Consult a Certified Financial Planner for personalized advice."
            ))
            pdf.set_text_color(0, 0, 0)

            # ── PAGE 2 -- CHECKLIST ──────────────────────────────────────────
            pdf.add_page()
            page_header()

            section_header("YOUR FINANCIAL ORDER OF OPERATIONS")
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(0, 5, "Crawl, walk, run. Work these in order.", ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(2)

            _BOX = 4     # checkbox square size
            _LH = 6      # line height
            _IND = 22     # text indent from left margin

            def checklist_group(title):
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_fill_color(235, 240, 250)
                pdf.set_text_color(30, 60, 114)
                pdf.cell(0, 6, safe(f"  {title}"), fill=True, ln=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)

            def checklist_item(text, link=None):
                _y = pdf.get_y()
                pdf.set_draw_color(100, 100, 100)
                pdf.rect(15, _y + 1, _BOX, _BOX)
                pdf.set_font("Helvetica", "", 8.5)
                pdf.set_xy(_IND, _y)
                full = f"{text}  {link}" if link else text
                pdf.multi_cell(180 - (_IND - 15), _LH, safe(full))
                pdf.ln(0.5)

            checklist_group("CRAWL -- Do all four simultaneously")
            checklist_item(
                "Get CAC access, log into MyPay, set TSP to at least 5% to "
                "capture full BRS match",
                "mypay.dfas.mil",
            )
            checklist_item("Open a high-yield savings account and get to $1,000")
            checklist_item(
                "Check pre-service debt for SCRA interest rate protection",
                "justice.gov/servicemembers",
            )
            checklist_item(
                "Kill high-interest debt -- Avalanche or Snowball, pick one and commit"
            )
            pdf.ln(2)

            checklist_group("WALK -- In order")
            checklist_item(
                "Build the full emergency fund -- 3 to 6 months of expenses in your HYSA"
            )
            checklist_item(
                "Check TSP fund allocation -- Contribution Allocation AND "
                "Interfund Transfer",
                "tsp.gov",
            )
            checklist_item(
                "Set your savings rate in MyPay and automate it",
                "mypay.dfas.mil",
            )
            pdf.ln(2)

            checklist_group("RUN -- Once the walk phase is solid")
            checklist_item(
                "Get your paperwork right -- JAG will, POA, SGLI beneficiary, "
                "TSP beneficiary",
                "milconnect.dmdc.osd.mil",
            )
            checklist_item(
                "Know your GI Bill transfer eligibility date -- decide and "
                "set a calendar reminder",
                "va.gov/education/transfer-post-9-11-gi-bill-benefits",
            )
            checklist_item(
                "Understand your VA benefits before you separate",
                "va.gov/benefits",
            )
            checklist_item(
                "Build beyond the plan -- max retirement accounts, real estate, "
                "goal-based saving",
                "reddit.com/r/financialindependence",
            )
            pdf.ln(4)

            pdf.set_font("Helvetica", "I", 7)
            pdf.set_text_color(140, 140, 140)
            pdf.multi_cell(180, 4, safe(
                "This document is for educational purposes only and does not "
                "constitute financial advice. "
                "F.I.R.E. for Effect -- fireforeffect.app"
            ))

            # ── Output ───────────────────────────────────────────────────────
            pdf_bytes = pdf.output()
            st.download_button(
                label="\u2B07\uFE0F Download Your Financial Plan (PDF)",
                data=bytes(pdf_bytes),
                file_name=f"fire_for_effect_{datetime.date.today()}.pdf",
                mime="application/pdf",
            )
            st.success("\u2705 PDF ready -- click above to download.")
