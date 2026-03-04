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

# Initialize session state for data persistence
for key in ["base_pay", "bah_amt", "bas_amt", "pmt_target"]:
    if key not in st.session_state: st.session_state[key] = 0.0

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
    # Base Pay
    rank_data = DATA.get("base_pay", {}).get(rank, {})
    base = rank_data.get(str(snapped), 0.0)
    # BAS
    bas = CONFIG["bas_officer"] if ("O" in rank or "W" in rank) else CONFIG["bas_enlisted"]
    # BAH
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

tab1, tab2, tab3 = st.tabs(["💰 Income Calculator", "📈 Retirement Goal", "⚖️ Conscious Spending Plan"])

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
        st.session_state.base_pay = base
        st.session_state.bas_amt = bas
        st.session_state.bah_amt = bah
        
        gross = base + bas + bah
        st.success(f"### Total Monthly Gross: ${gross:,.2f}")
        c_a, c_b, c_c = st.columns(3)
        c_a.metric("Base Pay", f"${base:,.2f}")
        c_b.metric("BAH (Tax-Free)", f"${bah:,.2f}")
        c_c.metric("BAS (Tax-Free)", f"${bas:,.2f}")

# --- TAB 2: RETIREMENT ---
with tab2:
    st.header("Step 2: Retirement & Pension Target")
    st.write("Calculate your 'Gap'—the monthly income your TSP/Savings must provide *after* your pension.")
    
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
        current_tsp = st.number_input("Current Value of TSP/IRAs/Retirement Accounts ($)", value=10000, step=1000)
        monthly_goal = st.number_input("Total Desired Monthly Income ($)", value=8000, step=500)
        
        # --- PENSION MATH ---
        est_pension = st.session_state.base_pay * (yrs_at_retire * multiplier)
        st.metric("Projected Monthly Pension", f"${est_pension:,.2f}")

    # --- THE "GAP" CALCULATION ---
    years_to_grow = age_at_retire - current_age
    
    if years_to_grow > 0:
        # 1. Income Gap
        monthly_income_gap = max(0, monthly_goal - est_pension)
        
        # 2. Total Nest Egg Needed (4% Rule)
        total_nest_egg_needed = (monthly_income_gap * 12) / 0.04
        
        # 3. Future Value of Current Savings (Assuming 7% annual return)
        annual_return = 0.07
        fv_current_savings = current_tsp * ((1 + annual_return) ** years_to_grow)
        
        # 4. Final Funding Gap (Total Needed minus what Current Savings will become)
        final_funding_gap = max(0, total_nest_egg_needed - fv_current_savings)
        
        # 5. Solve for Monthly Contribution (PMT)
        r = annual_return / 12
        n = years_to_grow * 12
        if final_funding_gap > 0:
            required_pmt = (final_funding_gap * r) / (((1 + r) ** n) - 1)
        else:
            required_pmt = 0.0

        st.divider()
        st.session_state.pmt_target = required_pmt
        
        # Result Metrics
# --- RESULTS SUMMARY ---
st.divider()
st.session_state.pmt_target = required_pmt

res_col1, res_col2, res_col3 = st.columns(3)
res_col1.metric("Goal Nest Egg", f"${total_nest_egg_needed:,.0f}")
res_col2.metric("Future Value", f"${fv_current_savings:,.0f}")
res_col3.metric("Monthly Investment", f"${required_pmt:,.2f}", delta="Sent to Budget")

