import streamlit as st
import json
import pandas as pd
import altair as alt

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="2026 Military Reality Check", page_icon="🎖️", layout="wide")

CONFIG = {
    "ranks": ["E-1", "E-2", "E-3", "E-4", "E-5", "E-6", "E-7", "E-8", "E-9", 
              "W-1", "W-2", "W-3", "W-4", "W-5", 
              "O-1", "O-1E", "O-2", "O-2E", "O-3", "O-3E", "O-4", "O-5", "O-6", "O-7"],
    "bas_enlisted": 515.00,
    "bas_officer": 360.00,
}

# Persistent State
if "base_pay" not in st.session_state: st.session_state.base_pay = 0.0
if "bah_amt" not in st.session_state: st.session_state.bah_amt = 0.0
if "bas_amt" not in st.session_state: st.session_state.bas_amt = 0.0
if "pmt_target" not in st.session_state: st.session_state.pmt_target = 0.0

# --- 2. DATA UTILITIES ---
@st.cache_data
def load_military_data():
    try:
        with open('military_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Data file missing. Please ensure 'military_data.json' is in the folder.")
        return {"base_pay": {}, "zip_to_mha": {}, "bah_rates": {}}

DATA = load_military_data()

def get_snapped_tis(tis):
    brackets = [0, 2, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40]
    for b in reversed(brackets):
        if tis >= b: return b
    return 0

def get_military_pay(rank, tis, zip_code, has_dep):
    snapped = get_snapped_tis(tis)
    rank_data = DATA.get("base_pay", {}).get(rank, {})
    base = rank_data.get(str(snapped), 0.0)
    bas = CONFIG["bas_officer"] if ("O" in rank or "W" in rank) else CONFIG["bas_enlisted"]
    zip_info = DATA.get("zip_to_mha", {}).get(zip_code)
    bah = 0.0
    if zip_info:
        mha_code = zip_info["mha"]
        dep_key = "with" if has_dep else "without"
        bah = DATA.get("bah_rates", {}).get(mha_code, {}).get(rank, {}).get(dep_key, 0.0)
    return float(base), float(bas), float(bah)

# --- 3. UI LAYOUT ---
st.title("🎖️ 2026 Military Reality Check")
st.markdown("---")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💰 Income Calculator", "📈 Retirement Goal", "⚖️ Conscious Spending Plan",
    "🧠 FinLit Quiz", "🗺️ Action Plan", "📬 Feedback & AAR"
])

# --- TAB 1: INCOME ---
with tab1:
    st.header("Step 1: Calculate Your 2026 Pay")
    col1, col2 = st.columns(2)
    with col1:
        rank = st.selectbox("Current or Target Rank", CONFIG["ranks"], index=4)
        tis = st.number_input("Years of Service (TIS)", 0, 40, 4)
    with col2:
        zip_code = st.text_input("Duty Station Zip Code", "92136")
        dep = st.checkbox("With Dependents?", value=True)

    if st.button("Calculate Monthly Income"):
        base, bas, bah = get_military_pay(rank, tis, zip_code, dep)
        st.session_state.base_pay, st.session_state.bas_amt, st.session_state.bah_amt = base, bas, bah
        gross = base + bas + bah
        st.success(f"### Total Monthly Gross: \\${gross:,.2f}")
        c_a, c_b, c_c = st.columns(3)
        c_a.metric("Base Pay", f"${base:,.2f}")
        c_b.metric("BAH (Tax-Free)", f"${bah:,.2f}")
        c_c.metric("BAS (Tax-Free)", f"${bas:,.2f}")

# --- TAB 2: RETIREMENT ---
with tab2:
    st.header("Step 2: Retirement & Pension Target")
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("The Career Timeline")
        retire_system = st.radio("Retirement System", ["BRS (2.0%)", "Legacy / High-3 (2.5%)"], horizontal=True)
        multiplier = 0.02 if "BRS" in retire_system else 0.025
        current_age = st.slider("Current Age", 18, 60, 25)
        yrs_at_retire = st.slider("Total Years of Service at Retirement", 20, 40, 20)
        age_at_retire = st.slider("Age when you stop working", 38, 75, 60)
    with col_r:
        st.subheader("Current Assets & Goals")
        current_tsp = st.number_input("Current Value of TSP/IRAs ($)", value=10000, step=1000)
        monthly_goal = st.number_input("Total Desired Monthly Income ($)", value=8000, step=500)
        est_pension = st.session_state.base_pay * (yrs_at_retire * multiplier)
        st.metric("Projected Monthly Pension", f"${est_pension:,.2f}")

    years_to_grow = age_at_retire - current_age
    if years_to_grow > 0:
        monthly_income_gap = max(0, monthly_goal - est_pension)
        total_nest_egg_needed = (monthly_income_gap * 12) / 0.04
        fv_current_savings = current_tsp * ((1.07) ** years_to_grow)
        final_funding_gap = max(0, total_nest_egg_needed - fv_current_savings)
        r, n = 0.07 / 12, years_to_grow * 12
        required_pmt = (final_funding_gap * r) / (((1 + r) ** n) - 1) if final_funding_gap > 0 else 0.0
        st.session_state.pmt_target = required_pmt
        st.divider()
        res_col1, res_col2, res_col3 = st.columns(3)
        res_col1.metric("Goal Nest Egg", f"${total_nest_egg_needed:,.0f}")
        res_col2.metric("Future Value", f"${fv_current_savings:,.0f}")
        res_col3.metric("Required Investment", f"${required_pmt:,.2f}", delta="Sent to Budget")
    else:
        st.error("Retirement age must be in the future.")

