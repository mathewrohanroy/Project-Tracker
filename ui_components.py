"""
ui_components.py
================
All CSS, HTML helpers, badge renderers, and reusable card components.
Import these into app.py — no Streamlit page logic lives here.
"""

import streamlit as st
from datetime import date

# ── Colour palette ────────────────────────────────────────────
COLORS = {
    "navy":        "#0f1b2d",
    "navy2":       "#1a2d45",
    "blue":        "#2563eb",
    "blue_light":  "#3b82f6",
    "teal":        "#0d9488",
    "teal_light":  "#14b8a6",
    "amber":       "#d97706",
    "red":         "#dc2626",
    "green":       "#16a34a",
    "gray":        "#94a3b8",
    "border":      "#1e3a5f",
    "card":        "#111827",
    "text":        "#e2e8f0",
    "text2":       "#94a3b8",
}

STATUS_BADGE_CLASS = {
    "To Do":       "badge-todo",
    "In Progress": "badge-doing",
    "In Review":   "badge-review",
    "Done":        "badge-done",
    "Blocked":     "badge-blocked",
}

STATUS_PAPER_COLOR = {
    "To Read": "#94a3b8",
    "Reading": "#fbbf24",
    "Read":    "#4ade80",
    "Cited":   "#2dd4bf",
}

PRIORITY_COLOR = {
    "High":   "#f87171",
    "Medium": "#fbbf24",
    "Low":    "#4ade80",
}


# ── Global CSS ────────────────────────────────────────────────

def inject_css():
    """Call once at app startup to inject all global styles."""
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

* { font-family: 'Space Grotesk', sans-serif; box-sizing: border-box; }

:root {
    --navy:       #0f1b2d;
    --navy2:      #1a2d45;
    --blue:       #2563eb;
    --blue-l:     #3b82f6;
    --teal:       #0d9488;
    --teal-l:     #14b8a6;
    --amber:      #d97706;
    --red:        #dc2626;
    --green:      #16a34a;
    --gray:       #94a3b8;
    --border:     #1e3a5f;
    --card:       #111827;
    --text:       #e2e8f0;
    --text2:      #94a3b8;
    --bg:         #080f1a;
}

/* ── Layout ── */
.stApp { background: var(--bg); color: var(--text); }
.block-container { padding: 1.5rem 2rem; max-width: 1400px; }
#MainMenu, footer, header { visibility: hidden; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0c1624 !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }
section[data-testid="stSidebar"] .stRadio label { font-size: 0.9rem !important; }

