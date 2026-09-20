"""Run event, manifest, verifier, and outcome models."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import Field

from proof.domain.common import (
    Confidence,
    EvidenceClass,
    EvidenceRef,
    FrozenModel,
    JsonValue,
    ResourceId,
    Sha256,
    UtcTime,
)
from proof.domain.effects import Effect


class RunEvent(FrozenModel):
    schema_version: Literal["1.0"] = "1.0"
    sequence: int = Field(ge=1)
    event_id: str
    run_id: str
    trial_id: str
    event_type: str
    recorded_at: UtcTime
    monotonic_ns: int = Field(ge=0)
    actor: str
    payload: dict[str, JsonValue]
    evidence_refs: tuple[str, ...] = ()
    previous_event_hash: Sha256 | None
    event_hash: Sha256


class AgentDefinition(FrozenModel):
    agent_id: str
    executor: Literal["SHELL", "HARBOR"]
    image_digest: str
    command: tuple[str, ...]
    working_directory: str = "/workspace"
    environment: dict[str, str] = Field(default_factory=dict)
    model_id: str | None = None
    model_parameters: dict[str, JsonValue] = Field(default_factory=dict)
    tool_manifest_hash: Sha256 | None = None
    mcp_manifest_hash: Sha256 | None = None
    timeout_ms: int = Field(default=900_000, ge=1000)


class WorldDefinition(FrozenModel):
    world_id: str
    backend_id: str
    fidelity: EvidenceClass
    image_or_template_digest: str
    region: str
    capabilities: tuple[str, ...]
    capability_hash: Sha256
    max_cost_micro_usd: int


class RunManifest(FrozenModel):
    schema_version: Literal["1.0"] = "1.0"
    run_id: str
    trial_id: str
    created_at: UtcTime
    repo_commit: str | None
    repo_dirty_hash: Sha256 | None
    terraform_version: str
    provider_versions: dict[str, str]
    terraform_lock_hash: Sha256
    ir_hash: Sha256
    scenario_manifest_hash: Sha256
    generator_version: str
    operator_versions: dict[str, str]
    run_seed: int
    scenario_seed: int
    world: WorldDefinition
    agent: AgentDefinition
    policy_hashes: tuple[Sha256, ...]
    context_hash: Sha256
    contract_hash: Sha256
    verifier_versions: dict[str, str]
    sandbox_image_digest: str
    sandbox_profile_hash: Sha256
    host_fingerprint: dict[str, str]
    replay_of_trial_id: str | None = None
    content_hash: Sha256


class CheckStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class Severity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class VerifierResult(FrozenModel):
    verifier_id: str
    verifier_version: str
    rule_id: str
    status: CheckStatus
    severity: Severity
    hard: bool
    message: str
    resource_ids: tuple[ResourceId, ...] = ()
    effect_ids: tuple[str, ...] = ()
    event_ids: tuple[str, ...] = ()
    evidence: tuple[EvidenceRef, ...]
    confidence: Confidence


class RunVerdict(StrEnum):
    SAFE_PASS = "SAFE_PASS"
    UNSAFE_PASS = "UNSAFE_PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class TrialDisposition(StrEnum):
    VALID = "VALID"
    INVALID_INFRASTRUCTURE = "INVALID_INFRASTRUCTURE"
    INVALID_SCENARIO = "INVALID_SCENARIO"
    INVALID_EVIDENCE = "INVALID_EVIDENCE"
    CANCELLED = "CANCELLED"


class RunResult(FrozenModel):
    run_id: str
    trial_id: str
    disposition: TrialDisposition
    verdict: RunVerdict | None
    goal_status: CheckStatus | None
    safety_status: CheckStatus | None
    verifier_results: tuple[VerifierResult, ...]
    effects: tuple[Effect, ...]
    started_at: UtcTime
    ended_at: UtcTime
    fidelity: EvidenceClass
    manifest_hash: Sha256
    event_chain_head: Sha256
    artifact_hashes: tuple[Sha256, ...]
    warnings: tuple[str, ...] = ()
