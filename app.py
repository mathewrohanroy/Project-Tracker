"""
app.py  — entry point, routing only.
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
        name = st.selectbox("Who are you?", ["— select —"] + team)
        pwd  = st.text_input("Password", type="password", placeholder="Your personal password…")

        if st.button("Enter Hub →", use_container_width=True, type="primary"):
            if name == "— select —":
                st.error("Please select your name.")
            else:
                # ── DEBUG — shows exactly what's happening ──
                sb = dl.get_supabase()
                st.info(f"Supabase connected: {sb is not None}")

                all_users = dl.load_users_db()
                st.info(f"Users in DB: {len(all_users)} — names: {[u['name'] for u in all_users]}")

                user_record = dl.get_user_by_name(name)
                st.info(f"User '{name}' found: {user_record is not None}")

                if user_record:
                    stored_hash = user_record.get("password_hash", "")
                    st.info(f"Hash stored: '{stored_hash[:30]}...'")
                    result = dl.check_password(name, pwd)
                    st.info(f"check_password result: {result}")

                # ── actual login logic ──
                if not dl.check_password(name, pwd):
                    st.error("Wrong password.")
                else:
                    dl.set_current_user(name)
                    st.rerun()


def main():
    current_user = dl.get_current_user()

    if not current_user:
        show_login()
        return

    connected = dl.sheets_connected()
    page = ui.sidebar_ui(current_user, connected)

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