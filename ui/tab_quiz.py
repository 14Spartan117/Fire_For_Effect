"""
Tab 4 -- Know the Game: Financial Readiness Quiz
"""

import streamlit as st


def render_tab_quiz(container):
    with container:
        ss = st.session_state
        ss.tabs_visited.add(4)
        ss.max_tab_reached = max(ss.max_tab_reached, 4)
        st.header("Know the Game: Financial Readiness Quiz")
        st.write(
            "Let's see if you're actually ready to build wealth, or if you're about "
            "to become a dealership's favorite customer."
        )

        with st.form("finlit_quiz"):
            st.markdown("### \U0001FAA6 The Basics")
            q1 = st.radio(
                "1. If you are in the Blended Retirement System (BRS), what is the maximum percentage the DoD will match?",
                ["3% - Standard government match", "4% - The default contribution rate",
                 "5% - The absolute maximum match"], index=None,
            )
            q2 = st.radio(
                "2. Which of the following military pay components are entirely tax-free?",
                ["Enlistment and Reenlistment Bonuses", "BAH (Housing) and BAS (Food)",
                 "Hazardous Duty and Flight Pay"], index=None,
            )
            q3 = st.radio(
                "3. When you sell leave days back to the military, what exactly are you getting paid?",
                ["Base Pay + BAH + BAS", "Just your Base Pay (taxed)", "Double your Base Pay"], index=None,
            )

            st.markdown("### \U0001F4C8 The TSP (Thrift Savings Plan)")
            q4 = st.radio(
                "4. If you joined after 2018, what fund does your TSP automatically invest in?",
                ["The G Fund (Government Securities)", "The C Fund (S&P 500)",
                 "An L Fund (Lifecycle) matched to your age"], index=None,
            )
            q5 = st.radio(
                "5. What is the fundamental difference between Traditional and Roth TSP?",
                ["Roth = Tax-deductible now, taxed later",
                 "Roth = Taxes paid now, tax-free growth and withdrawals later",
                 "Roth = No taxes ever, guaranteed"], index=None,
            )
            q6 = st.radio(
                "6. How much of your base pay are you legally allowed to contribute to the TSP?",
                ["Up to 15%", "Up to 60%",
                 "Up to 100% (minus taxes and standard deductions)"], index=None,
            )

            st.markdown("### \U0001F4B3 Debt & Credit")
            q7 = st.radio(
                "7. How does the Servicemembers Civil Relief Act (SCRA) protect you from debt?",
                ["Caps interest at 0% for all loans while deployed",
                 "Caps interest at 6% for debt acquired BEFORE joining the military",
                 "Caps interest at 18% for all credit cards"], index=None,
            )
            q8 = st.radio(
                "8. What is the guaranteed return rate of the Savings Deposit Program (SDP) while deployed?",
                ["5% annually", "10% annually (on up to $10,000)",
                 "It just matches the S&P 500"], index=None,
            )
            q9 = st.radio(
                "9. What is the mathematical target for a fully funded Emergency Fund?",
                ["Exactly $500", "1 month of your Base Pay",
                 "3 to 6 months of your fixed living expenses"], index=None,
            )
            q10 = st.radio(
                "10. Which of these actually hurts your credit score?",
                ["Checking your own score on Credit Karma",
                 "Maxing out your credit limit (high utilization)",
                 "Paying off a car loan completely"], index=None,
            )
            q11 = st.radio(
                "11. If you finance a $25,000 car at 24% APR over 72 months, what happens?",
                ["You build credit very fast", "You pay about $3,000 in interest",
                 "You end up paying nearly double the car's sticker price"], index=None,
            )
            q12 = st.radio(
                "12. In a normal economic market, what is a realistic, 'good' auto loan rate?",
                ["0% is standard everywhere", "4% to 8%", "15% to 20%"], index=None,
            )
            q13 = st.radio(
                "13. Which habit is the absolute best way to build an elite credit score?",
                ["Keeping a small balance to 'show usage'",
                 "Paying the minimum due on time every month",
                 "Paying the full statement balance every single month"], index=None,
            )
            q14 = st.radio(
                "14. What is mathematically the WORST place to store a $10,000 emergency fund?",
                ["A High-Yield Savings Account (HYSA)",
                 "A standard checking account earning 0.01%",
                 "A Money Market Account"], index=None,
            )

            st.markdown("### \U0001F985 Big Military Benefits")
            q15 = st.radio(
                "15. The Post-9/11 GI Bill pays your tuition, plus a monthly housing stipend equal to what?",
                ["The Base Pay of an E-5",
                 "BAH at the E-5 with dependents rate for your school's zip code",
                 "A flat $1,000 a month"], index=None,
            )
            q16 = st.radio(
                "16. What is the 'catch' for transferring your GI Bill to a spouse or child?",
                ["You can do it anytime after 10 years of service",
                 "You must have 6 years of service AND commit to serving 4 MORE years",
                 "You can only do it right before you retire"], index=None,
            )
            q17 = st.radio(
                "17. The VA Loan is famous for 'zero down payment'. What is the reality?",
                ["You need absolutely zero cash to buy a house",
                 "You still need cash for closing costs, earnest money, and inspections",
                 "You are secretly required to put down 3%"], index=None,
            )
            q18 = st.radio(
                "18. How do you get the expensive VA Loan 'Funding Fee' completely waived?",
                ["Receive a Good Conduct Medal",
                 "Get a VA disability rating of 10% or higher",
                 "Request a waiver from your Commanding Officer"], index=None,
            )
            q19 = st.radio(
                "19. Can you use a VA Loan to buy a multi-family property (like a duplex)?",
                ["No, single-family homes only",
                 "Yes, but you must put 20% down",
                 "Yes, as long as you live in one of the units for at least a year"], index=None,
            )

            submitted = st.form_submit_button("Submit Answers & Get Scored")

            if submitted:
                answers = {
                    q1: "5% - The absolute maximum match",
                    q2: "BAH (Housing) and BAS (Food)",
                    q3: "Just your Base Pay (taxed)",
                    q4: "An L Fund (Lifecycle) matched to your age",
                    q5: "Roth = Taxes paid now, tax-free growth and withdrawals later",
                    q6: "Up to 100% (minus taxes and standard deductions)",
                    q7: "Caps interest at 6% for debt acquired BEFORE joining the military",
                    q8: "10% annually (on up to $10,000)",
                    q9: "3 to 6 months of your fixed living expenses",
                    q10: "Maxing out your credit limit (high utilization)",
                    q11: "You end up paying nearly double the car's sticker price",
                    q12: "4% to 8%",
                    q13: "Paying the full statement balance every single month",
                    q14: "A standard checking account earning 0.01%",
                    q15: "BAH at the E-5 with dependents rate for your school's zip code",
                    q16: "You must have 6 years of service AND commit to serving 4 MORE years",
                    q17: "You still need cash for closing costs, earnest money, and inspections",
                    q18: "Get a VA disability rating of 10% or higher",
                    q19: "Yes, as long as you live in one of the units for at least a year",
                }
                score = sum(1 for user_ans, correct in answers.items() if user_ans == correct)
                p = int((score / 19) * 100)

                st.divider()
                st.metric("Final Score", f"{score}/19", f"{p}%")

                if score >= 18:
                    st.success(
                        "\U0001F3C6 **Elite Status.** You understand the game. "
                        "Don't let lifestyle creep steal your wealth."
                    )
                    st.balloons()
                elif score >= 14:
                    st.info(
                        "\U0001F44D **Solid Baseline.** You are safe from the Mustang trap, "
                        "but read up on your long-term benefits."
                    )
                else:
                    st.error(
                        "\U0001F6A8 **High Risk.** You are leaving thousands of dollars "
                        "on the table. Hit Tab 5 (The Action Plan) right now."
                    )
