# Share Link OTP Verification — Spec

## What and why
Before a recipient can download or preview a shared document/case, they must verify their identity by entering a 6-digit OTP sent to the email they provide. This proves email ownership, not just knowledge of the share URL. Without OTP, anyone who forwards the URL can access the content.

## Exact files modified
**Backend:**
- `app/core/email_otp.py` — NEW: in-memory OTP store + Gmail SMTP sender
- `app/config.py` — add `GMAIL_USER`, `GMAIL_APP_PASSWORD`
- `app/blueprints/share_access.py` — new `POST /{token}/request-otp` route; all access routes verify OTP before acting
- `app/core/rate_limit.py` — add `OTP_REQUEST_LIMITS`
- `app/schemas/sharing_schemas.py` — add `OtpRequestSchema`; add `otp` field to `ShareAccessSchema`
- `app/core/audit_events.py` — add `SHARE_OTP_SENT`
- `codebase/.env.example` — add `GMAIL_USER`, `GMAIL_APP_PASSWORD`

**Frontend:**
- `src/lib/shareApi.ts` — add `requestShareOtp()`; add `otp` param to all public access calls
- `src/pages/ShareAccessPage.tsx` — two-step UI: email → OTP → action

## OTP design
- 6-digit numeric, `secrets.randbelow(1_000_000)` padded to 6 digits
- TTL: 10 minutes
- Max 3 attempts then invalidate (force re-request)
- Store key: `sha256(raw_token + ":" + email_lower)` — decoupled per (link, email) pair
- Stored value: `{otp_hash: sha256(otp), expires_at, attempts}`
- Single-use: deleted from store on correct verification
- In-memory (no Redis in prototype); survives process restart as a known limitation

## API contract
```
POST /api/v1/share/{token}/request-otp
Body: { "email": "string" }
→ 200 { "message": "OTP sent to your email. Valid for 10 minutes." }
→ 400 VALIDATION_ERROR (no/invalid email)
→ 403 EMAIL_MISMATCH (link has allowed_email restriction; provided email doesn't match)
→ 410 LINK_EXPIRED / LINK_REVOKED / LINK_EXHAUSTED
→ 429 rate limit
→ 503 EMAIL_UNAVAILABLE / EMAIL_SEND_FAILED

All existing access endpoints (download, preview, file/download, file/preview):
Body now: { "email": "string", "otp": "string (6 digits)" }
OTP is checked in-memory BEFORE use_count is incremented (no wasted uses on OTP failure).
→ 403 OTP_REQUIRED — email given but no OTP
→ 403 OTP_INVALID — wrong code (message includes attempts remaining)
→ 403 OTP_EXPIRED — TTL elapsed or never requested
→ 403 OTP_EXHAUSTED — 3 bad attempts
```

## Security threat model
| Threat | Mitigation |
|--------|-----------|
| Attacker forwards share URL | Must also have inbox access to receive OTP |
| Brute-force OTP (1M possibilities) | Max 3 attempts → lock; rate limit 3/hr per IP |
| Timing attack on OTP compare | `sha256(otp)` compared — not constant-time but input space small enough that 3-attempt lock dominates |
| OTP reuse | Deleted from store on first correct use |
| OTP for wrong link | Store key includes raw_token — mismatched key → OTP_EXPIRED |
| Email enumeration via request-otp | Acceptable for law enforcement (closed-user system); 3/hr rate limit limits damage |
| Gmail credentials exposed | `GMAIL_APP_PASSWORD` is an app password (narrow scope, revocable); stored only in env |

## Edge cases
- Link has no `allowed_email`: OTP is still required (email is always collected). Any email gets OTP; that email is the identity proof for this access session.
- User changes email after OTP sent: Frontend resets `otpSent` → they must re-request OTP.
- OTP expires mid-session: Backend returns `OTP_EXPIRED`; frontend shows "OTP expired, request a new one."
- Email send failure (SMTP error): Backend returns 503; frontend shows "Failed to send OTP."
- Preview endpoints (no use_count): OTP verified same way.

## Review
1. **Security holes?** OTP exhaustion requires re-request (limits brute force). Store key includes the raw token so OTPs don't cross link boundaries. Email is not logged in audit metadata to avoid PII in logs. Timing differences on sha256 comparison are negligible given 3-attempt lockout.
2. **Contradictions with CLAUDE.md / docs/SECURITY.md?** None. Uses parameterized queries (no new DB writes for OTP). No PII in audit logs. Rate-limited.
3. **Simpler design?** Could use a database table for OTPs, but in-memory is sufficient for prototype and avoids a migration. Could skip OTP for open links, but universal OTP is consistent and was requested.
4. **EDGE_CASES.md?** §2.2 (share link race conditions) not affected — OTP check is before use_count increment. §2.1 (expired link) handled by validate_token_no_increment in request-otp.
5. **Breaking existing features?** Yes — existing share access clients must now send `otp` or they get 403 OTP_REQUIRED. Frontend updated in same change so no external clients are affected in the prototype.
