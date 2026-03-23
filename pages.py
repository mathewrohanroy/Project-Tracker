"""
pages.py
========
One function per page. All data via data_layer, all HTML via ui_components.
"""

import json
import streamlit as st
from datetime import date

import data_layer as dl
import ui_components as ui

ADMIN_FLAG = "is_admin"   # used for display only — truth comes from dl.is_admin()


# ─────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────

def page_dashboard(user: str):
    tasks  = dl.load_tasks()
    papers = dl.load_papers()

    ui.page_header(
        f"👋 Hey {user.split()[0]}",
        f"Here's where things stand — {date.today().strftime('%A, %d %B %Y')}"
    )

    total    = len(tasks)
    done     = sum(1 for t in tasks if t["status"] == "Done")
    in_prog  = sum(1 for t in tasks if t["status"] == "In Progress")
    blocked  = sum(1 for t in tasks if t["status"] == "Blocked")
    my_open  = sum(1 for t in tasks if user in t.get("assignees", []) and t["status"] != "Done")
    n_papers = len(papers)

    cols = st.columns(6)
    ui.metric_card(cols[0], total,    "Total Tasks",    "#3b82f6")
    ui.metric_card(cols[1], done,     "Completed",      "#4ade80")
    ui.metric_card(cols[2], in_prog,  "In Progress",    "#60a5fa")
    ui.metric_card(cols[3], blocked,  "Blocked",        "#f87171")
    ui.metric_card(cols[4], my_open,  "My Open Tasks",  "#fbbf24")
    ui.metric_card(cols[5], n_papers, "Papers Tracked", "#2dd4bf")

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    col_l, col_r = st.columns([3, 2])

    with col_l:
        ui.section_heading("My Tasks")
        my_tasks = sorted(
            [t for t in tasks if user in t.get("assignees", []) and t["status"] != "Done"],
            key=lambda x: x.get("due") or "9999"
        )
        if not my_tasks:
            st.markdown('<div class="card" style="color:#64748b;font-style:italic;">No open tasks assigned to you 🎉</div>', unsafe_allow_html=True)
        for t in my_tasks:
            st.markdown(ui.task_card_html(t), unsafe_allow_html=True)

    with col_r:
        ui.section_heading("Overdue / Due Soon")
        urgent = sorted(
            [t for t in tasks if t["status"] != "Done" and ui.days_until(t.get("due")) is not None and ui.days_until(t.get("due")) <= 3],
            key=lambda x: x.get("due", "")
        )
        if not urgent:
            st.markdown('<div class="card" style="color:#64748b;font-style:italic;">Nothing urgent right now ✓</div>', unsafe_allow_html=True)
        for t in urgent[:6]:
            st.markdown(ui.urgent_task_card_html(t), unsafe_allow_html=True)

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        ui.section_heading("Papers to Read")
        unread = [p for p in papers if p.get("status") in ["To Read", "Reading"]][:5]
        if not unread:
            st.markdown('<div class="card" style="color:#64748b;font-style:italic;">All caught up on reading!</div>', unsafe_allow_html=True)
        for p in unread:
            st.markdown(ui.paper_card_html(p), unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# TASK BOARD
# ─────────────────────────────────────────────────────────────

def page_tasks(user: str):
    tasks      = dl.load_tasks()
    statuses   = dl.get_task_statuses()
    priorities = dl.get_priorities()
    categories = dl.get_categories()
    team       = dl.get_team_names()

    ui.page_header("Task Board", "Filter, update status, and edit task details inline")

    f1, f2, f3, f4 = st.columns(4)
    f_status   = f1.selectbox("Status",   ["All"] + statuses)
    f_member   = f2.selectbox("Assignee", ["All"] + team)
    f_priority = f3.selectbox("Priority", ["All"] + priorities)
    f_cat      = f4.selectbox("Category", ["All"] + categories)

    filtered = tasks
    if f_status   != "All": filtered = [t for t in filtered if t["status"]       == f_status]
    if f_member   != "All": filtered = [t for t in filtered if f_member          in t.get("assignees", [])]
    if f_priority != "All": filtered = [t for t in filtered if t.get("priority") == f_priority]
    if f_cat      != "All": filtered = [t for t in filtered if t.get("category") == f_cat]
    filtered = sorted(filtered, key=lambda x: (x.get("due") or "9999", x.get("priority", "Medium")))

    st.markdown(f"<div style='color:#64748b;font-size:0.8rem;margin-bottom:0.75rem;'>{len(filtered)} tasks</div>", unsafe_allow_html=True)

    if not filtered:
        st.markdown('<div class="card" style="text-align:center;color:#64748b;padding:2rem;">No tasks match your filters.</div>', unsafe_allow_html=True)
        return

    for t in filtered:
        d    = ui.days_until(t.get("due"))
        icon = "🔴" if (d is not None and d < 0) else ("🟡" if (d is not None and d <= 3) else "⚪")

        with st.expander(f"{icon}  {t['title']}  [{t['status']}]", expanded=False):
            # ── Info row ─────────────────────────────────────
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"**Status:** {ui.badge_html(t['status'])}", unsafe_allow_html=True)
            pcolor = ui.PRIORITY_COLOR.get(t.get("priority", "Medium"), "#94a3b8")
            c2.markdown(f"**Priority:** <span style='color:{pcolor};font-weight:600;'>{t.get('priority','')}</span>", unsafe_allow_html=True)
            c3.markdown(f"**Category:** `{t.get('category','')}`")
            st.markdown(f"**Assigned to:** {ui.chips_html(t.get('assignees', []))}", unsafe_allow_html=True)
            if t.get("due"):
                st.markdown(f"**Due:** {ui.due_label_html(t['due'])}", unsafe_allow_html=True)

            st.markdown("---")

            # ── Editable description ──────────────────────────
            new_desc = st.text_area(
                "Description / Notes",
                value=t.get("description", ""),
                height=90,
                key=f"desc_{t['id']}",
                placeholder="Add notes, links, or context..."
            )
            if new_desc != t.get("description", ""):
                if st.button("💾 Save description", key=f"save_desc_{t['id']}"):
                    dl.update_task(t["id"], {"description": new_desc})
                    st.success("Saved!")
                    st.rerun()

            # ── Status update ─────────────────────────────────
            cur_idx    = statuses.index(t["status"]) if t["status"] in statuses else 0
            new_status = st.selectbox("Update status", statuses, index=cur_idx, key=f"st_{t['id']}")
            if new_status != t["status"]:
                dl.update_task(t["id"], {"status": new_status})
                st.rerun()

            # ── Admin: delete ─────────────────────────────────
            if dl.is_admin(user):
                if st.button("🗑 Delete task", key=f"del_{t['id']}"):
                    dl.delete_task(t["id"])
                    st.rerun()


