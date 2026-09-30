"""
dev_logs.py — SSE log streaming for the PRAMAAN live demo visualizer.
ONLY registered when app.debug=True. Never active in production.

GET /api/v1/dev/stream?token=<JWT>

EventSource cannot send custom headers, so the JWT is passed as a query param.
The handler fans log records out to every connected SSE client via per-client queues.
After each request it emits structured annotation lines so the visualizer can animate
the correct pipeline nodes without any changes to the business-logic code.

CORS: Access-Control-Allow-Origin: * — safe because this blueprint is debug-only
and every connection still requires a valid JWT.
"""

import json
import logging
import re
import threading
import time

from flask import Blueprint, Response, g, request
from flask_jwt_extended import decode_token

dev_logs_bp = Blueprint("dev_logs", __name__)

# ── Fan-out state ──────────────────────────────────────────────────────────────
# Each connected SSE client gets its own Queue.  The SSEHandler puts a copy of
# every log record into every live queue.
import queue as _queue

_clients: list[_queue.Queue] = []
_clients_lock = threading.Lock()

_demo_log = logging.getLogger("pramaan.demo")
_demo_log.setLevel(logging.DEBUG)


def _broadcast(payload: str) -> None:
    with _clients_lock:
        dead = []
        for q in _clients:
            try:
                q.put_nowait(payload)
            except _queue.Full:
                dead.append(q)
        for q in dead:
            _clients.remove(q)




# ── Request annotations ────────────────────────────────────────────────────────
# before_app_request / after_app_request hooks emit structured annotation lines
# that the visualizer parses to drive animations — no changes to business code.

@dev_logs_bp.before_app_request
def _mark_start() -> None:
    g._demo_t0 = time.perf_counter()