# --- TAB 3: CONSCIOUS SPENDING ---
with tab3:
    st.header("Step 3: Conscious Spending Plan")
    pay_mode = st.radio("Calculation Mode", ["Generalized Tax Estimate (22% on Base)", "Manual Entry"], horizontal=True)
    if pay_mode == "Manual Entry":
        take_home = st.number_input("Monthly Net Take-Home", value=5000.0)
    else:
        take_home = (st.session_state.base_pay * 0.78) + st.session_state.bas_amt + st.session_state.bah_amt
    st.info(f"Estimated Monthly Take-Home: **\\${take_home:,.2f}**")
    
    st.divider()
    col_a, col_b, col_c = st.columns(3)
    bp = st.session_state.base_pay if st.session_state.base_pay > 0 else (take_home * 0.6)
    
    with col_a:
        st.subheader("🛑 Fixed Costs")
        housing = st.number_input("Housing + Utilities", value=float(st.session_state.bah_amt))
        trans = st.number_input("Car/Insurance/Fuel", value=bp * 0.15)
        health = st.number_input("Healthcare", value=bp * 0.08)
        groceries = st.number_input("Groceries", value=bp * 0.13)
        fixed_total = housing + trans + health + groceries
        fixed_pct = (fixed_total / take_home * 100) if take_home > 0 else 0
        st.metric("Total Fixed", f"${fixed_total:,.2f}", f"{fixed_pct:.1f}%")

    with col_b:
        st.subheader("🚀 Invest/Save")
        retirement = st.number_input("Retirement (TSP/IRA)", value=float(st.session_state.pmt_target))
        emergency = st.number_input("Emergency Savings", value=take_home * 0.05)
        save_invest_total = retirement + emergency
        save_pct = (save_invest_total / take_home * 100) if take_home > 0 else 0
        st.metric("Total Invested", f"${save_invest_total:,.2f}", f"{save_pct:.1f}%")

    with col_c:
        st.subheader("🍹 Guilt-Free")
        fun_total = st.number_input("Fun/Dining/Travel", value=take_home * 0.15)
        fun_pct = (fun_total / take_home * 100) if take_home > 0 else 0
        st.metric("Guilt-Free Total", f"${fun_total:,.2f}", f"{fun_pct:.1f}%")

    # --- Chart ---
    chart_df = pd.DataFrame({
        'Category': ['Fixed Costs', 'Invest/Save', 'Guilt-Free'],
        'Actual %': [fixed_pct, save_pct, fun_pct],
        'Ideal Target %': [60, 20, 20]
    })
    st.subheader("Budget Utilization vs. Conscious Spending Ideals")
    c = alt.Chart(chart_df).mark_bar().encode(
        x=alt.X('Category', sort=None),
        y=alt.Y('Actual %', scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('Category', scale=alt.Scale(range=['#e74c3c', '#2ecc71', '#3498db']))
    )
    st.altair_chart(c, use_container_width=True)

# --- TAB 4: FINLIT QUIZ ---
with tab4:
    st.header("Step 4: Financial Readiness Quiz")
    with st.form("finlit_quiz"):
        st.markdown("### The Basics")
        q1 = st.radio("1. BRS Matching Max %?", ["0%", "3%", "4%", "5%"], index=None)
        q2 = st.radio("2. Tax-Free Allowances?", ["Bonuses", "BAH and BAS", "Special Pay"], index=None)
        q3 = st.radio("3. Selling leave pays:", ["Base+BAH+BAS", "Just Base Pay", "Double Base"], index=None)
        
        st.markdown("### The TSP")
        q4 = st.radio("4. Default fund for new accessions?", ["G Fund", "L Fund", "C Fund"], index=None)
        q5 = st.radio("5. Roth Difference?", ["Roth = Taxes Now", "Roth = Taxes Later"], index=None)
        q6 = st.radio("6. Max TSP Base Pay %?", ["5%", "15%", "Literally all of it"], index=None)
        
        st.markdown("### Debt & Credit")
        q7 = st.radio("7. SCRA Interest Cap?", ["0%", "6%", "10%"], index=None)
        q8 = st.radio("8. SDP Rate?", ["5%", "10%", "15%"], index=None)
        q9 = st.radio("9. E-Fund Target?", ["$500", "3-6 months essentials"], index=None)
        q10 = st.radio("10. Hurts credit score?", ["Checking score", "Maxing out cards"], index=None)
        q11 = st.radio("11. Dealership 24% APR?", ["Good deal", "Paying double car value"], index=None)
        q12 = st.radio("12. Realistic car rate?", ["0%", "4% - 8%", "20%"], index=None)
        q13 = st.multiselect("13. Increases score? (Select all)", ["Paying full", "Old cards open", "Auto-pay"])
        q14 = st.radio("14. Worst E-Fund spot?", ["HYSA", "Regular Checking"], index=None)
        
        st.markdown("### Big Benefits")
        q15 = st.radio("15. GI Bill benefit?", ["Laptop", "BAH at E-5 rate"], index=None)
        q16 = st.radio("16. Transfer Catch?", ["Immediately", "6 yrs in + 4 MORE years"], index=None)
        q17 = st.radio("17. VA Loan reality?", ["0 out of pocket", "Need cash for repairs/closing"], index=None)
        q18 = st.radio("18. Waive Funding Fee?", ["10%+ Disability", "CO request"], index=None)
        q19 = st.radio("19. Multi-family VA?", ["No", "Yes, if resident"], index=None)
        
        submitted = st.form_submit_button("Submit Answers")
        if submitted:
            score = 0
            if q1 == "5%": score += 1
            if q2 == "BAH and BAS": score += 1
            if q3 == "Just Base Pay": score += 1
            if q4 == "L Fund": score += 1
            if q5 == "Roth = Taxes Now": score += 1
            if q6 == "Literally all of it": score += 1
            if q7 == "6%": score += 1
            if q8 == "10%": score += 1
            if q9 == "3-6 months essentials": score += 1
            if q10 == "Maxing out cards": score += 1
            if q11 == "Paying double car value": score += 1
            if q12 == "4% - 8%": score += 1
            if "Paying full" in str(q13): score += 1
            if q14 == "Regular Checking": score += 1
            if q15 == "BAH at E-5 rate": score += 1
            if q16 == "6 yrs in + 4 MORE years": score += 1
            if q17 == "Need cash for repairs/closing": score += 1
            if q18 == "10%+ Disability": score += 1
            if q19 == "Yes, if resident": score += 1
            
            p = int((score/19)*100)
            st.metric("Final Score", f"{score}/19")
            if score >= 17: st.success(f"🏆 Nerd! Top {100-p}% status. You'll be wealthy.")
            elif score >= 13: st.info("Solid. You're safe from the Mustang trap.")
            else: st.error("🚨 Hit Tab 5. Now.")

# --- TAB 5: ACTION PLAN ---
with tab5:
    st.header("Step 5: Action Plan")
    st.checkbox("1. Budget created (Tab 3)", value=True)
    st.checkbox("2. SCRA Interest check (6% cap)")
    st.checkbox("3. Starter E-Fund ($1k)")
    st.checkbox("4. TSP Match set to 5%")
    st.checkbox("5. Debt Nuke: [Avalanche](https://www.investopedia.com/terms/d/debt-avalanche.asp) vs [Snowball](https://www.investopedia.com/articles/personal-finance/080716/debt-avalanche-vs-debt-snowball-which-best-you.asp)")
    st.checkbox("6. Full E-Fund (3-6 Months)")
    st.checkbox("7. Deploy? Max SDP (10% Guaranteed)")
    st.checkbox("8. Set TSP for retirement gap")
    st.checkbox("9. GI Bill Transfer evaluation")
    st.checkbox("10. HYSA for short-term goals")
    st.checkbox("11. Term Life Insurance setup")
    st.checkbox("12. Wealth building/Real Estate")


# --- TAB 6: FEEDBACK & AAR ---
with tab6:
    st.header("Step 6: After Action Review (AAR)")
    st.write("Got a question? Found a bug? Want a new feature added to the app? Drop it below.")
    
    contact_form = """
    <form action="https://formsubmit.co/ian.moss@nps.edu" method="POST">
        <input type="hidden" name="_captcha" value="false">
        <input type="hidden" name="_subject" value="New Fire For Effect App Feedback!">
        <input type="text" name="name" placeholder="Your Name/Callsign (Optional)" style="width: 100%; padding: 10px; margin-bottom: 10px; border-radius: 5px; border: 1px solid #ccc;">
        <input type="email" name="email" placeholder="Your Email (If you want a reply)" style="width: 100%; padding: 10px; margin-bottom: 10px; border-radius: 5px; border: 1px solid #ccc;">
        <textarea name="message" placeholder="Questions, comments, or brilliant ideas go here..." rows="5" required style="width: 100%; padding: 10px; margin-bottom: 10px; border-radius: 5px; border: 1px solid #ccc;"></textarea>
        <button type="submit" style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">Send to the Developer</button>
    </form>
    """
    st.markdown(contact_form, unsafe_allow_html=True)
