"""
data_layer.py
=============
Primary storage : Supabase (Postgres)
Fallback        : local JSON in /data/
"""

import os
import json
import uuid
import streamlit as st
from datetime import date

try:
    import bcrypt
    BCRYPT_OK = True
except ImportError:
    BCRYPT_OK = False

try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# ── Paths ─────────────────────────────────────────────────────
DATA_DIR    = "data"
TASKS_FILE  = os.path.join(DATA_DIR, "tasks.json")
PAPERS_FILE = os.path.join(DATA_DIR, "papers.json")
USERS_FILE  = os.path.join(DATA_DIR, "users.json")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")
CHARTER_FILE = os.path.join(DATA_DIR, "charter.json")
os.makedirs(DATA_DIR, exist_ok=True)

DEFAULT_CONFIG = {
    "categories":           ["Analysis","Data Collection","Literature Review","Report Writing","Meeting Prep","Experiments","Other"],
    "paper_tags":           ["Wavelet","Fourier/STFT","Rheology","Gelation","Blood Coagulation","Signal Processing","Methods","Background","Key Paper"],
    "paper_status_options": ["To Read","Reading","Read","Cited"],
    "task_status_options":  ["To Do","In Progress","In Review","Done","Blocked"],
    "priorities":           ["High","Medium","Low"],
}


# ─────────────────────────────────────────────────────────────
# Supabase client — NO cache_resource, just a simple function
# cache_resource caused the client to be built before st.secrets
# was ready, returning None permanently for the whole session
# ─────────────────────────────────────────────────────────────

def get_supabase():
    if not SUPABASE_AVAILABLE:
        return None
    # Store on session_state so we only create it once per session
    # but AFTER st.secrets is definitely available
    if "_sb_client" not in st.session_state:
        try:
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]
            st.session_state["_sb_client"] = create_client(url, key)
        except Exception as e:
            st.session_state["_sb_client"] = None
    return st.session_state["_sb_client"]


def supabase_connected() -> bool:
    return get_supabase() is not None


def sheets_connected() -> bool:
    return supabase_connected()


# ─────────────────────────────────────────────────────────────
# Local JSON helpers
# ─────────────────────────────────────────────────────────────

