# Winning SIH Idea-PPT Playbook

*Distilled from the reference decks in `references/` — the actual winning / high-scoring
SIH decks (Cannon Crew '24 security, Tech Pioneers '25 disaster-mgmt, Innovators '24
women-safety) plus ~15 other submitted decks — and cross-checked against our own
`initial-ppt.pdf` (PRAMAAN).*

> **Read this before touching the PPTX.** It is the checklist that separates a deck that
> *clears the round* from a deck that *is average and gets forgotten*. Every point below is
> something a winning deck did and a losing deck skipped.

---

## 0. The non-negotiable SIH frame (get this wrong and you're disqualified before judging)

Every single reference deck — winners and also-rans — obeys the **official SIH Idea
template**. This is not a stylistic choice; it is enforced by the portal and the evaluators
score against these exact headers.

| Slide | Fixed heading | What must be on it |
|------:|---------------|--------------------|
| 1 | **Title Page** | PS ID · PS Title · Theme · PS Category · Team ID · Team Name — plus the SIH brain-bulb logo (top-right) |
| 2 | **Idea Title** | Proposed Solution · **How it addresses the problem** · **Innovation & uniqueness** |
| 3 | **Technical Approach** | Technologies used · Methodology / flow-charts / architecture / working-prototype images |
| 4 | **Feasibility and Viability** | Feasibility analysis · Potential challenges & risks · Strategies to overcome |
| 5 | **Impact and Benefits** | Impact on target audience · Benefits (social / economic / environmental) |
| 6 | **Research and References** | Links / citations of reference & research work |

Hard rules pulled straight from the template's "Important Instructions" slide:

- **Maximum 6 slides including the title.** Do not add slides. (Judges see over-length as
  not following instructions.)
- **Avoid paragraphs.** Use points / diagrams / infographics / pictures. The single biggest
  quality gap between winners and losers is *paragraph walls vs. structured visuals*.
- **Keep explanation precise and easy to understand.**
- **Idea must be unique and novel.**
- **Export to PDF and upload the PDF.** No PPT/DOCX accepted on the portal.
- Do **not** change the idea-detail pointers / section headers in the template.

✅ *Our `initial-ppt.pdf` already nails the frame — 6 slides, exact headers, logo placed.
The playbook below is about lifting the **content quality** to winner level.*

---

## 1. The 12 features that make a deck *win* (elaborated)

These are the traits present in the winning decks and absent (or weak) in the forgettable
ones. Ordered by how much they move the needle.

### 1.1 Name the product — give the idea an identity
Winners never present "a system." They present a **named product**:
- Cannon Crew → *CIS-GPO Automator*
- Tech Pioneers → **RockVision AI**
- Innovators → *Women Safety India (WSI)* with a logo lockup

A name makes the idea memorable in a room where judges see 30 decks in a day. It signals
the team thinks in *product* terms, not *assignment* terms.
→ **PRAMAAN already does this well** — keep the name, tagline ("Secure Evidence Vault"), and
the "Separate the trust. Verify before release. Record every access." line. That triad is
exactly the kind of memorable hook winners use.

### 1.2 Bolded lead-in keyword on every bullet
Look at every winning bullet: **`Bold Term:` then the explanation.**
> **Local LLM Execution:** Runs LLMs offline using Ollama…
> **Real-Time Monitoring:** Utilizes AI-driven algorithms…

This lets a judge skim the **bold terms only** and still grasp the whole solution in 5
seconds. Never write a naked sentence bullet. Convert every bullet to
`**Capability name:** one-line benefit`.