# ─────────────────────────────────────────────────────────────
# ADD TASK
# ─────────────────────────────────────────────────────────────

def page_add_task(user: str):
    ui.page_header("Add New Task", "Create a task and assign it to team members")

    statuses   = dl.get_task_statuses()
    priorities = dl.get_priorities()
    categories = dl.get_categories()
    team       = dl.get_team_names()

    with st.form("add_task_form", clear_on_submit=True):
        title       = st.text_input("Task title *", placeholder="e.g. Implement CWT pipeline using PyWavelets")
        description = st.text_area("Description / Notes", placeholder="Details, links, context...", height=100)
        c1, c2, c3  = st.columns(3)
        status      = c1.selectbox("Status",   statuses)
        priority    = c2.selectbox("Priority", priorities)
        category    = c3.selectbox("Category", categories)
        c4, c5      = st.columns(2)
        assignees   = c4.multiselect("Assign to", team, default=[user])
        due         = c5.date_input("Due date", value=None)
        submitted   = st.form_submit_button("➕ Add Task", type="primary", use_container_width=True)

    if submitted:
        if not title.strip():
            st.error("Task title is required.")
        else:
            dl.add_task({
                "id":          dl.new_id(),
                "title":       title.strip(),
                "description": description.strip(),
                "status":      status,
                "priority":    priority,
                "category":    category,
                "assignees":   assignees,
                "due":         str(due) if due else None,
                "created_by":  user,
                "created":     str(date.today()),
                "updated":     str(date.today()),
            })
            st.success(f"Task '{title.strip()}' added!")


# ─────────────────────────────────────────────────────────────
# LITERATURE TRACKER
# ─────────────────────────────────────────────────────────────

