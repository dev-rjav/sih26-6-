"""
rate_limit.py — named rate-limit strings applied via the shared `limiter` extension.

USAGE (in a blueprint):
    from app.extensions import limiter
    from app.core.rate_limit import LOGIN_LIMITS

    @auth_bp.route("/login", methods=["POST"])
    @limiter.limit(LOGIN_LIMITS)
    def login(): ...

Policy source of truth: ../../docs/SECURITY.md (Rate Limiting Policy).
On limit breach the app returns 429 and records AuditEventType.RATE_LIMIT_EXCEEDED.
"""

LOGIN_LIMITS = "5 per minute;20 per hour"     # per IP
MFA_LIMITS = "5 per minute"                    # per IP
REFRESH_LIMITS = "20 per minute"               # per user
UPLOAD_LIMITS = "10 per minute"                # per user
SEARCH_LIMITS = "60 per minute"                # per user
SHARE_INFO_LIMITS = "200 per hour;1000 per day"  # per IP — metadata only, no content
SHARE_ACCESS_LIMITS = "100 per hour;500 per day"  # per IP — download/preview (content delivery)
OTP_REQUEST_LIMITS = "20 per hour;100 per day"  # per IP (OTP sends)
DEFAULT_LIMITS = "120 per minute"              # per user, everything else
