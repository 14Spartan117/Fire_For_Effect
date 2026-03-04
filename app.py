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

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💰 Income Calculator", 
    "📈 Retirement Goal", 
    "⚖️ Conscious Spending Plan",
    "🧠 FinLit Quiz",
    "🗺️ Action Plan"
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
        st.session_state.base_pay = base
        st.session_state.bas_amt = bas
        st.session_state.bah_amt = bah
        
        gross = base + bas + bah
        st.success(f"### Total Monthly Gross: \\${gross:,.2f}")
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
        
        # --- RESULTS SUMMARY ---
        res_col1, res_col2, res_col3 = st.columns(3)
        res_col1.metric("Goal Nest Egg", f"${total_nest_egg_needed:,.0f}")
        res_col2.metric("Future Value", f"${fv_current_savings:,.0f}")
        res_col3.metric("Monthly Investment", f"${required_pmt:,.2f}", delta="Sent to Budget")

        st.success(
            "### 🎯 Retirement Reality Check\n\n"
            f"- **Current Balance:** \\${current_tsp:,.0f} is projected to grow to **\\${fv_current_savings:,.0f}** by age **{age_at_retire}**.\n"
            f"- **The Target:** This covers a large portion of your **\\${total_nest_egg_needed:,.0f}** goal.\n"
            f"- **The Action:** To bridge the remaining gap, you need to invest **\\${required_pmt:,.2f}** per month."
        )
    else:
        st.error("Retirement age must be in the future.")

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
        st.info(f"Estimated Monthly Take-Home: **\\${take_home:,.2f}**")

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

