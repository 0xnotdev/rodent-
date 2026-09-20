"""Context, intent, policy, and contract domain models."""

from __future__ import annotations

from enum import StrEnum
from typing import Generic, Literal, TypeVar

from pydantic import Field

from proof.domain.common import (
    Confidence,
    EvidenceRef,
    FrozenModel,
    JsonValue,
    ResourceId,
    Sha256,
    StabilizationPolicy,
    UtcTime,
)
from proof.domain.effects import SemanticCategory
from proof.domain.ir import RelationshipType, ResourceCriticality

T = TypeVar("T")


class Assertion(FrozenModel, Generic[T]):
    value: T
    provenance: tuple[EvidenceRef, ...]
    confidence: Confidence
    asserted_by: str


class ScopeSelector(FrozenModel):
    canonical_ids: tuple[ResourceId, ...] = ()
    terraform_addresses: tuple[str, ...] = ()
    canonical_types: tuple[str, ...] = ()
    tag_equals: dict[str, str] = Field(default_factory=dict)
    relationship_closure: tuple[RelationshipType, ...] = ()
    max_depth: int = Field(default=0, ge=0, le=8)


class PredicateOperator(StrEnum):
    EQ = "EQ"
    NE = "NE"
    IN = "IN"
    NOT_IN = "NOT_IN"
    LTE = "LTE"
    GTE = "GTE"
    MATCHES = "MATCHES"
    EXISTS = "EXISTS"
    REACHABLE = "REACHABLE"
    HEALTHY = "HEALTHY"


class StatePredicate(FrozenModel):
    predicate_id: str
    selector: ScopeSelector
    property_path: str | None = None
    operator: PredicateOperator
    expected: JsonValue = None
    oracle_id: str | None = None
    stabilization: StabilizationPolicy


class Intent(FrozenModel):
    objective: Assertion[str]
    task_description: Assertion[str]
    target_scope: Assertion[ScopeSelector]
    change_type: Assertion[str]
    emergency: Assertion[bool]
    success_predicates: tuple[StatePredicate, ...]


class Approval(FrozenModel):
    approval_id: str
    approver: str
    authority: tuple[str, ...]
    approved_at: UtcTime
    valid_from: UtcTime
    expires_at: UtcTime
    scope: ScopeSelector
    effect_categories: tuple[SemanticCategory, ...]
    signature_or_record_hash: Sha256
    provenance: EvidenceRef


class TemporaryException(FrozenModel):
    exception_id: str
    invariant_ids: tuple[str, ...]
    scope: ScopeSelector
    allowed_effects: tuple[SemanticCategory, ...]
    valid_from: UtcTime
    expires_at: UtcTime
    cleanup_deadline: UtcTime
    cleanup_predicates: tuple[StatePredicate, ...]
    approval_ids: tuple[str, ...]
    reason: str
    provenance: tuple[EvidenceRef, ...]


class PolicyReference(FrozenModel):
    policy_id: str
    version: str
    bundle_hash: Sha256
    entrypoint: str
    priority: int = Field(ge=0, le=1000)
    non_overridable: bool
    source_uri: str


class Constraint(FrozenModel):
    constraint_id: str
    text: str
    hard: bool
    scope: ScopeSelector
    provenance: tuple[EvidenceRef, ...]
    confidence: Confidence


class ContextEnvelope(FrozenModel):
    schema_version: Literal["1.0"] = "1.0"
    context_id: str
    intent: Intent
    authorized_scope: Assertion[ScopeSelector]
    protected_scope: Assertion[ScopeSelector]
    allowed_effects: Assertion[tuple[SemanticCategory, ...]]
    forbidden_effects: Assertion[tuple[SemanticCategory, ...]]
    hard_constraints: tuple[Constraint, ...]
    soft_constraints: tuple[Constraint, ...]
    organization_policies: tuple[PolicyReference, ...]
    environment_class: Assertion[Literal["DEV", "TEST", "STAGING", "PROD_LIKE"]]
    environment_criticality: Assertion[ResourceCriticality]
    approvals: tuple[Approval, ...] = ()
    temporary_exceptions: tuple[TemporaryException, ...] = ()
    cleanup_requirements: tuple[StatePredicate, ...] = ()
    incident_reference: Assertion[str | None]
    valid_from: UtcTime
    expires_at: UtcTime
    content_hash: Sha256


class InvariantKind(StrEnum):
    STATE = "STATE"
    TRAJECTORY = "TRAJECTORY"
    SCOPE = "SCOPE"
    POLICY = "POLICY"
    TEMPORAL = "TEMPORAL"
    COST = "COST"


class Invariant(FrozenModel):
    invariant_id: str
    kind: InvariantKind
    description: str
    expression: dict[str, JsonValue]
    hard: bool
    non_overridable: bool
    scope: ScopeSelector
    active_from: UtcTime
    active_until: UtcTime
    source_priority: int
    provenance: tuple[EvidenceRef, ...]
    confidence: Confidence


class SafetyContract(FrozenModel):
    schema_version: Literal["1.0"] = "1.0"
    contract_id: str
    context_hash: Sha256
    ir_hash: Sha256
    policy_bundle_hashes: tuple[Sha256, ...]
    invariants: tuple[Invariant, ...]
    valid_exceptions: tuple[TemporaryException, ...]
    rejected_exceptions: tuple[dict[str, JsonValue], ...]
    conflicts: tuple[dict[str, JsonValue], ...]
    compilable: bool
    content_hash: Sha256