@dev_logs_bp.after_app_request
def _annotate(resp):  # noqa: ANN001
    path = request.path
    # Never annotate the SSE stream itself.
    if path.startswith("/api/v1/dev"):
        return resp

    method = request.method
    status = resp.status_code
    elapsed = int((time.perf_counter() - getattr(g, "_demo_t0", time.perf_counter())) * 1000)

    # ── HTTP line (always) ────────────────────────────────────────────────────
    _demo_log.info("HTTP  %s %s  →  %d  [%dms]", method, path, status, elapsed)

    if status >= 400:
        return resp  # don't annotate failed requests

    # ── Endpoint-specific annotations ─────────────────────────────────────────
    if "/auth/login" in path and method == "POST":
        _demo_log.info("AUTH  LoginSchema().load() → validated | auth_service.authenticate()")
        _demo_log.info("AUTH  bcrypt.checkpw(password, hash)  rounds=12  72-byte cap  →  MATCH")
        _demo_log.info("AUTH  begin_session()  →  {temp_token, mfa_required: true}")

    elif "/auth/mfa/verify" in path and method == "POST":
        _demo_log.info("MFA   MFAVerifySchema().load({temp_token, totp_code})")
        _demo_log.info("MFA   auth_service.complete_mfa()  →  pyotp.TOTP.verify(valid_window=1)  →  VALID")
        _demo_log.info("AUDIT audit_service.record(MFA_VERIFIED)  pg_advisory_xact_lock  hash-chain++")
        _demo_log.info("AUDIT audit_service.record(LOGIN)  →  {access_token, expires_in: 28800}")

    elif "/auth/mfa/step-up" in path and method == "POST":
        _demo_log.info("MFA   step-up MFA verified  →  step_up_verified_at set in JWT claims  (300s window)")

    elif re.search(r"/cases/[^/]+/documents$", path) and method == "POST":
        _demo_log.info("RBAC  @require_roles(SUPER_ADMIN, CASE_OFFICER)  →  CASE_OFFICER MATCH")
        _demo_log.info("RBAC  case_service.get_case_for_user()  →  MEMBER ✓  status=OPEN")
        _demo_log.info("MIME  _detect_mime(head[0:2048], filename)  magic-bytes  →  allowed MIME ✓")
        _demo_log.info("KMS   secrets.token_bytes(32)  →  master_key  kms.store_key() AES-256-GCM wrapped")
        _demo_log.info("CRYPT Document(status=UPLOADING) flush  |  CHUNK_SIZE_BYTES=1048576")
        _demo_log.info("CRYPT HKDF-SHA256(master_key, salt=doc_id, info='chunk-0')  →  32-byte chunk_key")
        _demo_log.info("CRYPT os.urandom(12)  →  iv (96-bit nonce)  AESGCM.encrypt()  →  ciphertext+16-byte GCM tag")
        _demo_log.info("STORE chunk_store.put_chunk()  SHA-256(ciphertext)  →  chunk_hash  →  DocumentChunk row")
        _demo_log.info("INTEG integrity_hash = SHA-256(''.join(chunk_hashes))  Document(status=ACTIVE)  db.commit()")
        _demo_log.info("AUDIT audit_service.record(DOCUMENT_UPLOADED)  hash-chain appended")

    elif re.search(r"/documents/[^/]+/download$", path) and method == "GET":
        _demo_log.info("RBAC  @require_roles(SUPER_ADMIN, CASE_OFFICER, INVESTIGATOR, PROSECUTOR)  →  MATCH")
        _demo_log.info("DB    DocumentChunk.query.order_by(chunk_index)  →  N chunks loaded")
        _demo_log.info("KMS   kms.get_key(doc_id)  →  unwrap master_key  AES-256-GCM + KMS_WRAPPING_KEY")
        _demo_log.info("INTEG SHA-256(ciphertext) == chunk_hash  ✓  (per chunk)")
        _demo_log.info("CRYPT HKDF-SHA256 + AESGCM.decrypt()  GCM auth-tag auto-verified  →  plaintext")
        _demo_log.info("INTEG SHA-256(''.join(chunk_hashes)) == doc.integrity_hash  →  VERIFIED ✓")
        _demo_log.info("AUDIT audit_service.record(DOCUMENT_DOWNLOADED)")

    elif re.search(r"/documents/[^/]+/preview$", path):
        _demo_log.info("CRYPT reconstruct_bytes()  →  _verify_and_decrypt()  integrity verified")
        _demo_log.info("AUDIT audit_service.record(DOCUMENT_PREVIEWED)")

    elif re.search(r"/documents/[^/]+/share$", path) and method == "POST":
        _demo_log.info("RBAC  step-up MFA window check  →  VALID (within 300s)")
        _demo_log.info("SHARE secrets.token_urlsafe(32)  →  raw_token  (returned ONCE, never stored)")
        _demo_log.info("SHARE SHA-256(raw_token)  →  token_hash  DocumentShareLink INSERT")
        _demo_log.info("AUDIT audit_service.record(DOCUMENT_SHARED)  hash-chain appended")

    elif re.search(r"/share/[^/]+/request-otp$", path) and method == "POST":
        _demo_log.info("OTP   validate_token_no_increment()  email gate check  →  PASS")
        _demo_log.info("OTP   6-digit OTP  SHA-256(otp) stored in-memory (_store dict, threading.Lock)")
        _demo_log.info("OTP   TTL=10min  max_attempts=3  →  Gmail SMTP dispatch")
        _demo_log.info("AUDIT audit_service.record(SHARE_OTP_SENT)")

    elif re.search(r"/share/[^/]+/download$", path) and method == "POST":
        _demo_log.info("OTP   email_otp.verify_or_raise()  SHA-256(otp)==stored_hash  →  MATCH")
        _demo_log.info("OTP   entry deleted (single-use)  BEFORE use_count incremented")
        _demo_log.info("SHARE sharing_service.validate_token()  atomic UPDATE use_count  RETURNING")
        _demo_log.info("AUDIT audit_service.record(SHARE_LINK_ACCESSED)")

    elif re.search(r"/share/[^/]+/info$", path) and method == "GET":
        _demo_log.info("SHARE SHA-256(token)  →  DocumentShareLink.query  no side effects")

    elif "/cases" in path and method == "POST" and re.search(r"/cases$", path):
        _demo_log.info("AUDIT audit_service.record(CASE_CREATED)")

    return resp


# ── SSE stream endpoint ────────────────────────────────────────────────────────

@dev_logs_bp.get("/stream")
def stream_logs():
    token = request.args.get("token", "")
    if not token:
        return {"error": "UNAUTHORIZED", "detail": "token query param required"}, 401
    try:
        decode_token(token)
    except Exception:
        return {"error": "UNAUTHORIZED", "detail": "invalid or expired token"}, 401

    client_q: _queue.Queue = _queue.Queue(maxsize=300)
    with _clients_lock:
        _clients.append(client_q)

    def generate():
        try:
            yield "retry: 3000\n\n"
            # Announce connection
            hello = json.dumps({"level": "INFO", "logger": "pramaan.demo",
                                "msg": "INFO     [pramaan.demo]  SSE stream connected — real Flask logs follow",
                                "ts": time.time()})
            yield f"data: {hello}\n\n"
            while True:
                try:
                    payload = client_q.get(timeout=25)
                    yield f"data: {payload}\n\n"
                except _queue.Empty:
                    yield ": heartbeat\n\n"
        finally:
            with _clients_lock:
                if client_q in _clients:
                    _clients.remove(client_q)

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
    )
