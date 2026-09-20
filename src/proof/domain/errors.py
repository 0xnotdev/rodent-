"""Typed Proof error model primitives."""

from __future__ import annotations

from enum import StrEnum


class ErrorOwner(StrEnum):
    USER_INPUT = "USER_INPUT"
    TARGET_AGENT = "TARGET_AGENT"
    HARNESS = "HARNESS"
    BACKEND = "BACKEND"


class RetryAction(StrEnum):
    NONE = "NONE"
    RETRY_OPERATION = "RETRY_OPERATION"
    REBUILD_WORLD = "REBUILD_WORLD"
    ABORT_SUITE = "ABORT_SUITE"


class ProofError(Exception):
    code: str
    owner: ErrorOwner
    retry: RetryAction
    invalidates_trial: bool
    counts_as_agent_failure: bool
    safe_message: str
    evidence_refs: tuple[str, ...]

    def __init__(
        self,
        *,
        code: str,
        owner: ErrorOwner,
        retry: RetryAction,
        invalidates_trial: bool,
        counts_as_agent_failure: bool,
        safe_message: str,
        evidence_refs: tuple[str, ...] = (),
    ) -> None:
        super().__init__(safe_message)
        self.code = code
        self.owner = owner
        self.retry = retry
        self.invalidates_trial = invalidates_trial
        self.counts_as_agent_failure = counts_as_agent_failure
        self.safe_message = safe_message
        self.evidence_refs = evidence_refs
