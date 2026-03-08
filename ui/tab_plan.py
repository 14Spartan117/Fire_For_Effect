"""
Tab 7 -- Your Plan (PDF snapshot)
"""

import datetime
import streamlit as st

from analytics import log_session


def render_tab_plan(container):
    with container:
        ss = st.session_state
        ss.tabs_visited.add(7)
        ss.max_tab_reached = max(ss.max_tab_reached, 7)
        st.header("\U0001F4C4 Your Plan")
        st.caption(
            "A snapshot of your numbers from each tab -- income, retirement targets, and budget. "
            "Download it as a PDF to keep, share, or brief your spouse."
        )

        # ── Check data readiness ─────────────────────────────────────────────
        missing = []
        if ss.get("base_pay", 0.0) == 0.0:
            missing.append("**What You Make** -- complete your rank, TIS, and zip code")
        if ss.get("pmt_target", 0.0) == 0.0:
            missing.append("**Retirement Goal Setting** -- complete your career inputs and fund allocation")
        if ss.get("tab3_take_home", 0.0) == 0.0:
            missing.append("**Where Does It Go?** -- enter your take-home pay")

        if missing:
            st.warning(
                "Complete the following tabs before generating your plan:\n\n"
                + "\n".join(f"- {m}" for m in missing)
            )
            return

        # ── Pull data ─────────────────────────────────────────────────────────
        base_pay = ss.get("base_pay", 0.0)
        bah_amt = ss.get("bah_amt", 0.0)
        bas_amt = ss.get("bas_amt", 0.0)
        special_pay = ss.get("special_pay", 0.0)
        gross_monthly = base_pay + bah_amt + bas_amt + special_pay

        pmt_target = ss.get("pmt_target", 0.0)
        savings_rate = ss.get("savings_rate_pct", 0.0)
        nest_egg = ss.get("nest_egg_target", 0.0)
        est_pension = ss.get("est_pension", 0.0)
        success_prob = ss.get("mc_success_rate", None)

        take_home = ss.get("tab3_take_home", 0.0)
        fixed_costs = ss.get("tab3_fixed", 0.0)
        invested = ss.get("tab3_invested", 0.0)
        guilt_free = ss.get("tab3_guilt_free", 0.0)
        surplus = take_home - fixed_costs - invested - guilt_free

        on_track = surplus >= 0 and invested >= pmt_target * 0.9

        if on_track:
            way_forward = (
                f"Based on your numbers, you're in a strong position. Your budget has a "
                f"${surplus:,.0f}/month surplus and your investments are on pace. Set your TSP "
                f"contribution to {savings_rate*100:.1f}% of base pay in MyPay and leave it alone. "
                "Every promotion is an opportunity to increase your contribution rate -- not your spending."
            )
            st.success(way_forward)
        else:
            shortfall = max(0, pmt_target - invested)
            way_forward = (
                f"Your numbers show there's work to do -- your budget is "
                f"{'in deficit by $' + f'{abs(surplus):,.0f}/month' if surplus < 0 else 'tight'} "
                f"and your investments are ${shortfall:,.0f}/month short of your goal. "
                "Start with the BRS match, eliminate high-interest debt, then automate your savings rate."
            )
            st.warning(way_forward)

        # ── PDF generation ────────────────────────────────────────────────────
        if st.button("\U0001F4E5 Generate & Download PDF", type="primary"):
            ss.pdf_downloaded = True
            if not ss.session_logged:
                ss.session_logged = True
                log_session()

            from fpdf import FPDF

            pdf = FPDF()
            pdf.add_page()
            pdf.set_margins(15, 15, 15)

            def safe(text):
                return (
                    text
                    .replace("\u2014", "-").replace("\u2013", "-")
                    .replace("\u2190", "<-").replace("\u2192", "->")
                    .replace("\u2019", "'").replace("\u2018", "'")
                    .replace("\u201c", '"').replace("\u201d", '"')
                    .replace("\u2026", "...")
                )

            pdf.set_font("Helvetica", "B", 18)
            pdf.set_fill_color(30, 60, 114)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(0, 12, safe("F.I.R.E. for Effect - Your Financial Plan"),
                     fill=True, ln=True, align="C")
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(0, 6, safe(
                f"Generated {datetime.date.today().strftime('%B %d, %Y')}  |  "
                "For planning purposes only - not financial advice."
            ), ln=True, align="C")
            pdf.ln(4)

            def section_header(title):
                pdf.set_font("Helvetica", "B", 11)
                pdf.set_fill_color(220, 230, 245)
                pdf.cell(0, 7, safe(f"  {title}"), fill=True, ln=True)
                pdf.ln(1)

            def row(label, value, indent=4):
                pdf.set_font("Helvetica", "B", 9)
                pdf.cell(80, 6, safe(" " * indent + label), ln=False)
                pdf.set_font("Helvetica", "", 9)
                pdf.cell(0, 6, safe(value), ln=True)

            section_header("INCOME SNAPSHOT")
            row("Monthly Gross Pay:", f"${gross_monthly:,.0f}")
            row("  Base Pay:", f"${base_pay:,.0f}")
            row("  BAH (Tax-Free):", f"${bah_amt:,.0f}")
            row("  BAS (Tax-Free):", f"${bas_amt:,.0f}")
            row("  Special Pays:", f"${special_pay:,.0f}")
            pdf.ln(2)

            section_header("RETIREMENT TARGETS")
            row("Estimated Monthly Pension:", f"${est_pension:,.0f}  (High-3 Average)")
            row("Target Nest Egg:", f"${nest_egg:,.0f}")
            row("Required Savings Rate:",
                f"{savings_rate*100:.1f}% of Base Pay  <- Set this in MyPay" if savings_rate else "N/A")
            if success_prob is not None:
                row("Monte Carlo Probability of Success:", f"{success_prob:.0f}%")
            pdf.ln(2)

            section_header("MONTHLY BUDGET SUMMARY")
            row("Take-Home Pay:", f"${take_home:,.0f}")
            row("Fixed Costs:", f"${fixed_costs:,.0f}")
            row("Investments / Savings:", f"${invested:,.0f}")
            row("Guilt-Free Spending:", f"${guilt_free:,.0f}")
            status = "SURPLUS" if surplus >= 0 else "DEFICIT"
            row(f"Budget {status}:", f"${abs(surplus):,.0f}/month")
            pdf.ln(2)

            section_header("YOUR WAY FORWARD")
            pdf.set_font("Helvetica", "", 9)
            pdf.set_x(15)
            pdf.multi_cell(180, 5, safe(way_forward))
            pdf.ln(2)

            section_header("PRIORITY ACTIONS")
            if on_track:
                actions = [
                    f"Set TSP contribution to {savings_rate*100:.1f}% of base pay in MyPay",
                    "Verify TSP fund allocation matches your plan (Interfund Transfer if needed)",
                    "After every promotion -- increase savings rate, not spending",
                    "Keep emergency fund in a High-Yield Savings Account (HYSA)",
                ]
            else:
                actions = [
                    "Secure your 5% BRS match in MyPay immediately -- this is free money",
                    "Identify and cut the largest negotiable fixed cost (housing, vehicle)",
                    "Eliminate all debt above 8% APR before increasing discretionary spending",
                    f"Work toward {savings_rate*100:.1f}% TSP contribution -- start lower, increase with promotions",
                    "Review full Way Ahead checklist in the app for step-by-step guidance",
                ]
            for i, action in enumerate(actions, 1):
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_x(15)
                pdf.cell(8, 5, f"{i}.", ln=False)
                pdf.set_font("Helvetica", "", 9)
                pdf.multi_cell(167, 5, safe(action))
                pdf.set_x(15)

            pdf.ln(3)
            pdf.set_font("Helvetica", "I", 7)
            pdf.set_text_color(120, 120, 120)
            pdf.multi_cell(180, 4, safe(
                "This document is for educational purposes only. Projections use simplified assumptions "
                "including primary-zone promotion timelines, historical TSP fund return averages, and a "
                "4% safe withdrawal rate. Actual results will vary. Consult a Certified Financial Planner "
                "for personalized advice."
            ))

            pdf_bytes = pdf.output()
            st.download_button(
                label="\u2B07\uFE0F Download Your Financial Plan (PDF)",
                data=bytes(pdf_bytes),
                file_name=f"military_financial_plan_{datetime.date.today()}.pdf",
                mime="application/pdf",
            )
            st.success("\u2705 PDF ready -- click above to download.")

        st.divider()

        # ── On-screen preview ─────────────────────────────────────────────────
        st.subheader("\U0001F4CA Snapshot Preview")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown("**\U0001F4B0 Income**")
            st.metric("Monthly Gross", f"${gross_monthly:,.0f}")
            st.metric("Base Pay", f"${base_pay:,.0f}")
            st.metric("BAH", f"${bah_amt:,.0f}")
            st.metric("BAS", f"${bas_amt:,.0f}")
        with col_b:
            st.markdown("**\U0001F4C8 Retirement**")
            st.metric("Est. Monthly Pension", f"${est_pension:,.0f}")
            st.metric("Target Nest Egg", f"${nest_egg:,.0f}")
            st.metric("Required Savings Rate",
                      f"{savings_rate*100:.1f}% of Base Pay" if savings_rate else "--")
            if success_prob is not None:
                st.metric("Monte Carlo Success", f"{success_prob:.0f}%")
        with col_c:
            st.markdown("**\u2696\uFE0F Budget**")
            st.metric("Take-Home", f"${take_home:,.0f}")
            st.metric("Fixed Costs", f"${fixed_costs:,.0f}")
            st.metric("Invested", f"${invested:,.0f}")
            delta_color = "normal" if surplus >= 0 else "inverse"
            st.metric(
                "Surplus / Deficit", f"${surplus:,.0f}",
                delta="On track" if surplus >= 0 else "Needs attention",
                delta_color=delta_color,
            )
