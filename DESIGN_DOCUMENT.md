# defriends — Complete Design Document

> **Version:** 1.0.0  
> **Last Updated:** 2026-03-03  
> **Repository:** https://github.com/autobot786/secmesh_scaffold  
> **Website:** https://www.dirtybots.com

---

## Table of Contents

1. [Executive Summary (Non-Technical)](#1-executive-summary-non-technical)
2. [What Problem Does defriends Solve?](#2-what-problem-does-dirtybots-solve)
3. [How It Works — The Simple Version](#3-how-it-works--the-simple-version)
4. [System Architecture Overview](#4-system-architecture-overview)
5. [Service-by-Service Breakdown](#5-service-by-service-breakdown)
6. [Data Flow — End-to-End Pipeline](#6-data-flow--end-to-end-pipeline)
7. [Data Models & Schemas](#7-data-models--schemas)
8. [Rule Engine & Mapping Logic](#8-rule-engine--mapping-logic)
9. [Risk Scoring Algorithm](#9-risk-scoring-algorithm)
10. [PDF Report Generation](#10-pdf-report-generation)
11. [Project Structure](#11-project-structure)
12. [Deployment Architecture](#12-deployment-architecture)
13. [API Reference](#13-api-reference)
14. [Security Design](#14-security-design)
15. [Testing Strategy](#15-testing-strategy)
16. [Glossary](#16-glossary)

---

## 1. Executive Summary (Non-Technical)

**defriends** is a security assessment platform that automatically analyzes software applications for vulnerabilities, maps those vulnerabilities to real-world attack techniques, calculates risk scores, and generates professional PDF reports.

### In Plain English:

Imagine you run a company with a payment processing application. You want to know:

- **"Is our app safe?"** → defriends collects security evidence from your tools
- **"What can hackers actually do?"** → It maps vulnerabilities to real attack methods
- **"How bad is it?"** → It calculates a risk score (0-100)
- **"What should we fix first?"** → It generates a prioritized report with recommendations

### Key Benefits:

| Benefit | Description |
|---------|-------------|
| **Automated** | No manual spreadsheet work — data flows automatically |
| **Standardized** | Uses industry frameworks (MITRE ATT&CK, OWASP ASVS) |
| **Actionable** | Prioritized recommendations tell you exactly what to fix |
| **Auditable** | PDF reports for compliance, audits, and stakeholder reviews |

---

## 2. What Problem Does defriends Solve?

### The Problem

Modern organizations use dozens of security tools: vulnerability scanners, code analyzers, configuration checkers, and more. Each tool produces its own reports in its own format. Security teams drown in data but lack a unified view of actual risk.

### The defriends Solution

```
┌─────────────────────────────────────────────────────────────┐
│                    WITHOUT defriends                        │
│                                                             │
│   Scanner A → Report A (CSV)                                │
│   Scanner B → Report B (JSON)         ❌ No unified view    │
│   SAST Tool → Report C (XML)         ❌ No prioritization   │
│   Config Check → Report D (text)     ❌ No attack mapping   │
│                                                             │
│   Result: 4 reports, 500+ findings, no idea where to start  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     WITH defriends                          │
│                                                             │
│   Scanner A ─┐                                              │
│   Scanner B ─┤                     ┌─────────────────────┐  │
│   SAST Tool ─┼──→  defriends  ──→ │ Single PDF Report   │  │
│   Config     ─┤                    │ • Risk Score: 76/100│  │
│   Check      ─┘                    │ • Top 3 fixes       │  │
│                                    │ • Attack map         │  │
│   Result: 1 report, clear actions  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. How It Works — The Simple Version

Think of defriends as a **5-step security assembly line**:

```
  📥 COLLECT        🔄 CLEAN UP       🗺️ MAP            📊 SCORE          📄 REPORT
  ─────────        ──────────        ─────────         ──────────        ──────────
  Gather data      Standardize       Link to real      Calculate         Generate
  from your        into a common     attack methods    risk numbers      PDF report
  security tools   format            (MITRE ATT&CK)   (0-100)           with fixes

  Step 1           Step 2            Step 3            Step 4            Step 5
  "Ingestion"      "Normalizer"      "Mapping"         "Scoring"         "Reporting"
```

### Real-World Example:

1. **COLLECT**: Your CI/CD pipeline finds that your app uses an outdated library with a known vulnerability (CVE-2025-12345)
2. **CLEAN UP**: defriends standardizes this into a common format with all relevant details
3. **MAP**: The vulnerability (unsafe deserialization, CWE-502) is mapped to "Exploit Public-Facing Application" (T1190) — a technique hackers actually use
4. **SCORE**: Risk score = 95/100 (critical!) because it's internet-facing, has a high CVSS score, and is actively exploited
5. **REPORT**: A professional PDF is generated showing the CEO exactly what to worry about and what to fix first

---

## 4. System Architecture Overview

### High-Level Architecture

```
                              ┌─────────────────────────────────────┐
                              │         defriends Platform          │
                              │                                     │
  Security Tools              │  ┌───────────┐   ┌──────────────┐  │
  ─────────────               │  │ Ingestion │──→│  Normalizer  │  │
  • SBOM Scanners             │  │  Service  │   │   Service    │  │
  • SAST / DAST        ──────→│  └───────────┘   └──────┬───────┘  │
  • Config Auditors           │                         │          │
  • Manual Findings           │                         ▼          │
                              │                  ┌──────────────┐  │
                              │                  │   Mapping    │  │
                              │                  │   Service    │  │
                              │                  │  (Rule Packs)│  │
                              │                  └──────┬───────┘  │    ┌──────────┐
                              │                         │          │    │          │
                              │                         ▼          │    │  PDF     │
                              │                  ┌──────────────┐  │───→│  Report  │
                              │                  │   Scoring    │  │    │          │
                              │                  │   Service    │  │    └──────────┘
                              │                  └──────┬───────┘  │
                              │                         │          │
                              │                         ▼          │
                              │                  ┌──────────────┐  │
                              │                  │  Reporting   │  │
                              │                  │   Service    │  │
                              │                  └──────────────┘  │
                              │                                     │
                              └─────────────────────────────────────┘
```

### Deployment Modes

defriends supports two deployment modes:

| Mode | Description | Use Case |
|------|-------------|----------|
| **Microservices** | 6 separate Docker containers + API Gateway | Production, team environments |
| **Unified** | Single process with all services combined | Development, free-tier hosting (Render) |

### Technology Stack

| Layer | Technology |
|-------|------------|
| **Language** | Python 3.11+ |
| **API Framework** | FastAPI (async, OpenAPI auto-docs) |
| **Data Validation** | Pydantic v2 |
| **Rule Engine** | Custom YAML-based (PyYAML) |
| **Schema Validation** | JSON Schema (Draft 2020-12) |
| **PDF Generation** | ReportLab (Platypus) |
| **HTTP Client** | HTTPX (async, for gateway proxy) |
| **Containerization** | Docker + Docker Compose |
| **Hosting** | Render (Blueprint), any Docker host |

---

## 5. Service-by-Service Breakdown

### 5.1 Ingestion Service

> **Non-Technical:** The "mailroom" — receives security evidence from your tools and stamps it with a tracking number.

| Property | Value |
|----------|-------|
| **Endpoint** | `POST /v1/ingest` |
| **Input** | `EvidenceEvent` (structured security finding) |
| **Output** | Acceptance confirmation + tracking ID |
| **Port (microservice)** | 8001 |

**What it does:**
- Accepts security evidence from any source (CI/CD pipelines, scanners, manual entry)
- Validates the event structure using Pydantic models
- Returns a unique `ingestion_id` for tracking

**Example flow:**
```
CI/CD Pipeline → "We found CVE-2025-12345 in payments-api" → Ingestion → ✅ Accepted (ID: abc-123)
```

---

### 5.2 Normalizer Service

> **Non-Technical:** The "translator" — takes data from different sources and puts it in a standard language everyone understands.

| Property | Value |
|----------|-------|
| **Endpoint** | `POST /v1/normalize` |
| **Input** | `EvidenceEvent` |
| **Output** | Normalized event with sorted, validated keys |
| **Port (microservice)** | 8002 |

**What it does:**
- Validates and normalizes incoming events into typed objects
- Sorts payload and context keys for consistent processing
- Extracts asset metadata (org, app, environment)

---

### 5.3 Mapping Service

> **Non-Technical:** The "intelligence analyst" — takes a vulnerability and figures out which real-world attack techniques a hacker could use to exploit it.

| Property | Value |
|----------|-------|
| **Endpoint** | `POST /v1/map` |
| **Input** | CVE, CWE, exposure context |
| **Output** | List of MITRE ATT&CK techniques with confidence scores |
| **Port (microservice)** | 8003 |

**What it does:**
- Loads YAML rule packs (e.g., `mitre_cwe_context.v1.yaml`)
- Evaluates conditions: vulnerability type + exposure context
- Returns matched attack techniques with confidence scores and rationale

**Example mapping:**
```
Input:  CWE-502 (Unsafe Deserialization) + Internet-Facing + Reachable
Output: T1190 (Exploit Public-Facing App) [confidence: 0.85]
        T1059 (Command Interpreter)       [confidence: 0.65]
```

**Rule Pack Structure:**
```yaml
rules:
  - rule_id: R001
    name: "Public-facing server-side injection"
    when:                           # ALL conditions must match
      - any:                        # At least one CWE matches
          - path: cwe
            op: in
            value: [CWE-94, CWE-78, CWE-502]
      - path: exposure.internet_facing
        op: truthy                  # Must be internet-facing
      - path: exposure.reachable
        op: truthy                  # Must be reachable
    then:
      confidence: 0.8
      techniques:
        - id: T1190
          name: "Exploit Public-Facing Application"
          tactic: "Initial Access"
```

---

### 5.4 Scoring Service

> **Non-Technical:** The "risk calculator" — takes all the vulnerabilities and gives each one a danger score from 0 to 100, then tells you which ones to fix first.

| Property | Value |
|----------|-------|
| **Endpoint** | `POST /v1/score` |
| **Input** | List of `VulnerabilityFinding` objects |
| **Output** | Overall risk score + per-finding scores and priorities |
| **Port (microservice)** | 8004 |

**Scoring Formula:**

```
Risk Score = (CVSS/10 × 55) + (EPSS × 25) + (KEV × 10) + (Reachable × 7) + (Internet × 3)
                 ↑                  ↑            ↑              ↑                ↑
           How severe?      How likely to    Is it being    Can code path    Is it exposed
           (0-10 scale)     be exploited?    exploited now? reach the vuln?  to the internet?
```

**Priority Mapping:**

| Score Range | Priority | Meaning |
|-------------|----------|---------|
| 85 – 100 | **P0** | Fix immediately (critical) |
| 70 – 84 | **P1** | Fix this sprint (high) |
| 50 – 69 | **P2** | Fix this quarter (medium) |
| 0 – 49 | **P3** | Track and plan (low) |

---

### 5.5 Reporting Service

> **Non-Technical:** The "publisher" — takes all the results and creates a professional PDF report that executives, auditors, and engineers can all understand.

| Property | Value |
|----------|-------|
| **Endpoints** | `POST /v1/report/validate`, `POST /v1/report/pdf` |
| **Input** | `AssessmentReport` (complete assessment data) |
| **Output** | Validation result or PDF document |
| **Port (microservice)** | 8005 |

**What it does:**
- Validates reports against JSON Schema (Draft 2020-12)
- Generates multi-page PDF reports using ReportLab
- HTML-escapes all user input to prevent injection attacks

**PDF Report Sections:**
1. **Title Page** — Asset name, report ID, date, organization
2. **Executive Summary** — Risk score tiles, finding counts, top techniques
3. **Methodology** — What tools and data sources were used
4. **Vulnerability Findings Table** — CVE, severity, CVSS, EPSS, techniques
5. **Technique Rationale** — Why each attack technique was mapped
6. **Gap Analysis (Controls)** — OWASP ASVS control status
7. **Prioritized Recommendations** — What to fix, in what order

---

### 5.6 Gateway Service (Microservices Mode Only)

> **Non-Technical:** The "front desk" — a single entry point that routes requests to the right service behind the scenes.

| Property | Value |
|----------|-------|
| **Endpoint** | All routes proxied to downstream services |
| **Port** | 8080 |
| **Health Check** | Aggregated status of all services |

---

## 6. Data Flow — End-to-End Pipeline

### Non-Technical Flow Diagram

```
  👨‍💻 Developer                    🤖 defriends                         📄 Output
  ───────────                    ──────────                         ──────────

  Pushes code to               Security scanner                   Stakeholders receive
  GitHub/GitLab    ────→       finds vulnerability    ────→       a clear report
                                                                   showing:
  "I updated the               "CVE-2025-12345:                   • Risk: 95/100 ⚠️
   payments API"                Unsafe deserialization             • Priority: P0
                                in request parser"                 • Fix: Upgrade to v1.4.6
                                                                   • Attack: Hackers can
                                                                     exploit this remotely
```

### Technical Flow Diagram

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌──────────────┐
│  INGESTION  │    │ NORMALIZER  │    │   MAPPING   │    │   SCORING   │    │  REPORTING   │
│             │    │             │    │             │    │             │    │              │
│ POST        │    │ POST        │    │ POST        │    │ POST        │    │ POST         │
│ /v1/ingest  │    │ /v1/normalize│   │ /v1/map     │    │ /v1/score   │    │ /v1/report/* │
│             │    │             │    │             │    │             │    │              │
│ Input:      │    │ Input:      │    │ Input:      │    │ Input:      │    │ Input:       │
│ Evidence    │───→│ Evidence    │───→│ MapRequest  │───→│ ScoreRequest│───→│ Assessment   │
│ Event       │    │ Event       │    │ {cve, cwe,  │    │ {findings}  │    │ Report       │
│ {event_id,  │    │             │    │  exposure}  │    │             │    │              │
│  asset,     │    │ Output:     │    │             │    │ Output:     │    │ Output:      │
│  payload,   │    │ Normalized  │    │ Output:     │    │ ScoreResp   │    │ {valid:true} │
│  context}   │    │ keys +      │    │ MapResponse │    │ {overall,   │    │   or         │
│             │    │ asset info  │    │ {techniques,│    │  scored[]}  │    │ PDF binary   │
│ Output:     │    │             │    │  confidence}│    │             │    │              │
│ {accepted,  │    │             │    │             │    │             │    │              │
│  ingestion_ │    │             │    │             │    │             │    │              │
│  id}        │    │             │    │             │    │             │    │              │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └──────────────┘
      │                   │                  │                  │                  │
      ▼                   ▼                  ▼                  ▼                  ▼
 ┌─────────┐        ┌─────────┐       ┌──────────┐      ┌──────────┐      ┌───────────┐
 │Pydantic │        │Pydantic │       │YAML Rule │      │ Scoring  │      │JSON Schema│
 │  Model  │        │  Model  │       │  Engine  │      │ Formula  │      │+ ReportLab│
 │Validation│       │Validation│      │(4 rules) │      │(weighted)│      │   (PDF)   │
 └─────────┘        └─────────┘       └──────────┘      └──────────┘      └───────────┘
```

### Sequence Diagram — Full Pipeline

```
  Client          Ingestion      Normalizer      Mapping        Scoring       Reporting
    │                │               │              │              │              │
    │  POST /v1/ingest               │              │              │              │
    │───────────────→│               │              │              │              │
    │  {event}       │               │              │              │              │
    │←───────────────│               │              │              │              │
    │  {accepted, id}│               │              │              │              │
    │                │               │              │              │              │
    │  POST /v1/normalize            │              │              │              │
    │───────────────────────────────→│              │              │              │
    │  {event}                       │              │              │              │
    │←───────────────────────────────│              │              │              │
    │  {normalized keys, asset}      │              │              │              │
    │                │               │              │              │              │
    │  POST /v1/map                                 │              │              │
    │──────────────────────────────────────────────→│              │              │
    │  {cwe, exposure}                              │              │              │
    │←──────────────────────────────────────────────│              │              │
    │  {techniques: [T1190, T1059]}                 │              │              │
    │                │               │              │              │              │
    │  POST /v1/score                                              │              │
    │─────────────────────────────────────────────────────────────→│              │
    │  {findings: [...]}                                           │              │
    │←─────────────────────────────────────────────────────────────│              │
    │  {overall_risk_score: 95.2, scored: [...]}                   │              │
    │                │               │              │              │              │
    │  POST /v1/report/pdf                                                        │
    │────────────────────────────────────────────────────────────────────────────→│
    │  {full AssessmentReport}                                                    │
    │←────────────────────────────────────────────────────────────────────────────│
    │  ← PDF binary (application/pdf)                                             │
    │                │               │              │              │              │
```

---

## 7. Data Models & Schemas

### Core Data Model Hierarchy

```
AssessmentReport
├── asset: AssetRef
│   ├── org_id          (string, required)     — "demo-org"
│   ├── asset_id        (string, required)     — "payments-api"
│   ├── environment     (dev|staging|prod)     — "prod"
│   ├── name            (string, optional)     — "Payments API"
│   └── version         (string, optional)     — "2.7.3"
│
├── summary: ReportSummary
│   ├── overall_risk_score  (0.0 – 100.0)
│   ├── findings_total      (integer)
│   ├── findings_by_severity {critical: 1, high: 1, ...}
│   ├── controls_total      (integer)
│   ├── controls_by_status  {pass: 1, fail: 1, ...}
│   └── top_techniques      ["T1190", "T1059.007"]
│
├── mapped_findings: [MappedFinding]
│   ├── finding: VulnerabilityFinding
│   │   ├── cve                 — "CVE-2025-12345"
│   │   ├── title               — "Unsafe deserialization"
│   │   ├── cwe                 — "CWE-502"
│   │   ├── component           — "acme-request-parser"
│   │   ├── cvss_v3             — 9.8 (0.0 – 10.0)
│   │   ├── epss                — 0.72 (0.0 – 1.0)
│   │   ├── kev                 — true (in Known Exploited list?)
│   │   ├── exposure: ExposureContext
│   │   │   ├── internet_facing         — true
│   │   │   ├── authenticated_required  — false
│   │   │   ├── privilege_boundary      — "none"
│   │   │   └── reachable              — true
│   │   └── references: [EvidenceRef]
│   │
│   └── techniques: [MitreTechnique]
│       ├── technique_id    — "T1190"
│       ├── technique_name  — "Exploit Public-Facing Application"
│       ├── tactic          — "Initial Access"
│       ├── confidence      — 0.85 (0.0 – 1.0)
│       └── rationale       — "If a server-side injection..."
│
├── control_results: [ControlResult]
│   ├── control_id      — "ASVS.V2.1.1"
│   ├── title           — "Verify all pages require auth..."
│   ├── status          — pass|partial|fail|not_applicable
│   ├── confidence      — 0.7 (0.0 – 1.0)
│   ├── evidence        — [{kind, ref, sha256}]
│   ├── notes           — "8 routes lack auth requirements"
│   └── mitigation_links
│
├── recommendations: [Recommendation]
│   ├── recommendation_id   — "rec_0001"
│   ├── priority            — p0|p1|p2|p3
│   ├── title               — "Upgrade request parser"
│   ├── description         — "Update to v1.4.6+..."
│   ├── owner               — app|platform|secops|iam|...
│   ├── related_controls    — ["ASVS.V4.1.1"]
│   ├── related_cves        — ["CVE-2025-12345"]
│   └── related_techniques  — ["T1190", "T1059"]
│
├── methodology: {inputs, notes}
└── provenance: {mapping_pack, baseline_pack}
```

### EvidenceEvent (Input Model)

```
EvidenceEvent
├── schema_version  — "v1"
├── event_id        — "evt_demo_0001"
├── observed_at     — "2026-03-03T09:00:00Z"
├── source          — sdk|agent|cicd|manual
├── asset: AssetRef
├── event_type      — "sbom" | "vuln_finding" | "config_check" | "control_check"
├── payload         — {arbitrary tool-specific data}
└── context         — {pipeline: "github-actions", commit: "abc1234"}
```

---

## 8. Rule Engine & Mapping Logic

### How Rules Work (Non-Technical)

The rule engine is like a decision tree:

```
  Question 1: "Is this a deserialization or injection bug?" (CWE-502, CWE-78, CWE-94)
     YES ──→ Question 2: "Is the application internet-facing?"
                YES ──→ Question 3: "Can code actually reach the vulnerability?"
                           YES ──→ 🎯 Map to T1190 (Exploit Public-Facing App)
                           NO  ──→ ❌ No match
                NO  ──→ ❌ No match
     NO  ──→ Try next rule...
```

### Rule Pack (Technical)

**File:** `rules/mapping/mitre_cwe_context.v1.yaml`

| Rule | Name | Conditions | Techniques Mapped |
|------|------|------------|-------------------|
| R001 | Server-side injection (public-facing) | CWE ∈ {502, 78, 94} AND internet-facing AND reachable | T1190, T1059 |
| R002 | SQL injection (reachable) | CWE = 89 AND reachable | T1190, T1555, T1078 |
| R003 | XSS with auth session | CWE = 79 AND authenticated_required | T1059.007, T1539 |
| R004 | Weak auth on privilege boundary | CWE ∈ {287, 306, 307} AND privilege_boundary ∈ {user_to_admin, app_to_cloud_admin} | T1078, T1110 |

### Supported Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `eq` | Equals | `path: cwe, op: eq, value: CWE-89` |
| `neq` | Not equals | `op: neq, value: null` |
| `in` | Value in list | `op: in, value: [CWE-94, CWE-78]` |
| `nin` | Not in list | `op: nin` |
| `regex` | Regex match | `op: regex, value: ^CWE-\d+$` |
| `truthy` | Boolean true / non-empty | `op: truthy` |
| `falsy` | Boolean false / empty | `op: falsy` |

### Baseline Pack (OWASP ASVS Controls)

**File:** `rules/baseline/owasp_asvs_l2_subset.v1.yaml`

| Control ID | Title | Automated Check |
|------------|-------|-----------------|
| ASVS.V2.1.1 | All pages require authentication | `routes.auth_required_coverage >= 0.95` |
| ASVS.V2.2.1 | Anti-automation controls | `auth.rate_limiting == truthy` |
| ASVS.V4.1.1 | Secure headers set | HSTS + CSP present |

---

## 9. Risk Scoring Algorithm

### Non-Technical Explanation

Each vulnerability gets a "danger score" from 0 to 100 based on five factors:

```
  ┌──────────────────────────────────────────────────────────────┐
  │                    RISK SCORE FORMULA                        │
  │                                                              │
  │   ██████████████████████████████████████████████████ 55%     │
  │   How severe is the bug? (CVSS score)                        │
  │                                                              │
  │   ████████████████████████████ 25%                           │
  │   How likely is it to be exploited? (EPSS probability)       │
  │                                                              │
  │   ███████████ 10%                                            │
  │   Is it being actively exploited RIGHT NOW? (KEV list)       │
  │                                                              │
  │   ████████ 7%                                                │
  │   Can code actually reach the vulnerability? (Reachability)  │
  │                                                              │
  │   ████ 3%                                                    │
  │   Is it exposed to the internet? (Internet-facing)           │
  └──────────────────────────────────────────────────────────────┘
```

### Technical Formula

```python
score = (
    (cvss_v3 / 10.0) * 55.0 +     # Severity weight: 55%
    (epss)            * 25.0 +     # Exploit probability: 25%
    (kev)             * 10.0 +     # Known exploited: 10%
    (reachable)       *  7.0 +     # Code reachability: 7%
    (internet_facing) *  3.0       # Internet exposure: 3%
)
score = clamp(score, 0.0, 100.0)
overall = average(all_finding_scores)
```

### Scoring Examples

| Scenario | CVSS | EPSS | KEV | Reach | Internet | **Score** | **Priority** |
|----------|------|------|-----|-------|----------|-----------|-------------|
| Critical RCE, actively exploited | 9.8 | 0.72 | ✅ | ✅ | ✅ | **95.9** | **P0** |
| High SQLi, internal only | 7.5 | 0.38 | ❌ | ✅ | ❌ | **57.8** | **P2** |
| Medium XSS, auth required | 6.1 | 0.21 | ❌ | ✅ | ❌ | **45.8** | **P3** |
| Low info disclosure | 2.0 | 0.01 | ❌ | ❌ | ❌ | **11.3** | **P3** |

---

## 10. PDF Report Generation

### Report Layout

```
┌──────────────────────────────────┐
│    PAGE 1: TITLE & SUMMARY       │
│                                  │
│  Security Assessment Report      │
│  defriends Assessment -          │
│  Payments API (prod)             │
│                                  │
│  ┌────────────┬────────────────┐ │
│  │ Report ID  │ rep_demo_0001  │ │
│  │ Generated  │ 2026-03-03     │ │
│  │ Version    │ 2.7.3          │ │
│  └────────────┴────────────────┘ │
│                                  │
│  ┌──────────────────────────┐    │
│  │ Risk Score: 76.4/100     │    │
│  │ Findings: 3              │    │
│  │ Controls: 3              │    │
│  │ Top: T1190, T1059.007    │    │
│  └──────────────────────────┘    │
│                                  │
│  Methodology: SBOM, DAST, SAST   │
│  Provenance: mitre-cwe v1.0.0   │
├──────────────────────────────────┤
│    PAGE 2: FINDINGS TABLE        │
│                                  │
│  CVE    │Title │Sev │CVSS│Techs  │
│  ───────┼──────┼────┼────┼────── │
│  CVE-   │Unsafe│crit│9.8 │T1190  │
│  2025-  │deser.│    │    │T1059  │
│  12345  │      │    │    │       │
│  ───────┼──────┼────┼────┼────── │
│  ...    │      │    │    │       │
│                                  │
│  Technique Rationale:            │
│  CVE-2025-12345:                 │
│  - T1190 (Initial Access): ...   │
│  - T1059 (Execution): ...        │
├──────────────────────────────────┤
│    PAGE 3: GAP ANALYSIS          │
│                                  │
│  Control     │Status │Confidence │
│  ────────────┼───────┼────────── │
│  ASVS.V2.1.1│partial│ 0.70      │
│  ASVS.V2.2.1│fail   │ 0.80      │
│  ASVS.V4.1.1│pass   │ 0.90      │
│                                  │
│  Prioritized Recommendations:    │
│  P0 - Upgrade request parser     │
│  P1 - Add rate limiting          │
│  P2 - Harden admin UI            │
└──────────────────────────────────┘
```

---

## 11. Project Structure

```
secmesh_scaffold/
├── app_unified.py                  # 🏠 Unified FastAPI app (all services combined)
├── Dockerfile                      # 🐳 Production Docker image
├── docker-compose.yml              # 🐳 Microservices orchestration
├── render.yaml                     # ☁️  Render deployment blueprint
├── requirements.txt                # 📦 Python dependencies
├── .env / .env.example             # ⚙️  Environment configuration
│
├── packages/
│   └── common/                     # 📚 Shared library (dirtybot_common)
│       └── src/dirtybot_common/
│           ├── models.py           #    Pydantic data models (13 models)
│           └── util.py             #    Utility functions (get_path)
│
├── services/                       # 🔧 Microservices
│   ├── ingestion/app/              #    Evidence intake
│   │   ├── api.py                  #    POST /v1/ingest
│   │   └── main.py                 #    Standalone FastAPI app
│   ├── normalizer/app/             #    Data normalization
│   │   ├── api.py                  #    POST /v1/normalize
│   │   └── main.py
│   ├── mapping/app/                #    MITRE ATT&CK mapping
│   │   ├── api.py                  #    POST /v1/map
│   │   ├── rule_engine.py          #    YAML rule evaluation engine
│   │   └── main.py
│   ├── scoring/app/                #    Risk scoring
│   │   ├── api.py                  #    POST /v1/score
│   │   └── main.py
│   ├── reporting/app/              #    Report validation & PDF
│   │   ├── api.py                  #    POST /v1/report/*
│   │   ├── pdf_renderer.py         #    ReportLab PDF generation
│   │   └── main.py
│   └── gateway/app/                #    API gateway (microservices mode)
│       ├── api.py                  #    Proxy routes
│       ├── config.py               #    Service URLs
│       ├── proxy.py                #    HTTPX async client
│       └── main.py
│
├── rules/                          # 📋 Rule packs
│   ├── mapping/
│   │   └── mitre_cwe_context.v1.yaml   # CWE → MITRE ATT&CK rules (4 rules)
│   └── baseline/
│       └── owasp_asvs_l2_subset.v1.yaml # OWASP ASVS controls (3 controls)
│
├── schemas/                        # 📐 JSON Schemas
│   ├── report.schema.json          #    Assessment report validation
│   └── evidence_event.schema.json  #    Evidence event validation
│
├── examples/                       # 📝 Sample data
│   ├── sample_evidence_event.json
│   ├── sample_report.json
│   └── sample_report.pdf
│
├── tests/                          # 🧪 Test suites
│   ├── test_e2e.py                 #    72 functional E2E tests
│   ├── test_security_e2e.py        #    161 security E2E tests
│   └── test_rule_engine.py         #    Rule engine unit test
│
├── reports/pdf/                    # 📄 Standalone PDF renderer
│   ├── render_report.py
│   └── template_notes.md
│
└── scripts/                        # 🔨 Development scripts
    ├── dev_up.sh                   #    Start local Docker environment
    └── gen_sample_pdf.sh           #    Generate sample PDF
```

---

## 12. Deployment Architecture

### Option A: Unified Mode (Render / Single Container)

```
┌─────────────────────────────────────────────┐
│              Render Web Service              │
│                                             │
│  ┌────────────────────────────────────────┐ │
│  │         app_unified.py                 │ │
│  │                                        │ │
│  │  FastAPI app                           │ │
│  │  ├── /v1/ingest     (ingestion)        │ │
│  │  ├── /v1/normalize  (normalizer)       │ │
│  │  ├── /v1/map        (mapping)          │ │
│  │  ├── /v1/score      (scoring)          │ │
│  │  ├── /v1/report/*   (reporting)        │ │
│  │  ├── /health                           │ │
│  │  └── /docs          (Swagger UI)       │ │
│  │                                        │ │
│  │  uvicorn :8000                         │ │
│  └────────────────────────────────────────┘ │
│                                             │
│  Docker image: python:3.11-slim            │
│  Plan: free                                │
│  Health check: /health                     │
└─────────────────────────────────────────────┘
```

### Option B: Microservices Mode (Docker Compose)

```
┌──────────────────────────────────────────────────────────────────┐
│                      Docker Compose Network                      │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │Ingestion │  │Normalizer│  │ Mapping  │  │ Scoring  │        │
│  │  :8001   │  │  :8002   │  │  :8003   │  │  :8004   │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
│       │              │              │              │              │
│       └──────────────┴──────────────┴──────────────┘              │
│                              │                                    │
│                    ┌─────────┴─────────┐                          │
│  ┌──────────┐     │     Gateway       │                          │
│  │Reporting │     │      :8080        │  ←── External traffic    │
│  │  :8005   │     │  (Proxy to all)   │                          │
│  └──────────┘     └───────────────────┘                          │
│                                                                  │
│  Shared volumes: /rules (read-only), /schemas (read-only)        │
└──────────────────────────────────────────────────────────────────┘
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DIRTYBOT_ORG_ID` | `demo-org` | Tenant organization ID |
| `DIRTYBOT_MAPPING_PACK` | `/app/rules/mapping/mitre_cwe_context.v1.yaml` | Path to MITRE mapping rules |
| `DIRTYBOT_REPORT_SCHEMA` | `/app/schemas/report.schema.json` | Path to report JSON Schema |
| `DIRTYBOT_JWT_AUDIENCE` | `dirtybot` | JWT audience (future auth) |
| `DIRTYBOT_JWT_ISSUER` | `dirtybot-local` | JWT issuer (future auth) |
| `DIRTYBOT_DEV_SECRET` | `change-me` | Development secret (⚠️ change in prod!) |

---

## 13. API Reference

### Base URL

| Mode | URL |
|------|-----|
| Local development | `http://127.0.0.1:8000` |
| Render deployment | `https://dirtybots.onrender.com` |
| Swagger UI | `{base_url}/docs` |

### Endpoints

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|-------------|----------|
| `GET` | `/` | Service info | — | `{service, version, docs, health}` |
| `GET` | `/health` | Health check | — | `{status, services}` |
| `POST` | `/v1/ingest` | Ingest evidence | `EvidenceEvent` | `{accepted, ingestion_id}` |
| `POST` | `/v1/normalize` | Normalize event | `EvidenceEvent` | `{event_id, asset, keys}` |
| `POST` | `/v1/map` | Map to MITRE | `MapRequest` | `{pack_id, techniques[]}` |
| `POST` | `/v1/score` | Score findings | `ScoreRequest` | `{overall_risk_score, scored[]}` |
| `POST` | `/v1/report/validate` | Validate report | `AssessmentReport` | `{valid: true}` |
| `POST` | `/v1/report/pdf` | Generate PDF | `AssessmentReport` | `application/pdf` binary |

---

## 14. Security Design

### Implemented Protections

| Protection | Status | Details |
|------------|--------|---------|
| **Input Validation** | ✅ | Pydantic v2 strict type checking on all endpoints |
| **CORS** | ✅ | Allowlist-only origins, credentials enabled |
| **HTML Injection (PDF)** | ✅ | All user input HTML-escaped before ReportLab Paragraphs |
| **JSON Schema Validation** | ✅ | Reports validated against Draft 2020-12 schema |
| **Safe YAML Loading** | ✅ | `yaml.safe_load()` prevents YAML deserialization attacks |
| **Content-Type Enforcement** | ✅ | Only `application/json` accepted |
| **No Static File Serving** | ✅ | `.env`, `.git`, internal files not served |

### Known Gaps (Scaffold)

| Gap | Risk | Recommendation |
|-----|------|----------------|
| No Authentication | Medium | Add JWT/API-key middleware |
| No Rate Limiting | Medium | Add per-IP throttling |
| No HTTPS enforcement | Medium | Enable in reverse proxy |
| HEAD method returns 405 | Low | Add explicit HEAD handlers |
| Binary body causes 500 | Low | Add custom exception handler for UnicodeDecodeError |

### Security Test Coverage

| Category | Tests | Result |
|----------|-------|--------|
| SQL/NoSQL/Command/SSTI Injection | 31 | ✅ Safe |
| Cross-Site Scripting (XSS) | 17 | ✅ Safe |
| Path Traversal / LFI | 15 | ✅ Safe |
| SSRF | 21 | ✅ Safe |
| Denial of Service | 8 | ✅ Handled |
| CORS Bypass | 10 | ✅ Blocked |
| Information Disclosure | 6 | ✅ No leaks |
| **Total** | **161** | **All passing** |

---

## 15. Testing Strategy

### Test Suites

| Suite | File | Tests | Focus |
|-------|------|-------|-------|
| **Functional E2E** | `tests/test_e2e.py` | 72 | All endpoints, models, pipeline flow |
| **Security E2E** | `tests/test_security_e2e.py` | 161 | OWASP Top-10, injection, XSS, SSRF |
| **Rule Engine** | `tests/test_rule_engine.py` | 1 | Rule pack loading and matching |
| **Total** | — | **233** | — |

### How to Run Tests

```bash
# All tests
cd secmesh_scaffold
python -m pytest tests/ -v

# Only security tests
python -m pytest tests/test_security_e2e.py -v

# Only functional tests
python -m pytest tests/test_e2e.py -v
```

---

## 16. Glossary

### For Non-Technical Readers

| Term | Plain English |
|------|---------------|
| **CVE** | A unique ID for a known software bug (e.g., CVE-2025-12345) |
| **CWE** | A category of bug type (e.g., CWE-502 = "Unsafe Deserialization") |
| **CVSS** | A severity score for bugs (0-10, where 10 is worst) |
| **EPSS** | The probability (0-100%) that a bug will be exploited in the wild |
| **KEV** | A list of bugs that are actively being exploited right now |
| **MITRE ATT&CK** | A catalog of real-world hacker techniques |
| **OWASP ASVS** | A checklist of security controls your app should have |
| **SBOM** | A list of all software components in your application |
| **API** | A way for software to talk to other software |

### For Technical Readers

| Term | Description |
|------|-------------|
| **FastAPI** | Python async web framework with auto-generated OpenAPI docs |
| **Pydantic** | Data validation library using Python type hints |
| **ReportLab** | Python library for generating PDF documents |
| **HTTPX** | Async HTTP client used for gateway proxy |
| **JSON Schema** | Standard for validating JSON document structure |
| **Docker Compose** | Tool for defining multi-container Docker applications |
| **Render Blueprint** | Infrastructure-as-code for Render deployments |
| **Rule Pack** | YAML file containing conditional logic for threat mapping |

---

*Document generated for the defriends Security Assessment Platform.*
