"""
create_first_user.py
====================
Run this ONCE on your local machine to create the first admin user.

Usage:
    pip install supabase bcrypt
    python create_first_user.py

It will ask for your Supabase URL, key, and the password you want.
Then it hashes it with bcrypt and inserts directly into the database.
"""

import uuid
from datetime import date

# ── Get Supabase credentials ──────────────────────────────────
print()
print("=" * 55)
print("  Gel Squad Hub — First User Setup")
print("=" * 55)
print()

SUPABASE_URL = input("Paste your Supabase URL (https://xxx.supabase.co): ").strip()
SUPABASE_KEY = input("Paste your Supabase anon key: ").strip()
print()

NAME     = input("Your full name (exactly as it appears in the app): ").strip()
PASSWORD = input("Choose a password (min 6 chars): ").strip()
print()

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Supabase URL and key are required.")
    exit(1)

if not NAME:
    print("❌ Name is required.")
    exit(1)

if len(PASSWORD) < 6:
    print("❌ Password must be at least 6 characters.")
    exit(1)

# ── Hash password ─────────────────────────────────────────────
print("Hashing password...")
try:
    import bcrypt
    password_hash = bcrypt.hashpw(PASSWORD.encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")
    method = "bcrypt"
except ImportError:
    import hashlib
    password_hash = "sha256:" + hashlib.sha256(PASSWORD.encode()).hexdigest()
    method = "sha256 (bcrypt not installed — run: pip install bcrypt for stronger security)"

print(f"✅ Password hashed using {method}")

# ── Connect to Supabase ───────────────────────────────────────
print("Connecting to Supabase...")
try:
    from supabase import create_client
    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Connected")
except ImportError:
    print("❌ supabase not installed. Run: pip install supabase")
    exit(1)
except Exception as e:
    print(f"❌ Could not connect: {e}")
    exit(1)

# ── Delete existing row if any ────────────────────────────────
try:
    sb.table("users").delete().eq("name", NAME).execute()
    print(f"Cleared any existing record for '{NAME}'")
except Exception as e:
    print(f"Note: {e}")

# ── Insert user ───────────────────────────────────────────────
user = {
    "id":            str(uuid.uuid4())[:8],
    "name":          NAME,
    "password_hash": password_hash,
    "is_admin":      True,
    "created":       str(date.today()),
}

try:
    sb.table("users").insert(user).execute()
    print()
    print("=" * 55)
    print(f"  ✅ User created successfully!")
    print(f"  Name    : {NAME}")
    print(f"  Password: {PASSWORD}")
    print(f"  Role    : Admin")
    print("=" * 55)
    print()
    print("You can now log into the app with these credentials.")
    print("Go to My Account to change your password after login.")
    print()
except Exception as e:
    print(f"❌ Failed to insert user: {e}")
    print()
    print("Make sure you ran supabase_setup.sql first in Supabase.")