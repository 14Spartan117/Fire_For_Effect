import streamlit as st
import json
import pandas as pd
import altair as alt
import plotly.graph_objects as go

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
# --- TAB 1: INCOME TRUTH ---
with tab1:
    st.header("Step 1: Calculate Your 2026 Pay")

    col1, col2 = st.columns(2)
    with col1:
        rank = st.selectbox("Current Rank", CONFIG["ranks"], index=4)
        tis = st.number_input("Years of Service (TIS)", 0, 40, 4)
    with col2:
        zip_code = st.text_input("Duty Station Zip Code", "92136")
        dep = st.checkbox("With Dependents?", value=True)

    # Wrapped in an expander to keep the UI clean
    with st.expander("🎖️ Optional Special / Incentive Pays (Monthly)"):
        # --- HDIP (DFAS table: mostly fixed monthly amounts) ---
        sp1, sp2 = st.columns(2)
        with sp1:
            hdip_static = st.checkbox("HDIP: Parachute (Static Line) (+$150)")
            hdip_mff = st.checkbox("HDIP: Military Free Fall / HALO (+$225)")
            hdip_demo = st.checkbox("HDIP: Demolition (+$150)")
        with sp2:
            hfp_idp = st.checkbox("Hostile Fire / Imminent Danger Pay (up to +$225)") 
            flpb_on = st.checkbox("Foreign Language Proficiency Bonus (FLPB)")
            avip_on = st.checkbox("Aviation Incentive Pay (Army Officer AvIP)")

        # --- Conditional inputs for pays that need more detail ---
        flpb_amt = 0
        if flpb_on:
            flpb_amt = st.number_input(
                "FLPB monthly amount (enter your known amount from orders/LES)",
                min_value=0, max_value=1000, value=0, step=50,
                help="FLPB varies by language, modality, and proficiency. This field lets you use your real entitlement."
            )

        # Aviation Incentive Pay logic (FIXED INDENTATION)
        avip_amt = 0
        if avip_on:
            yas = st.number_input(
                "Years of Aviation Service (YAS)",
                min_value=0.0, max_value=40.0, value=2.0, step=0.5
            )
            # DFAS Monthly Army Officer AvIP Rates
            if yas <= 2:
                avip_amt = 125
            elif yas <= 6:
                avip_amt = 200
            elif yas <= 10:
                avip_amt = 700
            elif yas <= 22:
                avip_amt = 1000
            elif yas <= 24:
                avip_amt = 700
            else:
                avip_amt = 400

        # Dive Pay
        dive_on = st.checkbox("Diving Duty Pay")
        dive_amt = 0
        if dive_on:
            dive_category = st.selectbox(
                "Dive category (Army)",
                [
                    "Under instruction at approved dive school ($110)",
                    "Combat Diver ($215)",
                    "Diver Second Class ($150)",
                    "Salvage Diver ($175)",
                    "Diver First Class ($215)",
                    "Master Diver ($340)",
                    "Officer: Marine Diving Officer ($240)",
                    "Officer: Diving Medical Officer ($215)",
                ]
            )
            dive_map = {
                "Under instruction at approved dive school ($110)": 110,
                "Combat Diver ($215)": 215,
                "Diver Second Class ($150)": 150,
                "Salvage Diver ($175)": 175,
                "Diver First Class ($215)": 215,
                "Master Diver ($340)": 340,
                "Officer: Marine Diving Officer ($240)": 240,
                "Officer: Diving Medical Officer ($215)": 215,
            }
            dive_amt = dive_map.get(dive_category, 0)

        # SDAP
        sdap_on = st.checkbox("Special Duty Assignment Pay (SDAP) (Recruiter/Drill/etc.)")
        sdap_amt = 0
        if sdap_on:
            sdap_amt = st.number_input(
                "SDAP monthly amount (enter your known amount from LES/orders)",
                min_value=0, max_value=1000, value=0, step=25,
                help="SDAP varies by assignment and level. Use your actual entitlement for accuracy."
            )

    # --- Compute total special pays ---
    special_pay = 0
    if hdip_static: special_pay += 150
    if hdip_mff: special_pay += 225
    if hdip_demo: special_pay += 150
    if hfp_idp: special_pay += 225
    special_pay += flpb_amt 
    special_pay += avip_amt 
    special_pay += dive_amt 
    special_pay += sdap_amt 

    st.divider()

    if st.button("Calculate Monthly Income"):
        base, bas, bah = get_military_pay(rank, tis, zip_code, dep)
        
        # Saved to session state so Tab 3 can access it
        st.session_state.base_pay = base
        st.session_state.bas_amt = bas
        st.session_state.bah_amt = bah
        st.session_state.special_pay = special_pay

        gross = base + bas + bah + special_pay
        annual_gross = gross * 12

        # --- NEW DASHBOARD LAYOUT ---
        col_monthly, col_annual = st.columns(2)
        
        with col_monthly:
            st.info(f"### 🗓️ Monthly Gross\n# ${gross:,.2f}")
            
        with col_annual:
            st.success(f"### 💰 Annual Gross\n# ${annual_gross:,.2f}")

        st.write("") # Adds a little breathing room

        c_a, c_b, c_c, c_d = st.columns(4)
        c_a.metric("Base Pay", f"${base:,.2f}")
        c_b.metric("BAH (Tax-Free)", f"${bah:,.2f}")
        c_c.metric("BAS (Tax-Free)", f"${bas:,.2f}")
        c_d.metric("Special Pays", f"${special_pay:,.2f}")
