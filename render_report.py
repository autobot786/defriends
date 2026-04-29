from __future__ import annotations

import json
import sys
from datetime import datetime
from typing import Any, BinaryIO

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

def _fmt_dt(s: str) -> str:
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return s

def _severity_from_cvss(cvss: float | None) -> str:
    if cvss is None:
        return "unknown"
    if cvss >= 9.0:
        return "critical"
    if cvss >= 7.0:
        return "high"
    if cvss >= 4.0:
        return "medium"
    return "low"

def _header_footer(canvas, doc, header_text: str):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.grey)
    canvas.drawString(doc.leftMargin, doc.height + doc.topMargin - 10, header_text)
    canvas.drawRightString(doc.leftMargin + doc.width, 0.5 * inch, f"Page {doc.page}")
    canvas.restoreState()

def render_report_pdf(report: dict[str, Any], out: BinaryIO) -> None:
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=20, leading=24, spaceAfter=12))
    styles.add(ParagraphStyle(name="H2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=14, leading=18, spaceBefore=10, spaceAfter=8))
    styles.add(ParagraphStyle(name="Body", parent=styles["BodyText"], fontName="Helvetica", fontSize=10.5, leading=14))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontName="Helvetica", fontSize=9, leading=12, textColor=colors.grey))
    styles.add(ParagraphStyle(name="Cell", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.5, leading=12))
    styles.add(ParagraphStyle(name="CellBold", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=9.5, leading=12))

    asset = report.get("asset", {})
    header_text = f"SecMesh Assessment - {asset.get('name') or asset.get('asset_id', 'asset')} ({asset.get('environment', '')})"

    doc = SimpleDocTemplate(
        out, pagesize=LETTER,
        leftMargin=0.75*inch, rightMargin=0.75*inch,
        topMargin=0.8*inch, bottomMargin=0.8*inch,
        title="SecMesh Assessment Report", author="SecMesh Scaffold"
    )

    story = []

    # Title page
    story.append(Paragraph("Security Assessment Report", styles["H1"]))
    story.append(Paragraph(header_text, styles["H2"]))

    meta_tbl = Table([
        ["Report ID", report.get("report_id", "")],
        ["Generated", _fmt_dt(report.get("generated_at", ""))],
        ["Time Window", f"{_fmt_dt(report.get('time_window', {}).get('from',''))} to {_fmt_dt(report.get('time_window', {}).get('to',''))}"],
        ["Asset Version", asset.get("version", "")],
        ["Organization", asset.get("org_id", "")],
    ], colWidths=[1.5*inch, 5.5*inch])

    meta_tbl.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("TEXTCOLOR", (0,0), (0,-1), colors.grey),
        ("LINEBELOW", (0,0), (-1,0), 0.5, colors.lightgrey),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.whitesmoke, colors.white]),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 0.2*inch))

    summary = report.get("summary", {})
    tiles = Table([
        ["Overall Risk Score", f"{float(summary.get('overall_risk_score', 0)):.1f}/100", "Findings", str(summary.get("findings_total", 0))],
        ["Controls", str(summary.get("controls_total", 0)), "Top Techniques", ", ".join(summary.get("top_techniques", [])[:4])],
    ], colWidths=[1.6*inch, 1.4*inch, 1.2*inch, 2.8*inch])

    tiles.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#F3F6FA")),
        ("BACKGROUND", (0,1), (-1,1), colors.white),
        ("BOX", (0,0), (-1,-1), 0.75, colors.lightgrey),
        ("INNERGRID", (0,0), (-1,-1), 0.5, colors.lightgrey),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 10.5),
        ("TEXTCOLOR", (0,0), (0,-1), colors.grey),
        ("TEXTCOLOR", (2,0), (2,-1), colors.grey),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(tiles)

    story.append(Spacer(1, 0.25*inch))
    story.append(Paragraph("Methodology", styles["H2"]))
    methodology = report.get("methodology", {})
    inputs = methodology.get("inputs", [])
    notes = methodology.get("notes", "")
    story.append(Paragraph(f"<b>Inputs:</b> {', '.join(inputs) if inputs else 'N/A'}", styles["Body"]))
    if notes:
        story.append(Paragraph(f"<b>Notes:</b> {notes}", styles["Body"]))

    prov = report.get("provenance", {})
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph("Provenance", styles["H2"]))
    story.append(Paragraph(f"<b>Mapping pack:</b> {prov.get('mapping_pack', {}).get('pack_id', '')} {prov.get('mapping_pack', {}).get('version', '')}", styles["Body"]))
    story.append(Paragraph(f"<b>Baseline pack:</b> {prov.get('baseline_pack', {}).get('pack_id', '')} {prov.get('baseline_pack', {}).get('version', '')}", styles["Body"]))

    story.append(PageBreak())

    # Findings
    story.append(Paragraph("Vulnerability Findings and ATT&CK Mapping", styles["H1"]))
    story.append(Paragraph("Prioritized findings with technique mappings derived from the rule pack and exposure context.", styles["Body"]))
    story.append(Spacer(1, 0.15*inch))

    header = [
        Paragraph("CVE", styles["CellBold"]),
        Paragraph("Title", styles["CellBold"]),
        Paragraph("Severity", styles["CellBold"]),
        Paragraph("CVSS", styles["CellBold"]),
        Paragraph("EPSS", styles["CellBold"]),
        Paragraph("Reachable", styles["CellBold"]),
        Paragraph("Techniques (Top)", styles["CellBold"]),
    ]
    rows = [header]

    for mf in report.get("mapped_findings", []):
        f = mf.get("finding", {})
        techs = mf.get("techniques", [])
        cvss = f.get("cvss_v3")
        epss = f.get("epss")
        sev = _severity_from_cvss(cvss if isinstance(cvss, (int, float)) else None)
        exposure = f.get("exposure", {})
        reachable = "Yes" if exposure.get("reachable") else "No"
        top_tech = ", ".join([t.get("technique_id") for t in techs[:4]]) if techs else ""
        title = f.get("title", "")
        rows.append([
            Paragraph(f.get("cve", ""), styles["Cell"]),
            Paragraph(title, styles["Cell"]),
            Paragraph(sev, styles["Cell"]),
            Paragraph(f"{cvss:.1f}" if isinstance(cvss, (int, float)) else "", styles["Cell"]),
            Paragraph(f"{epss:.2f}" if isinstance(epss, (int, float)) else "", styles["Cell"]),
            Paragraph(reachable, styles["Cell"]),
            Paragraph(top_tech, styles["Cell"]),
        ])

    tbl = Table(rows, colWidths=[1.1*inch, 2.6*inch, 0.8*inch, 0.6*inch, 0.6*inch, 0.7*inch, 1.5*inch], repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#F3F6FA")),
        ("GRID", (0,0), (-1,-1), 0.5, colors.lightgrey),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story.append(tbl)

    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Technique rationale highlights", styles["H2"]))
    for mf in report.get("mapped_findings", []):
        f = mf.get("finding", {})
        techs = mf.get("techniques", [])
        if not techs:
            continue
        story.append(Paragraph(f"<b>{f.get('cve','')}</b> - {f.get('title','')}", styles["Body"]))
        seen = set()
        for t in techs[:3]:
            r = t.get("rationale", "")
            if r in seen:
                continue
            seen.add(r)
            story.append(Paragraph(f"- {t.get('technique_id')} ({t.get('tactic')}): {r}", styles["Body"]))
        story.append(Spacer(1, 0.1*inch))

    story.append(PageBreak())

    # Gap analysis
    story.append(Paragraph("Gap Analysis (Controls)", styles["H1"]))
    story.append(Paragraph("Control status is based on available evidence and automated checks. Confidence reflects evidence quality and coverage.", styles["Body"]))
    story.append(Spacer(1, 0.15*inch))

    cheader = [
        Paragraph("Control", styles["CellBold"]),
        Paragraph("Status", styles["CellBold"]),
        Paragraph("Confidence", styles["CellBold"]),
        Paragraph("Notes", styles["CellBold"]),
    ]
    crows = [cheader]
    for c in report.get("control_results", []):
        notes = c.get("notes") or ""
        crows.append([
            Paragraph(c.get("control_id",""), styles["Cell"]),
            Paragraph(c.get("status",""), styles["Cell"]),
            Paragraph(f"{float(c.get('confidence',0)):.2f}", styles["Cell"]),
            Paragraph(notes, styles["Cell"]),
        ])

    ctbl = Table(crows, colWidths=[1.2*inch, 0.9*inch, 0.9*inch, 4.3*inch], repeatRows=1)
    ctbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#F3F6FA")),
        ("GRID", (0,0), (-1,-1), 0.5, colors.lightgrey),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story.append(ctbl)

    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Prioritized Recommendations", styles["H2"]))
    for r in report.get("recommendations", []):
        story.append(Paragraph(f"<b>{r.get('priority','').upper()}</b> - {r.get('title','')}", styles["Body"]))
        story.append(Paragraph(r.get("description",""), styles["Body"]))
        links = []
        if r.get("related_controls"):
            links.append("Controls: " + ", ".join(r["related_controls"]))
        if r.get("related_cves"):
            links.append("CVEs: " + ", ".join(r["related_cves"]))
        if r.get("related_techniques"):
            links.append("Techniques: " + ", ".join(r["related_techniques"]))
        if links:
            story.append(Paragraph("<i>" + " | ".join(links) + "</i>", styles["Small"]))
        story.append(Spacer(1, 0.12*inch))

    doc.build(
        story,
        onFirstPage=lambda c, d: _header_footer(c, d, header_text),
        onLaterPages=lambda c, d: _header_footer(c, d, header_text),
    )

def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: python render_report.py <input_report.json> <output.pdf>")
        return 2
    in_path, out_path = argv[1], argv[2]
    report = json.loads(open(in_path, "r", encoding="utf-8").read())
    with open(out_path, "wb") as f:
        render_report_pdf(report, f)
    print(f"Wrote: {out_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
