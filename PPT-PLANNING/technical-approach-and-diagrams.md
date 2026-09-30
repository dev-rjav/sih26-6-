# PRAMAAN — System Diagrams & Technical-Approach Copy (PPT-ready)

*Companion to `winning-ppt-playbook.md`. Everything here is grounded in
`docs/ARCHITECTURE.md`, `docs/SECURITY.md` and `docs/THREAT_MODEL.md` — the numbers,
algorithms and flows are the real build, not marketing.*

**How to use the diagrams:** every diagram is given twice —
1. as a **Mermaid** block (paste into <https://mermaid.live>, export SVG/PNG, drop into the
   slide — clean vector, matches the deck's navy/blue palette), and
2. as **ASCII** (already-laid-out fallback for a text box or speaker reference).

Recommended slide-3 layout: **Diagram A (split-trust topology)** as the hero, with
**Diagram C (integrity gate)** inset bottom-right — that RELEASE/BLOCK decision is the
single most persuasive visual in the whole deck.

---

## Diagram A — Split-Trust System Topology (the hero diagram)

*The one-glance proof that no single machine can reconstruct a document.*

```mermaid
flowchart TB
    subgraph CLIENT["🖥️  OFFICER — Browser (React 18 + Vite SPA)"]
        U["Holds NO keys · NO plaintext<br/>native fetch via apiFetch()"]
    end

    subgraph APP["⚙️  APPLICATION SERVER — Flask 3 / Python 3.12"]
        direction TB
        A1["Auth Layer — JWT 8h + TOTP MFA<br/>@require_recent_mfa on sensitive actions"]
        A2["RBAC guards — least privilege, re-checked per request"]
        A3["Service Layer — case · doc · audit · search · share"]
        A4["Crypto Layer — AES-256-GCM · HKDF · Ed25519 · SHA-256"]
        A1 --> A2 --> A3 --> A4
        NB["✗ stores NO document bytes"]
    end

    subgraph SA["🗄️  SERVER A — PostgreSQL 16 (metadata only)"]
        DA["chunk order · IV · chunk hashes<br/>document hash · search index · audit chain<br/><b>✗ no document bytes, ever</b>"]
    end

    subgraph SB["📦  SERVER B — Encrypted Chunk Store (ciphertext only)"]
        DB2["1 AES-GCM object per chunk (opaque filename)<br/>each carries its own auth tag<br/><b>✗ no keys · no plaintext · no structure</b>"]
    end

    subgraph KMS["🔑  KMS — Local file KMS (key material only)"]
        DK["1 master key / document, AES-wrapped<br/>with KMS_WRAPPING_KEY (≠ SECRET_KEY)<br/>chunk keys derived on use, never stored<br/><b>✗ no ciphertext to unlock</b>"]
    end

    CLIENT -->|HTTPS · every request authenticated & authorised| APP
    APP --> SA
    APP --> SB
    APP --> KMS

    classDef srv fill:#eaf1fb,stroke:#1e3a8a,stroke-width:1px,color:#0a0c10;
    classDef danger fill:#fdecea,stroke:#b91c1c,color:#0a0c10;
    class SA,SB,KMS srv;
```

**ASCII fallback:**
```
        ┌───────────────────────────────────────────────┐
        │  OFFICER — Browser (React 18 SPA)             │
        │  holds NO keys · NO plaintext                 │
        └───────────────────────┬───────────────────────┘
                 HTTPS · every request authenticated & authorised
                                ▼
        ┌───────────────────────────────────────────────┐
        │  APPLICATION SERVER — Flask / Python 3.12     │
        │  Auth(JWT+TOTP) → RBAC → Services → Crypto     │
        │  AES-256-GCM · HKDF · Ed25519 · SHA-256        │
        │  ✗ stores NO document bytes                    │
        └─────────┬──────────────┬──────────────┬────────┘
                  ▼              ▼              ▼
        ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
        │  SERVER A    │ │  SERVER B    │ │    KMS       │
        │  PostgreSQL  │ │ Chunk store  │ │ key material │
        │  metadata    │ │  ciphertext  │ │   only       │
        │  ✗ no bytes  │ │ ✗ no keys    │ │ ✗ no cipher  │
        └──────────────┘ └──────────────┘ └──────────────┘
   Any ONE compromised → useless. All THREE needed to read one document.
```

> **Speaker line:** *"Metadata, ciphertext, and keys live on three separate trust domains.
> Breach any one and you get nothing readable — you need all three at once."*

---

## Diagram B — Upload & Per-Chunk Encryption Pipeline

*Shows the core innovation: a fresh derived key per 1 MB chunk, streamed, never held whole.*

```mermaid
flowchart LR
    F["📄 Exhibit<br/>up to 500 MB"] --> S["Stream in<br/>1 MB chunks"]
    S --> MK["Generate master key<br/>(32 random bytes)<br/>→ AES-wrapped in KMS"]
    MK --> LOOP{{"for each chunk i"}}
    LOOP --> K["chunk_key = HKDF(<br/>master_key, salt=doc_id,<br/>info=chunk-i)"]
    K --> IV["fresh 96-bit IV"]
    IV --> ENC["ciphertext =<br/>AES-256-GCM(chunk_key, iv, chunk)"]
    ENC --> H["chunk_hash = SHA-256(ciphertext)"]
    H --> ST["chunk_store.put(opaque_key, ciphertext)<br/>→ Server B"]
    H --> META["DB row: chunk_index · storage_key<br/>· iv · chunk_hash → Server A"]
    ST --> DOC["document_hash =<br/>SHA-256(all chunk hashes)"]
    META --> DOC
    DOC --> AUD["Audit: DOCUMENT_UPLOADED"]

    classDef hot fill:#fff4e5,stroke:#c2410c,color:#0a0c10;
    class K,IV,ENC,H hot;
```

**Why it wins (say this):** *"One AES key never protects two chunks. Each chunk gets a key
derived by HKDF and a fresh 96-bit IV, so a nonce can never repeat under a key — the classic
GCM failure mode is designed out, not hoped away."*

**ASCII fallback:**
```
Exhibit (≤500MB) → stream 1MB chunks → master key (random, wrapped in KMS)
   for each chunk i:
     chunk_key = HKDF(master_key, salt=doc_id, info="chunk-i")
     iv = random 96-bit
     ciphertext = AES-256-GCM(chunk_key, iv, chunk)
     chunk_hash = SHA-256(ciphertext)
     → Server B: put(opaque_key, ciphertext)
     → Server A: {chunk_index, storage_key, iv, chunk_hash}
   document_hash = SHA-256(chunk_0_hash ‖ chunk_1_hash ‖ …)
   → Audit: DOCUMENT_UPLOADED
```

---

## Diagram C — The Integrity Gate: verify-before-release (the money shot)

*This is the demo. Evidence is NEVER streamed until every check passes.*

```mermaid
flowchart TB
    REQ["GET /documents/{id}/download"] --> RBAC{"RBAC: user may<br/>see this case?"}
    RBAC -->|no| E404["404 (existence not confirmed)"]
    RBAC -->|yes| KEY["Fetch master key from KMS"]
    KEY --> ORD["Load chunk metadata<br/>ordered by chunk_index"]
    ORD --> V["PASS 1 — verify every chunk<br/>SHA-256(ciphertext)==chunk_hash<br/>GCM tag valid · document_hash matches"]
    V --> GATE{"ALL CHECKS<br/>PASS?"}
    GATE -->|YES| REL["✅ RELEASE<br/>decrypt · stream in order<br/>Audit: DOCUMENT_DOWNLOADED"]
    GATE -->|NO| BLK["⛔ BLOCK<br/>HTTP 422 · 0 bytes served<br/>Audit: INTEGRITY_VIOLATION"]

    classDef ok fill:#e7f6ec,stroke:#15803d,color:#0a0c10;
    classDef bad fill:#fdecea,stroke:#b91c1c,color:#0a0c10;
    class REL ok;
    class BLK,E404 bad;
```

**Speaker line:** *"A tampered exhibit produces exactly zero downloaded bytes. The system
refuses to release evidence it cannot verify — and it records the refusal."*

**ASCII fallback:**
```
 download request
      │
  RBAC check ──no──► 404 (never confirm the file exists)
      │yes
  fetch master key → load chunks (by index) → PASS 1: verify ALL
      │                                    (chunk hash · GCM tag · document hash)
      ▼
 ┌─────────── ALL CHECKS PASS? ───────────┐
 │YES                                   NO│
 ▼                                        ▼
 ✅ RELEASE                            ⛔ BLOCK
 decrypt · stream in order            HTTP 422 · 0 bytes
 Audit: DOCUMENT_DOWNLOADED           Audit: INTEGRITY_VIOLATION
```

---

## Diagram D — Tamper-Evident Audit Hash-Chain

*Each event hashes the previous one; any edit breaks every hash after it.*

```mermaid
flowchart LR
    G["Event 1 — Genesis<br/>prev = 000…0<br/>hash = SHA-256(prev ‖ payload)"] --> E2["Event 2<br/>prev = hash₁<br/>hash = SHA-256(prev ‖ payload)"]
    E2 --> E3["Event 3<br/>prev = hash₂<br/>hash = SHA-256(prev ‖ payload)"]
    E3 --> EN["Event n …"]
    EN --> VER["/audit/verify recomputes chain<br/>→ returns first_break_at<br/>(null = intact) · verification is itself logged"]

    classDef chain fill:#eaf1fb,stroke:#1e3a8a,color:#0a0c10;
    class G,E2,E3,EN chain;
```

**Precise wording (matches CLAUDE.md terminology):** *"hash-chained, tamper-**evident** — we
**detect** modification, we do not claim it's impossible. DB-level `REVOKE UPDATE, DELETE`
closes the easy path; the chain catches the rest."* **Never say "blockchain" or "immutable."**

---

## Diagram E — Auth, RBAC & Step-Up MFA (defence in depth)

```mermaid
flowchart TB
    L["Login: password (bcrypt) + TOTP"] --> J["Issue JWT (8h) with mfa_at claim"]
    J --> R["Every request → RBAC guard<br/>(least privilege, per-request)"]
    R --> A{"Sensitive action?<br/>sign · share · delete · user/role"}
    A -->|no| GO["Proceed"]
    A -->|yes| M{"mfa_at fresher<br/>than 15 min?"}
    M -->|yes| GO
    M -->|no| STEP["401 MFA_REQUIRED →<br/>prompt fresh TOTP (not full re-login)<br/>→ re-stamp JWT mfa_at"]
    STEP --> GO

    classDef step fill:#fff4e5,stroke:#c2410c,color:#0a0c10;
    class STEP,M step;
```

---

## Diagram F — Secure Share: recipient-bound, OTP-gated, time-limited

```mermaid
flowchart LR
    O["Officer: Create share<br/>(step-up MFA required)"] --> LINK["Generate link:<br/>recipient-bound · expiry · allow_download flag"]
    LINK --> REC["Recipient opens link"]
    REC --> OTP["Enter OTP sent to bound identity"]
    OTP --> CHK{"OTP valid &<br/>not expired?"}
    CHK -->|no| DENY["Denied · Audit: SHARE_ACCESS_DENIED"]
    CHK -->|yes| GATE["Runs through the SAME integrity gate<br/>(Diagram C) before any byte is served"]
    GATE --> VIEW["Preview / download per policy<br/>Audit: SHARE_ACCESSED"]

    classDef bad fill:#fdecea,stroke:#b91c1c,color:#0a0c10;
    class DENY bad;
```

---

## Technical-Approach copy — drop-in bullet text for Slide 3

*Written in the winning "**bold term:** benefit" style from the playbook (§1.2). Trim to fit.*

**Architecture — split trust, one document end-to-end**
- **Two-server topology:** metadata (PostgreSQL) and ciphertext (chunk store) live on
  separate machines; keys live in a third KMS domain — no single host can reconstruct a file.
- **Per-chunk encryption:** every 1 MB chunk gets an HKDF-derived key + fresh 96-bit IV under
  AES-256-GCM — one key never covers two chunks.
- **Opaque storage keys:** chunk filenames are random tokens; Server B holds no document IDs,
  no order, no keys — just authenticated ciphertext.
- **Verify-before-release:** every chunk hash, every GCM tag and the document hash are checked
  *before* a single byte is streamed; failure returns HTTP 422 and serves 0 bytes.
- **Tamper-evident audit:** a SHA-256 hash-chain logs every action; `/audit/verify` names the
  first broken event; DB-level `REVOKE UPDATE, DELETE` blocks the easy edit path.
- **Least-privilege access:** six roles, RBAC re-checked on every request; case-scoped
  resources return 404 (never 403) so existence is never confirmed.
- **Step-up MFA:** TOTP at login, plus a fresh TOTP re-check before sign / share / delete /
  user-role changes.

**Technologies used** (render the marks as a grouped logo wall — playbook §1.4)
- **Frontend:** React 18 · Vite · TypeScript · Tailwind
- **Backend:** Python 3.12 · Flask 3 · SQLAlchemy · Flask-Migrate · JWT · marshmallow
- **Data:** PostgreSQL 16 (metadata, full-text search, audit chain) · encrypted chunk store
- **Crypto:** AES-256-GCM · HKDF-SHA256 · SHA-256 · Ed25519 · bcrypt · TOTP *(pyca/cryptography — audited, no hand-rolled crypto)*
- **OCR:** Tesseract (offline · English + Hindi/Tamil/Telugu/Bengali/Gujarati)
- **Production swap-ins:** MinIO (chunk store) · HashiCorp Vault (KMS) · Redis · Celery · Nginx+TLS — all behind existing interfaces

**Methodology (one line):** *Threat-model first → write the spec → implement against audited
libraries → verify integrity before every release → log every action to a verifiable chain.*

---

## Guardrails when you write these into the deck
- Use **"tamper-evident,"** never "immutable" / "blockchain."
- Use **"least-privilege,"** never "zero-trust."
- Say **"chunk store (local disk; MinIO in production),"** not "MinIO" as if it exists now.
- Say **"cryptographically signed; legal admissibility is out of scope."**
- **PRAMAAN is standalone** — no comparison to ICJS / eSakshya / CCTNS / CCTNS-like systems.
- Numbers on the impact slide are **targets measured from the prototype**, not claims.