### 1.3 A real architecture diagram / flowchart — not a text wall
Slide 3 is where decks are won or lost. Winners show a **labelled diagram** of data flowing
through the system (Cannon Crew's LLM-agent flow; Tech Pioneers' client→Node-RED→DB→AI
flow; RockVision's box-and-arrow pipeline). Weak decks write paragraphs about "the
methodology."
- The diagram must show **flow direction** (arrows) and **named components**.
- Pair the diagram with a short **Components** list beside it.
→ **PRAMAAN's slide 3 is a strong example** — the officer → app server → chunk → per-chunk
key → 3 stores → ALL CHECKS PASS? → RELEASE/BLOCK flow is exactly this pattern, and the
"BLOCK · HTTP 422 · 0 bytes" branch is a standout. This is arguably better than any
reference deck's tech slide. Keep it.

### 1.4 Tech stack as a *logo wall*
Every winner renders the stack as **recognizable logos**, not a comma list. Judges
instantly read credibility from seeing React / PostgreSQL / Docker / TensorFlow marks.
- Group by layer (Frontend / Backend / AI-ML / Infra).
- Keep the text list too, but the **logos do the persuading**.

### 1.5 Quantified impact — put numbers on it
The strongest impact slide (Tech Pioneers) is stuffed with **hard numbers**:
> "70–90% reduction in rockfall incidents" · "15–60 minutes advance warning" ·
> "$2–5 million annual savings per operation."

Numbers convert a claim into a measurable promise. Even *targets* beat adjectives.
→ **PRAMAAN handles this honestly and cleverly** — the "WHAT WE WILL MEASURE (stated as
targets, not claimed now)" block is the right move for a security product where fake numbers
would be caught. Strengthen it with concrete target figures (e.g., "verify a 100 MB exhibit
in < X s", "0 bytes served on any integrity failure — demonstrated live").

### 1.6 Comparison table vs. existing systems ⭐ (biggest differentiator)
Tech Pioneers' reference slide carried a **feature-comparison matrix** (RockVision vs
MineGUARD vs RockWatch vs SafeMine vs GeoAlert) with ✓/✗ per feature. This single artifact
does more than any paragraph: it proves the team **surveyed the landscape** and shows
exactly where they win.
- Rows = capabilities that matter. Columns = your product + 3–4 alternatives.
- Your column is all ✓; competitors have visible ✗ gaps.
> ⚠️ **PRAMAAN caveat:** CLAUDE.md forbids comparing to ICJS / eSakshya / CCTNS / national
> systems. So build the matrix against **generic alternatives** instead — e.g. *Paper
> register · Shared network drive · Generic DMS / cloud storage · PRAMAAN* — with rows like
> encryption-at-rest, tamper-evident audit, per-request RBAC, integrity-gated release,
> split-trust storage, offline/on-prem. This keeps the winning technique while respecting
> the naming rule.

### 1.7 A concrete user story / scenario
Cannon Crew devoted half of slide 5 to a **"FOR INSTANCE: USER STORY"** — a named scenario
(a government agency on an air-gapped network) walked through Scenario → Impact → Benefits.
This makes an abstract security tool *tangible*. Judges remember stories, not features.
→ For PRAMAAN: a one-paragraph scenario — "An investigator uploads a seized-device image;
weeks later a prosecutor requests it; PRAMAAN re-verifies every chunk hash before release
and logs the access — the chain proves nothing was altered in between." Consider adding a
compact version.

### 1.8 Consistent visual identity across all 6 slides
Winners look like *one deck*: team badge top-left, SIH logo top-right, a coloured footer
bar with slide number, one heading font, one accent colour. Weak decks change fonts/colours
per slide and look assembled by 6 different people the night before.
→ **PRAMAAN already has this** (navy heading, blue footer, "leet" badge, consistent section
sub-header strip). Protect it — don't let anyone introduce clip-art or a rogue colour.

### 1.9 Segment the audience — "who gets what"
Innovators split benefits by stakeholder (*For women / For law enforcement / For urban
communities*); Tech Pioneers by *Mining execs / Miners / Regulators / Communities*.
Showing the solution from **each user's point of view** proves you understand the whole
ecosystem, not just the tech.
→ **PRAMAAN does this** with the role-scoped "what each person actually sees" (Case Officer
/ Courts & Prosecutors / Auditors / System Admin). Strong — keep it.