# --- TAB 2: RETIREMENT ---
# --- TAB 2: RETIREMENT ---
with tab2:
    st.header("Step 2: Retirement & Pension Target")
    st.info("💡 **Reality Check:** This is a goal-setting tool to determine how much you need to save to hit your target income. It is not a crystal ball for exact market returns.")
    
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("The Career Timeline")
        retire_system = st.radio("Retirement System", ["BRS (2.0%)", "Legacy / High-3 (2.5%)"], horizontal=True)
        multiplier = 0.02 if "BRS" in retire_system else 0.025
        
        # PHASE 0 UPDATE: Expected Retirement Rank (Defaults to E-7)
        retire_rank = st.selectbox("Expected Rank at Retirement", CONFIG["ranks"], index=6)
        
        current_age = st.slider("Current Age", 18, 60, 25)
        yrs_at_retire = st.slider("Total Years of Service at Retirement", 20, 40, 20)
        age_at_retire = st.slider("Age when you stop working", 38, 75, 60)
        
    with col_r:
        st.subheader("Current Assets & Goals")
        current_tsp = st.number_input("Current Value of TSP/IRAs ($)", value=10000, step=1000)
        monthly_goal = st.number_input("Total Desired Monthly Income ($)", value=8000, step=500)
        
        # PHASE 0 UPDATE: Pension uses projected rank & TIS, acting as a High-3 proxy
        retire_base, _, _ = get_military_pay(retire_rank, yrs_at_retire, "92136", False) 
        est_pension = retire_base * (yrs_at_retire * multiplier)
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
        
        # PHASE 0 UPDATE: Assumptions Footprint
        with st.expander("🔍 See the Math & Assumptions"):
            st.markdown("""
            * **Pension Base:** Uses the 2026 Base Pay for your expected Retirement Rank and TIS (acts as a High-3 proxy).
            * **The 4% Rule:** Assumes a safe withdrawal rate of 4% per year in retirement to ensure your portfolio survives.
            * **Market Growth:** Assumes an inflation-adjusted (real) return of **7% annually** on your current and future investments.
            * **Taxes & Inflation:** All calculations are presented in today's pre-tax, real dollars to keep your baseline target clear and actionable.
            """)
    else:
        st.error("Retirement age must be in the future.")
