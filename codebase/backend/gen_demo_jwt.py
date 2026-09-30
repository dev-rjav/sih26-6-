#!/usr/bin/env python3
"""
gen_demo_jwt.py — generate a SUPER_ADMIN JWT for the PRAMAAN live demo visualizer.

Usage (from codebase/backend/):
    python gen_demo_jwt.py

Or pass a role explicitly:
    python gen_demo_jwt.py --role AUDITOR

What it does:
    Boots the Flask app factory (reads .env, loads config), then calls
    flask_jwt_extended.create_access_token() with the same claims as
    issue_access_token() in core/security.py — so the token is 100%
    accepted by every @jwt_required() endpoint and by dev_logs /stream.

    No database connection is made (SQLAlchemy only connects on first query).

Paste the printed token into the LIVE MODE panel in pramaan-demo.html.
"""

import argparse
import datetime as dt
import sys
import uuid
from pathlib import Path

# ── Ensure imports resolve from codebase/backend/ ─────────────────────────────
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# ── Parse args ─────────────────────────────────────────────────────────────────
VALID_ROLES = ["SUPER_ADMIN", "CASE_OFFICER", "INVESTIGATOR", "PROSECUTOR", "AUDITOR", "VIEWER"]

parser = argparse.ArgumentParser(description="Generate a demo JWT for PRAMAAN.")
parser.add_argument(
    "--role", default="SUPER_ADMIN",
    choices=VALID_ROLES,
    help="Role embedded in the token (default: SUPER_ADMIN — can reach all endpoints).",
)
parser.add_argument(
    "--ttl", type=int, default=None,
    help="Override TTL in seconds (default: JWT_ACCESS_TTL_SECONDS from .env, or 28800).",
)
args = parser.parse_args()

# ── Boot Flask app (loads .env, configures JWT) ────────────────────────────────
print("Booting Flask app factory…", flush=True)
try:
    from app import create_app
except ImportError as e:
    print(f"\nERROR: could not import app factory: {e}")
    print("Make sure you run this script from codebase/backend/")
    print("  cd codebase/backend && python gen_demo_jwt.py")
    sys.exit(1)

try:
    app = create_app()
except Exception as e:
    print(f"\nERROR: create_app() failed: {e}")
    print("Check that your .env has SECRET_KEY, JWT_SECRET, KMS_WRAPPING_KEY, DATABASE_URL set.")
    sys.exit(1)

# ── Generate token inside app context ─────────────────────────────────────────
with app.app_context():
    from flask_jwt_extended import create_access_token

    now = dt.datetime.now(dt.timezone.utc)
    ttl_secs = args.ttl or int(app.config.get("JWT_ACCESS_TTL_SECONDS", 28800))

    # Fake identity UUID — dev_logs only calls decode_token() to verify the
    # signature; it never looks up the user in the DB.
    demo_user_id = str(uuid.uuid4())
    demo_dept_id = str(uuid.uuid4())

    token = create_access_token(
        identity=demo_user_id,
        expires_delta=dt.timedelta(seconds=ttl_secs),
        additional_claims={
            "role": args.role,
            "dept": demo_dept_id,
            "mfa_at": int(now.timestamp()),
        },
    )

    expires_at = now + dt.timedelta(seconds=ttl_secs)
    hours = ttl_secs // 3600

# ── Print result ───────────────────────────────────────────────────────────────
SEP = "─" * 72

print(f"\n{SEP}")
print("  PRAMAAN Demo JWT")
print(SEP)
print(f"  Role     : {args.role}")
print(f"  User ID  : {demo_user_id}  (synthetic — no DB record)")
print(f"  Issued   : {now.strftime('%Y-%m-%d %H:%M:%S UTC')}")
print(f"  Expires  : {expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}  ({hours}h)")
print(SEP)
print()
print(token)
print()
print(SEP)
print("  Paste the token above into the LIVE MODE panel → JWT field.")
print(f"  SSE endpoint: http://localhost:5000/api/v1/dev/stream?token=<token>")
print(f"  Requires Flask running with DEBUG=True (ENVIRONMENT=development in .env).")
print(SEP)
print()
