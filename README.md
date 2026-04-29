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

defriends is a defensive security platform that runs on the machines you own, with your permission, and tells you — in plain language — what's wrong and exactly how to fix it. It is designed around:

**Consent before collection.** No log, no scan, no behavior signal leaves the client until you have signed a consent receipt. Every receipt is granular (per data category, per retention window), hash-chained for auditability, and revocable.

**Short retention by default.** Seven days. Always. The only exception is a serious finding (CVSS ≥ 7 or on CISA's Known-Exploited list) — and even then, the client requires a fresh consent receipt.

**Layman-friendly remediation.** Every finding ships with a plain-language explanation ("your firewall is off, anyone on your network can reach you") plus an exact fix plan. Fixes are dry-run first and consent-gated.

---

## Architecture at a glance

defriends processes security evidence through an 8-layer pipeline.

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

---

## Interactive Demo

Open the **live, interactive demo** to see the end-to-end working process (consent → evidence → MITRE mapping → risk scoring → remediation):

- **Demo file:** [`demo.html`](./demo.html)

### Run the demo (no install)

```bash
# Clone the repo and open the demo directly
open demo.html          # macOS
xdg-open demo.html      # Linux
start demo.html         # Windows
```

### What the demo shows

| Section | What you can do |
|:--------|:----------------|
| 🔄 **Pipeline** | Click "Run Demo Pipeline" — watch an evidence packet flow through all 8 layers with a streaming log |
| 🔐 **Consent Wizard** | Walk through the 4-step consent flow and generate a `crcpt-*` receipt |
| 📊 **Risk Scorer** | Drag CVSS/EPSS sliders and toggle KEV/Reachable/Internet flags — the score gauge updates live |
| 🗺️ **MITRE ATT&CK Map** | Explore tactic columns populated from sample findings; click any card for CVE/CWE details |
| 🛠️ **Remediation** | Step through P0→P1→P2 playbooks with a dry-run; "Apply" is consent-gated |
| 📡 **Live Feed** | Watch a simulated behavioral-event stream with MITRE mappings and anomaly scores |

### Optional: API call examples (mirrors real endpoints)

The demo is **fully static** (it runs without a backend), but it includes an **API Examples** panel with copy/paste `curl` requests that mirror the real endpoints described in this repo.

> If you run the server locally (see Quickstart below), you can use those `curl` calls against `http://127.0.0.1:8080`.

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

---

## Privacy, consent & data handling

defriends is built around ISO/IEC 29184 consent-receipt semantics, mapped to each jurisdiction's legal framework.

| Framework | Rights honored | API |
|:---|:---|:---|
| **GDPR (EU)** | Access (Art. 15), rectify (16), erase (17), restrict (18), portability (20), object (21). Lawful basis is always recorded. | `POST /v1/consent/dsr` with `request_type=access|erase|portability|restrict|object` |
| **CCPA / CPRA (CA)** | Right to know, delete, correct, opt-out of sale/share. Opt-out of sale is honored by default for all users, account or not. | `POST /v1/consent/dsr` with `request_type=opt_out|know|delete|correct` |
| **HIPAA (US healthcare)** | PHI-adjacent scope is off by default and requires a separately signed authorization (45 CFR § 164.508). Accounting-of-disclosures is available. | `POST /v1/consent/dsr` |
| **SOC 2 CC6.1 / ISO 27001 A.5.34** | Every consent action is appended to a hash-chained audit log. Any tampering invalidates every subsequent link. | `GET /v1/consent/audit` |

### Retention

* **Default: 7 days** for every data scope. The client-side log collector runs a reaper every hour and hard-deletes anything past the window.
* **Extended retention** is only possible when (a) the scoring service flags a finding as serious (CVSS ≥ 7 or KEV-listed) AND (b) you grant a new consent receipt. The ceiling is 90 days.
* **Revocation** wipes the local cache and invalidates every in-flight collection on the next heartbeat.

### What is collected

Every scope is opt-in, set separately, and defaults to 7-day retention.

Raw logs never leave the client. The upstream receives only aggregated counters plus up to 25 PII-redacted "interesting" snippets per batch.

---

## MITRE ATT&CK mapping

Every finding is resolved to a MITRE technique. The rule pack at `rules/mapping/mitre_cwe_context.v1.yaml` has rules covering techniques across multiple tactics.

---

## Risk scoring

```
score = (cvss/10 × 55) + (epss × 25) + (kev × 10) + (reachable × 7) + (internet × 3)
```

---

## Remediation with auto-fix (dry-run first)

Every finding maps to a `Playbook` with a plain-language explanation, OS-aware commands, a pre-flight check, a verify step, and a rollback. Every run defaults to **dry-run** — the apply mode requires a valid consent receipt.

---

## Test suite

```
236 tests passing — 100% success rate
```

---

## Project structure

```text
secmesh_scaffold/
├── app_unified.py
├── services/
│   ├── security_core/
│   ├── consent/
│   ├── behavioral/
│   ├── remediation/
│   ├── ai_assistant/
│   ├── ingestion/
│   ├── normalizer/
│   ├── mapping/
│   ├── scoring/
│   ├── reporting/
│   └── gateway/
├── agents/
│   ├── collectors/
│   │   └── log_collector.py
│   └── dirtybots_agent.py
├── packages/common/
├── rules/
├── schemas/
├── tests/
└── reports/pdf/
```

---

## Defensive-only notice

defriends is a defensive security platform. It identifies, correlates, and reports on weaknesses — it does not contain exploit code, offensive payloads, or attack tools.

---

<div align="center">

**Built with care — because security shouldn't require a PhD.**

</div>