# --- TAB 3: CONSCIOUS SPENDING ---
# --- TAB 3: CONSCIOUS SPENDING ---
with tab3:
    st.header("Step 3: Conscious Spending Plan")
    
    # 1. Fetch Military Gross
    special_pay = st.session_state.get("special_pay", 0.0)
    mil_taxable = st.session_state.base_pay + special_pay
    mil_nontaxable = st.session_state.bah_amt + st.session_state.bas_amt

    # 2. Dynamic Additional Income Section
    st.subheader("➕ Additional Income")
    st.write("Add gross income from a spouse, rental property, or side hustles.")
    
    if "extra_income_rows" not in st.session_state:
        st.session_state.extra_income_rows = 0

    if st.button("Add Income Stream"):
        st.session_state.extra_income_rows += 1

    total_extra_income = 0.0

    for i in range(st.session_state.extra_income_rows):
        c_name, c_amt, c_freq = st.columns([2, 1, 1])
        with c_name:
            st.text_input("Source Name", key=f"ei_name_{i}", placeholder="e.g. Spouse's Job, Uber, Rental")
        with c_amt:
            amt = st.number_input("Amount ($)", key=f"ei_amt_{i}", min_value=0.0, step=100.0)
        with c_freq:
            freq = st.selectbox("Frequency", ["Monthly", "Bi-weekly", "Annually"], key=f"ei_freq_{i}")
            
        if freq == "Monthly":
            monthly_amt = amt
        elif freq == "Bi-weekly":
            monthly_amt = (amt * 26) / 12  # 26 pay periods
        else: # Annually
            monthly_amt = amt / 12
            
        total_extra_income += monthly_amt
        
    if st.session_state.extra_income_rows > 0:
        if st.button("Clear Extra Income", type="secondary"):
            st.session_state.extra_income_rows = 0
            st.rerun()

    st.divider()

    # 3. Take-Home & Tax Engine (Moved Below Income)
    st.subheader("💸 Net Take-Home Pay")
    pay_mode = st.radio(
        "Calculation Mode", 
        ["Manual Entry (From LES / Bank Statement) ⭐ Recommended", "Calculate Estimate (2026 Marginal Tax Rates)"], 
        horizontal=True
    )
    
    if "Manual Entry" in pay_mode:
        st.write("For the most accurate budget, look at your checking account and input exactly what hits it every month.")
        est_net = mil_taxable + mil_nontaxable + total_extra_income
        take_home = st.number_input("Total Monthly Take-Home ($)", value=est_net * 0.85, step=100.0)
    else:
        # 2026 MARGINAL TAX ESTIMATOR (Approx Single Filer)
        taxable_monthly = mil_taxable + total_extra_income
        annual_taxable = taxable_monthly * 12

        # 2026 Standard Deduction (Approx $15,000 for single filer)
        std_deduction = 15000
        tax_base = max(0, annual_taxable - std_deduction)

        # Walk through the marginal brackets
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
        monthly_fica = taxable_monthly * 0.0765 # 6.2% SS + 1.45% Medicare

        st.caption(f"*Estimated Taxes Deducted: Federal **${monthly_fed_tax:,.0f}** | FICA **${monthly_fica:,.0f}** (BAH/BAS excluded from tax)*")

        take_home = taxable_monthly - monthly_fed_tax - monthly_fica + mil_nontaxable

    st.info(f"💰 Total Combined Monthly Take-Home: **${take_home:,.2f}**")
    
    st.divider()
    
    # 4. Budget Columns
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
        available_for_fun = take_home - fixed_total - save_invest_total
        
        if available_for_fun > 0:
            st.success(f"**Available to allocate:** ${available_for_fun:,.2f}")
        else:
            st.error(f"**Available to allocate:** $0.00 (Check fixed costs!)")
            
        base_alloc = float(int((take_home * 0.20) / 6)) 
        
        experiences = st.number_input("Experiences (Travel, Events)", value=base_alloc)
        convenience = st.number_input("Convenience (Delivery, Time-savers)", value=base_alloc)
        hobbies = st.number_input("Hobbies (Gear, Gym, Gaming)", value=base_alloc)
        personal = st.number_input("Personal (Clothes, Grooming)", value=base_alloc)
        entertainment = st.number_input("Entertainment (Dining Out, Bars)", value=base_alloc)
        generosity = st.number_input("Generosity (Gifts, Donations)", value=base_alloc)
        
        fun_total = experiences + convenience + hobbies + personal + entertainment + generosity
        fun_pct = (fun_total / take_home * 100) if take_home > 0 else 0
        
        st.divider()
        if fun_total > available_for_fun:
            st.metric("Guilt-Free Total", f"${fun_total:,.2f}", f"{fun_pct:.1f}%", delta_color="inverse")
            st.warning("⚠️ You've allocated more Guilt-Free money than you have available!")
        else:
            st.metric("Guilt-Free Total", f"${fun_total:,.2f}", f"{fun_pct:.1f}%", delta_color="normal")

