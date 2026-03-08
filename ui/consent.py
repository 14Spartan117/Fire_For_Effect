"""
Pre-app consent / disclaimer screen.
"""

import streamlit as st


def render_consent_screen():
    """
    Show the consent screen and return True if the user has already consented
    (so the caller can continue). Returns False and calls st.stop() otherwise.
    """
    if st.session_state.consent_given:
        return True

    st.title("\U0001F396\uFE0F F.I.R.E. for Effect")
    st.markdown("""
**Before you go any further -- a quick note from the developer.**

This is the first app I've ever built. I think there's something genuinely useful here, but there's probably more wrong with it than right -- and the only way I find that out is by seeing how people actually use it.

So I'm asking your permission to collect some anonymous usage data while you're in the app.

**What I collect:**
- When you opened the app and how long you stayed
- What tabs you visited and how far you got
- Your duty station zip code (if you enter one)
- Whether you're on a phone or computer
- Whether you ran the Monte Carlo simulation, completed the financial quiz, or downloaded the PDF
- Whether anything broke while you were using it

**What I do NOT collect:**
- Your name, email, rank, TIS, or SSN
- Anything that could identify you personally
- Any financial numbers you enter -- those never leave your device

**What this lets me do:**
- See if people are using it or closing it immediately
- Find where it breaks
- Understand whether it's spreading or just being perpetually opened by my mom to be nice
- Decide whether this is worth anything or just adding more trash to the pile

**One more thing:** this is a test, so the link may be dead in a few weeks. If there's something worth saving, I'll build it back better.
    """)

    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "\u2705 Alright, Let's Do This.", type="primary", use_container_width=True
        ):
            st.session_state.consent_given = True
            st.rerun()
    with col2:
        if st.button(
            "\u274C No thanks, close the tab.", use_container_width=True
        ):
            st.markdown("### No problem. Come back if you change your mind.")
            st.stop()
    st.stop()
    return False  # unreachable, but keeps the type checker happy
