# defriends — Real-Time Usage, Integration & Incident Response Guide

> **Version:** 1.0.0  
> **Platform:** defriends Security Assessment API  
> **Base URL (Local):** `http://127.0.0.1:8000`  
> **Interactive Docs:** `http://127.0.0.1:8000/docs`

---

## Table of Contents

1. [Quick Start — Running defriends](#1-quick-start--running-dirtybots)
2. [Real-Time Usage — Swagger UI Walkthrough](#2-real-time-usage--swagger-ui-walkthrough)
3. [Step-by-Step Integration Guide](#3-step-by-step-integration-guide)
4. [Step-by-Step Implementation Guide](#4-step-by-step-implementation-guide)
5. [Incident-Based Workflows — Inspecting Correct Results](#5-incident-based-workflows--inspecting-correct-results)
   - [Incident A: Critical RCE / Unsafe Deserialization](#incident-a-critical-rce--unsafe-deserialization-cwe-502)
   - [Incident B: SQL Injection](#incident-b-sql-injection-cwe-89)
   - [Incident C: Cross-Site Scripting (XSS)](#incident-c-cross-site-scripting-xss-cwe-79)
   - [Incident D: Broken Authentication / Weak Auth](#incident-d-broken-authentication--weak-auth-cwe-287)
   - [Incident E: Multi-Vulnerability Assessment](#incident-e-multi-vulnerability-full-assessment)
6. [Full Pipeline Walkthrough — From Evidence to PDF](#6-full-pipeline-walkthrough--from-evidence-to-pdf)
7. [Integration with CI/CD Pipelines](#7-integration-with-cicd-pipelines)
8. [Integration with Security Tools](#8-integration-with-security-tools)
9. [Result Verification Checklist](#9-result-verification-checklist)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Quick Start — Running defriends

### Prerequisites

- Python 3.11+ installed
- `pip install fastapi uvicorn pydantic pydantic-settings pyyaml jsonschema httpx reportlab pytest`
- defriends common library installed: `pip install -e packages/common`

### Start the Server

```powershell
cd secmesh_scaffold

# Set environment variables
$env:DIRTYBOT_MAPPING_PACK = "rules/mapping/mitre_cwe_context.v1.yaml"
$env:DIRTYBOT_REPORT_SCHEMA = "schemas/report.schema.json"
$env:DIRTYBOT_ORG_ID = "demo-org"

# Start with hot-reload
python -m uvicorn app_unified:app --host 127.0.0.1 --port 8000 --reload
```

### Verify It's Running

```powershell
# Check health
curl http://127.0.0.1:8000/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "service": "dirtybots-unified",
  "services": {
    "ingestion": "ok",
    "normalizer": "ok",
    "mapping": "ok",
    "scoring": "ok",
    "reporting": "ok"
  }
}
```

### Access Points

| URL | Purpose |
|-----|---------|
| http://127.0.0.1:8000/docs | **Swagger UI** — Click "Try it out" on any endpoint |
| http://127.0.0.1:8000/redoc | **ReDoc** — Clean read-only API documentation |
| http://127.0.0.1:8000/ | Root — Service info and version |
| http://127.0.0.1:8000/openapi.json | OpenAPI 3.0 specification (machine-readable) |

---

## 2. Real-Time Usage — Swagger UI Walkthrough

### How to Use the Swagger UI

1. Open **http://127.0.0.1:8000/docs** in your browser
2. You'll see all endpoints grouped by tags: `gateway`, `ingestion`, `normalizer`, `mapping`, `scoring`, `reporting`
3. Click any endpoint → Click **"Try it out"** → Paste the JSON body → Click **"Execute"**
4. View the **Response body**, **Response code**, and **Response headers** below

### Testing Each Endpoint (Copy-Paste Ready)

#### Test 1: Ingest an Evidence Event

**Endpoint:** `POST /v1/ingest`  
**Paste this body:**
```json
{
  "schema_version": "v1",
  "event_id": "evt_test_001",
  "observed_at": "2026-03-15T10:00:00Z",
  "source": "cicd",
  "asset": {
    "org_id": "my-company",
    "asset_id": "web-app",
    "environment": "prod",
    "name": "Customer Portal",
    "version": "3.2.1"
  },
  "event_type": "vuln_finding",
  "payload": {
    "scanner": "trivy",
    "finding_count": 5
  },
  "context": {
    "pipeline": "github-actions",
    "commit": "a1b2c3d"
  }
}
```

**Expected Response (200 OK):**
```json
{
  "accepted": true,
  "received_event_id": "evt_test_001",
  "ingestion_id": "c5038c1a-cb53-4cfc-a8d2-6565ca9f220d"
}
```

**What to verify:**
- ✅ `accepted` is `true`
- ✅ `received_event_id` matches your input
- ✅ `ingestion_id` is a unique UUID (tracking number)

---

#### Test 2: Normalize an Event

**Endpoint:** `POST /v1/normalize`  
**Paste the same body as Test 1.**

**Expected Response (200 OK):**
```json
{
  "event_id": "evt_test_001",
  "asset": {
    "org_id": "my-company",
    "asset_id": "web-app",
    "environment": "prod",
    "name": "Customer Portal",
    "version": "3.2.1"
  },
  "event_type": "vuln_finding",
  "normalized_payload_keys": ["finding_count", "scanner"],
  "context_keys": ["commit", "pipeline"]
}
```

**What to verify:**
- ✅ `normalized_payload_keys` are **alphabetically sorted**
- ✅ `context_keys` are **alphabetically sorted**
- ✅ `asset` object is fully extracted

---

#### Test 3: Map a Vulnerability to Attack Techniques

**Endpoint:** `POST /v1/map`  
**Paste this body:**
```json
{
  "cwe": "CWE-502",
  "exposure": {
    "internet_facing": true,
    "reachable": true
  }
}
```

**Expected Response (200 OK):**
```json
{
  "pack_id": "mitre-cwe-context",
  "pack_version": "1.0.0",
  "mitre_version": "ATT&CK v14 (Enterprise)",
  "techniques": [
    {
      "technique_id": "T1190",
      "technique_name": "Exploit Public-Facing Application",
      "tactic": "Initial Access",
      "confidence": 0.85,
      "rationale": "If a server-side injection weakness is reachable on an internet-facing surface, it is commonly leveraged for Initial Access."
    },
    {
      "technique_id": "T1059",
      "technique_name": "Command and Scripting Interpreter",
      "tactic": "Execution",
      "confidence": 0.65,
      "rationale": "If a server-side injection weakness is reachable on an internet-facing surface, it is commonly leveraged for Initial Access."
    }
  ]
}
```

**What to verify:**
- ✅ `pack_id` is `mitre-cwe-context` (correct rule pack loaded)
- ✅ `techniques` array is **not empty** (rules matched)
- ✅ Each technique has `confidence` between 0.0 and 1.0
- ✅ `T1190` is present (the primary expected technique for CWE-502)

---

#### Test 4: Score Vulnerabilities

**Endpoint:** `POST /v1/score`  
**Paste this body:**
```json
{
  "findings": [
    {
      "cve": "CVE-2025-12345",
      "title": "Unsafe deserialization in request parser",
      "cvss_v3": 9.8,
      "epss": 0.72,
      "kev": true,
      "exposure": {
        "internet_facing": true,
        "reachable": true
      }
    }
  ]
}
```

**Expected Response (200 OK):**
```json
{
  "overall_risk_score": 91.9,
  "scored": [
    {
      "cve": "CVE-2025-12345",
      "risk_score": 91.9,
      "priority": "p0"
    }
  ]
}
```

**What to verify:**
- ✅ `risk_score` is **91.9** (manually verify: 9.8/10×55 + 0.72×25 + 10 + 7 + 3 = 91.9)
- ✅ `priority` is **p0** (score ≥ 85)
- ✅ `overall_risk_score` equals the single finding's score

**Manual calculation breakdown:**
```
CVSS component:    (9.8 / 10.0) × 55.0  = 53.90
EPSS component:    0.72 × 25.0           = 18.00
KEV component:     1.0 × 10.0            = 10.00
Reachable:         1.0 × 7.0             =  7.00
Internet-facing:   1.0 × 3.0             =  3.00
                                    TOTAL = 91.90 → Priority: P0
```

---

#### Test 5: Validate a Report

**Endpoint:** `POST /v1/report/validate`  
**Paste the content from `examples/sample_report.json`**

**Expected Response (200 OK):**
```json
{
  "valid": true
}
```

---

#### Test 6: Generate a PDF Report

**Endpoint:** `POST /v1/report/pdf`  
**Paste the same content from `examples/sample_report.json`**

**Expected Response (200 OK):**
- Content-Type: `application/pdf`
- Download the PDF file
- Open it → Verify it contains the title page, findings table, gap analysis, and recommendations

---

## 3. Step-by-Step Integration Guide

### Integration Architecture

```
┌─────────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│   YOUR SYSTEMS       │     │     defriends API     │     │   YOUR OUTPUT    │
│                      │     │                      │     │                  │
│  CI/CD Pipeline     ─┼────→│  POST /v1/ingest     │     │                  │
│  (GitHub Actions,    │     │         ↓             │     │                  │
│   GitLab CI, etc.)   │     │  POST /v1/normalize   │     │                  │
│                      │     │         ↓             │     │                  │
│  Scanner Output     ─┼────→│  POST /v1/map         │     │  Dashboard       │
│  (Trivy, Snyk,      │     │         ↓             │     │  SIEM            │
│   SonarQube, etc.)   │     │  POST /v1/score       │     │  Jira Tickets    │
│                      │     │         ↓             │     │  Slack Alerts    │
│  Manual Findings    ─┼────→│  POST /v1/report/pdf  │────→│  PDF Reports     │
│                      │     │                      │     │  Compliance Docs  │
└─────────────────────┘     └──────────────────────┘     └─────────────────┘
```

### Step 1: Install Python HTTP Client

```bash
pip install requests
```

### Step 2: Create a defriends Client

```python
"""dirtybots_client.py — Reusable client for defriends API integration."""

import requests

class defriendsClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base = base_url.rstrip("/")

    def health(self) -> dict:
        return requests.get(f"{self.base}/health").json()

    def ingest(self, event: dict) -> dict:
        r = requests.post(f"{self.base}/v1/ingest", json=event)
        r.raise_for_status()
        return r.json()

    def normalize(self, event: dict) -> dict:
        r = requests.post(f"{self.base}/v1/normalize", json=event)
        r.raise_for_status()
        return r.json()

    def map_to_mitre(self, cve: str = None, cwe: str = None, exposure: dict = None) -> dict:
        payload = {"cve": cve, "cwe": cwe, "exposure": exposure or {}}
        r = requests.post(f"{self.base}/v1/map", json=payload)
        r.raise_for_status()
        return r.json()

    def score(self, findings: list[dict]) -> dict:
        r = requests.post(f"{self.base}/v1/score", json={"findings": findings})
        r.raise_for_status()
        return r.json()

    def validate_report(self, report: dict) -> dict:
        r = requests.post(f"{self.base}/v1/report/validate", json=report)
        r.raise_for_status()
        return r.json()

    def generate_pdf(self, report: dict, output_path: str) -> str:
        r = requests.post(f"{self.base}/v1/report/pdf", json=report)
        r.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(r.content)
        return output_path
```

### Step 3: Use the Client

```python
from dirtybots_client import defriendsClient

client = defriendsClient("http://127.0.0.1:8000")

# Check health
print(client.health())

# Ingest evidence
result = client.ingest({
    "schema_version": "v1",
    "event_id": "evt_001",
    "observed_at": "2026-03-15T10:00:00Z",
    "source": "cicd",
    "asset": {"org_id": "my-org", "asset_id": "my-app", "environment": "prod"},
    "event_type": "vuln_finding",
    "payload": {"scanner": "trivy"},
    "context": {"pipeline": "github-actions"},
})
print(f"Ingested: {result['ingestion_id']}")

# Map vulnerability
techniques = client.map_to_mitre(cwe="CWE-502", exposure={"internet_facing": True, "reachable": True})
print(f"Matched {len(techniques['techniques'])} techniques")

# Score findings
scores = client.score([
    {"cve": "CVE-2025-12345", "title": "RCE", "cvss_v3": 9.8, "epss": 0.72, "kev": True,
     "exposure": {"internet_facing": True, "reachable": True}}
])
print(f"Risk Score: {scores['overall_risk_score']}, Priority: {scores['scored'][0]['priority']}")
```

### Step 4: cURL Commands (for any language/tool)

```bash
# Ingest
curl -X POST http://127.0.0.1:8000/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{"schema_version":"v1","event_id":"evt_001","observed_at":"2026-03-15T10:00:00Z","source":"cicd","asset":{"org_id":"my-org","asset_id":"my-app","environment":"prod"},"event_type":"vuln_finding","payload":{},"context":{}}'

# Map
curl -X POST http://127.0.0.1:8000/v1/map \
  -H "Content-Type: application/json" \
  -d '{"cwe":"CWE-502","exposure":{"internet_facing":true,"reachable":true}}'

# Score
curl -X POST http://127.0.0.1:8000/v1/score \
  -H "Content-Type: application/json" \
  -d '{"findings":[{"cve":"CVE-2025-12345","title":"RCE","cvss_v3":9.8,"epss":0.72,"kev":true,"exposure":{"internet_facing":true,"reachable":true}}]}'

# Generate PDF (save to file)
curl -X POST http://127.0.0.1:8000/v1/report/pdf \
  -H "Content-Type: application/json" \
  -d @examples/sample_report.json \
  -o report.pdf
```

---

## 4. Step-by-Step Implementation Guide

### Phase 1: Connect Your Scanner

1. **Identify your scanner output format** (Trivy JSON, Snyk JSON, SonarQube API, etc.)
2. **Write a parser** that converts scanner output into `EvidenceEvent` format
3. **POST to `/v1/ingest`** after each scan

Example — Trivy to defriends:
```python
import json
import subprocess
from dirtybots_client import defriendsClient

# Run Trivy scan
result = subprocess.run(
    ["trivy", "image", "--format", "json", "my-app:latest"],
    capture_output=True, text=True
)
trivy_output = json.loads(result.stdout)

# Convert to defriends event
client = defriendsClient()
for vuln in trivy_output.get("Results", []):
    for v in vuln.get("Vulnerabilities", []):
        client.ingest({
            "schema_version": "v1",
            "event_id": f"trivy_{v['VulnerabilityID']}",
            "observed_at": "2026-03-15T10:00:00Z",
            "source": "cicd",
            "asset": {"org_id": "my-org", "asset_id": "my-app", "environment": "prod"},
            "event_type": "vuln_finding",
            "payload": {
                "cve": v["VulnerabilityID"],
                "severity": v.get("Severity"),
                "package": v.get("PkgName"),
                "installed": v.get("InstalledVersion"),
                "fixed": v.get("FixedVersion"),
            },
            "context": {"scanner": "trivy"},
        })
```

### Phase 2: Map & Score

```python
# For each CVE found, map to MITRE techniques
mapping = client.map_to_mitre(
    cve="CVE-2025-12345",
    cwe="CWE-502",
    exposure={"internet_facing": True, "reachable": True}
)

# Prepare findings for scoring
findings = [
    {
        "cve": "CVE-2025-12345",
        "title": "Unsafe deserialization",
        "cwe": "CWE-502",
        "cvss_v3": 9.8,
        "epss": 0.72,
        "kev": True,
        "exposure": {"internet_facing": True, "reachable": True},
    }
]

# Score all findings
score_result = client.score(findings)
print(f"Overall Risk: {score_result['overall_risk_score']}/100")
for s in score_result['scored']:
    print(f"  {s['cve']}: {s['risk_score']} ({s['priority']})")
```

### Phase 3: Generate Report

```python
# Build the full assessment report
report = {
    "schema_version": "v1",
    "report_id": "rep_weekly_001",
    "generated_at": "2026-03-15T12:00:00Z",
    "asset": {"org_id": "my-org", "asset_id": "my-app", "environment": "prod",
              "name": "Customer Portal", "version": "3.2.1"},
    "time_window": {"from": "2026-03-08T00:00:00Z", "to": "2026-03-15T12:00:00Z"},
    "summary": {
        "overall_risk_score": score_result["overall_risk_score"],
        "findings_total": len(findings),
        "findings_by_severity": {"critical": 1},
        "controls_total": 0,
        "controls_by_status": {},
        "top_techniques": [t["technique_id"] for t in mapping["techniques"][:3]],
    },
    "mapped_findings": [
        {"finding": findings[0], "techniques": mapping["techniques"]}
    ],
    "control_results": [],
    "recommendations": [
        {
            "recommendation_id": "rec_001",
            "priority": "p0",
            "title": "Upgrade vulnerable library immediately",
            "description": "Update to the fixed version to remediate CVE-2025-12345.",
            "owner": "app",
            "related_cves": ["CVE-2025-12345"],
            "related_techniques": ["T1190"],
            "related_controls": [],
        }
    ],
    "methodology": {"inputs": ["SBOM scan (Trivy)"], "notes": "Weekly automated assessment."},
    "provenance": {"mapping_pack": {"pack_id": "mitre-cwe-context", "version": "1.0.0"}},
}

# Validate
validation = client.validate_report(report)
print(f"Report valid: {validation['valid']}")

# Generate PDF
client.generate_pdf(report, "weekly_assessment.pdf")
print("PDF saved to weekly_assessment.pdf")
```

---

## 5. Incident-Based Workflows — Inspecting Correct Results

### Incident A: Critical RCE / Unsafe Deserialization (CWE-502)

**Scenario:** Your SBOM scanner finds that `acme-request-parser v1.4.2` has CVE-2025-12345, an unsafe deserialization vulnerability. The application is internet-facing and the vulnerable code path is reachable.

#### Step 1: Ingest the Evidence

```bash
curl -X POST http://127.0.0.1:8000/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "schema_version": "v1",
    "event_id": "evt_rce_001",
    "observed_at": "2026-03-15T10:00:00Z",
    "source": "cicd",
    "asset": {"org_id": "demo-org", "asset_id": "payments-api", "environment": "prod", "name": "Payments API", "version": "2.7.3"},
    "event_type": "vuln_finding",
    "payload": {"cve": "CVE-2025-12345", "component": "acme-request-parser", "installed": "1.4.2", "fixed": "1.4.6"},
    "context": {"pipeline": "github-actions", "commit": "abc1234"}
  }'
```

**✅ Expected Result:**
```json
{"accepted": true, "received_event_id": "evt_rce_001", "ingestion_id": "<uuid>"}
```

#### Step 2: Map to MITRE ATT&CK

```bash
curl -X POST http://127.0.0.1:8000/v1/map \
  -H "Content-Type: application/json" \
  -d '{"cwe": "CWE-502", "exposure": {"internet_facing": true, "reachable": true}}'
```

**✅ Expected Result:**
```json
{
  "pack_id": "mitre-cwe-context",
  "pack_version": "1.0.0",
  "mitre_version": "ATT&CK v14 (Enterprise)",
  "techniques": [
    {"technique_id": "T1190", "technique_name": "Exploit Public-Facing Application", "tactic": "Initial Access", "confidence": 0.85},
    {"technique_id": "T1059", "technique_name": "Command and Scripting Interpreter", "tactic": "Execution", "confidence": 0.65}
  ]
}
```

**🔍 How to verify this is correct:**
- CWE-502 matches Rule R001 (server-side injection CWEs: 94, 78, 502)
- `internet_facing=true` satisfies the second condition
- `reachable=true` satisfies the third condition
- T1190 is the correct technique — deserialization on a public app is a classic Initial Access vector
- T1059 is correct — successful exploitation often leads to command execution
- Confidence 0.85 for T1190 > 0.65 for T1059 (Initial Access is more certain than Execution)

#### Step 3: Score the Finding

```bash
curl -X POST http://127.0.0.1:8000/v1/score \
  -H "Content-Type: application/json" \
  -d '{"findings": [{"cve": "CVE-2025-12345", "title": "Unsafe deserialization in request parser", "cvss_v3": 9.8, "epss": 0.72, "kev": true, "exposure": {"internet_facing": true, "reachable": true}}]}'
```

**✅ Expected Result:**
```json
{
  "overall_risk_score": 91.9,
  "scored": [{"cve": "CVE-2025-12345", "risk_score": 91.9, "priority": "p0"}]
}
```

**🔍 Manual verification:**
| Factor | Value | Weight | Contribution |
|--------|-------|--------|-------------|
| CVSS 9.8 | 9.8/10 = 0.98 | ×55 | **53.90** |
| EPSS 0.72 | 0.72 | ×25 | **18.00** |
| KEV (active exploit) | 1.0 | ×10 | **10.00** |
| Reachable | 1.0 | ×7 | **7.00** |
| Internet-facing | 1.0 | ×3 | **3.00** |
| | | **Total** | **91.90** |

Priority = **P0** (score ≥ 85) → Fix immediately

---

### Incident B: SQL Injection (CWE-89)

**Scenario:** SAST tool finds SQL injection in a legacy reporting endpoint. Internal only, no authentication required, code path is reachable.

#### Step 1: Map to MITRE ATT&CK

```bash
curl -X POST http://127.0.0.1:8000/v1/map \
  -H "Content-Type: application/json" \
  -d '{"cwe": "CWE-89", "exposure": {"reachable": true, "internet_facing": false, "authenticated_required": false}}'
```

**✅ Expected Result:**
```json
{
  "techniques": [
    {"technique_id": "T1190", "technique_name": "Exploit Public-Facing Application", "tactic": "Initial Access", "confidence": 0.6},
    {"technique_id": "T1555", "technique_name": "Credentials from Password Stores", "tactic": "Credential Access", "confidence": 0.55},
    {"technique_id": "T1078", "technique_name": "Valid Accounts", "tactic": "Initial Access", "confidence": 0.45}
  ]
}
```

**🔍 How to verify this is correct:**
- CWE-89 matches Rule R002 (`cwe == CWE-89`)
- `reachable=true` satisfies the second condition
- T1190: SQLi can be exploited for initial access (correct)
- T1555: SQLi can dump credential stores (correct)
- T1078: Stolen credentials enable valid account access (correct)
- Confidences decrease because SQLi impact depends on DB/app architecture

#### Step 2: Score the Finding

```bash
curl -X POST http://127.0.0.1:8000/v1/score \
  -H "Content-Type: application/json" \
  -d '{"findings": [{"cve": "CVE-2024-99999", "title": "SQL injection in legacy endpoint", "cwe": "CWE-89", "cvss_v3": 7.5, "epss": 0.38, "kev": false, "exposure": {"internet_facing": false, "reachable": true, "authenticated_required": false, "privilege_boundary": "none"}}]}'
```

**✅ Expected Result:**
```json
{
  "overall_risk_score": 57.75,
  "scored": [{"cve": "CVE-2024-99999", "risk_score": 57.75, "priority": "p2"}]
}
```

**🔍 Manual verification:**
| Factor | Value | Weight | Contribution |
|--------|-------|--------|-------------|
| CVSS 7.5 | 7.5/10 = 0.75 | ×55 | **41.25** |
| EPSS 0.38 | 0.38 | ×25 | **9.50** |
| KEV (not exploited) | 0.0 | ×10 | **0.00** |
| Reachable | 1.0 | ×7 | **7.00** |
| Internet-facing (no) | 0.0 | ×3 | **0.00** |
| | | **Total** | **57.75** |

Priority = **P2** (50 ≤ score < 70) → Fix this quarter

---

### Incident C: Cross-Site Scripting / XSS (CWE-79)

**Scenario:** DAST scan finds reflected XSS in an admin search page. Behind authentication, privilege boundary is user-to-admin.

#### Step 1: Map to MITRE ATT&CK

```bash
curl -X POST http://127.0.0.1:8000/v1/map \
  -H "Content-Type: application/json" \
  -d '{"cwe": "CWE-79", "exposure": {"authenticated_required": true, "privilege_boundary": "user_to_admin", "reachable": true}}'
```

**✅ Expected Result:**
```json
{
  "techniques": [
    {"technique_id": "T1059.007", "technique_name": "JavaScript", "tactic": "Execution", "confidence": 0.6},
    {"technique_id": "T1539", "technique_name": "Steal Web Session Cookie", "tactic": "Credential Access", "confidence": 0.55}
  ]
}
```

**🔍 How to verify this is correct:**
- CWE-79 matches Rule R003 (`cwe == CWE-79`)
- `authenticated_required=true` satisfies the second condition
- T1059.007 (JavaScript): XSS executes JavaScript in victim's browser (correct)
- T1539 (Cookie Theft): XSS commonly used to steal session cookies (correct)
- **Note:** Rule R004 also fires because `privilege_boundary=user_to_admin` matches

#### Step 2: Score the Finding

```bash
curl -X POST http://127.0.0.1:8000/v1/score \
  -H "Content-Type: application/json" \
  -d '{"findings": [{"cve": "CVE-2025-22222", "title": "Reflected XSS in admin search page", "cwe": "CWE-79", "cvss_v3": 6.1, "epss": 0.21, "kev": false, "exposure": {"internet_facing": false, "reachable": true, "authenticated_required": true, "privilege_boundary": "user_to_admin"}}]}'
```

**✅ Expected Result:**
```json
{
  "overall_risk_score": 45.8,
  "scored": [{"cve": "CVE-2025-22222", "risk_score": 45.8, "priority": "p3"}]
}
```

**🔍 Manual verification:**
| Factor | Value | Weight | Contribution |
|--------|-------|--------|-------------|
| CVSS 6.1 | 6.1/10 = 0.61 | ×55 | **33.55** |
| EPSS 0.21 | 0.21 | ×25 | **5.25** |
| KEV | 0.0 | ×10 | **0.00** |
| Reachable | 1.0 | ×7 | **7.00** |
| Internet-facing (no) | 0.0 | ×3 | **0.00** |
| | | **Total** | **45.80** |

Priority = **P3** (score < 50) → Track and plan

---

### Incident D: Broken Authentication / Weak Auth (CWE-287)

**Scenario:** Security audit reveals missing MFA on the admin panel. The privilege boundary is user-to-admin.

#### Step 1: Map to MITRE ATT&CK

```bash
curl -X POST http://127.0.0.1:8000/v1/map \
  -H "Content-Type: application/json" \
  -d '{"cwe": "CWE-287", "exposure": {"privilege_boundary": "user_to_admin"}, "tags": ["missing_mfa"]}'
```

**✅ Expected Result:**
```json
{
  "techniques": [
    {"technique_id": "T1078", "technique_name": "Valid Accounts", "tactic": "Initial Access", "confidence": 0.7},
    {"technique_id": "T1110", "technique_name": "Brute Force", "tactic": "Credential Access", "confidence": 0.45}
  ]
}
```

**🔍 How to verify this is correct:**
- CWE-287 matches Rule R004 (CWE ∈ {287, 306, 307} OR tags ∈ {missing_mfa, weak_auth})
- `privilege_boundary=user_to_admin` satisfies the privilege condition
- T1078 (Valid Accounts): Weak auth enables account takeover (correct)
- T1110 (Brute Force): Missing MFA enables brute force attacks (correct)

---

### Incident E: Multi-Vulnerability Full Assessment

**Scenario:** Weekly assessment with 3 findings — run them all through scoring together.

```bash
curl -X POST http://127.0.0.1:8000/v1/score \
  -H "Content-Type: application/json" \
  -d '{
    "findings": [
      {"cve": "CVE-2025-12345", "title": "Unsafe deserialization", "cvss_v3": 9.8, "epss": 0.72, "kev": true, "exposure": {"internet_facing": true, "reachable": true}},
      {"cve": "CVE-2025-22222", "title": "Reflected XSS", "cvss_v3": 6.1, "epss": 0.21, "kev": false, "exposure": {"internet_facing": false, "reachable": true}},
      {"cve": "CVE-2024-99999", "title": "SQL injection", "cvss_v3": 7.5, "epss": 0.38, "kev": false, "exposure": {"internet_facing": false, "reachable": true}}
    ]
  }'
```

**✅ Expected Result:**
```json
{
  "overall_risk_score": 65.15,
  "scored": [
    {"cve": "CVE-2025-12345", "risk_score": 91.9,  "priority": "p0"},
    {"cve": "CVE-2025-22222", "risk_score": 45.8,  "priority": "p3"},
    {"cve": "CVE-2024-99999", "risk_score": 57.75, "priority": "p2"}
  ]
}
```

**🔍 Verification:**
- Overall = (91.9 + 45.8 + 57.75) / 3 = **65.15** ✅
- Findings are individually scored, priorities correctly assigned
- P0 > P2 > P3 ordering shows correct prioritization

---

## 6. Full Pipeline Walkthrough — From Evidence to PDF

This section walks through the complete end-to-end flow for a real assessment:

```
Step 1: Ingest Evidence
        ↓
Step 2: Normalize Event
        ↓
Step 3: Map Each Finding to MITRE ATT&CK
        ↓
Step 4: Score All Findings
        ↓
Step 5: Build the Assessment Report
        ↓
Step 6: Validate the Report
        ↓
Step 7: Generate PDF
        ↓
Step 8: Open and Review the PDF
```

### Complete Script

```python
"""full_pipeline.py — Complete defriends assessment pipeline."""

import json
import datetime
from dirtybots_client import defriendsClient

client = defriendsClient("http://127.0.0.1:8000")

# === STEP 1: INGEST ===
print("Step 1: Ingesting evidence...")
ingest_result = client.ingest({
    "schema_version": "v1",
    "event_id": "evt_weekly_001",
    "observed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "source": "cicd",
    "asset": {
        "org_id": "acme-corp",
        "asset_id": "payments-api",
        "environment": "prod",
        "name": "Payments API",
        "version": "2.7.3",
    },
    "event_type": "vuln_finding",
    "payload": {"scanner": "trivy", "finding_count": 3},
    "context": {"pipeline": "github-actions", "commit": "abc1234"},
})
print(f"  ✅ Ingested: {ingest_result['ingestion_id']}")

# === STEP 2: NORMALIZE ===
print("Step 2: Normalizing...")
norm_result = client.normalize({
    "schema_version": "v1",
    "event_id": "evt_weekly_001",
    "observed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "source": "cicd",
    "asset": {"org_id": "acme-corp", "asset_id": "payments-api", "environment": "prod"},
    "event_type": "vuln_finding",
    "payload": {"scanner": "trivy", "finding_count": 3},
    "context": {"pipeline": "github-actions"},
})
print(f"  ✅ Normalized keys: {norm_result['normalized_payload_keys']}")

# === STEP 3: MAP EACH FINDING ===
print("Step 3: Mapping to MITRE ATT&CK...")
findings_data = [
    {"cve": "CVE-2025-12345", "title": "Unsafe deserialization", "cwe": "CWE-502",
     "cvss_v3": 9.8, "epss": 0.72, "kev": True,
     "exposure": {"internet_facing": True, "reachable": True,
                  "authenticated_required": False, "privilege_boundary": "none"}},
    {"cve": "CVE-2025-22222", "title": "Reflected XSS in admin search", "cwe": "CWE-79",
     "cvss_v3": 6.1, "epss": 0.21, "kev": False,
     "exposure": {"internet_facing": False, "reachable": True,
                  "authenticated_required": True, "privilege_boundary": "user_to_admin"}},
    {"cve": "CVE-2024-99999", "title": "SQL injection in legacy endpoint", "cwe": "CWE-89",
     "cvss_v3": 7.5, "epss": 0.38, "kev": False,
     "exposure": {"internet_facing": False, "reachable": True,
                  "authenticated_required": False, "privilege_boundary": "none"}},
]

mapped_findings = []
for f in findings_data:
    mapping = client.map_to_mitre(cve=f["cve"], cwe=f["cwe"], exposure=f["exposure"])
    mapped_findings.append({"finding": f, "techniques": mapping["techniques"]})
    techs = ", ".join([t["technique_id"] for t in mapping["techniques"]])
    print(f"  ✅ {f['cve']} → {techs or 'No match'}")

# === STEP 4: SCORE ALL FINDINGS ===
print("Step 4: Scoring...")
score_result = client.score(findings_data)
print(f"  ✅ Overall Risk Score: {score_result['overall_risk_score']}/100")
for s in score_result["scored"]:
    print(f"     {s['cve']}: {s['risk_score']} ({s['priority'].upper()})")

# === STEP 5: BUILD REPORT ===
print("Step 5: Building assessment report...")
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
report = {
    "schema_version": "v1",
    "report_id": "rep_weekly_001",
    "generated_at": now,
    "asset": {"org_id": "acme-corp", "asset_id": "payments-api",
              "environment": "prod", "name": "Payments API", "version": "2.7.3"},
    "time_window": {"from": "2026-03-08T00:00:00Z", "to": now},
    "summary": {
        "overall_risk_score": score_result["overall_risk_score"],
        "findings_total": len(findings_data),
        "findings_by_severity": {"critical": 1, "high": 1, "medium": 1},
        "controls_total": 3,
        "controls_by_status": {"pass": 1, "partial": 1, "fail": 1},
        "top_techniques": ["T1190", "T1059.007", "T1078"],
    },
    "mapped_findings": mapped_findings,
    "control_results": [
        {"control_id": "ASVS.V2.1.1", "title": "All pages require auth", "status": "partial",
         "confidence": 0.7, "evidence": [], "notes": "8 routes lack auth."},
        {"control_id": "ASVS.V2.2.1", "title": "Anti-automation controls", "status": "fail",
         "confidence": 0.8, "evidence": [], "notes": "No rate limiting on login."},
        {"control_id": "ASVS.V4.1.1", "title": "Secure headers set", "status": "pass",
         "confidence": 0.9, "evidence": [], "notes": "HSTS and CSP present."},
    ],
    "recommendations": [
        {"recommendation_id": "rec_001", "priority": "p0",
         "title": "Upgrade acme-request-parser to v1.4.6+",
         "description": "Remediate CVE-2025-12345 (unsafe deserialization). Verify fix with regression tests.",
         "owner": "app", "related_cves": ["CVE-2025-12345"],
         "related_techniques": ["T1190", "T1059"], "related_controls": []},
        {"recommendation_id": "rec_002", "priority": "p1",
         "title": "Add rate limiting to login endpoints",
         "description": "Implement per-IP throttling and account lockout.",
         "owner": "platform", "related_cves": [],
         "related_techniques": ["T1110", "T1078"], "related_controls": ["ASVS.V2.2.1"]},
        {"recommendation_id": "rec_003", "priority": "p2",
         "title": "Fix XSS and add CSP reporting",
         "description": "Fix reflected XSS, add output encoding, enable CSP report-only.",
         "owner": "app", "related_cves": ["CVE-2025-22222"],
         "related_techniques": ["T1059.007", "T1539"], "related_controls": ["ASVS.V2.1.1"]},
    ],
    "methodology": {"inputs": ["SBOM (Trivy)", "DAST", "SAST"], "notes": "Weekly automated assessment."},
    "provenance": {
        "mapping_pack": {"pack_id": "mitre-cwe-context", "version": "1.0.0"},
        "baseline_pack": {"pack_id": "asvs-l2-subset", "version": "1.0.0"},
    },
}
print(f"  ✅ Report built with {len(report['mapped_findings'])} findings, {len(report['recommendations'])} recommendations")

# === STEP 6: VALIDATE ===
print("Step 6: Validating report...")
validation = client.validate_report(report)
print(f"  ✅ Valid: {validation['valid']}")

# === STEP 7: GENERATE PDF ===
print("Step 7: Generating PDF...")
pdf_path = client.generate_pdf(report, "weekly_assessment.pdf")
print(f"  ✅ PDF saved to: {pdf_path}")

# === STEP 8: SUMMARY ===
print("\n" + "=" * 60)
print("  ASSESSMENT COMPLETE")
print("=" * 60)
print(f"  Asset:          {report['asset']['name']} v{report['asset']['version']}")
print(f"  Risk Score:     {score_result['overall_risk_score']}/100")
print(f"  Findings:       {len(findings_data)}")
print(f"  P0 (Critical):  {sum(1 for s in score_result['scored'] if s['priority'] == 'p0')}")
print(f"  P1 (High):      {sum(1 for s in score_result['scored'] if s['priority'] == 'p1')}")
print(f"  P2 (Medium):    {sum(1 for s in score_result['scored'] if s['priority'] == 'p2')}")
print(f"  P3 (Low):       {sum(1 for s in score_result['scored'] if s['priority'] == 'p3')}")
print(f"  Report:         {pdf_path}")
print("=" * 60)
```

---

## 7. Integration with CI/CD Pipelines

### GitHub Actions

```yaml
# .github/workflows/security-assessment.yml
name: defriends Security Assessment
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 6 * * 1'  # Weekly Monday 6am

jobs:
  assess:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          format: 'json'
          output: 'trivy-results.json'

      - name: Send to defriends
        run: |
          # Ingest scan results
          curl -X POST ${{ secrets.DIRTYBOTS_URL }}/v1/ingest \
            -H "Content-Type: application/json" \
            -d @trivy-results-formatted.json

          # Score findings
          curl -X POST ${{ secrets.DIRTYBOTS_URL }}/v1/score \
            -H "Content-Type: application/json" \
            -d @findings.json \
            -o score-result.json

          # Check if any P0 findings
          P0_COUNT=$(jq '[.scored[] | select(.priority == "p0")] | length' score-result.json)
          if [ "$P0_COUNT" -gt "0" ]; then
            echo "::error::$P0_COUNT critical (P0) vulnerabilities found!"
            exit 1
          fi

      - name: Generate Report
        run: |
          curl -X POST ${{ secrets.DIRTYBOTS_URL }}/v1/report/pdf \
            -H "Content-Type: application/json" \
            -d @report.json \
            -o assessment-report.pdf

      - name: Upload Report
        uses: actions/upload-artifact@v4
        with:
          name: security-report
          path: assessment-report.pdf
```

### GitLab CI

```yaml
# .gitlab-ci.yml
security-assessment:
  stage: test
  script:
    - trivy fs --format json -o trivy.json .
    - python scripts/send_to_dirtybots.py trivy.json
    - curl -X POST $DIRTYBOTS_URL/v1/report/pdf -d @report.json -o report.pdf
  artifacts:
    paths: [report.pdf]
    expire_in: 30 days
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

---

## 8. Integration with Security Tools

### Supported Scanner Outputs → defriends Input Mapping

| Scanner | Output Format | defriends `event_type` | Key Fields to Map |
|---------|--------------|----------------------|-------------------|
| **Trivy** | JSON | `vuln_finding` | VulnerabilityID → cve, Severity, PkgName |
| **Snyk** | JSON | `vuln_finding` | id → cve, cvssScore, exploitMaturity |
| **SonarQube** | API JSON | `vuln_finding` | key → cve, severity, component |
| **OWASP ZAP** | JSON | `vuln_finding` | cweid → cwe, riskcode → cvss_v3 |
| **Nessus** | JSON | `vuln_finding` | pluginID, cve, cvss3_base_score |
| **CycloneDX SBOM** | JSON/XML | `sbom` | Full SBOM as payload |
| **Manual** | N/A | `control_check` | Human-entered evidence |

### Webhook / Event-Driven Integration

```python
"""webhook_receiver.py — Receive scanner webhooks and forward to defriends."""

from fastapi import FastAPI, Request
from dirtybots_client import defriendsClient
import datetime

app = FastAPI()
dirtybots = defriendsClient("http://127.0.0.1:8000")

@app.post("/webhook/trivy")
async def trivy_webhook(request: Request):
    data = await request.json()
    for result in data.get("Results", []):
        for vuln in result.get("Vulnerabilities", []):
            dirtybots.ingest({
                "schema_version": "v1",
                "event_id": f"trivy_{vuln['VulnerabilityID']}_{datetime.date.today()}",
                "observed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "source": "agent",
                "asset": {"org_id": "my-org", "asset_id": result["Target"], "environment": "prod"},
                "event_type": "vuln_finding",
                "payload": vuln,
                "context": {"source": "trivy-webhook"},
            })
    return {"status": "ok", "processed": len(data.get("Results", []))}
```

---

## 9. Result Verification Checklist

Use this checklist when inspecting results from defriends:

### Ingestion Verification
- [ ] Response status is `200`
- [ ] `accepted` is `true`
- [ ] `received_event_id` matches your input
- [ ] `ingestion_id` is a valid UUID

### Normalization Verification
- [ ] Response status is `200`
- [ ] `event_id` matches input
- [ ] `normalized_payload_keys` are alphabetically sorted
- [ ] `context_keys` are alphabetically sorted
- [ ] `asset` object contains all input fields

### Mapping Verification
- [ ] `pack_id` is `mitre-cwe-context` (correct rule pack)
- [ ] `techniques` array is non-empty for known CWEs with matching exposure
- [ ] `techniques` array is empty for unknown CWEs or non-matching exposure
- [ ] Each technique has `confidence` between 0.0 and 1.0
- [ ] Technique IDs match expected MITRE ATT&CK framework IDs
- [ ] Rationale text is relevant to the vulnerability type

### Scoring Verification
- [ ] `overall_risk_score` is between 0.0 and 100.0
- [ ] `overall_risk_score` equals average of all individual scores
- [ ] Each finding has a `risk_score` and `priority`
- [ ] Priority mapping is correct: P0 ≥ 85, P1 ≥ 70, P2 ≥ 50, P3 < 50
- [ ] Manual calculation matches: `(cvss/10×55) + (epss×25) + (kev×10) + (reach×7) + (inet×3)`
- [ ] Empty findings list returns `overall_risk_score: 0.0`

### Report Verification
- [ ] `/v1/report/validate` returns `{"valid": true}`
- [ ] PDF starts with `%PDF-` header
- [ ] PDF contains title page with asset name and report ID
- [ ] PDF contains findings table with correct CVEs
- [ ] PDF contains gap analysis controls table
- [ ] PDF contains prioritized recommendations

### Mapping Quick Reference (Expected Results by CWE)

| Input CWE + Exposure | Expected Techniques | Rule |
|-----------------------|-------------------|------|
| CWE-502 + internet_facing + reachable | T1190, T1059 | R001 |
| CWE-78 + internet_facing + reachable | T1190, T1059 | R001 |
| CWE-94 + internet_facing + reachable | T1190, T1059 | R001 |
| CWE-89 + reachable | T1190, T1555, T1078 | R002 |
| CWE-79 + authenticated_required | T1059.007, T1539 | R003 |
| CWE-287 + user_to_admin boundary | T1078, T1110 | R004 |
| CWE-306 + user_to_admin boundary | T1078, T1110 | R004 |
| CWE-307 + app_to_cloud_admin boundary | T1078, T1110 | R004 |
| tags: missing_mfa + user_to_admin | T1078, T1110 | R004 |
| Unknown CWE, no exposure | Empty [] | No match |

### Scoring Quick Reference (Expected Priority by Inputs)

| CVSS | EPSS | KEV | Reach | Internet | Score | Priority |
|------|------|-----|-------|----------|-------|----------|
| 10.0 | 1.0 | ✅ | ✅ | ✅ | 100.0 | P0 |
| 9.8 | 0.72 | ✅ | ✅ | ✅ | 91.9 | P0 |
| 7.5 | 0.38 | ❌ | ✅ | ❌ | 57.75 | P2 |
| 6.1 | 0.21 | ❌ | ✅ | ❌ | 45.80 | P3 |
| 2.0 | 0.01 | ❌ | ❌ | ❌ | 11.25 | P3 |
| 0.0 | 0.0 | ❌ | ❌ | ❌ | 0.0 | P3 |

---

## 10. Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `422 Unprocessable Entity` | Missing or invalid field in request body | Check required fields against the schema in Swagger UI |
| `500 Rule pack not found` | `DIRTYBOT_MAPPING_PACK` env var points to wrong path | Set to absolute path of `rules/mapping/mitre_cwe_context.v1.yaml` |
| `500 Report schema not found` | `DIRTYBOT_REPORT_SCHEMA` env var wrong | Set to absolute path of `schemas/report.schema.json` |
| Empty techniques from `/v1/map` | CWE + exposure doesn't match any rule | Check the mapping quick reference table above |
| PDF generation fails | Invalid characters in report fields | Ensure no raw HTML/XML markup in user text fields |
| `ConnectionRefused` | Server not running | Start with `python -m uvicorn app_unified:app --port 8000` |

### Validating Your Environment

```bash
# Check all endpoints
curl http://127.0.0.1:8000/           # Should return service info
curl http://127.0.0.1:8000/health     # Should return {status: ok}
curl http://127.0.0.1:8000/openapi.json | python -m json.tool | head -20

# Quick smoke test
curl -X POST http://127.0.0.1:8000/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{"schema_version":"v1","event_id":"smoke","observed_at":"2026-01-01T00:00:00Z","source":"sdk","asset":{"org_id":"test","asset_id":"test","environment":"dev"},"event_type":"test","payload":{},"context":{}}'
```

---

*Guide generated for the defriends Security Assessment Platform v0.1.0*
