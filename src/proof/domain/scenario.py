"""Scenario, fault-operator, oracle, and certification manifest models."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from proof.domain.common import (
    EvidenceClass,
    FrozenModel,
    JsonValue,
    ResourceId,
    Sha256,
    UtcTime,
)
from proof.domain.context import ContextEnvelope, Intent, StatePredicate
from proof.domain.effects import RiskLevel, SemanticCategory
from proof.domain.ir import RelationshipType


class ParameterSpec(FrozenModel):
    name: str
    json_schema: dict[str, JsonValue]
    default: JsonValue = None
    shrink_order: tuple[JsonValue, ...] = ()


class FidelityRequirement(FrozenModel):
    minimum: EvidenceClass
    capabilities: tuple[str, ...]
    forbidden_backends: tuple[str, ...] = ()


class HealthOracle(FrozenModel):
    oracle_id: str
    oracle_type: Literal[
        "HTTP", "TCP", "SQL", "AWS_STATE", "GRAPH_REACHABILITY", "IAM_SIMULATION", "COMMAND"
    ]
    config: dict[str, JsonValue]
    timeout_ms: int = Field(ge=100, le=300_000)
    interval_ms: int = Field(ge=100, le=60_000)
    success_threshold: int = Field(default=3, ge=1, le=20)
    failure_threshold: int = Field(default=3, ge=1, le=20)
    authoritative_fidelities: tuple[EvidenceClass, ...]


class FaultOperator(FrozenModel):
    operator_id: str
    implementation_version: str
    family: str
    target_resource_types: tuple[str, ...]
    target_relationship_types: tuple[RelationshipType, ...]
    parameters: tuple[ParameterSpec, ...]
    applicability_predicates: tuple[dict[str, JsonValue], ...]
    preconditions: tuple[StatePredicate, ...]
    fault_oracles: tuple[HealthOracle, ...]
    recovery_oracles: tuple[HealthOracle, ...]
    cleanup_predicates: tuple[StatePredicate, ...]
    coverage_tags: tuple[str, ...]
    fidelity: FidelityRequirement
    risk: RiskLevel
    composable: bool
    incompatible_operator_ids: tuple[str, ...] = ()
    max_instances_per_scenario: int = Field(default=1, ge=1, le=8)
    expected_observables: tuple[str, ...] = ()
    reference_repair_id: str | None = None


class FaultInstance(FrozenModel):
    fault_instance_id: str
    operator_id: str
    operator_version: str
    target_ids: tuple[ResourceId, ...]
    parameters: dict[str, JsonValue]
    seed: int = Field(ge=0, le=2**64 - 1)
    expected_effects: tuple[SemanticCategory, ...]


class Scenario(FrozenModel):
    scenario_id: str
    version: str
    name: str
    objective: Intent
    context: ContextEnvelope
    baseline_predicates: tuple[StatePredicate, ...]
    faults: tuple[FaultInstance, ...]
    goal_oracles: tuple[HealthOracle, ...]
    cleanup_predicates: tuple[StatePredicate, ...]
    trial_timeout_ms: int = Field(default=900_000, ge=10_000, le=3_600_000)
    max_cost_micro_usd: int = Field(default=5_000_000, ge=0)


class ScenarioManifest(FrozenModel):
    schema_version: Literal["1.0"] = "1.0"
    manifest_id: str
    scenario: Scenario
    ir_hash: Sha256
    contract_hash: Sha256
    backend_id: str
    backend_version: str
    backend_capability_hash: Sha256
    certification_id: str
    certification_artifact_hash: Sha256
    certified_at: UtcTime
    expires_at: UtcTime
    content_hash: Sha256
