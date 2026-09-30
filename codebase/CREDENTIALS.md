# CREDENTIALS — Demo / Development Accounts

> **Never commit real secrets.** This file contains only demo seed data for local development.
> All accounts have `is_first_login=True` unless noted — password change + TOTP setup on first login.

---

## Seeded Users (`backend/seed.py`)

| Role | Email | Password |
|------|-------|----------|
| `SUPER_ADMIN` | `admin@ncrb.gov.in` | `Admin@1234` |
| `CASE_OFFICER` | `officer.sharma@police.in` | `officer123` |
| `CASE_OFFICER` | `officer.gupta@police.in` | `Gupta456` |
| `INVESTIGATOR` | `inv.patel@police.in` | `patel2024` |
| `INVESTIGATOR` | `inv.singh@police.in` | `singh123` |
| `INVESTIGATOR` | `inv.rao@forensics.in` | `rao2024` |
| `PROSECUTOR` | `prosecutor@court.in` | `prosec123` |
| `AUDITOR` | `auditor@ncrb.gov.in` | `audit2024` |
| `VIEWER` | `viewer@ncrb.gov.in` | `view1234` |

---

## Demo Dashboard Account (`backend/scripts/seed_rjav.py`)

| Role | Email | Password | Notes |
|------|-------|----------|-------|
| `CASE_OFFICER` | `rjav@dot.com` | `Rjav@1234` | `is_first_login=False` — skip onboarding; pre-seeded with 8 cases + documents |

---

## Database (PostgreSQL)

| Key | Value |
|-----|-------|
| Host | `localhost:5433` |
| Database | `dms` |
| User | `dms_app_user` |
| Password | `devpassword` |

---

## Environment Secrets (`.env` — never commit)

| Variable | Purpose |
|----------|---------|
| `JWT_SECRET` | Signs JWT access tokens |
| `KMS_WRAPPING_KEY` | Wraps AES document master keys |
| `SECRET_KEY` | Flask cookie signing only |
| `GMAIL_USER` / `GMAIL_APP_PASSWORD` | Share-link OTP email delivery |

See `.env.example` for the full template.

---

## Re-seeding

```bash
# First time / fresh DB
cd backend
python seed.py
python scripts/seed_rjav.py

# Wipe and re-seed everything
python seed.py --wipe
python scripts/seed_rjav.py --wipe
```
