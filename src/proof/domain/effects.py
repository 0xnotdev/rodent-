"""Effect, action, and causality domain models."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from proof.domain.common import (
    Confidence,
    EvidenceRef,
    FrozenModel,
    JsonValue,
    KnownValue,
    ResourceId,
    Sha256,
    UtcTime,
)


class SemanticCategory(StrEnum):
    NETWORK_EXPOSURE_BROADENED = "NETWORK_EXPOSURE_BROADENED"
    NETWORK_EXPOSURE_RESTRICTED = "NETWORK_EXPOSURE_RESTRICTED"
    PRIVILEGE_EXPANDED = "PRIVILEGE_EXPANDED"
    PRIVILEGE_REDUCED = "PRIVILEGE_REDUCED"
    PUBLIC_ACCESS_ENABLED = "PUBLIC_ACCESS_ENABLED"
    PUBLIC_ACCESS_DISABLED = "PUBLIC_ACCESS_DISABLED"
    ENCRYPTION_DISABLED = "ENCRYPTION_DISABLED"
    ENCRYPTION_ENABLED = "ENCRYPTION_ENABLED"
    PROTECTION_DISABLED = "PROTECTION_DISABLED"
    PROTECTION_ENABLED = "PROTECTION_ENABLED"
    STATEFUL_RESOURCE_DELETED = "STATEFUL_RESOURCE_DELETED"
    STATEFUL_RESOURCE_REPLACED = "STATEFUL_RESOURCE_REPLACED"
    OUT_OF_SCOPE_RESOURCE_MUTATED = "OUT_OF_SCOPE_RESOURCE_MUTATED"
    DEPENDENCY_BROKEN = "DEPENDENCY_BROKEN"
    DEPENDENCY_RESTORED = "DEPENDENCY_RESTORED"
    CAPACITY_REDUCED = "CAPACITY_REDUCED"
    CAPACITY_EXPANDED = "CAPACITY_EXPANDED"
    TRIGGER_CREATED = "TRIGGER_CREATED"
    TRIGGER_REMOVED = "TRIGGER_REMOVED"
    CONFIGURATION_CHANGED = "CONFIGURATION_CHANGED"
    UNKNOWN_CHANGE = "UNKNOWN_CHANGE"


class RiskLevel(StrEnum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Effect(FrozenModel):
    effect_id: str
    category: SemanticCategory
    resource_id: ResourceId
    property_path: str | None
    before: KnownValue
    after: KnownValue
    risk: RiskLevel
    reversible: bool | None
    direct_action_ids: tuple[str, ...]
    evidence: tuple[EvidenceRef, ...]
    confidence: Confidence


class MutationEvent(FrozenModel):
    mutation_event_id: str
    fault_instance_id: str
    started_at: UtcTime
    ended_at: UtcTime
    target_ids: tuple[ResourceId, ...]
    requested_parameters: dict[str, JsonValue]
    observed_effects: tuple[Effect, ...]
    success: bool
    evidence: tuple[EvidenceRef, ...]


class ActionEvent(FrozenModel):
    action_id: str
    actor: Literal[
        "ORCHESTRATOR", "FAULT_INJECTOR", "TARGET_AGENT", "REFERENCE_AGENT", "AWS_SERVICE"
    ]
    kind: Literal["PROCESS", "AWS_API", "TERRAFORM", "GIT", "NETWORK", "FILESYSTEM", "HEALTH_CHECK"]
    operation: str
    target: str | None
    request_hash: Sha256 | None
    response_hash: Sha256 | None
    started_at: UtcTime
    ended_at: UtcTime | None
    status: Literal["STARTED", "SUCCEEDED", "FAILED", "DENIED", "TIMED_OUT"]
    exit_code: int | None = None
    aws_request_id: str | None = None
    evidence: tuple[EvidenceRef, ...] = ()


class CausalLink(FrozenModel):
    cause_event_id: str
    effect_event_id: str
    mechanism: Literal[
        "REQUEST_ID",
        "PROCESS_PARENT",
        "DECLARED_TRIGGER",
        "RESOURCE_VERSION",
        "TEMPORAL_INFERENCE",
    ]
    confidence: Confidence
    evidence: tuple[EvidenceRef, ...]


class RequestedAction(FrozenModel):
    requested_action_id: str
    actor: str
    description: str
    requested_at: UtcTime
    source_event_id: str | None = None
    provenance: tuple[EvidenceRef, ...] = ()


class ObservedAction(FrozenModel):
    observed_action_id: str
    action: ActionEvent
    requested_action_ids: tuple[str, ...] = ()
    observer_id: str
    confidence: Confidence


class DerivedEffect(FrozenModel):
    derived_effect_id: str
    effect: Effect
    causal_links: tuple[CausalLink, ...]
    derivation_rule_id: str
    derivation_version: str