# --- TAB 4: FINLIT QUIZ ---
# --- TAB 4: FINLIT QUIZ ---
with tab4:
    st.header("Step 4: Financial Readiness Quiz")
    st.write("Let's test your knowledge on military money hacks and basic investing. No stress, just good stuff to know.")
    
    with st.form("finlit_quiz"):
        st.markdown("### The Basics: Pay & Benefits")
        q1 = st.radio("1. Free money alert! Under the BRS (Blended Retirement System), what’s the maximum percentage of your base pay the DoD will match in your TSP?", 
                      ["0%", "3%", "4%", "5%"], index=None)
        
        q2 = st.radio("2. Uncle Sam taxes your Base Pay, but which of these sweet, sweet allowances are completely tax-free?",
                      ["Reenlistment Bonuses", "BAH and BAS", "Hazardous Duty Pay", "Special Duty Assignment Pay"], index=None)
        
        q3 = st.radio("3. You've hoarded a bunch of leave days. When you get out, you can 'sell' them back. But what are you actually getting paid for?",
                      ["Base Pay + BAH + BAS", "Just Base Pay", "Base Pay + BAH", "Double Base Pay"], index=None)

        st.markdown("### The TSP (Thrift Savings Plan)")
        q4 = st.radio("4. When you first join and money starts going into your TSP, where does it automatically go if you don't touch anything?",
                      ["The G Fund (Basically cash/bonds)", "An L Fund (Lifecycle - based on your retirement year)", "The C Fund (Top 500 US Companies)", "It sits in a holding account doing nothing"], index=None)

        q5 = st.radio("5. You hear people arguing about 'Roth' vs 'Traditional' TSP. What’s the actual difference?",
                      ["Roth means you pay taxes NOW and it grows tax-free; Traditional is taxed LATER when you withdraw.", "Traditional is for officers, Roth is for enlisted.", "Roth is invested in stocks, Traditional is just government bonds.", "They are exactly the same, just different names."], index=None)

        q6 = st.radio("6. How much of your base pay *can* you put into your TSP if you really wanted to?",
                      ["Up to 5%", "Up to 15%", "Up to 60%", "Literally all of it (up to the annual IRS limit)"], index=None)

        st.markdown("### Real World Money Survival")
        q7 = st.radio("7. You racked up a crazy high interest rate on a credit card *before* you joined. Thanks to the SCRA, what is the absolute highest interest rate they can charge you now?",
                      ["0%", "6%", "15%", "36%"], index=None)

        q8 = st.radio("8. You're deployed to a combat zone. The military offers a crazy good guaranteed return on your cash through the SDP (Savings Deposit Program). What's the interest rate?",
                      ["2%", "5%", "10%", "15%"], index=None)

        q9 = st.radio("9. Life happens (like your car breaking down right before a PCS). What’s the golden rule for how much cash you should keep in an emergency fund?",
                      ["$500", "1 month of base pay", "3 to 6 months of essential living expenses", "A whole year of income"], index=None)

        q10 = st.radio("10. Which of these moves actually hurts your credit score?",
                       ["Checking your own score on a banking app", "Paying off an auto loan completely", "Maxing out your credit cards (even if you make the minimum payment)", "Getting a new cell phone plan"], index=None)

        st.markdown("### Common r/personalfinance Traps & Credit")
        q11 = st.radio("11. You just graduated training and want a sweet new ride. The dealership right outside the gate offers you a 24% interest rate. What does this actually mean?",
                       ["It's a great deal for a first-time buyer to build credit.", "You'll end up paying double or triple the car's actual value over the life of the loan.", "The military will pay off the interest for you later.", "It's totally normal, just refinance it next month."], index=None)
        
        q12 = st.radio("12. You avoided the 24% trap, but what actually *is* a 'good' interest rate for a car loan if you have decent credit?",
                       ["0% (They give these out all the time)", "4% - 8% (A solid, realistic rate from a credit union)", "12% - 15% (Totally average)", "20%+ (Just standard inflation)"], index=None)

        q13 = st.multiselect("13. Which of the following moves will actually INCREASE your credit score? (Select all that apply)",
                                  ["Paying your credit card balance in full every month", 
                                   "Keeping your oldest credit card open (even if you rarely use it)", 
                                   "Opening 5 new credit cards on the same day", 
                                   "Setting up auto-pay so you never miss a payment by accident", 
                                   "Carrying a balance and paying interest so the bank 'trusts' you"])

        q14 = st.radio("14. You've built up your 3-6 month emergency fund. Where is the absolute worst place to keep it?",
                       ["A High-Yield Savings Account (HYSA) earning 4-5%", "Stuffed in a regular checking account making 0.01% (or under your mattress)", "A Money Market Account", "A short-term Certificate of Deposit (CD)"], index=None)

        st.markdown("### The Big Ticket Benefits: Education & Housing")
        q15 = st.radio("15. The Post-9/11 GI Bill is the crown jewel of benefits. Besides paying your full tuition at a public school, what else does it give you every month you are in class?",
                         ["A brand new laptop", "A Monthly Housing Allowance (BAH) at the E-5 with dependents rate for the school's zip code", "Base Pay for your highest rank", "A guaranteed government job"], index=None)

        q16 = st.radio("16. You want to pass your GI Bill to your spouse or kids. What’s the catch?",
                         ["You can transfer it the day you graduate boot camp.", "You must have served at least 6 years, AND you have to commit to serving 4 MORE years.", "You have to pay \\$1,200 to unlock the transfer.", "You can only transfer it to someone who also joins the military."], index=None)

        q17 = st.radio("17. You're PCSing and thinking about using your VA Loan to buy a house with 0% down. What’s the reality check you need to prepare for?",
                       ["There is no catch, the government buys the house for you.", "You still need cash for closing costs, property taxes, maintenance, and potentially the VA Funding Fee.", "You can only buy a house if you are an NCO or higher.", "You have to stay in the exact same house for 20 years to keep the loan."], index=None)

        q18 = st.radio("18. The VA Loan usually comes with a 'VA Funding Fee' (which can add thousands to your loan). How do you get this fee completely waived?",
                         ["By having a service-connected VA disability rating of 10% or higher", "By asking your chain of command for a waiver", "By buying a house right outside a base", "By paying off your car first"], index=None)

        q19 = st.radio("19. Can you use the VA Loan to buy a multi-family property (like a duplex or 4-plex)?",
                         ["No, it's only for single-family suburban homes.", "Yes, but ONLY if you live in one of the units as your primary residence.", "Yes, you can buy an entire apartment building and rent it all out.", "No, officers can, but enlisted cannot."], index=None)

        submitted = st.form_submit_button("Submit Answers & See How You Did")

        if submitted:
            st.divider()
            st.subheader("Quiz Results:")
            
            # 1-10 Evaluations
            if q1 == "5%": st.success("✅ **Q1:** Nailed it. Set your TSP to at least 5% in MyPay, or you are literally leaving free money on the table.")
            else: st.error("❌ **Q1:** It's 5%! If you are BRS, you need to contribute at least 5% of your base pay to get the full DoD match. Don't leave free money behind!")
                
            if q2 == "BAH and BAS": st.success("✅ **Q2:** You got it. BAH and BAS are tax-free. This is why a $60k military salary spends like an $80k civilian salary.")
            else: st.error("❌ **Q2:** It's BAH and BAS. Housing and food allowances are totally tax-free, which is a massive hidden perk of military pay.")
            
            if q3 == "Just Base Pay": st.success("✅ **Q3:** Correct. When you sell leave, you ONLY get the base pay portion. It's usually better to actually take your terminal leave so you get BAH/BAS while you transition out!")
            else: st.error("❌ **Q3:** You only get Just Base Pay. You lose out on the tax-free BAH and BAS, which is why taking 'Terminal Leave' is usually a better deal than selling it.")
                
            if q4 == "An L Fund (Lifecycle - based on your retirement year)": st.success("✅ **Q4:** Yep! New accessions go into the L Fund. (Heads up: If you joined before 2018, your default was the ultra-safe G Fund—make sure you aren't still stuck in it!)")
            else: st.error("❌ **Q4:** It's the L Fund. It automatically adjusts based on your age. (Note: If you joined before 2018, you defaulted into the G Fund, which barely beats inflation!)")
                
            if "taxes NOW" in str(q5): st.success("✅ **Q5:** Spot on. Since your taxes are generally pretty low while serving (thanks to tax-free BAH/BAS), paying taxes NOW via the Roth TSP is usually a massive win for military folks.")
            else: st.error("❌ **Q5:** Roth means paying taxes NOW so the growth is tax-free forever. Because so much of military pay is tax-free allowances, the Roth option is incredibly powerful for servicemembers.")
            
            if "Literally all of it" in str(q6): st.success("✅ **Q6:** Correct! You can contribute up to the IRS limit. You can pump a massive percentage of your base pay in if you want to aggressively save.")
            else: st.error("❌ **Q6:** You can put in literally all of it, up to the IRS annual limit. Don't stop at 5% if you have extra cash to invest!")

            if q7 == "6%": st.success("✅ **Q7:** 6% is the magic number! The Servicemembers Civil Relief Act (SCRA) forces lenders to drop pre-service debt to 6%. Call your credit card companies if this applies to you.")
            else: st.error("❌ **Q7:** It's 6%! The SCRA is a legal cheat code. If you have civilian debt from before you joined, you need to notify your lender to get that rate dropped to 6%.")

            if q8 == "10%": st.success("✅ **Q8:** A guaranteed 10% return! The SDP is one of the best deals in the military. If you deploy to a combat zone, ask finance how to set it up immediately.")
            else: st.error("❌ **Q8:** It's 10%. A guaranteed 10% return on your money is practically unheard of in the civilian world. Take advantage of the SDP if you deploy!")

            if "3 to 6 months" in str(q9): st.success("✅ **Q9:** 3 to 6 months of essential expenses. This keeps you off high-interest credit cards when your car breaks down or the government shuts down.")
            else: st.error("❌ **Q9:** 3 to 6 months of living expenses. This is your financial armor. Build this up in a high-yield savings account before you start aggressively investing.")

            if "Maxing out" in str(q10): st.success("✅ **Q10:** Maxing out your cards crushes your 'credit utilization' ratio and tanks your score, even if you never miss a payment. Keep your balances low!")
            else: st.error("❌ **Q10:** Maxing out your cards hurts your score! 'Credit utilization' (how much debt you have vs. your limit) is a huge part of your score. Keep your balances well below your limits.")

            # 11-14 Evaluations (Traps & Credit)
            if "paying double or triple" in str(q11): st.success("✅ **Q11:** Run away! A 24% APR on a depreciating asset like a car is financial suicide. Get pre-approved at a credit union before you ever step foot on a lot.")
            else: st.error("❌ **Q11:** You will pay double or triple for the car! Dealerships right outside the gate prey on young troops. Never finance at these crazy rates.")

            if "4% - 8%" in str(q12): st.success("✅ **Q12:** Correct! While rates fluctuate with the economy, getting a rate in the 4-8% range from a credit union like Navy Fed or USAA is generally a solid deal.")
            else: st.error("❌ **Q12:** Look for 4% - 8%. Don't fall for double-digit interest rates. Go to a credit union and get pre-approved before you shop.")

            correct_credit = {"Paying your credit card balance in full every month", "Keeping your oldest credit card open (even if you rarely use it)", "Setting up auto-pay so you never miss a payment by accident"}
            if set(q13) == correct_credit: st.success("✅ **Q13:** Flawless! Paying in full, keeping old accounts open to show credit history, and never missing a payment are the holy trinity of an 800+ credit score. (And NO, you do not need to carry a balance and pay interest to build credit!)")
            else: st.error("❌ **Q13:** Not quite! The correct answers are: Paying in full, Keeping your oldest card open, and Setting up auto-pay. Never carry a balance just to 'build credit'—that is a total myth that just costs you money!")

            if "regular checking account" in str(q14): st.success("✅ **Q14:** Don't let your money be lazy! A traditional bank pays you pennies. Open a High-Yield Savings Account (HYSA) online so your emergency fund earns actual money every month.")
            else: st.error("❌ **Q14:** A regular checking account (or mattress) is the worst! Inflation eats your money. Put your emergency fund in a High-Yield Savings Account (HYSA) so it earns 4-5% while it sits there.")

            # 15-19 Evaluations (Education & Housing)
            if "Housing Allowance" in str(q15): st.success("✅ **Q15:** You got it! You get an E-5 with dependents BAH rate for the zip code of your school. This is literally thousands of dollars a month tax-free just to be a student.")
            else: st.error("❌ **Q15:** You get a Monthly Housing Allowance! The GI Bill pays your tuition AND pays your rent at the E-5 w/ Dependents rate for your school's zip code.")

            if "serve 4 MORE years" in str(q16): st.success("✅ **Q16:** Yep. You need 6 years in, and you have to sign on the dotted line for 4 more. Do this AS SOON as you hit your 6-year mark if you plan on staying in!")
            else: st.error("❌ **Q16:** You have to serve 6 years, and commit to 4 more. Don't wait until you are 1 year from retirement to try and transfer this—they will make you serve another 3 years!")

            if "still need cash" in str(q17): st.success("✅ **Q17:** The VA loan is amazing, but 0% down does NOT mean 0 out of pocket. You still need cash for closing costs, inspections, and sudden home repairs.")
            else: st.error("❌ **Q17:** You still need thousands in cash! The VA loan removes the down payment, but you still have to pay closing costs, inspections, and potentially a VA funding fee. Don't buy a house completely broke.")

            if "disability rating" in str(q18): st.success("✅ **Q18:** Correct! Even a 10% VA disability rating waives the Funding Fee entirely, saving you thousands of dollars at the closing table.")
            else: st.error("❌ **Q18:** You need a service-connected disability rating of at least 10%. This is a massive reason to make sure you get everything documented in your medical records before you separate!")

            if "live in one of the units" in str(q19): st.success("✅ **Q19:** Yes! This is called 'house hacking.' You can buy a duplex, triplex, or 4-plex with 0% down, live in one unit, and rent out the others to pay your mortgage.")
            else: st.error("❌ **Q19:** You CAN buy up to a 4-plex, but you MUST live in one of the units as your primary residence. It's an incredible way to start building real estate wealth.")

# --- TAB 5: ACTION PLAN ---
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