def page_literature(user: str):
    papers         = dl.load_papers()
    paper_statuses = dl.get_paper_statuses()
    paper_tags     = dl.get_paper_tags()
    team           = dl.get_team_names()

    ui.page_header("Literature Tracker", "Track research papers for the literature review")

    cols = st.columns(4)
    ui.metric_card(cols[0], len(papers),                                              "Total",    "#3b82f6")
    ui.metric_card(cols[1], sum(1 for p in papers if p.get("status") == "Read"),      "Read",     "#4ade80")
    ui.metric_card(cols[2], sum(1 for p in papers if p.get("status") == "Reading"),   "Reading",  "#fbbf24")
    ui.metric_card(cols[3], sum(1 for p in papers if p.get("status") == "To Read"),   "To Read",  "#94a3b8")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)
    f_status = f1.selectbox("Status",  ["All"] + paper_statuses)
    f_tag    = f2.selectbox("Tag",     ["All"] + paper_tags)
    f_reader = f3.selectbox("Reader",  ["All"] + team)

    filtered = papers
    if f_status != "All": filtered = [p for p in filtered if p.get("status")  == f_status]
    if f_tag    != "All": filtered = [p for p in filtered if f_tag             in p.get("tags", [])]
    if f_reader != "All": filtered = [p for p in filtered if f_reader          in p.get("readers", [])]

    st.markdown(f"<div style='color:#64748b;font-size:0.8rem;margin-bottom:0.75rem;'>{len(filtered)} papers</div>", unsafe_allow_html=True)

    if not filtered:
        st.markdown('<div class="card" style="text-align:center;color:#64748b;padding:2rem;">No papers match your filters.</div>', unsafe_allow_html=True)
        return

    for p in filtered:
        title_short  = p["title"][:80] + ("…" if len(p["title"]) > 80 else "")
        status_color = ui.STATUS_PAPER_COLOR.get(p.get("status", ""), "#94a3b8")

        with st.expander(f"📄  {title_short}", expanded=False):
            c1, c2 = st.columns(2)
            c1.markdown(f"**Authors:** {p.get('authors','—')}")
            c1.markdown(f"**Year:** {p.get('year','—')}  ·  **Source:** {p.get('journal','—')}")
            c2.markdown(f"**Status:** <span style='color:{status_color};font-weight:600;'>{p.get('status','')}</span>", unsafe_allow_html=True)
            c2.markdown(f"**Readers:** {ui.chips_html(p.get('readers',[]))}", unsafe_allow_html=True)
            if p.get("doi"):
                st.markdown(f"**DOI / URL:** [{p['doi']}]({p['doi']})")
            if p.get("tags"):
                st.markdown(f"**Tags:** {ui.tags_html(p['tags'])}", unsafe_allow_html=True)

            st.markdown("---")

            # ── Editable fields (everyone) ────────────────────
            new_abstract = st.text_area(
                "Abstract note",
                value=p.get("abstract", ""),
                height=80,
                key=f"abs_{p['id']}",
                placeholder="Short summary of what this paper is about..."
            )
            new_findings = st.text_area(
                "Key findings / relevance to project",
                value=p.get("key_findings", ""),
                height=80,
                key=f"kf_{p['id']}",
                placeholder="Why does this matter for the capstone?"
            )
            new_notes = st.text_area(
                "Team notes",
                value=p.get("notes", ""),
                height=80,
                key=f"nt_{p['id']}",
                placeholder="Quotes, follow-up questions, links..."
            )

            changed = (
                new_abstract != p.get("abstract", "") or
                new_findings != p.get("key_findings", "") or
                new_notes    != p.get("notes", "")
            )
            if changed:
                if st.button("💾 Save notes", key=f"save_notes_{p['id']}"):
                    dl.update_paper(p["id"], {
                        "abstract":     new_abstract,
                        "key_findings": new_findings,
                        "notes":        new_notes,
                    })
                    st.success("Notes saved!")
                    st.rerun()

            # ── Status update ─────────────────────────────────
            cur_idx    = paper_statuses.index(p["status"]) if p.get("status") in paper_statuses else 0
            new_status = st.selectbox("Update status", paper_statuses, index=cur_idx, key=f"pst_{p['id']}")
            if new_status != p.get("status"):
                dl.update_paper(p["id"], {"status": new_status})
                st.rerun()

            if dl.is_admin(user):
                if st.button("🗑 Delete paper", key=f"pdel_{p['id']}"):
                    dl.delete_paper(p["id"])
                    st.rerun()


# ─────────────────────────────────────────────────────────────
# ADD PAPER
# ─────────────────────────────────────────────────────────────