### 1.10 Feasibility as a clean triplet: Feasibility → Challenges → Mitigation
Every good slide 4 is three stacked blocks: **(a)** why it's feasible (technical/operational/
financial), **(b)** honest risks, **(c)** how each risk is mitigated. Never list challenges
without the matching mitigation — unanswered risk reads as naïveté.
→ **PRAMAAN goes further** with an explicit **threat model** (Defended / Partially addressed
/ Out of scope) and a 9-day build timeline proving execution. The honesty ("does not claim
compromise is impossible") is a maturity signal judges reward in a cybersecurity PS. This is
best-in-class — keep it.

### 1.11 Show a *working* prototype, not slideware
The template literally invites "working prototype" images. PRAMAAN's slide 2 uses **six real
screenshots of the running build** ("six real screens from the build"). This is a massive
credibility lever most idea-round decks lack — they show mockups or nothing. Lead with it
and say it out loud: *this is real, running software.*

### 1.12 Credible references — standards, not blog posts
Winners cite **IEEE papers, NIST/RFC standards, official docs.** Weak decks link random
Scribd/blog pages.
→ **PRAMAAN's references slide is exemplary** — NIST SP 800-38D/57, RFC 5869/8032/6238,
OWASP ASVS/Top-10, Saltzer & Schroeder, plus a "how the reading changed the build" column
that proves the research was *used*, not decorative. This is above every reference deck we
reviewed. Keep it.

---

## 2. Anti-patterns seen in the *losing* reference decks (do the opposite)

- **Paragraph walls** (AIKYAM traffic deck, some slide-2s) — dense justified text, no
  structure. Judges skim; walls get skipped.
- **Empty template placeholders left in** ("Your Team Name", generic "Technical, Financial,
  Market" with no specifics) — signals a rushed, un-customised submission.
- **Cut-off / overflowing text** (Innovators title & references slides literally clip
  off-screen). Always export to PDF and *look at every slide* — overflow = careless.
- **Decorative clip-art with no information** — cartoons that fill space but say nothing.
- **Tech list with no architecture** — naming languages without showing how they connect.
- **Challenges with no mitigations** — raising a risk and leaving it hanging.
- **Vague impact** ("improved efficiency", "enhanced safety") with zero numbers or targets.
- **Weak references** — Scribd, random blogs, or "Elsevier, Science Direct" with no actual
  paper.
- **Inconsistent styling** across slides — different fonts/colours per slide.

---

## 3. Scoring rubric — how to self-grade the PRAMAAN deck

Rate each 1–5 before submitting; anything under 4 gets reworked.

| # | Criterion | Winner benchmark |
|---|-----------|------------------|
| 1 | Follows exact 6-slide SIH template & headers | Non-negotiable pass |
| 2 | Named, memorable product + one-line hook | PRAMAAN + "Separate the trust…" ✅ |
| 3 | Every bullet = **bold term:** benefit | Skim-readable in 5s |
| 4 | Slide 3 has a real labelled architecture flow | Split-trust flow ✅ |
| 5 | Tech stack shown as logos, grouped by layer | Add logo wall |
| 6 | Impact carries numbers / explicit targets | "What we will measure" ✅, add figures |
| 7 | Comparison matrix vs generic alternatives | ⬅ **add this** |
| 8 | Concrete user story / scenario | ⬅ consider adding |
| 9 | Consistent identity on all 6 slides | ✅ |
| 10 | Feasibility → challenges → mitigation + threat model | ✅ best-in-class |
| 11 | Real prototype screenshots, stated as real | ✅ six screens |
| 12 | Standards-grade references, shown to shape build | ✅ best-in-class |

---

## 4. Bottom line for PRAMAAN

Our `initial-ppt.pdf` is **already stronger than every reference deck** on architecture
(1.3), threat-model honesty (1.10), real prototype (1.11), and references (1.12) — these are
exactly the axes a Ministry of Home Affairs / NCRB cybersecurity panel weighs most heavily.

The three concrete upgrades that would take it from "clearly good" to "clearly the winner":

1. **Add a comparison matrix** (§1.6) vs generic alternatives (paper register / shared drive
   / generic DMS) — respecting the no-national-systems rule. This is the one winning device
   we're currently missing.
2. **Add a tech-stack logo wall** (§1.4) on slide 3 alongside the existing text row — instant
   credibility.
3. **Put target numbers** on the "What we will measure" block (§1.5) and, if room allows, a
   two-line **user story** (§1.7) so the security value lands emotionally, not just
   technically.

Everything else is already at or above winner standard — protect it, don't dilute it.
