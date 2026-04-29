<div align="center">

# 🛡️ defriends

### Consent-First Defensive Security Platform

**Map real attack techniques. Score risk with precision. Fix it — with plain-language guidance, not jargon.**

[![Tests](https://img.shields.io/badge/Tests-236%2F236_Passing-22c997?style=for-the-badge)](#test-suite)
[![Privacy](https://img.shields.io/badge/Privacy-GDPR%20%7C%20CCPA%20%7C%20HIPAA-22d3ee?style=for-the-badge)](#privacy-consent--data-handling)
[![Retention](https://img.shields.io/badge/Default%20Retention-7%20days-7c6af0?style=for-the-badge)](#retention)
[![Python](https://img.shields.io/badge/Python-3.10+-3b82f6?style=for-the-badge&logo=python&logoColor=white)](#quickstart)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Interactive-06b6d4?style=for-the-badge)](#interactive-demo)

</div>

---

## What is defriends?

defriends is a defensive security platform that runs on the machines you own, with your permission, and tells you — in plain language — what's wrong and exactly how to fix it. It is designed around three promises:

**Consent before collection.** No log, no scan, no behavior signal leaves the client until you have signed a consent receipt. Every receipt is granular (per data category, per retention window), hash-chained, and revocable in one click.

**Short retention by default.** Seven days. Always. The only exception is a serious finding (CVSS ≥ 7 or on CISA's Known-Exploited list) — and even then, the extension requires a fresh consent receipt from you, and caps at 90 days.

**Layman-friendly remediation.** Every finding ships with a plain-language explanation ("your firewall is off, anyone on your network can reach you") and an exact, dry-runnable fix. Nothing destructive runs without your explicit per-finding approval.

---

## Architecture at a glance

defriends processes security evidence through an 8-layer pipeline. The first four layers are new in this release and wrap the original 5-stage assessment pipeline (ingest → normalize → map → score → report).

| # | Layer | Responsibility |
|:--:|:----|:---|
| 0 | **Security Core** | `services/security_core/` — HMAC-signed events, rate limiting, CSP/HSTS, secret redaction, SSRF guards. Installed as middleware before every other route. |
| 1 | **Consent** | `services/consent/` — captures, stores, revokes, and audits every permission grant. GDPR, CCPA/CPRA, HIPAA, SOC 2, ISO 27001 aligned. |
| 2 | **Client Collectors** | `agents/collectors/log_collector.py` — cross-platform logs, AES-256-GCM at rest, PII redaction, 7-day auto-purge. |
| 3 | **Behavioral Analytics** | `services/behavioral/` — UEBA baselines, MAD-robust anomaly scores, emits EvidenceEvents into the core pipeline. |
| 4 | **Ingestion** | `services/ingestion/` — validates every `EvidenceEvent`, refuses anything without a valid `consent_receipt_id`. |
| 5 | **Normalizer** | `services/normalizer/` — deduplicates and standardizes CWE/CVE fields. |
| 6 | **Mapping** | `services/mapping/` — YAML rule engine maps CWEs to MITRE ATT&CK techniques. |
| 7 | **Scoring** | `services/scoring/` — `score = CVSS×55 + EPSS×25 + KEV×10 + Reachable×7 + Internet×3` → P0-P3. |
| 8 | **Reporting + Remediation + AI** | `services/reporting/` + `services/remediation/` + `services/ai_assistant/` — PDF/JSON reports, dry-run playbooks, plain-language walkthroughs. |

```
┌────────── Client machine (with your consent) ──────────┐
│  agent + log_collector.py (AES-GCM, 7-day purge)       │
│       │                                                │
│       │ (HMAC-signed EvidenceEvents, TLS 1.3)          │
└───────┼────────────────────────────────────────────────┘
        ▼
  [0] security middleware ──► [1] consent gate ──► [4] ingestion
                                                       │
             [3] behavioral ────────────────────────► [5] normalizer
                                                       │
                         [6] mapping (MITRE ATT&CK) ◄──┘
                                                       │
                                                       ▼
                                              [7] risk scoring
                                                       │
                                                       ▼
                          [8] report + remediation + AI assistant
                                                       │
                                                       ▼
                          PDF + JSON + dry-run fix scripts + chat
```

---

## Interactive Demo

`demo.html` is a self-contained, zero-dependency browser demo that lets you explore the full defriends pipeline without running a server. Open it with any modern browser — no build step, no install.

```bash
# Clone the repo and open the demo directly
open demo.html          # macOS
xdg-open demo.html      # Linux
start demo.html         # Windows
```

| Section | What you can do |
|:--------|:----------------|
| 🔄 **Pipeline** | Click "Run Demo Pipeline" — watch a data packet flow through all 8 layers with a streaming log |
| 🔐 **Consent Wizard** | Walk through the 4-step GDPR/CCPA/HIPAA consent flow and generate a `crcpt-*` receipt |
| 📊 **Risk Scorer** | Drag CVSS/EPSS sliders and toggle KEV/Reachable/Internet flags — the score gauge updates live |
| 🗺️ **MITRE ATT&CK Map** | Explore tactic columns populated from real sample findings; click any card for CVE/CWE details |
| 🛠️ **Remediation** | Step through P0→P1→P2 playbooks with an animated dry-run; Apply Fix is consent-gated |
| 📡 **Live Feed** | Watch a simulated behavioral-event stream with MITRE mappings and anomaly scores |

---

## Quickstart

```bash
# 1. Clone and install
git clone https://github.com/autobot786/secmesh_scaffold.git
cd secmesh_scaffold/secmesh_scaffold
python -m venv .venv && source .venv/bin/activate
pip install -e packages/common && pip install -r requirements.txt

# 2. Run the unified server
python -m secmesh_scaffold
# → http://127.0.0.1:8080
#   /dashboard  /docs  /user  /login

# 3. On the machine you want to scan: grant consent, then scan
python agents/dirtybots_agent.py --server http://127.0.0.1:8080 \
      --org demo-org --asset my-laptop --env prod

# 4. Watch the pipeline
curl http://127.0.0.1:8080/health
```

First-time users get the 4-question onboarding wizard at `/v1/ai/app/onboarding/steps`; the assistant tailors a "what to do first" checklist based on role, jurisdiction, platform, and risk appetite.

---

## Privacy, consent & data handling

defriends is built around ISO/IEC 29184 consent-receipt semantics, mapped to each jurisdiction's legal framework.

| Framework | Rights honored | API |
|:---|:---|:---|
| **GDPR (EU)** | Access (Art. 15), rectify (16), erase (17), restrict (18), portability (20), object (21). Lawful basis is always recorded. | `POST /v1/consent/dsr` with `request_type=access|erase|portability|...` |
| **CCPA / CPRA (CA)** | Right to know, delete, correct, opt-out of sale/share. Opt-out of sale is honored by default for all users, account or not. | `POST /v1/consent/dsr` with `request_type=opt_out_sale` |
| **HIPAA (US healthcare)** | PHI-adjacent scope is off by default and requires a separately signed authorization (45 CFR § 164.508). Accounting-of-disclosures is available. | `POST /v1/consent/dsr` with `request_type=accounting` |
| **SOC 2 CC6.1 / ISO 27001 A.5.34** | Every consent action is appended to a hash-chained audit log. Any tampering invalidates every subsequent link. | `GET /v1/consent/audit` |

### Retention

* **Default: 7 days** for every data scope. The client-side log collector runs a reaper every hour and hard-deletes anything past the window.
* **Extended retention** is only possible when (a) the scoring service flags a finding as serious (CVSS ≥ 7 or KEV-listed) AND (b) you grant a new consent receipt. The ceiling is 90 days.
* **Revocation** wipes the local cache and invalidates every in-flight collection on the next heartbeat.

### What is collected

Every scope is opt-in, set separately, and defaults to 7-day retention:

`system_logs` · `application_logs` · `auth_logs` · `network_metadata` · `process_metadata` · `installed_software` · `file_integrity_hashes` · `vulnerability_scans` · `behavioral_telemetry` · `phi_adjacent` (HIPAA only) · `browser_history` (never on by default)

Raw logs never leave the client. The upstream receives only aggregated counters plus up to 25 PII-redacted "interesting" snippets per batch.

---

## MITRE ATT&CK mapping

Every finding is resolved to a MITRE technique. The rule pack at `rules/mapping/mitre_cwe_context.v1.yaml` has 19 rules covering 15+ techniques across 7 tactics.

| CWE | Finding | Technique | Confidence |
|:---|:---|:---|:---:|
| CWE-693 | host firewall disabled | T1562.004 — Impair Defenses | 0.95 |
| CWE-295 | self-signed TLS cert | T1557 — Adversary-in-the-Middle | 0.85 |
| CWE-1104 | outdated system package | T1195.002 — Supply Chain | 0.80 |
| CWE-78 | SSH exposed with password auth | T1110 / T1021.004 | 0.85 |
| CWE-287 | missing MFA on admin | T1078 — Valid Accounts | 0.85 |

Behavioral anomalies also emit EvidenceEvents with MITRE alignment:

| Signal | Technique |
|:---|:---|
| auth_failures spike | T1110 Brute Force |
| new_process for this user | T1059 Scripting Interpreter |
| impossible_travel | T1078 Valid Accounts |
| log_clear | T1070.001 Clear Event Logs |
| security_tool_stop | T1562.001 Disable Tools |

---

## Risk scoring

```
score = (cvss/10 × 55) + (epss × 25) + (kev × 10) + (reachable × 7) + (internet × 3)
```

| Priority | Score | Action |
|:---|:---:|:---|
| **P0 — Critical** | ≥ 85 | Fix today |
| **P1 — High** | ≥ 70 | Fix within 7 days |
| **P2 — Medium** | ≥ 50 | Fix this sprint |
| **P3 — Low** | < 50 | Track and monitor |

The formula weighs exploitability heavily (CVSS + EPSS), then accounts for real-world context: known-exploited status, whether the vulnerable code path is reachable, and whether the asset is internet-facing.

---

## Remediation with auto-fix (dry-run first)

Every finding maps to a `Playbook` with a plain-language explanation, OS-aware commands, a pre-flight check, a verify step, and a rollback. Every run defaults to **dry-run** — the apply mode requires a fresh consent receipt AND a per-step confirmation for anything destructive.

```bash
# Plan a fix for a finding (safe, no execution)
curl -X POST http://127.0.0.1:8080/v1/remediation/plan \
  -H 'Content-Type: application/json' \
  -d '{"finding":{"cwe":"CWE-693","platform":"linux"}}'

# Dry-run: shows exactly what would run
curl -X POST http://127.0.0.1:8080/v1/remediation/run \
  -H 'Content-Type: application/json' \
  -d '{"finding":{"cwe":"CWE-693","platform":"linux"},"mode":"dry_run"}'

# Apply: requires consent receipt + per-step confirmation
curl -X POST http://127.0.0.1:8080/v1/remediation/run \
  -H 'Content-Type: application/json' \
  -d '{"finding":{"cwe":"CWE-693","platform":"linux"},
       "mode":"apply","consent_receipt_id":"crcpt-...",
       "confirm_destructive":true}'

# Rollback
curl -X POST http://127.0.0.1:8080/v1/remediation/rollback \
  -H 'Content-Type: application/json' \
  -d '{"run_id":"rem-...","consent_receipt_id":"crcpt-..."}'
```

Current playbook catalog: macOS/Linux/Windows firewall enablement, TLS cert replacement via Let's Encrypt, package upgrades, SSH hardening, MFA enforcement, log PII-redaction. Playbook matching uses `(CWE, platform)` with fallback to `(CWE, any)`.

---

## AI application assistant

`/v1/ai/app/ask` is a deterministic, local, layman-friendly assistant. It explains anything in plain language — what P0 means, how long data is kept, how to revoke consent, how to apply a fix, what CVSS/EPSS/KEV are — and it hard-sanitizes prompts against injection attempts before processing.

The onboarding wizard (`/v1/ai/app/onboarding/plan`) turns a 4-question intake into a tailored checklist: which consent scopes fit your jurisdiction, which deployment path matches your platform, whether to keep auto-fix in dry-run or let safe fixes auto-apply.

---

## Security posture

| Control | Where it lives | What it does |
|:---|:---|:---|
| HMAC-SHA256 event signing | `security_core/hmac_signer.py` | Ingestion rejects any event with bad signature or > 5-min timestamp skew |
| Token-bucket rate limiting | `security_core/rate_limit.py` | 120 req/min per IP or API key, returns 429 + Retry-After |
| Security response headers | `security_core/middleware.py` | HSTS (2y), CSP with frame-ancestors=none, COOP, CORP, X-Content-Type-Options |
| Request body size cap | `security_core/middleware.py` | 5 MiB hard cap, 413 on exceed |
| Secret redaction | `security_core/sanitize.py` | Strips AWS keys, GH tokens, JWTs, private keys from every outbound log/error |
| Prompt-injection filter | `security_core/sanitize.py` | Every AI prompt passes through 6 regex + HTML-strip defenses |
| SSRF guard | `security_core/sanitize.py` | Blocks private/link-local/metadata IPs on any server-side fetch |
| At-rest encryption | `agents/collectors/log_collector.py` | AES-256-GCM on the SQLite cache, per-agent 256-bit key with 0600 perms |
| Tamper-evident audit log | `services/consent/app/store.py` | Every audit entry hash-chains to the previous — `GET /v1/consent/audit` includes `chain_valid` |

---

## Test suite

```
236 tests passing — 100% success rate
```

| Suite | Covers |
|:---|:---|
| `test_e2e.py` | Full pipeline, all endpoints, schema validation |
| `test_security_e2e.py` | OWASP Top-10: injection, XSS, CSRF, header hardening |
| `test_rule_engine.py` | YAML rule parsing, condition evaluation, dedup |

```bash
cd secmesh_scaffold && pytest tests/ -v
```

---

## Project structure

```
secmesh_scaffold/
├── app_unified.py                         # single-process entry point
├── services/
│   ├── security_core/                     # 🆕 middleware, HMAC, rate limit, sanitize
│   ├── consent/                           # 🆕 GDPR/CCPA/HIPAA receipts + DSR
│   ├── behavioral/                        # 🆕 UEBA engine
│   ├── remediation/                       # 🆕 playbooks, dry-run-first engine
│   ├── ai_assistant/                      # 🆕 layman guidance + onboarding
│   ├── ingestion/                         # stage 1 — evidence intake
│   ├── normalizer/                        # stage 2 — schema standardization
│   ├── mapping/                           # stage 3 — CWE → MITRE ATT&CK
│   ├── scoring/                           # stage 4 — risk scoring
│   ├── reporting/                         # stage 5 — PDF + JSON output
│   └── gateway/                           # reverse-proxy for microservice mode
├── agents/
│   ├── collectors/
│   │   └── log_collector.py               # 🆕 7-day AES-GCM retention, PII-redact
│   ├── dirtybots_agent.py                 # on-machine collection + reporting
│   ├── scripts/                           # one-line installers
│   └── examples/                          # GitHub Actions, GitLab CI
├── packages/common/                       # shared Pydantic models
├── rules/                                 # MITRE mapping + OWASP ASVS
├── schemas/                               # JSON Schema (Draft 2020-12)
├── tests/
└── reports/pdf/
```

---

## Deployment modes

| Mode | Command | Best for |
|:---|:---|:---|
| **Unified** | `python -m secmesh_scaffold` | Dev, laptops, free-tier |
| **Microservices** | `docker compose up --build` | Production, horizontal scale |

In microservices mode, 6 containers run: gateway (8000), ingestion (8001), normalizer (8002), mapping (8003), scoring (8004), reporting (8005). The new services (consent, behavioral, remediation, AI) mount inside the gateway process in this first release; a follow-up will split them into independent containers.

---

## Defensive-only notice

defriends is a defensive security platform. It identifies, correlates, and reports on weaknesses — it does not contain exploit code, offensive payloads, or attack tools. All collection is non-destructive and consent-gated. The `dirtybots_agent.py` filename is retained for backward compatibility with existing installers; all user-facing branding is defriends.

---

<div align="center">

**Built with care — because security shouldn't require a PhD.**

</div>