def page_add_paper(user: str):
    ui.page_header("Add Research Paper", "Log a paper for the literature review")

    paper_statuses = dl.get_paper_statuses()
    paper_tags     = dl.get_paper_tags()
    team           = dl.get_team_names()

    with st.form("add_paper_form", clear_on_submit=True):
        title   = st.text_input("Paper title *", placeholder="e.g. Wavelet-based analysis of oscillatory rheological data...")
        authors = st.text_input("Authors", placeholder="e.g. Smith J., Jones A.")
        c1, c2, c3 = st.columns(3)
        year    = c1.text_input("Year", placeholder="2023")
        journal = c2.text_input("Journal / Source", placeholder="e.g. Soft Matter")
        status  = c3.selectbox("Status", paper_statuses)
        doi     = st.text_input("DOI or URL", placeholder="https://doi.org/...")
        c4, c5  = st.columns(2)
        readers = c4.multiselect("Assigned reader(s)", team, default=[user])
        tags    = c5.multiselect("Tags", paper_tags)
        abstract     = st.text_area("Abstract note", placeholder="One or two sentences on what this paper is about...", height=80)
        key_findings = st.text_area("Key findings / relevance", placeholder="Why does this matter for the capstone?", height=80)
        notes        = st.text_area("Team notes", placeholder="Quotes to keep, follow-up questions, links...", height=80)
        submitted    = st.form_submit_button("📄 Add Paper", type="primary", use_container_width=True)

    if submitted:
        if not title.strip():
            st.error("Paper title is required.")
        else:
            dl.add_paper({
                "id":           dl.new_id(),
                "title":        title.strip(),
                "authors":      authors.strip(),
                "year":         year.strip(),
                "journal":      journal.strip(),
                "status":       status,
                "doi":          doi.strip(),
                "readers":      readers,
                "tags":         tags,
                "abstract":     abstract.strip(),
                "key_findings": key_findings.strip(),
                "notes":        notes.strip(),
                "added_by":     user,
                "added":        str(date.today()),
            })
            st.success("Paper added!")


# ─────────────────────────────────────────────────────────────
# MY ACCOUNT  (password change — available to everyone)
# ─────────────────────────────────────────────────────────────

def page_my_account(user: str):
    ui.page_header("My Account", "Change your password")

    st.markdown("#### 🔐 Change Password")
    with st.form("change_pwd_form"):
        current = st.text_input("Current password", type="password")
        new1    = st.text_input("New password", type="password")
        new2    = st.text_input("Confirm new password", type="password")
        if st.form_submit_button("Update Password", type="primary"):
            if not dl.check_password(user, current):
                st.error("Current password is wrong.")
            elif not new1:
                st.error("New password cannot be empty.")
            elif new1 != new2:
                st.error("Passwords do not match.")
            elif len(new1) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                dl.change_password(user, new1)
                st.success("Password updated!")


# ─────────────────────────────────────────────────────────────
# ADMIN PAGE  (admins only)
# ─────────────────────────────────────────────────────────────

