# 🌊 Gel Squad Hub

Project management + literature tracker for the Haemograph capstone team.

## File structure

```
capstone_app/
├── app.py                        ← entry point, routing only
├── data_layer.py                 ← Supabase + local JSON fallback
├── ui_components.py              ← CSS, HTML helpers, card renderers
├── pages.py                      ← one function per page
├── requirements.txt
├── supabase_setup.sql            ← run this once in Supabase
├── .gitignore
└── .streamlit/
    └── secrets_template.toml    ← copy → secrets.toml and fill in
```

---

## Step 1 — Set up Supabase (~5 minutes)

### 1a. Create a free Supabase project
1. Go to [supabase.com](https://supabase.com) and sign up (free)
2. Click **New Project** — give it any name, set a database password, pick a region close to you (e.g. Sydney)
3. Wait ~1 minute for it to spin up

### 1b. Create the tables
1. In your project dashboard go to **SQL Editor → New Query**
2. Paste the entire contents of `supabase_setup.sql`
3. Click **Run** — you should see "Success"
4. Go to **Table Editor** to confirm `tasks` and `papers` tables exist

### 1c. Get your credentials
1. Go to **Settings → API** in your Supabase project
2. Copy the **Project URL** (looks like `https://abcdefgh.supabase.co`)
3. Copy the **anon public** key (long string starting with `eyJ...`)

### 1d. Set up secrets
1. Copy `.streamlit/secrets_template.toml` → `.streamlit/secrets.toml`
2. Paste in your URL and key:
```toml
SUPABASE_URL = "https://abcdefgh.supabase.co"
SUPABASE_KEY = "eyJhbGc..."
```

---

## Step 2 — Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Works without Supabase too — falls back to local JSON in `/data/`.

---

## Step 3 — Deploy free on Streamlit Community Cloud

1. Push this folder to a **private GitHub repo**
2. Go to [share.streamlit.io](https://share.streamlit.io) → sign in with GitHub
3. Click **New app** → select repo → set file to `app.py` → Deploy
4. Once live: **App Settings → Secrets** → paste your `secrets.toml` contents → Save
5. Reboot the app — green **"Supabase synced"** pill appears in sidebar ✅

---

## Default login

- **Password:** `gelsquad2026`
- Change it in **Settings** (Rohan only)

---

## How the sync works

| Action | What happens |
|---|---|
| Load page | Reads from Supabase, saves local JSON backup |
| Add item | Writes to Supabase + local JSON simultaneously |
| Update status | Updates Supabase row + local JSON |
| Delete | Deletes from Supabase + local JSON |
| Supabase unreachable | Falls back to local JSON silently, syncs next time |

The sidebar shows **"Supabase synced"** (green) or **"Local only"** (red) so you always know the state.
