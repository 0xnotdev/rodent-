"""Infrastructure IR domain models."""

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
    KnownValue,
    ResourceId,
    Sha256,
    StatePlane,
    UtcTime,
)


class ResourceIdentity(FrozenModel):
    canonical_id: ResourceId
    terraform_address: str | None = None
    provider_address: str | None = None
    arn: str | None = None
    account_id: str | None = Field(default=None, pattern=r"^[0-9]{12}$")
    region: str | None = None
    native_id: str | None = None


class ResourceProperty(FrozenModel):
    path: str
    plane: StatePlane
    value: KnownValue
    normalized_type: str
    observed_at: UtcTime | None = None


class ResourceCriticality(StrEnum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class Resource(FrozenModel):
    identity: ResourceIdentity
    canonical_type: str
    provider_type: str
    properties: tuple[ResourceProperty, ...]
    sensitive_paths: tuple[str, ...] = ()
    criticality: ResourceCriticality = ResourceCriticality.UNKNOWN
    ownership: tuple[str, ...] = ()
    tags: dict[str, str] = Field(default_factory=dict)
    lifecycle: dict[str, JsonValue] = Field(default_factory=dict)
    provider_metadata: dict[str, JsonValue] = Field(default_factory=dict)
    environment_metadata: dict[str, JsonValue] = Field(default_factory=dict)
    evidence: tuple[EvidenceRef, ...] = ()


class RelationshipType(StrEnum):
    NETWORK = "NETWORK_DEPENDENCY"
    IDENTITY = "IDENTITY_DEPENDENCY"
    STORAGE = "STORAGE_DEPENDENCY"
    ROUTING = "ROUTING_DEPENDENCY"
    SECRET = "SECRET_DEPENDENCY"
    DEPLOYMENT = "DEPLOYMENT_DEPENDENCY"
    CONFIGURATION = "CONFIGURATION_DEPENDENCY"
    TRIGGER = "TRIGGER_DEPENDENCY"
    OBSERVABILITY = "OBSERVABILITY_DEPENDENCY"
    ATTACHMENT = "ATTACHMENT"
    CONTAINS = "CONTAINS"


class Relationship(FrozenModel):
    edge_id: str
    source: ResourceId
    target: ResourceId
    relationship_type: RelationshipType
    directed: bool = True
    attributes: dict[str, JsonValue] = Field(default_factory=dict)
    evidence: tuple[EvidenceRef, ...]
    confidence: Confidence


class InfrastructureIR(FrozenModel):
    schema_version: Literal["1.0"] = "1.0"
    ir_id: str
    generated_at: UtcTime
    terraform_version: str
    provider_versions: dict[str, str]
    source_hash: Sha256
    resources: tuple[Resource, ...]
    relationships: tuple[Relationship, ...]
    unsupported: tuple[dict[str, JsonValue], ...] = ()
    warnings: tuple[str, ...] = ()
    content_hash: Sha256


class CanonicalResourceState(FrozenModel):
    identity: ResourceIdentity
    canonical_type: str
    attributes: dict[str, KnownValue]
    status: str | None = None
    observed_at: UtcTime
    evidence: tuple[EvidenceRef, ...]


class StateSnapshot(FrozenModel):
    snapshot_id: str
    world_id: str
    plane: StatePlane
    taken_at: UtcTime
    consistency_attempt: int = Field(ge=1)
    complete: bool
    resources: tuple[CanonicalResourceState, ...]
    missing_capabilities: tuple[str, ...] = ()
    content_hash: Sha256


class WorldState(FrozenModel):
    world_id: str
    fidelity: EvidenceClass
    backend_id: str
    backend_version: str
    capability_hash: Sha256
    snapshot: StateSnapshot
