"""Agentic Senate — core data models."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Track(str, Enum):
    FAST_TRACK = "FAST_TRACK"
    FULL_DELIBERATION = "FULL_DELIBERATION"


class Vote(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    ABSTAIN = "ABSTAIN"


class Verdict(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    ESCALATE = "ESCALATE"  # needs human custodian


@dataclass
class Proposal:
    """A change under review — normally a GitHub PR."""

    number: int
    title: str
    author: str
    body: str
    diff: str
    changed_files: list[str] = field(default_factory=list)
    is_amendment: bool = False  # touches CONSTITUTION.md or protected paths


@dataclass
class SenatorOpinion:
    senator: str
    model: str
    assessment: str
    vote: Vote | None = None
    justification: str = ""


@dataclass
class Deliberation:
    proposal: Proposal
    track: Track
    triage_reasoning: str = ""
    opinions: list[SenatorOpinion] = field(default_factory=list)
    rebuttals: list[SenatorOpinion] = field(default_factory=list)
    verdict: Verdict | None = None
    verdict_reasoning: str = ""
    cost_usd: float = 0.0
