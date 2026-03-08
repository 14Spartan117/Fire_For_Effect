"""
Tab 6 -- Feedback & AAR
"""

import streamlit as st


def render_tab_feedback(container):
    with container:
        ss = st.session_state
        ss.tabs_visited.add(6)
        ss.max_tab_reached = max(ss.max_tab_reached, 6)
        st.header("Feedback")
        st.write("Got a question? Found a bug? Want a new feature? Drop it below.")

        contact_form = """
        <form action="https://formsubmit.co/ian.moss@nps.edu" method="POST">
            <input type="hidden" name="_captcha" value="false">
            <input type="hidden" name="_subject" value="F.I.R.E. for Effect -- Feedback">
            <input type="text" name="name" placeholder="Your Name/Callsign (Optional)"
                   style="width:100%;padding:10px;margin-bottom:10px;border-radius:5px;border:1px solid #ccc;">
            <input type="email" name="email" placeholder="Your Email (If you want a reply)"
                   style="width:100%;padding:10px;margin-bottom:10px;border-radius:5px;border:1px solid #ccc;">
            <textarea name="message" placeholder="Questions, comments, or brilliant ideas go here..."
                      rows="5" required
                      style="width:100%;padding:10px;margin-bottom:10px;border-radius:5px;border:1px solid #ccc;">
            </textarea>
            <button type="submit"
                    style="background-color:#4CAF50;color:white;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;">
                Send to the Developer
            </button>
        </form>
        """
        st.markdown(contact_form, unsafe_allow_html=True)