st.success(
    f"""
### 🎯 Retirement Reality Check

- **Current Balance:** \\${current_tsp:,.0f} is projected to grow to **\\${fv_current_savings:,.0f}** by age **{age_at_retire}**.
- **The Target:** This covers a large portion of your **\\${total_nest_egg_needed:,.0f}** goal.
- **The Action:** To bridge the remaining gap, you need to invest **\\${required_pmt:,.2f}** per month.
"""
)
# --- TAB 3: REALITY CHECK (CONSCIOUS SPENDING) ---
with tab3:
    st.header("Step 3: Conscious Spending Plan")
    
    # Take-Home Logic
    pay_mode = st.radio("How should we calculate your net income?", 
                        ["Generalized Tax Estimate (22% on Base Pay)", "Manual Entry (Exact Net from LES)"], 
                        horizontal=True)
    
    if pay_mode == "Manual Entry (Exact Net from LES)":
        take_home = st.number_input("Monthly Net Take-Home (After taxes/TSP/Insurance)", value=5000.0)
    else:
        # 22% estimate on Base Pay only; Allowances are tax-free
        est_net_base = st.session_state.base_pay * 0.78
        take_home = est_net_base + st.session_state.bas_amt + st.session_state.bah_amt
        st.info(f"Estimated Monthly Take-Home: **${take_home:,.2f}**")

    st.divider()

    # Column Organization
    col_a, col_b, col_c = st.columns(3)
    
    bp = st.session_state.base_pay if st.session_state.base_pay > 0 else (take_home * 0.6)

    with col_a:
        st.subheader("🛑 Fixed Costs")
        # Automating based on PRD anchors
        housing = st.number_input("Housing + Utilities", value=float(st.session_state.bah_amt))
        trans = st.number_input("Transportation (Car/Insurance/Fuel)", value=bp * 0.15)
        health = st.number_input("Healthcare", value=bp * 0.08)
        ins_fin = st.number_input("Insurance + Financial Fees", value=bp * 0.05)
        debt = st.number_input("Min Debt Payments", value=0.0)
        essentials = st.number_input("Household (Phone/Internet/Toiletries)", value=bp * 0.07)
        kids = st.number_input("Kids / Childcare / Education", value=0.0)
        groceries = st.number_input("Groceries (Food at Home)", value=bp * 0.13)
        fixed_total = housing + trans + health + ins_fin + debt + essentials + kids + groceries

    with col_b:
        st.subheader("🚀 Investments & Savings")
        retirement = st.number_input("Retirement (TSP/IRA(Don't Forget Automatic Contributions in MyPay!))", value=float(st.session_state.pmt_target))
        brokerage = st.number_input("Brokerage/Taxable Investing", value=take_home * 0.05)
        emergency = st.number_input("Emergency Fund", value=take_home * 0.02)
        sinking = st.number_input("Travel/Fun Fund)", value=take_home * 0.07)
        goals = st.number_input("Additional Savings/529/Education", value=0.0)
        save_invest_total = retirement + brokerage + emergency + sinking + goals

    with col_c:
        st.subheader("🍹 Guilt-Free Spending")
        dining = st.number_input("Dining Out", value=take_home * 0.04)
        fun = st.number_input("Entertainment / Hobbies", value=take_home * 0.04)
        subs = st.number_input("Subscriptions", value=50.0)
        gifts = st.number_input("Gifts", value=take_home * 0.02)
        travel_spend = st.number_input("Travel", value=take_home * 0.03)
        fun_total = dining + fun + subs + gifts + travel_spend

    # --- RESULTS & VISUALIZATION ---
    st.divider()
    total_spent = fixed_total + save_invest_total + fun_total
    remainder = take_home - total_spent
    
    # Prep chart data
    chart_df = pd.DataFrame({
        'Category': ['Fixed Costs', 'Invest/Save', 'Guilt-Free'],
        'Actual %': [
            (fixed_total / take_home * 100) if take_home > 0 else 0,
            (save_invest_total / take_home * 100) if take_home > 0 else 0,
            (fun_total / take_home * 100) if take_home > 0 else 0
        ],
        'Ideal Target %': [60, 20, 20]
    })

    st.subheader("Budget Utilization vs. Conscious Spending Ideals")
    
    base_chart = alt.Chart(chart_df).encode(x=alt.X('Category:N', title=None))
    
    bars = base_chart.mark_bar(color='#1f77b4', cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
        y=alt.Y('Actual %:Q', title='Percentage of Income (%)', scale=alt.Scale(domain=[0, 100])),
        tooltip=['Category', alt.Tooltip('Actual %:Q', format='.1f')]
    )

    # The Red "Ideal" Marker
    rules = base_chart.mark_tick(color='red', thickness=4, size=40).encode(y='Ideal Target %:Q')

    st.altair_chart(bars + rules, use_container_width=True)

    res1, res2, res3 = st.columns(3)
    res1.metric("Take-Home Pay", f"${take_home:,.2f}")
    res2.metric("Total Spending", f"${total_spent:,.2f}")
    
    if remainder >= 0:
        res3.metric("Monthly Surplus", f"${remainder:,.2f}", delta_color="normal")
        st.success("✅ You are living within your means.")
    else:
        res3.metric("Monthly Shortfall", f"-${abs(remainder):,.2f}", delta_color="inverse")
        st.error("🚨 Warning: Expenses exceed income. Adjust Fixed Costs or Guilt-Free Spending.")