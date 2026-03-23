"""
app.py  — entry point, routing only.
  data_layer.py    ← Supabase + local JSON, bcrypt auth, config
  ui_components.py ← CSS + HTML helpers
  pages.py         ← one function per page
"""

import streamlit as st
import data_layer as dl
import ui_components as ui
from pages import (
    page_dashboard,
    page_tasks,
    page_add_task,
    page_literature,
    page_add_paper,
    page_my_account,
    page_admin,
)

st.set_page_config(
    page_title="Gel Squad — Project Hub",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)
ui.inject_css()


# ── Login wall ────────────────────────────────────────────────
def show_login():
    st.markdown("""
    <div style="max-width:420px;margin:4rem auto;text-align:center;">
        <div style="font-size:3.5rem;margin-bottom:0.75rem;">🌊</div>
        <h2 style="color:#e2e8f0;font-size:1.7rem;font-weight:700;
                   letter-spacing:-0.02em;margin-bottom:0.3rem;">
            Gel Squad Hub
        </h2>
        <p style="color:#475569;font-size:0.85rem;">
            Haemograph Capstone — Project Management &amp; Literature Tracker
        </p>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        team = dl.get_team_names()
        name = st.selectbox("Who are you?", ["— select —"] + team, label_visibility="visible")
        pwd  = st.text_input("Password", type="password", placeholder="Your personal password…")

        if st.button("Enter Hub →", use_container_width=True, type="primary"):
            if name == "— select —":
                st.error("Please select your name.")
            elif not dl.check_password(name, pwd):
                st.error("Wrong password.")
            else:
                dl.set_current_user(name)
                st.rerun()

        st.markdown(
            "<div style='color:#475569;font-size:0.75rem;text-align:center;margin-top:0.75rem;'>"
            "First time? Ask Rohan for your temporary password, then change it in My Account."
            "</div>",
            unsafe_allow_html=True
        )


# ── Main ──────────────────────────────────────────────────────
def main():
    current_user = dl.get_current_user()

    if not current_user:
        show_login()
        return

    connected = dl.sheets_connected()
    page      = ui.sidebar_ui(current_user, connected)

    if page == "__logout__":
        dl.set_current_user(None)
        st.rerun()
        return

    routes = {
        "Dashboard":          page_dashboard,
        "Task Board":         page_tasks,
        "Literature Tracker": page_literature,
        "Add Task":           page_add_task,
        "Add Paper":          page_add_paper,
        "My Account":         page_my_account,
        "Admin Panel":        page_admin,
    }

    fn = routes.get(page)
    if fn:
        fn(current_user)


main()
