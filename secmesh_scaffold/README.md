# SecMesh Scaffold (defensive-only)

This repository is a scaffold for an embeddable security assessment platform:
- Ingest evidence from SDK/agent/CI/CD
- Normalize into a common schema
- Map weaknesses to MITRE ATT&CK techniques using versioned rule packs
- Score and prioritize findings using exploitability + context
- Produce a machine-readable JSON report and a polished PDF report

## Quickstart (local)

```bash
cp .env.example .env
docker compose up --build
```

Services:
- Ingestion:  http://localhost:8001/docs
- Normalizer: http://localhost:8002/docs
- Mapping:    http://localhost:8003/docs
- Scoring:    http://localhost:8004/docs
- Reporting:  http://localhost:8005/docs

## Generate the sample PDF report

```bash
python reports/pdf/render_report.py examples/sample_report.json examples/sample_report.pdf
```

## Rule packs
- Mapping rules: `rules/mapping/mitre_cwe_context.v1.yaml`
- Baseline controls example: `rules/baseline/owasp_asvs_l2_subset.v1.yaml`

## Defensive-only note
This scaffold focuses on risk identification, correlation, and reporting.
It intentionally avoids exploit code or offensive payloads.