def _load_json(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default


def _save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


# ─────────────────────────────────────────────────────────────
# Password hashing
# ─────────────────────────────────────────────────────────────

def hash_password(plaintext: str) -> str:
    if BCRYPT_OK:
        return bcrypt.hashpw(plaintext.encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")
    import hashlib
    return "sha256:" + hashlib.sha256(plaintext.encode()).hexdigest()


def verify_password(plaintext: str, stored_hash: str) -> bool:
    if not stored_hash:
        return False
    if stored_hash.startswith("sha256:"):
        import hashlib
        return stored_hash == "sha256:" + hashlib.sha256(plaintext.encode()).hexdigest()
    if BCRYPT_OK:
        try:
            return bcrypt.checkpw(plaintext.encode("utf-8"), stored_hash.encode("utf-8"))
        except Exception:
            return False
    return False


# ─────────────────────────────────────────────────────────────
# Row normalisation
# ─────────────────────────────────────────────────────────────

def _norm_task(row):
    return {
        "id":          row.get("id", ""),
        "title":       row.get("title", ""),
        "description": row.get("description", "") or "",
        "status":      row.get("status", "To Do"),
        "priority":    row.get("priority", "Medium"),
        "category":    row.get("category", "Other"),
        "assignees":   row.get("assignees") or [],
        "due":         row.get("due") or None,
        "created_by":  row.get("created_by", ""),
        "created":     str(row.get("created", "")),
        "updated":     str(row.get("updated", "")),
    }

def _norm_paper(row):
    return {
        "id":           row.get("id", ""),
        "title":        row.get("title", ""),
        "authors":      row.get("authors", "") or "",
        "year":         row.get("year", "") or "",
        "journal":      row.get("journal", "") or "",
        "status":       row.get("status", "To Read"),
        "doi":          row.get("doi", "") or "",
        "readers":      row.get("readers") or [],
        "tags":         row.get("tags") or [],
        "abstract":     row.get("abstract", "") or "",
        "key_findings": row.get("key_findings", "") or "",
        "notes":        row.get("notes", "") or "",
        "added_by":     row.get("added_by", ""),
        "added":        str(row.get("added", "")),
    }

def _norm_user(row):
    return {
        "id":            row.get("id", ""),
        "name":          row.get("name", ""),
        "password_hash": row.get("password_hash", ""),
        "is_admin":      bool(row.get("is_admin", False)),
        "created":       str(row.get("created", "")),
    }


# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────

def load_config():
    sb = get_supabase()
    if sb:
        try:
            res = sb.table("config").select("*").execute()
            cfg = {row["key"]: row["value"] for row in res.data}
            merged = {**DEFAULT_CONFIG, **cfg}
            _save_json(CONFIG_FILE, merged)
            return merged
        except Exception:
            pass
    return _load_json(CONFIG_FILE, DEFAULT_CONFIG)


def update_config(key, value):
    cfg = load_config()
    cfg[key] = value
    _save_json(CONFIG_FILE, cfg)
    sb = get_supabase()
    if sb:
        try:
            sb.table("config").upsert({"key": key, "value": value}).execute()
        except Exception:
            pass


def get_categories():     return load_config().get("categories",           DEFAULT_CONFIG["categories"])
def get_paper_tags():     return load_config().get("paper_tags",           DEFAULT_CONFIG["paper_tags"])
def get_paper_statuses(): return load_config().get("paper_status_options", DEFAULT_CONFIG["paper_status_options"])
def get_task_statuses():  return load_config().get("task_status_options",  DEFAULT_CONFIG["task_status_options"])
def get_priorities():     return load_config().get("priorities",           DEFAULT_CONFIG["priorities"])


# ─────────────────────────────────────────────────────────────
# USERS
# ─────────────────────────────────────────────────────────────

def load_users_db():
    sb = get_supabase()
    if sb:
        try:
            res = sb.table("users").select("*").execute()
            users = [_norm_user(r) for r in res.data]
            _save_json(USERS_FILE, users)
            return users
        except Exception:
            pass
    stored = _load_json(USERS_FILE, [])
    if isinstance(stored, dict):
        return []
    return [_norm_user(u) for u in stored]


def get_user_by_name(name):
    for u in load_users_db():
        if u["name"] == name:
            return u
    return None


def get_team_names():
    users = load_users_db()
    if users:
        return [u["name"] for u in users]
    return ["Rohan Roy Mathew", "Jianhao Zhang", "Xuan Zhang", "Xingcan Wang", "Ria Mishra"]


def user_exists(name):
    return get_user_by_name(name) is not None


def create_user(name, password, is_admin=False):
    if user_exists(name):
        return False
    user = {
        "id":            new_id(),
        "name":          name,
        "password_hash": hash_password(password),
        "is_admin":      is_admin,
        "created":       str(date.today()),
    }
    users = load_users_db()
    users.append(user)
    _save_json(USERS_FILE, users)
    sb = get_supabase()
    if sb:
        try:
            sb.table("users").insert(user).execute()
        except Exception:
            pass
    return True


def update_user_password(name, new_password):
    new_hash = hash_password(new_password)
    users = load_users_db()
    for u in users:
        if u["name"] == name:
            u["password_hash"] = new_hash
    _save_json(USERS_FILE, users)
    sb = get_supabase()
    if sb:
        try:
            sb.table("users").update({"password_hash": new_hash}).eq("name", name).execute()
        except Exception:
            pass


def set_user_admin(name, is_admin_val):
    users = load_users_db()
    for u in users:
        if u["name"] == name:
            u["is_admin"] = is_admin_val
    _save_json(USERS_FILE, users)
    sb = get_supabase()
    if sb:
        try:
            sb.table("users").update({"is_admin": is_admin_val}).eq("name", name).execute()
        except Exception:
            pass


def delete_user(name):
    users = [u for u in load_users_db() if u["name"] != name]
    _save_json(USERS_FILE, users)
    sb = get_supabase()
    if sb:
        try:
            sb.table("users").delete().eq("name", name).execute()
        except Exception:
            pass


def is_admin(name):
    u = get_user_by_name(name)
    return bool(u and u.get("is_admin"))


# ─────────────────────────────────────────────────────────────
# SESSION AUTH
# ─────────────────────────────────────────────────────────────

def get_current_user():
    return st.session_state.get("current_user")


def set_current_user(name):
    st.session_state["current_user"] = name


def check_password(name, pwd):
    u = get_user_by_name(name)
    if not u:
        return False
    return verify_password(pwd, u.get("password_hash", ""))


def change_password(name, new_pwd):
    update_user_password(name, new_pwd)


# ─────────────────────────────────────────────────────────────
# TASKS
# ─────────────────────────────────────────────────────────────

def load_tasks():
    sb = get_supabase()
    if sb:
        try:
            res = sb.table("tasks").select("*").order("created").execute()
            tasks = [_norm_task(r) for r in res.data]
            _save_json(TASKS_FILE, tasks)
            return tasks
        except Exception:
            pass
    return _load_json(TASKS_FILE, [])


def add_task(task):
    task = _norm_task(task)
    tasks = load_tasks()
    tasks = [t for t in tasks if t.get("id") != task.get("id")]
    tasks.append(task)
    _save_json(TASKS_FILE, tasks)
    sb = get_supabase()
    if sb:
        try:
            sb.table("tasks").upsert(task).execute()
        except Exception:
            pass


def update_task(task_id, updates):
    tasks = load_tasks()
    updated_task = None
    for t in tasks:
        if t["id"] == task_id:
            t.update(updates)
            t["updated"] = str(date.today())
            updated_task = _norm_task(t)
            t.update(updated_task)
            break
    _save_json(TASKS_FILE, tasks)
    sb = get_supabase()
    if sb and updated_task:
        try:
            sb.table("tasks").upsert(updated_task).execute()
        except Exception:
            try:
                fallback_updates = dict(updates)
                fallback_updates["updated"] = str(date.today())
                sb.table("tasks").update(fallback_updates).eq("id", task_id).execute()
            except Exception:
                pass


def delete_task(task_id):
    tasks = [t for t in load_tasks() if t["id"] != task_id]
    _save_json(TASKS_FILE, tasks)
    sb = get_supabase()
    if sb:
        try:
            sb.table("tasks").delete().eq("id", task_id).execute()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────
# PAPERS
# ─────────────────────────────────────────────────────────────

def load_papers():
    sb = get_supabase()
    if sb:
        try:
            res = sb.table("papers").select("*").order("added").execute()
            papers = [_norm_paper(r) for r in res.data]
            _save_json(PAPERS_FILE, papers)
            return papers
        except Exception:
            pass
    return _load_json(PAPERS_FILE, [])


def add_paper(paper):
    paper = _norm_paper(paper)
    papers = load_papers()
    papers = [p for p in papers if p.get("id") != paper.get("id")]
    papers.append(paper)
    _save_json(PAPERS_FILE, papers)
    sb = get_supabase()
    if sb:
        try:
            sb.table("papers").upsert(paper).execute()
        except Exception:
            pass


def update_paper(paper_id, updates):
    papers = load_papers()
    updated_paper = None
    for p in papers:
        if p["id"] == paper_id:
            p.update(updates)
            updated_paper = _norm_paper(p)
            p.update(updated_paper)
            break
    _save_json(PAPERS_FILE, papers)
    sb = get_supabase()
    if sb and updated_paper:
        try:
            sb.table("papers").upsert(updated_paper).execute()
        except Exception:
            try:
                sb.table("papers").update(updates).eq("id", paper_id).execute()
            except Exception:
                pass


def delete_paper(paper_id):
    papers = [p for p in load_papers() if p["id"] != paper_id]
    _save_json(PAPERS_FILE, papers)
    sb = get_supabase()
    if sb:
        try:
            sb.table("papers").delete().eq("id", paper_id).execute()
        except Exception:
            pass




# ─────────────────────────────────────────────────────────────
# PROJECT CHARTER
# ─────────────────────────────────────────────────────────────

def _default_charter():
    return {
        "id": "main",
        "project_name": "Gel Squad Capstone",
        "project_owner": "",
        "project_summary": "",
        "objective": "",
        "scope": "",
        "success_metrics": "",
        "deliverables": "",
        "risks": "",
        "notes": "",
        "start_date": None,
        "target_date": None,
        "updated": str(date.today()),
        "milestones": [],
    }


def _norm_milestone(row):
    return {
        "id": row.get("id", new_id()),
        "title": row.get("title", ""),
        "owner": row.get("owner", ""),
        "description": row.get("description", "") or "",
        "status": row.get("status", "Planned") or "Planned",
        "due": row.get("due") or None,
    }


def _norm_charter(row):
    base = _default_charter()
    base.update({
        "id": row.get("id", "main"),
        "project_name": row.get("project_name", base["project_name"]),
        "project_owner": row.get("project_owner", "") or "",
        "project_summary": row.get("project_summary", "") or "",
        "objective": row.get("objective", "") or "",
        "scope": row.get("scope", "") or "",
        "success_metrics": row.get("success_metrics", "") or "",
        "deliverables": row.get("deliverables", "") or "",
        "risks": row.get("risks", "") or "",
        "notes": row.get("notes", "") or "",
        "start_date": row.get("start_date") or None,
        "target_date": row.get("target_date") or None,
        "updated": str(row.get("updated", date.today())),
        "milestones": [_norm_milestone(m) for m in (row.get("milestones") or [])],
    })
    return base


def load_charter():
    sb = get_supabase()
    if sb:
        try:
            res = sb.table("project_charter").select("*").limit(1).execute()
            if res.data:
                charter = _norm_charter(res.data[0])
                _save_json(CHARTER_FILE, charter)
                return charter
        except Exception:
            pass
    stored = _load_json(CHARTER_FILE, _default_charter())
    if isinstance(stored, list):
        stored = stored[0] if stored else _default_charter()
    return _norm_charter(stored)


def save_charter(updates: dict):
    charter = load_charter()
    charter.update(updates or {})
    charter["milestones"] = [_norm_milestone(m) for m in charter.get("milestones", [])]
    charter["updated"] = str(date.today())
    _save_json(CHARTER_FILE, charter)
    sb = get_supabase()
    if sb:
        try:
            sb.table("project_charter").upsert(charter).execute()
        except Exception:
            pass
    return charter


def add_milestone(milestone: dict):
    charter = load_charter()
    ms = _norm_milestone(milestone)
    charter.setdefault("milestones", []).append(ms)
    save_charter(charter)
    return ms


def update_milestone(milestone_id: str, updates: dict):
    charter = load_charter()
    milestones = charter.get("milestones", [])
    for m in milestones:
        if m.get("id") == milestone_id:
            m.update(updates or {})
    charter["milestones"] = [_norm_milestone(m) for m in milestones]
    save_charter(charter)


def delete_milestone(milestone_id: str):
    charter = load_charter()
    charter["milestones"] = [m for m in charter.get("milestones", []) if m.get("id") != milestone_id]
    save_charter(charter)


# ─────────────────────────────────────────────────────────────
# Unique ID
# ─────────────────────────────────────────────────────────────

def new_id():
    return str(uuid.uuid4())[:8]