/* ── Hide sidebar collapse button — sidebar is always open ── */
button[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"] > div:first-child button[kind="header"] { display: none !important; }
/* Hide the chevron/collapse arrow inside the sidebar */
section[data-testid="stSidebar"] button[data-testid="baseButton-header"] { display: none !important; }

/* ── Cards ── */
.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.65rem;
    transition: border-color 0.2s, transform 0.15s;
}
.card:hover { border-color: var(--blue-l); transform: translateY(-1px); }
.card.overdue  { border-left: 3px solid var(--red)   !important; }
.card.due-soon { border-left: 3px solid var(--amber) !important; }
.card.paper    { border-left: 3px solid var(--teal)  !important; background: #0d1829; }

/* ── Badges ── */
.badge {
    display: inline-block; padding: 2px 10px;
    border-radius: 20px; font-size: 0.7rem;
    font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase;
}
.badge-todo    { background:#1e293b; color:#94a3b8; border:1px solid #334155; }
.badge-doing   { background:#1e3a5f; color:#60a5fa; border:1px solid #2563eb; }
.badge-review  { background:#2d1f5e; color:#a78bfa; border:1px solid #7c3aed; }
.badge-done    { background:#14311f; color:#4ade80; border:1px solid #16a34a; }
.badge-blocked { background:#3b1111; color:#f87171; border:1px solid #dc2626; }

/* ── Tags & chips ── */
.chip {
    display:inline-block; background:#1e3a5f; color:#93c5fd;
    border-radius:20px; padding:2px 9px; font-size:0.72rem;
    margin:2px; border:1px solid #2563eb44;
}
.tag {
    display:inline-block; background:#0d2a2a; color:#2dd4bf;
    border:1px solid #0d9488; border-radius:4px;
    padding:1px 7px; font-size:0.68rem; margin:2px;
}

/* ── Metric cards ── */
.metric-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 12px; padding: 1rem 1.1rem; text-align: center;
}
.metric-num { font-size: 2rem; font-weight: 700; }
.metric-lbl { font-size: 0.72rem; color: var(--text2); text-transform:uppercase; letter-spacing:0.08em; margin-top:0.15rem; }

/* ── Section headings ── */
.section-title {
    font-size: 1.45rem; font-weight: 700; color: var(--text);
    margin-bottom: 0.2rem; letter-spacing: -0.02em;
}
.section-sub {
    font-size: 0.82rem; color: var(--text2); margin-bottom: 1.25rem;
}

/* ── Page header ── */
.page-header {
    border-bottom: 1px solid var(--border);
    padding-bottom: 1rem; margin-bottom: 1.75rem;
}
.page-header h1 {
    font-size: 1.6rem; font-weight: 700; color: var(--text);
    margin: 0 0 0.2rem; letter-spacing: -0.025em;
}
.page-header .sub { font-size: 0.82rem; color: var(--text2); }

/* ── Sheets status pill ── */
.sheets-ok   { background:#14311f; color:#4ade80; border:1px solid #16a34a; border-radius:20px; padding:3px 12px; font-size:0.72rem; font-weight:600; }
.sheets-off  { background:#3b1111; color:#f87171; border:1px solid #dc2626; border-radius:20px; padding:3px 12px; font-size:0.72rem; font-weight:600; }

/* ── Form inputs ── */
.stTextInput > div > div > input,
.stTextArea  > div > div > textarea,
.stSelectbox > div > div > div,
.stDateInput > div > div > input {
    background: #0c1624 !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
}
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'Space Grotesk', sans-serif !important;
}
div[data-testid="stExpander"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}
div[data-testid="stExpander"]:hover {
    border-color: var(--blue-l) !important;
}

/* ── Additional: hide ALL sidebar toggle buttons aggressively ── */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
button[aria-label="Close sidebar"],
button[aria-label="Open sidebar"] {
    display: none !important;
    visibility: hidden !important;
    pointer-events: none !important;
}

/* ── Sidebar toggle via session state ── */
.sidebar-hidden section[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
</style>
""", unsafe_allow_html=True)


# ── Primitive renderers ───────────────────────────────────────

def badge_html(status: str) -> str:
    cls = STATUS_BADGE_CLASS.get(status, "badge-todo")
    return f'<span class="badge {cls}">{status}</span>'


def chip_html(name: str) -> str:
    short = name.split()[0]
    return f'<span class="chip">{short}</span>'


def tag_html(t: str) -> str:
    return f'<span class="tag">{t}</span>'


def chips_html(names: list) -> str:
    return "".join(chip_html(n) for n in names)


def tags_html(tags: list) -> str:
    return "".join(tag_html(t) for t in tags)


def days_until(due_str) -> int | None:
    if not due_str:
        return None
    try:
        from datetime import datetime
        due = datetime.strptime(str(due_str), "%Y-%m-%d").date()
        return (due - date.today()).days
    except Exception:
        return None


def due_label_html(due_str) -> str:
    d = days_until(due_str)
    if d is None:
        return ""
    if d < 0:
        return f'<span style="color:#f87171;">⚠ {abs(d)}d overdue</span>'
    if d == 0:
        return '<span style="color:#fbbf24;">Due today!</span>'
    if d <= 3:
        return f'<span style="color:#fbbf24;">Due in {d}d</span>'
    return f'<span style="color:#64748b;">{due_str}</span>'


def urgency_class(due_str, status) -> str:
    if status == "Done":
        return ""
    d = days_until(due_str)
    if d is None:
        return ""
    if d < 0:
        return "overdue"
    if d <= 3:
        return "due-soon"
    return ""


# ── Composite components ──────────────────────────────────────

def metric_card(col, value, label, color):
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-num" style="color:{color};">{value}</div>
        <div class="metric-lbl">{label}</div>
    </div>""", unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    st.markdown(f"""
    <div class="page-header">
        <h1>{title}</h1>
        {"" if not subtitle else f'<div class="sub">{subtitle}</div>'}
    </div>""", unsafe_allow_html=True)


def section_heading(title: str, sub: str = ""):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if sub:
        st.markdown(f'<div class="section-sub">{sub}</div>', unsafe_allow_html=True)


def task_card_html(task: dict) -> str:
    urg = urgency_class(task.get("due"), task["status"])
    due = due_label_html(task.get("due"))
    assignees = chips_html(task.get("assignees", []))
    pcolor = PRIORITY_COLOR.get(task.get("priority", "Medium"), "#94a3b8")
    cat = task.get("category", "")
    return f"""
    <div class="card {urg}">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:0.5rem;">
            <div style="font-weight:600;font-size:0.92rem;color:#e2e8f0;flex:1;">{task['title']}</div>
            {badge_html(task['status'])}
        </div>
        <div style="margin-top:0.5rem;display:flex;flex-wrap:wrap;gap:0.5rem;align-items:center;">
            <span style="font-size:0.73rem;color:#64748b;">{cat}</span>
            <span style="font-size:0.73rem;color:{pcolor};">● {task.get('priority','')}</span>
            {due}
        </div>
        <div style="margin-top:0.45rem;">{assignees}</div>
    </div>"""


def paper_card_html(paper: dict) -> str:
    status_color = STATUS_PAPER_COLOR.get(paper.get("status", ""), "#94a3b8")
    t_html = tags_html(paper.get("tags", []))
    r_html = chips_html(paper.get("readers", []))
    title = paper["title"][:72] + ("…" if len(paper["title"]) > 72 else "")
    return f"""
    <div class="card paper">
        <div style="font-weight:600;font-size:0.92rem;color:#e2e8f0;margin-bottom:0.3rem;">{title}</div>
        <div style="font-size:0.75rem;color:#64748b;margin-bottom:0.35rem;">
            {paper.get('authors','')[:50]}
            {"&nbsp;·&nbsp;" + paper.get('year','') if paper.get('year') else ""}
            {"&nbsp;·&nbsp;" + paper.get('journal','') if paper.get('journal') else ""}
        </div>
        <div style="display:flex;flex-wrap:wrap;align-items:center;gap:4px;margin-bottom:0.35rem;">
            <span style="color:{status_color};font-size:0.73rem;font-weight:600;">{paper.get('status','')}</span>
            &nbsp;{t_html}
        </div>
        <div>{r_html}</div>
    </div>"""


def urgent_task_card_html(task: dict) -> str:
    d = days_until(task.get("due"))
    color = "#f87171" if (d is not None and d < 0) else "#fbbf24"
    if d is None:
        label = ""
    elif d < 0:
        label = f"{abs(d)}d overdue"
    elif d == 0:
        label = "Due today"
    else:
        label = f"{d}d left"
    assignees = ", ".join(n.split()[0] for n in task.get("assignees", []))
    return f"""
    <div class="card" style="border-left:3px solid {color};">
        <div style="font-size:0.88rem;font-weight:600;color:#e2e8f0;">{task['title']}</div>
        <div style="font-size:0.73rem;color:{color};margin-top:0.3rem;">{label} · {assignees}</div>
    </div>"""


def sheets_status_pill(connected: bool) -> str:
    if connected:
        return '<span class="sheets-ok">● Sheets synced</span>'
    return '<span class="sheets-off">● Local only</span>'


def sidebar_ui(current_user: str, connected: bool) -> str:
    """Render sidebar content, return selected page key."""
    nav = {
        "📊 Dashboard":          "Dashboard",
        "✅ Task Board":         "Task Board",
        "📚 Literature Tracker": "Literature Tracker",
        "➕ Add Task":           "Add Task",
        "📄 Add Paper":          "Add Paper",
        "👤 My Account":         "My Account",
    }
    try:
        import data_layer as _dl
        if _dl.is_admin(current_user):
            nav["🛠 Admin Panel"] = "Admin Panel"
    except Exception:
        pass

    with st.sidebar:
        st.markdown(f"""
        <div style="padding:1rem 0 1.25rem;">
            <div style="font-size:1.35rem;font-weight:700;color:#e2e8f0;
                        letter-spacing:-0.02em;">🌊 Gel Squad</div>
            <div style="font-size:0.72rem;color:#475569;margin-top:0.15rem;">
                Haemograph Capstone 2026</div>
        </div>
        <div style="background:#0c1f0c;border:1px solid #166534;border-radius:8px;
                    padding:0.55rem 0.9rem;margin-bottom:0.75rem;">
            <div style="font-size:0.68rem;color:#4ade80;text-transform:uppercase;
                        letter-spacing:0.08em;">Logged in as</div>
            <div style="font-size:0.9rem;font-weight:600;color:#86efac;">
                {current_user.split()[0]}</div>
        </div>
        <div style="margin-bottom:1.25rem;">{sheets_status_pill(connected)}</div>
        """, unsafe_allow_html=True)

        selected = st.radio("Navigation", list(nav.keys()), label_visibility="collapsed")

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        if st.button("Log out", use_container_width=True):
            return "__logout__"

        return nav[selected]
