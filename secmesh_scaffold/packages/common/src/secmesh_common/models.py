from __future__ import annotations

from typing import Any, Literal, Optional
from pydantic import BaseModel, Field

class AssetRef(BaseModel):
    org_id: str = Field(..., description="Tenant / organization identifier.")
    asset_id: str = Field(..., description="Application/service identifier.")
    environment: Literal["dev", "staging", "prod"] = "prod"
    name: Optional[str] = None
    version: Optional[str] = None

class EvidenceRef(BaseModel):
    kind: str
    ref: str
    sha256: Optional[str] = None

class ExposureContext(BaseModel):
    internet_facing: bool = False
    authenticated_required: bool = False
    privilege_boundary: Literal["none", "user_to_admin", "container_to_host", "app_to_cloud_admin"] = "none"
    reachable: bool = False

class EvidenceEvent(BaseModel):
    schema_version: str = "v1"
    event_id: str
    observed_at: str
    source: Literal["sdk", "agent", "cicd", "manual"] = "sdk"
    asset: AssetRef
    event_type: str = Field(..., description="e.g. sbom, config_check, vuln_finding, control_check")
    payload: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)

class VulnerabilityFinding(BaseModel):
    cve: str
    title: str
    cwe: Optional[str] = None
    component: Optional[str] = None
    installed_version: Optional[str] = None
    fixed_version: Optional[str] = None

    cvss_v3: Optional[float] = None
    epss: Optional[float] = None
    kev: bool = False

    exposure: ExposureContext = Field(default_factory=ExposureContext)
    references: list[EvidenceRef] = Field(default_factory=list)

class MitreTechnique(BaseModel):
    technique_id: str
    technique_name: str
    tactic: str
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str

class MappedFinding(BaseModel):
    finding: VulnerabilityFinding
    techniques: list[MitreTechnique] = Field(default_factory=list)

class ControlResult(BaseModel):
    control_id: str
    title: str
    status: Literal["pass", "partial", "fail", "not_applicable"] = "fail"
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[EvidenceRef] = Field(default_factory=list)
    notes: Optional[str] = None
    mitigation_links: list[str] = Field(default_factory=list)

class Recommendation(BaseModel):
    recommendation_id: str
    priority: Literal["p0", "p1", "p2", "p3"] = "p2"
    title: str
    description: str
    owner: Literal["app", "platform", "secops", "iam", "network", "data", "other"] = "app"
    related_controls: list[str] = Field(default_factory=list)
    related_cves: list[str] = Field(default_factory=list)
    related_techniques: list[str] = Field(default_factory=list)

class ReportSummary(BaseModel):
    overall_risk_score: float = Field(ge=0.0, le=100.0)
    findings_total: int
    findings_by_severity: dict[str, int] = Field(default_factory=dict)
    controls_total: int
    controls_by_status: dict[str, int] = Field(default_factory=dict)
    top_techniques: list[str] = Field(default_factory=list)

class AssessmentReport(BaseModel):
    schema_version: str = "v1"
    report_id: str
    generated_at: str
    asset: AssetRef
    time_window: dict[str, str] = Field(default_factory=dict)

    summary: ReportSummary
    mapped_findings: list[MappedFinding] = Field(default_factory=list)
    control_results: list[ControlResult] = Field(default_factory=list)
    recommendations: list[Recommendation] = Field(default_factory=list)

    methodology: dict[str, Any] = Field(default_factory=dict)
    provenance: dict[str, Any] = Field(default_factory=dict)
