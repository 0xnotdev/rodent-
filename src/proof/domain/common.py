"""Common strict domain primitives and canonical serialization helpers."""

from __future__ import annotations

import hashlib
import math
import re
import secrets
import time
import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Any, TypeVar

import rfc8785
from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    PlainSerializer,
    WithJsonSchema,
    model_validator,
)

_JSON_VALUE_SCHEMA = {
    "anyOf": [
        {"type": "null"},
        {"type": "boolean"},
        {"type": "integer"},
        {"type": "number"},
        {"type": "string"},
        {"type": "array", "items": {}},
        {"type": "object", "additionalProperties": {}},
    ]
}
type Sha256 = Annotated[str, Field(pattern="^sha256:[0-9a-f]{64}$")]
type ResourceId = Annotated[str, Field(min_length=1, max_length=1024)]

UUIDV7_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
UUIDV7_PATTERN_TEXT = UUIDV7_PATTERN.pattern
type Uuid7 = Annotated[str, Field(pattern=UUIDV7_PATTERN_TEXT)]
UTC_RFC3339_MICRO_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$")
UTC_RFC3339_MICRO_PATTERN_TEXT = UTC_RFC3339_MICRO_PATTERN.pattern
T = TypeVar("T")


def uuid7() -> str:
    """Return a lowercase RFC 9562 UUIDv7 string."""
    timestamp_ms = (time.time_ns() // 1_000_000) & ((1 << 48) - 1)
    rand_a = secrets.randbits(12)
    rand_b = secrets.randbits(62)
    value = timestamp_ms << 80
    value |= 0x7 << 76
    value |= rand_a << 64
    value |= 0b10 << 62
    value |= rand_b
    return str(uuid.UUID(int=value))


def is_uuid7(value: str) -> bool:
    """Return whether *value* is a lowercase textual UUIDv7."""
    return UUIDV7_PATTERN.fullmatch(value) is not None


def _parse_utc_time(value: Any) -> Any:
    if isinstance(value, str):
        if UTC_RFC3339_MICRO_PATTERN.fullmatch(value) is None:
            raise ValueError("times must be UTC RFC 3339 with microseconds and Z")
        return datetime.fromisoformat(value[:-1] + "+00:00")
    return value


def _validate_utc_time(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value):
        raise ValueError("times must be timezone-aware UTC")
    return value.astimezone(UTC)


def _serialize_utc_time(value: datetime) -> str:
    utc_value = _validate_utc_time(value)
    return utc_value.isoformat(timespec="microseconds").replace("+00:00", "Z")


type UtcTime = Annotated[
    datetime,
    BeforeValidator(_parse_utc_time),
    PlainSerializer(_serialize_utc_time, return_type=str, when_used="json"),
    AfterValidator(_validate_utc_time),
    WithJsonSchema(
        {"type": "string", "format": "date-time", "pattern": UTC_RFC3339_MICRO_PATTERN_TEXT}
    ),
]


def validate_json_value(value: Any) -> Any:
    """Validate recursively that *value* is JSON-compatible and finite."""
    if value is None or isinstance(value, bool | str):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("JSON floats may not contain NaN or Infinity")
        return value
    if isinstance(value, list):
        return [validate_json_value(item) for item in value]
    if isinstance(value, dict):
        invalid_keys = [key for key in value if not isinstance(key, str)]
        if invalid_keys:
            raise ValueError("JSON object keys must be strings")
        return {key: validate_json_value(item) for key, item in value.items()}
    raise ValueError(f"unsupported JSON value type: {type(value).__name__}")


type JsonValue = Annotated[
    Any, AfterValidator(validate_json_value), WithJsonSchema(_JSON_VALUE_SCHEMA)
]


class FrozenModel(BaseModel):
    """Base class for strict, immutable authoritative domain models."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        frozen=True,
        allow_inf_nan=False,
        arbitrary_types_allowed=False,
    )


class Confidence(StrEnum):
    CERTAIN = "CERTAIN"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class EvidenceClass(StrEnum):
    MODELLED = "MODELLED"
    EMULATED = "EMULATED"
    REAL_AWS = "REAL_AWS"


class ProvenanceKind(StrEnum):
    EXPLICIT_SCENARIO = "EXPLICIT_SCENARIO"
    ORG_POLICY = "ORG_POLICY"
    TERRAFORM_PLAN = "TERRAFORM_PLAN"
    TERRAFORM_SCHEMA = "TERRAFORM_SCHEMA"
    LIVE_API = "LIVE_API"
    CLOUDTRAIL = "CLOUDTRAIL"
    AWS_CONFIG = "AWS_CONFIG"
    CHANGE_TICKET = "CHANGE_TICKET"
    HUMAN_APPROVAL = "HUMAN_APPROVAL"
    INCIDENT_RECORD = "INCIDENT_RECORD"
    LLM_INFERENCE = "LLM_INFERENCE"
    HEURISTIC = "HEURISTIC"
    REFERENCE_REPAIR = "REFERENCE_REPAIR"


class Evidence(FrozenModel):
    evidence_id: str
    kind: ProvenanceKind
    artifact_hash: Sha256
    json_pointer: str = ""
    observed_at: UtcTime
    collector: str
    collector_version: str
    confidence: Confidence
    redacted: bool = False
    summary: str = Field(min_length=1, max_length=2048)


EvidenceRef = Evidence


class KnownValue(FrozenModel):
    known: bool
    value: JsonValue = None
    sensitive: bool = False
    value_hash: Sha256 | None = None
    evidence: tuple[EvidenceRef, ...] = ()

    @model_validator(mode="after")
    def consistency(self) -> KnownValue:
        if self.value is not None:
            validated_value = validate_json_value(self.value)
            if validated_value != self.value:
                object.__setattr__(self, "value", validated_value)
        if not self.known and self.value is not None:
            raise ValueError("unknown values cannot carry plaintext")
        if self.sensitive and self.value is not None:
            raise ValueError("sensitive values retain only a hash")
        return self


class StatePlane(StrEnum):
    DECLARED = "DECLARED"
    ACTUAL = "ACTUAL"
    HISTORICAL = "HISTORICAL"
    INTENDED = "INTENDED"


class StabilizationPolicy(FrozenModel):
    deadline_ms: int = Field(default=120_000, ge=1000, le=1_800_000)
    initial_delay_ms: int = Field(default=500, ge=0, le=60_000)
    backoff_multiplier: float = Field(default=1.7, ge=1.0, le=4.0)
    max_delay_ms: int = Field(default=10_000, ge=100, le=120_000)
    consecutive_equal_snapshots: int = Field(default=3, ge=1, le=10)
    jitter_fraction: float = Field(default=0.1, ge=0.0, le=0.5)


def _json_ready(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json", by_alias=False, exclude_none=False)
    if isinstance(value, datetime):
        return _serialize_utc_time(value)
    if isinstance(value, StrEnum):
        return str(value)
    if isinstance(value, tuple | list):
        return [_json_ready(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    return value


def _strip_content_hash(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): _strip_content_hash(item)
            for key, item in value.items()
            if str(key) != "content_hash"
        }
    if isinstance(value, list):
        return [_strip_content_hash(item) for item in value]
    return value


def canonical_bytes(model: BaseModel | Any) -> bytes:
    """Return RFC 8785 canonical JSON bytes used for Proof content hashes."""
    json_ready = _strip_content_hash(_json_ready(model))
    validate_json_value(json_ready)
    return rfc8785.dumps(json_ready)


def content_hash(model: BaseModel | Any) -> Sha256:
    """Return ``sha256:<hex>`` over ``canonical_bytes(model)``."""
    return f"sha256:{hashlib.sha256(canonical_bytes(model)).hexdigest()}"