# --- TAB 3: CASH FLOW CALCULATIONS (REPAIRED) ---

    # 1. Calculate Taxes for the Sankey Flow
    if "Manual Entry" in pay_mode:
        sankey_tax = take_home * 0.15 
        sankey_gross = take_home + sankey_tax
    else:
        sankey_tax = monthly_fed_tax + monthly_fica
        sankey_gross = mil_taxable + total_extra_income + mil_nontaxable

    # 2. Map variables (fixed_total, save_invest_total, and fun_total are already defined in your code)
    invest_total = save_invest_total 
    guilt_free_total = fun_total
    surplus_amt = take_home - (fixed_total + invest_total + guilt_free_total)

    st.divider()
    st.subheader("📊 Your 2026 Monthly Cash Flow Architecture")

    import plotly.graph_objects as go

    # 3. Define Nodes and Links
    nodes = ["Gross Income", "Taxes", "Take-Home Pay", "Fixed Costs", "Investments", "Guilt-Free", "Surplus"]

    links = {
        "source": [0, 0, 2, 2, 2, 2],
        "target": [1, 2, 3, 4, 5, 6],
        "value": [
            max(0.1, sankey_tax),      
            max(0.1, take_home),       
            max(0.1, fixed_total),     
            max(0.1, invest_total),    
            max(0.1, guilt_free_total),
            max(0.1, surplus_amt)      
        ],
        "color": [
            "rgba(200, 200, 200, 0.4)", # Taxes
            "rgba(0, 212, 255, 0.4)",   # Take-Home
            "rgba(255, 99, 132, 0.5)",  # Fixed
            "rgba(75, 192, 192, 0.5)",  # Invest
            "rgba(255, 206, 86, 0.5)",  # Guilt-Free
            "rgba(0, 255, 127, 0.7)"    # Surplus
        ]
    }

    # 4. Create Figure (Removed 'font' from node dict)
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15, 
            thickness=20, 
            label=nodes, 
            color="#00D4FF"
        ),
        link=links
    )])

    # 5. Global Styling (Font goes here!)
    fig.update_layout(
        font=dict(color="white", size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        template="plotly_dark",
        height=600,
        margin=dict(l=10, r=10, t=40, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)

    # Surplus/Deficit Messages
    if surplus_amt < -5:
        st.error(f"⚠️ **Budget Deficit:** You are over-allocated by **${abs(surplus_amt):,.2f}**.")
    elif surplus_amt > 5:
        st.success(f"✅ **Budget Surplus:** You have **${surplus_amt:,.2f}** unallocated.")
# --- TAB 4: FINLIT QUIZ ---
# --- TAB 4: FINANCIAL READINESS QUIZ ---
with tab4:
    st.header("Step 4: Financial Readiness Quiz")
    st.write("Let's see if you're actually ready to build wealth, or if you're about to become a dealership's favorite customer.")
    
    with st.form("finlit_quiz"):
        st.markdown("### 🪖 The Basics")
        q1 = st.radio("1. If you are in the Blended Retirement System (BRS), what is the maximum percentage the DoD will match?", 
                      ["3% - Standard government match", "4% - The default contribution rate", "5% - The absolute maximum match"], index=None)
        q2 = st.radio("2. Which of the following military pay components are entirely tax-free?", 
                      ["Enlistment and Reenlistment Bonuses", "BAH (Housing) and BAS (Food)", "Hazardous Duty and Flight Pay"], index=None)
        q3 = st.radio("3. When you sell leave days back to the military, what exactly are you getting paid?", 
                      ["Base Pay + BAH + BAS", "Just your Base Pay (taxed)", "Double your Base Pay"], index=None)
        
        st.markdown("### 📈 The TSP (Thrift Savings Plan)")
        q4 = st.radio("4. If you joined after 2018, what fund does your TSP automatically invest in?", 
                      ["The G Fund (Government Securities)", "The C Fund (S&P 500)", "An L Fund (Lifecycle) matched to your age"], index=None) 
        q5 = st.radio("5. What is the fundamental difference between Traditional and Roth TSP?", 
                      ["Roth = Tax-deductible now, taxed later", "Roth = Taxes paid now, tax-free growth and withdrawals later", "Roth = No taxes ever, guaranteed"], index=None)
        q6 = st.radio("6. How much of your base pay are you legally allowed to contribute to the TSP?", 
                      ["Up to 15%", "Up to 60%", "Up to 100% (minus taxes and standard deductions)"], index=None)
        
        st.markdown("### 💳 Debt & Credit")
        q7 = st.radio("7. How does the Servicemembers Civil Relief Act (SCRA) protect you from debt?", 
                      ["Caps interest at 0% for all loans while deployed", "Caps interest at 6% for debt acquired BEFORE joining the military", "Caps interest at 18% for all credit cards"], index=None)
        q8 = st.radio("8. What is the guaranteed return rate of the Savings Deposit Program (SDP) while deployed?", 
                      ["5% annually", "10% annually (on up to $10,000)", "It just matches the S&P 500"], index=None)
        q9 = st.radio("9. What is the mathematical target for a fully funded Emergency Fund?", 
                      ["Exactly $500", "1 month of your Base Pay", "3 to 6 months of your fixed living expenses"], index=None)
        q10 = st.radio("10. Which of these actually hurts your credit score?", 
                       ["Checking your own score on Credit Karma", "Maxing out your credit limit (high utilization)", "Paying off a car loan completely"], index=None)
        q11 = st.radio("11. If you finance a $25,000 car at 24% APR over 72 months, what happens?", 
                       ["You build credit very fast", "You pay about $3,000 in interest", "You end up paying nearly double the car's sticker price"], index=None)
        q12 = st.radio("12. In a normal economic market, what is a realistic, 'good' auto loan rate?", 
                       ["0% is standard everywhere", "4% to 8%", "15% to 20%"], index=None)
        q13 = st.radio("13. Which habit is the absolute best way to build an elite credit score?", 
                       ["Keeping a small balance to 'show usage'", "Paying the minimum due on time every month", "Paying the full statement balance every single month"], index=None) 
        q14 = st.radio("14. What is mathematically the WORST place to store a $10,000 emergency fund?", 
                       ["A High-Yield Savings Account (HYSA)", "A standard checking account earning 0.01%", "A Money Market Account"], index=None)
        
        st.markdown("### 🦅 Big Military Benefits")
        q15 = st.radio("15. The Post-9/11 GI Bill pays your tuition, plus a monthly housing stipend equal to what?", 
                       ["The Base Pay of an E-5", "BAH at the E-5 with dependents rate for your school's zip code", "A flat $1,000 a month"], index=None)
        q16 = st.radio("16. What is the 'catch' for transferring your GI Bill to a spouse or child?", 
                       ["You can do it anytime after 10 years", "You must have 6 years of service AND commit to serving 4 MORE years", "You can only do it right before you retire"], index=None)
        q17 = st.radio("17. The VA Loan is famous for 'zero down payment'. What is the reality of buying a home?", 
                       ["You need absolutely zero cash to buy a house", "You still need cash for closing costs, earnest money, and inspections", "You are secretly required to put down 3%"], index=None)
        q18 = st.radio("18. How do you get the expensive VA Loan 'Funding Fee' completely waived?", 
                       ["Receive a Good Conduct Medal", "Get a VA disability rating of 10% or higher", "Request a waiver from your Commanding Officer"], index=None)
        q19 = st.radio("19. Can you use a VA Loan to buy a multi-family property (like a duplex or quadplex)?", 
                       ["No, single-family homes only", "Yes, but you must put 20% down", "Yes, as long as you live in one of the units for at least a year"], index=None)
        
        submitted = st.form_submit_button("Submit Answers & Get Scored")
        
        if submitted:
            score = 0
            # Grading logic based on exact string matches
            if q1 == "5% - The absolute maximum match": score += 1
            if q2 == "BAH (Housing) and BAS (Food)": score += 1
            if q3 == "Just your Base Pay (taxed)": score += 1
            if q4 == "An L Fund (Lifecycle) matched to your age": score += 1
            if q5 == "Roth = Taxes paid now, tax-free growth and withdrawals later": score += 1
            if q6 == "Up to 100% (minus taxes and standard deductions)": score += 1
            if q7 == "Caps interest at 6% for debt acquired BEFORE joining the military": score += 1
            if q8 == "10% annually (on up to $10,000)": score += 1
            if q9 == "3 to 6 months of your fixed living expenses": score += 1
            if q10 == "Maxing out your credit limit (high utilization)": score += 1
            if q11 == "You end up paying nearly double the car's sticker price": score += 1
            if q12 == "4% to 8%": score += 1
            if q13 == "Paying the full statement balance every single month": score += 1
            if q14 == "A standard checking account earning 0.01%": score += 1
            if q15 == "BAH at the E-5 with dependents rate for your school's zip code": score += 1
            if q16 == "You must have 6 years of service AND commit to serving 4 MORE years": score += 1
            if q17 == "You still need cash for closing costs, earnest money, and inspections": score += 1
            if q18 == "Get a VA disability rating of 10% or higher": score += 1
            if q19 == "Yes, as long as you live in one of the units for at least a year": score += 1
            
            p = int((score / 19) * 100)
            
            st.divider()
            st.metric("Final Score", f"{score}/19", f"{p}%")
            
            if score >= 18: 
                st.success("🏆 **Elite Status.** You understand the game. Don't let lifestyle creep steal your wealth.")
                st.balloons()
            elif score >= 14: 
                st.info("👍 **Solid Baseline.** You are safe from the Mustang trap, but you need to read up on your long-term benefits.")
            else: 
                st.error("🚨 **High Risk.** You are leaving thousands of dollars on the table. Hit Tab 5 (The Action Plan) right now.")
# --- TAB 5: ACTION PLAN ---
with tab5:
    st.header("Step 5: The Action Plan")
    st.write("Gamifying the classic financial order of operations. Expand each step, execute the mission, and check it off.")

    # --- PROGRESS BAR LOGIC ---
    total_steps = 9
    steps_completed = sum([st.session_state.get(f"step_{i}", False) for i in range(1, total_steps + 1)])
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
        st.success("🎉 Outstanding! You have executed the order of operations, killed your toxic debt, and set your wealth generation on autopilot.")
    
    st.divider()

    # --- PHASE 1 ---
    st.subheader("Phase 1: Stop the Bleeding (Immediate Action)")
    
    with st.expander("1. Secure the BRS Match (Free Money)"):
        st.markdown("""
        * **The Mission:** If you are in the Blended Retirement System (BRS), the DoD matches up to 5% of your base pay. If you contribute 4%, you are taking a voluntary pay cut.
        * **Action Steps:** Log into MyPay. Navigate to the "Traditional/Roth TSP" section. Set your contribution to a minimum of 5% (Roth is usually best for junior/mid-grade ranks due to tax-free allowances).
        * **Link:** [MyPay Portal](https://mypay.dfas.mil/)
        """)
        st.checkbox("✅ I have secured my 5% BRS Match", key="step_1")

    with st.expander("2. The SCRA Debt Hack"):
        st.markdown("""
        * **The Mission:** The Servicemembers Civil Relief Act (SCRA) legally caps interest rates at 6% for any debt you acquired *before* entering active duty. 
        * **Action Steps:** Identify pre-military credit cards, auto loans, or student loans. Call your lender’s specific SCRA department. Submit a copy of your active-duty orders. They are legally required to drop the rate and backdate the refund.
        * **Link:** [CFPB Guide to SCRA](https://www.consumerfinance.gov/consumer-tools/educator-tools/servicemembers/the-servicemembers-civil-relief-act-scra/)
        """)
        st.checkbox("✅ I have verified my SCRA eligibility and contacted lenders", key="step_2")

    with st.expander("3. Nuke Toxic Debt (The 24% APR Trap)"):
        st.markdown("""
        * **The Mission:** You cannot out-invest a 20% credit card or a predatory car loan from outside the gate. 
        * **Action Steps:** Take the "Surplus" from your Tab 3 budget and route 100% of it toward your highest-interest debt. Use the Avalanche Method (mathematically optimal) or Snowball Method (psychological wins).
        * **Link:** [Avalanche vs. Snowball Calculator](https://unbury.me/)
        """)
        st.checkbox("✅ I have a plan in place to eliminate all debt over 8% APR", key="step_3")

    # --- PHASE 2 ---
    st.subheader("Phase 2: Build Financial Armor")
    
    with st.expander("4. Escape the 0.01% Checking Account (HYSA)"):
        st.markdown("""
        * **The Mission:** Traditional banks pay you pennies while inflation eats your money. Keep your Emergency Fund in a Higher Yield Option for maximum accessibility *and* high interest (typically 4-5%).
        * **Action Steps:** Open a High-Yield Savings Account (HYSA). Change your direct deposit on MyPay or set up an auto-transfer from your checking account to route your "Emergency Fund" savings directly to this account. Aim for 3-6 months of your Fixed Costs.
        * **Link:** [Bankrate's Updated HYSA List](https://www.bankrate.com/banking/savings/best-high-yield-interests-savings-accounts/)
        """)
        st.checkbox("✅ My emergency fund is sitting in an HYSA", key="step_4")

    # --- PHASE 3 ---
    st.subheader("Phase 3: The Engine (Wealth Generation)")
    
    with st.expander("5. Escape the G-Fund Trap"):
        st.markdown("""
        * **The Mission:** If you joined before 2018, your TSP defaulted into the G-Fund (Government Securities). It is hyper-conservative and barely beats inflation. 
        * **Action Steps:** Move your investments into the C-Fund, S-Fund, I-Fund, or an L-Fund (Lifecycle) that matches your expected retirement year. 
        * **Links (TSP Fund Fact Sheets):** [C-Fund](https://www.tsp.gov/funds-individual/c-fund/) | [S-Fund](https://www.tsp.gov/funds-individual/s-fund/) | [I-Fund](https://www.tsp.gov/funds-individual/i-fund/) | [L-Funds](https://www.tsp.gov/funds-lifecycle/)
        """)
        st.checkbox("✅ My TSP is out of the G-Fund and properly invested", key="step_5")

    with st.expander("6. Automate the 'Retirement Gap'"):
        st.markdown("""
        * **The Mission:** Tab 2 showed you exactly how much extra you need to invest monthly to hit your FIRE number. Willpower fails; automation doesn't.
        * **Action Steps:** 1. Increase your TSP contributions to the percentage that will meet your monthly retirement goals. 
            2. **Crucial TSP Step:** Log into TSP.gov. You must change your **Contribution Allocation** (where *new* money from your paycheck goes) AND conduct an **Interfund Transfer** (moving the *existing* money already in your account) into your desired funds. 
            3. Alternatively, or if you are on track to max out your TSP entirely, open a Roth IRA. Set up an auto-draft from your checking account on the 1st of every month to fund it.
        * **Links:** [TSP.gov Login](https://www.tsp.gov/) | [Fidelity Roth IRA](https://www.fidelity.com/retirement-ira/roth-ira) | [Vanguard Roth IRA](https://investor.vanguard.com/accounts-plans/roth-ira) | [Charles Schwab Roth IRA](https://www.schwab.com/ira/roth-ira)
        """)
        st.checkbox("✅ My required monthly investments are fully automated", key="step_6")

    # --- PHASE 4 ---
    st.subheader("Phase 4: Military Cheat Codes")
    
    with st.expander("7. The GI Bill Transfer Trap"):
        st.markdown("""
        * **The Mission:** You cannot transfer the Post-9/11 GI Bill to your spouse or kids as a retirement gift. You must have at least 6 years of service, AND you must commit to serving 4 *more* years from the date of transfer. 
        * **Action Steps:** The exact day you hit your 6-year mark, log into MilConnect and initiate the transfer. If you wait until you are 18 years in, you will be forced to serve until 22 years to keep the benefit.
        * **Link:** [MilConnect Transfer Portal](https://milconnect.dmdc.osd.mil/milconnect/)
        """)
        st.checkbox("✅ I have transferred my GI Bill (Or decided not to)", key="step_7")

    with st.expander("8. The Deployment Multiplier (SDP)"):
        st.markdown("""
        * **The Mission:** If you deploy to a combat zone, the military offers the Savings Deposit Program (SDP), which guarantees a massive 10% annual return on up to $10,000.
        * **Action Steps:** Once you are in theater for 30 days, go to the local finance office (or set it up via MyPay) and max this out before investing another dime in the stock market.
        * **Link:** [DFAS SDP Fact Sheet](https://www.dfas.mil/MilitaryMembers/travelpay/armypcs/sdp/)
        """)
        st.checkbox("✅ I am aware of the SDP and will use it if deployed", key="step_8")

    with st.expander("9. VA Loan & The 'Funding Fee' Waiver"):
        st.markdown("""
        * **The Mission:** The VA loan allows 0% down, but it charges a "Funding Fee" (up to 3.3% of the loan amount). However, if you have a service-connected disability rating of just **10%**, that fee is completely waived—saving you thousands at closing.
        * **Action Steps:** Go to medical. Document your back, your knees, and your tinnitus *now*. When you separate, file your BDD (Benefits Delivery at Discharge) claim 180 days out.
        * **Link:** [VA Funding Fee Tables](https://www.va.gov/housing-assistance/home-loans/funding-fee-and-closing-costs/)
        """)
        st.checkbox("✅ I am documenting my medical records for my BDD claim", key="step_9")
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

# --- GLOBAL FOOTER & DISCLAIMER ---
st.markdown("---")

st.markdown("""
<div style='text-align: center; font-size: 0.85em; color: gray;'>

<b>Disclaimer:</b> This tool is for educational purposes only and uses simplified assumptions (like a constant real return). I am not a financial advisor. But financial literacy isn’t reserved for people with CFP after their name. Take charge of your money and take responsibility for your future—it’s one of the few investments guaranteed to pay dividends.

<br><br>

<b>For Further Reading:</b><br><br>

<a href='https://www.reddit.com/r/personalfinance/' target='_blank' style='color: gray; text-decoration: none;'>
r/personalfinance - The internet's group chat for "Is this a terrible financial decision?"
</a><br>

<a href='https://www.reddit.com/r/MilitaryFinance/' target='_blank' style='color: gray; text-decoration: none;'>
r/MilitaryFinance - Where troops compare BAH strategies and warn each other about 24% APR Mustangs
</a><br>

<a href='https://militaryfinancialindependence.com/' target='_blank' style='color: gray; text-decoration: none;'>
The Military Guide - Doug Nordman's legendary playbook for military financial independence
</a><br>

<a href='https://www.mrmoneymustache.com/blog/' target='_blank' style='color: gray; text-decoration: none;'>
Mr. Money Mustache - Aggressively anti-lifestyle-inflation and surprisingly entertaining
</a><br>

<a href='https://www.iwillteachyoutoberich.com/' target='_blank' style='color: gray; text-decoration: none;'>
I Will Teach You To Be Rich - Ramit Sethi on spending intentionally and building wealth
</a>

</div>
""", unsafe_allow_html=True)