def page_admin(user: str):
    if not dl.is_admin(user):
        st.error("Access denied — admins only.")
        return

    ui.page_header("Admin Panel", "Manage users, lists, and project data")

    tab1, tab2, tab3, tab4 = st.tabs(["👥 Users", "🏷 Lists & Tags", "⬇ Export Data", "⚠️ Danger Zone"])

    # ── Tab 1: Users ─────────────────────────────────────────
    with tab1:
        st.markdown("#### Current Team Members")
        all_users = dl.load_users_db()

        for u in all_users:
            is_me = u["name"] == user
            cols  = st.columns([3, 1, 1, 1])
            admin_label = "👑 Admin" if u["is_admin"] else "Member"
            cols[0].markdown(f"**{u['name']}**  <span style='color:#64748b;font-size:0.75rem;'>{admin_label}</span>", unsafe_allow_html=True)

            # Toggle admin (can't remove your own admin)
            if not is_me:
                new_admin = cols[1].checkbox(
                    "Admin",
                    value=u["is_admin"],
                    key=f"admin_toggle_{u['id']}"
                )
                if new_admin != u["is_admin"]:
                    dl.set_user_admin(u["name"], new_admin)
                    st.rerun()
            else:
                cols[1].markdown("<span style='color:#64748b;font-size:0.75rem;'>You</span>", unsafe_allow_html=True)

            # Delete user (can't delete yourself)
            if not is_me:
                if cols[3].button("🗑", key=f"del_user_{u['id']}", help="Delete user"):
                    dl.delete_user(u["name"])
                    st.rerun()

        st.markdown("---")
        st.markdown("#### Add New Team Member")
        with st.form("add_user_form", clear_on_submit=True):
            new_name  = st.text_input("Full name", placeholder="e.g. Jane Smith")
            new_pwd   = st.text_input("Temporary password", type="password", placeholder="They can change this after login")
            new_admin = st.checkbox("Grant admin access")
            if st.form_submit_button("➕ Add Member", type="primary"):
                if not new_name.strip():
                    st.error("Name is required.")
                elif not new_pwd:
                    st.error("Password is required.")
                elif len(new_pwd) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    ok = dl.create_user(new_name.strip(), new_pwd, is_admin=new_admin)
                    if ok:
                        st.success(f"User '{new_name.strip()}' created!")
                        st.rerun()
                    else:
                        st.error("A user with that name already exists.")

    # ── Tab 2: Lists & Tags ──────────────────────────────────
    with tab2:
        cfg = dl.load_config()

        def list_editor(label, config_key, current_values):
            st.markdown(f"#### {label}")
            c1, c2 = st.columns([3, 1])
            new_item = c1.text_input(f"Add to {label}", key=f"new_{config_key}", placeholder="Type and press Add →")
            if c2.button("Add →", key=f"add_{config_key}"):
                if new_item.strip() and new_item.strip() not in current_values:
                    updated = current_values + [new_item.strip()]
                    dl.update_config(config_key, updated)
                    st.rerun()
                elif new_item.strip() in current_values:
                    st.warning("Already exists.")

            for item in current_values:
                ic1, ic2 = st.columns([5, 1])
                ic1.markdown(f"<div class='card' style='padding:0.5rem 0.75rem;margin-bottom:0.3rem;'>{item}</div>", unsafe_allow_html=True)
                if ic2.button("✕", key=f"rm_{config_key}_{item}"):
                    updated = [v for v in current_values if v != item]
                    dl.update_config(config_key, updated)
                    st.rerun()
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        list_editor("Task Categories",    "categories",    dl.get_categories())
        st.markdown("---")
        list_editor("Paper Tags",         "paper_tags",    dl.get_paper_tags())
        st.markdown("---")
        list_editor("Task Statuses",      "task_status_options",  dl.get_task_statuses())
        st.markdown("---")
        list_editor("Paper Statuses",     "paper_status_options", dl.get_paper_statuses())

    # ── Tab 3: Export ─────────────────────────────────────────
    with tab3:
        st.markdown("#### Export Project Data")
        tasks  = dl.load_tasks()
        papers = dl.load_papers()
        c1, c2 = st.columns(2)
        c1.download_button("⬇ Tasks (JSON)",  json.dumps(tasks,  indent=2), "tasks_export.json",  "application/json", use_container_width=True)
        c2.download_button("⬇ Papers (JSON)", json.dumps(papers, indent=2), "papers_export.json", "application/json", use_container_width=True)
        st.info("Exports include all data as of this moment. Data is also backed up to Supabase continuously.")

    # ── Tab 4: Danger Zone ────────────────────────────────────
    with tab4:
        st.markdown("#### ⚠️ Danger Zone")
        st.warning("These actions are irreversible.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🗑 Delete ALL tasks", type="primary", use_container_width=True):
                if st.session_state.get("confirm_del_tasks"):
                    sb = dl.get_supabase()
                    if sb:
                        sb.table("tasks").delete().neq("id", "").execute()
                    dl._save_json(dl.TASKS_FILE, [])
                    st.session_state.pop("confirm_del_tasks")
                    st.success("All tasks deleted.")
                    st.rerun()
                else:
                    st.session_state["confirm_del_tasks"] = True
                    st.error("Click again to confirm deletion of ALL tasks.")
        with c2:
            if st.button("🗑 Delete ALL papers", type="primary", use_container_width=True):
                if st.session_state.get("confirm_del_papers"):
                    sb = dl.get_supabase()
                    if sb:
                        sb.table("papers").delete().neq("id", "").execute()
                    dl._save_json(dl.PAPERS_FILE, [])
                    st.session_state.pop("confirm_del_papers")
                    st.success("All papers deleted.")
                    st.rerun()
                else:
                    st.session_state["confirm_del_papers"] = True
                    st.error("Click again to confirm deletion of ALL papers.")