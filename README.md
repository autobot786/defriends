# defriends

defriends is an authorized device security assessment workspace. It helps a user collect assessment records, understand risk in plain language, map findings to control domains, verify result legitimacy, generate a layman-friendly report, and guide remediation.

The public surface is intentionally small. The dashboard, API docs, user portal, and capability manifest require login so the product idea and assessment workflow are not exposed to casual visitors.

## UI Entry Points

| Page | URL | Access |
|---|---|---|
| Landing page | `http://127.0.0.1:8080/` | Public |
| Login / Register | `http://127.0.0.1:8080/login` | Public |
| Dashboard + Guided Tour | `http://127.0.0.1:8080/ui` | Login required |
| Health check | `http://127.0.0.1:8080/health` | Public |

After logging in, click **▶ Start Tour** in the dashboard to walk through the 8-step guided assessment pipeline (Ingestion → Normalizer → Mapping → Scoring → Reporting → Controls → Legitimacy → AI Assistant).

## Table of Contents

- [UI Entry Points](#ui-entry-points)
- [Interactive Demo](#interactive-demo)
- [API Quick Checks](#api-quick-checks)
- [Control Domains Included](#control-domains-included)
- [Running Tests](#running-tests)
- [Service Layout](#service-layout)
- [Key Files](#key-files)
- [Environment Variables](#environment-variables)
- [Privacy And Safety Notes](#privacy-and-safety-notes)
- [Development Notes](#development-notes)

## Interactive Demo

<details open>
<summary><strong>1. Start The App</strong></summary>

```bash
python -m secmesh_scaffold
```

Or run the unified FastAPI app directly:

```bash
DIRTYBOT_MAPPING_PACK=rules/mapping/mitre_cwe_context.v1.yaml \
DIRTYBOT_REPORT_SCHEMA=schemas/report.schema.json \
python -m uvicorn app_unified:app --host 127.0.0.1 --port 8080 --reload
```

On Windows PowerShell:

```powershell
$env:DIRTYBOT_MAPPING_PACK = "rules/mapping/mitre_cwe_context.v1.yaml"
$env:DIRTYBOT_REPORT_SCHEMA = "schemas/report.schema.json"
python -m uvicorn app_unified:app --host 127.0.0.1 --port 8080 --reload
```

Open:

```text
http://127.0.0.1:8080/login
```

</details>

<details>
<summary><strong>2. Create A Local Demo User</strong></summary>

Use a local-only account for the demo:

```bash
curl -X POST http://127.0.0.1:8080/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"ChangeMe123!","name":"Demo User","role":"admin"}'
```

Then sign in from `/login`. After login, the app redirects to `/ui`.

</details>

<details>
<summary><strong>3. Walk Through The Demo</strong></summary>

Use the dashboard cards in this order:

| Step | Dashboard Area | What To Try | Expected Result |
|---|---|---|---|
| 1 | Ingestion | Load the sample record and submit it | The app accepts the authorized assessment record |
| 2 | Normalizer | Send the record forward | The record is prepared consistently for assessment |
| 3 | Mapping | Run the mapped finding review | The app links the finding to likely attack patterns |
| 4 | Scoring | Run risk scoring | The app returns a priority and risk score |
| 5 | Reporting | Generate the report | The app produces a simple device risk report |
| 6 | Controls | Review control domain status | Failed and partial NIST/ISO areas are highlighted with fixes |
| 7 | Legitimacy | Run legitimacy verification | The app checks whether totals, risk, evidence, controls, and recommendations agree |
| 8 | AI Assistant | Ask "What should I do next?" | The assistant explains the next action and offers safe action buttons |

</details>

<details>
<summary><strong>4. What The Demo Proves</strong></summary>

The demo verifies that defriends can:

- keep sensitive workspace pages behind login;
- accept authorized assessment records;
- normalize incoming records for consistent analysis;
- map security findings to attack patterns;
- calculate a risk score and priority;
- integrate NIST SP 800-53 and ISO/IEC 27001:2022 control domains;
- explain failed and partial controls with practical remediation steps;
- verify report legitimacy with a confidence score;
- generate a plain-language PDF report for non-technical readers;
- guide a stuck user with an assistant that can suggest safe next actions.

</details>

<details>
<summary><strong>5. Expected Demo Output</strong></summary>

A completed demo should produce:

- a risk score and priority for the tested device or application;
- control status counts for pass, partial, and fail;
- remediation recommendations for failed or partial controls;
- a legitimacy verdict with confidence;
- a PDF report with simple sections such as "Bottom Line", "What To Do First", "Risks Found", and "Why The Results Are Legit".

</details>

<details>
<summary><strong>6. Public Exposure Check</strong></summary>

These routes are intentionally protected:

| Route | Public Behavior |
|---|---|
| `/ui` | Redirects to `/login?next=/ui` |
| `/docs` | Redirects to `/login?next=/docs` |
| `/user` | Redirects to `/login?next=/user` |
| `/v1/masterpiece/manifest` | Returns `401` without login |
| `/api` | Shows only minimal service, login, docs, and health links until authenticated |

`/health` remains public so deployments can check whether the app is running.

</details>

## API Quick Checks

<details open>
<summary><strong>Health</strong></summary>

```bash
curl http://127.0.0.1:8080/health
```

</details>

<details>
<summary><strong>Public API index</strong></summary>

```bash
curl http://127.0.0.1:8080/api
```

Expected unauthenticated shape:

```json
{
  "service": "defriends API",
  "status": "login_required",
  "login": "/login",
  "docs": "/login?next=/docs",
  "health": "/health"
}
```

</details>

## Control Domains Included

<details open>
<summary><strong>NIST SP 800-53 + ISO/IEC 27001:2022 enrichment</strong></summary>

The reporting layer enriches assessments with the requested NIST SP 800-53 and ISO/IEC 27001:2022 domains, including:

- flaw remediation;
- security alerts and advisories;
- boundary protection;
- configuration change control;
- vulnerability monitoring and scanning;
- continuous monitoring;
- incident handling;
- management of technical vulnerabilities;
- threat intelligence;
- network security;
- network segregation;
- configuration management;
- monitoring activities;
- protection against malware;
- incident management planning and preparation;
- secure development life cycle.

Failed and partial domains are not left as labels only. They are converted into clear recommended actions and included in the final report.

</details>

## Running Tests

```bash
pytest tests/test_e2e.py -q
```

Current verified result:

```text
79 passed
```

For broader local checks:

```bash
pytest tests/ -v
```

## Service Layout

| Service | Prefix | Entry Point |
|---|---|---|
| Unified Gateway | `/` | `app_unified.py` |
| Ingestion | `/v1` | `services/ingestion/app/api.py` |
| Normalizer | `/v1` | `services/normalizer/app/api.py` |
| Mapping | `/v1` | `services/mapping/app/api.py` |
| Scoring | `/v1` | `services/scoring/app/api.py` |
| Reporting | `/v1` | `services/reporting/app/api.py` |
| Consent | `/v1/consent` | `services/consent/app/api.py` |
| Behavioral | `/v1/behavioral` | `services/behavioral/app/api.py` |
| Remediation | `/v1/remediation` | `services/remediation/app/api.py` |
| AI Assistant | `/v1/ai/app` | `services/ai_assistant/app/api.py` |

## Key Files

- `app_unified.py` - FastAPI app, public landing, auth, protected pages, and static serving.
- `static/landing.html` - public landing page (colorful, animated, no login required).
- `static/login.html` - login and registration page.
- `static/dashboard.html` - authenticated dashboard with 8-step guided tour.
- `services/reporting/app/control_domains.py` - NIST/ISO control catalog and enrichment.
- `services/reporting/app/legitimacy.py` - legitimacy confidence checks.
- `services/reporting/app/pdf_renderer.py` - layman-friendly PDF report.
- `services/ai_assistant/app/assistant.py` - assistant responses and action suggestions.
- `rules/mapping/mitre_cwe_context.v1.yaml` - mapping rules.
- `schemas/report.schema.json` - report validation schema.
- `packages/common/src/dirtybot_common/models.py` - shared Pydantic models.

## Environment Variables

Environment variables still use the `DIRTYBOT_` prefix for compatibility with older deployments.

| Variable | Default | Purpose |
|---|---|---|
| `DIRTYBOT_MAPPING_PACK` | `rules/mapping/mitre_cwe_context.v1.yaml` | Mapping rule pack path |
| `DIRTYBOT_REPORT_SCHEMA` | `schemas/report.schema.json` | Report JSON Schema path |
| `DIRTYBOT_ORG_ID` | `demo-org` | Default organization identifier |
| `PORT` | `8080` | Unified app listen port |

## Privacy And Safety Notes

- Run assessments only on systems you own or are authorized to test.
- Do not publish real vulnerability records, device identifiers, credentials, tokens, or customer names in screenshots or GitHub issues.
- The interactive dashboard is designed for authenticated users. Keep it behind login in shared deployments.
- Treat generated reports as sensitive security documents.

## Development Notes

All services share models from:

```text
packages/common/src/dirtybot_common/models.py
```

After changing shared models, reinstall the local package when your environment supports editable installs:

```bash
pip install -e packages/common
```
