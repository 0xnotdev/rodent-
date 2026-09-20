"""Regression, coverage, and compare-result domain models."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from proof.domain.common import EvidenceClass, FrozenModel, JsonValue, Sha256, UtcTime
from proof.domain.context import ContextEnvelope
from proof.domain.scenario import FaultInstance


class RegressionCase(FrozenModel):
    case_id: str
    schema_version: Literal["1.0"] = "1.0"
    discovered_by: str
    first_seen_agent_id: str
    first_seen_at: UtcTime
    ir_fingerprint: Sha256
    resource_pattern: dict[str, JsonValue]
    fault_instances: tuple[FaultInstance, ...]
    context: ContextEnvelope
    contract_hash: Sha256
    failure_rule_ids: tuple[str, ...]
    evidence_hashes: tuple[Sha256, ...]
    reproductions: int = Field(ge=1)
    reproduction_failures: int = Field(ge=1)
    wilson_95_low: float = Field(ge=0.0, le=1.0)
    minimized: bool
    fidelity: EvidenceClass
    required_capabilities: tuple[str, ...]
    created_at: UtcTime
    fixed_in_agent_version: str | None = None
    content_hash: Sha256


class CoverageCell(FrozenModel):
    dimension: str
    key: tuple[str, ...]
    eligible_weight: float = Field(gt=0.0)
    attempts: int = Field(ge=0)
    valid_trials: int = Field(ge=0)
    safe_passes: int = Field(ge=0)
    unsafe_passes: int = Field(ge=0)
    failures: int = Field(ge=0)
    unknowns: int = Field(ge=0)
    highest_fidelity: EvidenceClass | None = None
    last_attempt_at: UtcTime | None = None


class CoverageRecord(FrozenModel):
    subject_id: str
    generated_at: UtcTime
    cells: tuple[CoverageCell, ...]
    gaps: tuple[tuple[str, ...], ...]
    content_hash: Sha256


class CompareResult(FrozenModel):
    compare_id: str
    baseline_agent_id: str
    candidate_agent_id: str
    paired_trial_ids: tuple[tuple[str, str], ...]
    task_success_delta: float
    safe_success_delta: float
    unsafe_rate_delta: float
    unknown_rate_delta: float
    new_violation_rule_ids: tuple[str, ...]
    fixed_violation_rule_ids: tuple[str, ...]
    scenario_regressions: tuple[str, ...]
    sample_size: int
    authoritative: bool
    gate_decision: Literal["PASS", "BLOCK", "WARN"]
    evidence_hashes: tuple[Sha256, ...]
