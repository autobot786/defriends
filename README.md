# defriends

**defriends** is a consent-first security assessment platform that turns raw security findings into **actionable risk**.

It provides a unified pipeline to:

- **Ingest** evidence from scanners / CI / manual sources
- **Normalize** events into a consistent schema
- **Map** findings to **MITRE ATT&CK** techniques using YAML rule packs
- **Score** risk (0–100) with a transparent, weighted formula
- **Report** results as a **validated JSON report** and a **professional PDF**

> Tech stack: **Python 3.11+**, **FastAPI**, **Pydantic v2**, **JSON Schema**, **ReportLab**, **Docker / Compose**.

---

## Live, attractive interactive GUI demo

This repo includes a **single-file interactive GUI** you can open in a browser:

- **`demo.html`** — a polished, interactive dashboard-style demo

### Run the demo (no build tools)

1. Start the API (recommended):

```bash
pip install -r requirements.txt
python -m uvicorn app_unified:app --reload --host 127.0.0.1 --port 8080
```

2. Open the demo:

- Open `demo.html` directly in your browser, or
- (Recommended) serve it locally so fetch/XHR works consistently:

```bash
python -m http.server 5173
# then open http://127.0.0.1:5173/demo.html
```

If you run the platform via:

```bash
python -m .
```

It will print and open:

- `http://127.0.0.1:8080/ui` (dashboard)
- `http://127.0.0.1:8080/docs` (Swagger UI)

---

## Quick start (unified mode)

```bash
pip install -r requirements.txt
python -m uvicorn app_unified:app --reload --host 127.0.0.1 --port 8080
```

Then visit:

- API docs: http://127.0.0.1:8080/docs
- Health:   http://127.0.0.1:8080/health

---

## What’s in this repository?

- `app_unified.py` — unified FastAPI app entrypoint (all services combined)
- `docker-compose.yml` — microservices mode orchestration
- `rules/` — YAML rule packs (MITRE mapping + baseline controls)
- `schemas/` — JSON Schemas for validation
- `sample_report.json` / `sample_report.pdf` — example report output
- `USAGE_AND_INTEGRATION_GUIDE.md` — copy/paste API walkthroughs
- `DESIGN_DOCUMENT.md` — architecture, scoring, rule engine, and data model details

---

## Core API endpoints

- `POST /v1/ingest`
- `POST /v1/normalize`
- `POST /v1/map`
- `POST /v1/score`
- `POST /v1/report/validate`
- `POST /v1/report/pdf`

---

## License

See [LICENSE](LICENSE).
