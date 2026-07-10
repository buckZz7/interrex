"""Offline tests for the Senate's constitutional process.

These run without any API key: a FakeLLM plays every model. They verify the
*procedure* (triage law, vote tallies, supermajority math, budget behavior),
which is exactly what the Constitution constrains.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from senate.deliberation import deliberate  # noqa: E402
from senate.llm import BudgetExceeded  # noqa: E402
from senate.models import Proposal, Track, Verdict, Vote  # noqa: E402
from senate.senators import Senator, parse_vote  # noqa: E402
from senate.triage import triage  # noqa: E402


class FakeLLM:
    """Scripted stand-in for LLMClient. Returns queued replies in order."""

    def __init__(self, replies: list[str]):
        self.replies = list(replies)
        self.spent_usd = 0.0
        self.max_usd = 1.0

    def chat(self, model, system, user, max_tokens=1200):  # noqa: ANN001
        if not self.replies:
            raise AssertionError("FakeLLM ran out of scripted replies")
        return self.replies.pop(0)


CFG = {
    "triage": {
        "model": "fake",
        "always_deliberate_paths": ["CONSTITUTION.md", ".github/workflows/*"],
    },
    "budget": {"max_tokens_per_turn": 100},
    "amendment": {"supermajority": 0.6667, "custodian_approval_required": True},
}

SENATORS = [
    Senator(name="A", model="fake-a", family="fa", mandate="m"),
    Senator(name="B", model="fake-b", family="fb", mandate="m"),
    Senator(name="C", model="fake-c", family="fc", mandate="m"),
]


def make_proposal(files: list[str], amendment: bool = False) -> Proposal:
    return Proposal(
        number=1, title="t", author="miner", body="b", diff="d",
        changed_files=files, is_amendment=amendment,
    )


def test_protected_path_forces_deliberation():
    p = make_proposal([".github/workflows/senate-review.yml"])
    track, why = triage(p, FakeLLM(["FAST_TRACK: looks trivial"]), "fake",
                        CFG["triage"]["always_deliberate_paths"])
    assert track == Track.FULL_DELIBERATION, "protected path must override the clerk"
    assert "Protected path" in why


def test_amendment_forces_deliberation():
    p = make_proposal(["CONSTITUTION.md"], amendment=True)
    track, _ = triage(p, FakeLLM([]), "fake", [])
    assert track == Track.FULL_DELIBERATION


def test_clerk_defaults_to_deliberation_on_garbage():
    p = make_proposal(["README.md"])
    track, _ = triage(p, FakeLLM(["banana"]), "fake", [])
    assert track == Track.FULL_DELIBERATION


def test_parse_vote_malformed_is_abstain():
    vote, _ = parse_vote("I think probably yes?")
    assert vote == Vote.ABSTAIN


def test_ordinary_majority_approves():
    # triage -> 3 opinions -> 3 rebuttals -> 3 votes
    replies = ["FULL_DELIBERATION: logic change"] + ["assessment"] * 3 + \
        ["rebuttal"] * 3 + ["APPROVE\nyes", "APPROVE\nyes", "REJECT\nno"]
    d = deliberate(make_proposal(["senate/models.py"]), SENATORS,
                   "constitution text", FakeLLM(replies), CFG)
    assert d.verdict == Verdict.APPROVE
    assert "2 approve / 1 reject" in d.verdict_reasoning


def test_amendment_two_thirds_with_abstention_fails():
    # 2/3 approve but one ABSTAIN counts against: 2/3 = 66.66% < 66.67 threshold
    replies = ["assessment"] * 3 + ["rebuttal"] * 3 + \
        ["APPROVE\nyes", "APPROVE\nyes", "ABSTAIN\nunsure"]
    d = deliberate(make_proposal(["CONSTITUTION.md"], amendment=True), SENATORS,
                   "constitution text", FakeLLM(replies), CFG)
    assert d.verdict == Verdict.REJECT


def test_amendment_unanimous_escalates_to_custodian():
    replies = ["assessment"] * 3 + ["rebuttal"] * 3 + ["APPROVE\nyes"] * 3
    d = deliberate(make_proposal(["CONSTITUTION.md"], amendment=True), SENATORS,
                   "constitution text", FakeLLM(replies), CFG)
    assert d.verdict == Verdict.ESCALATE  # custodian approval required in Phase 0
    assert "Custodian" in d.verdict_reasoning


def test_budget_exhaustion_escalates_not_approves():
    class BrokeLLM(FakeLLM):
        def chat(self, *a, **k):  # noqa: ANN002, ANN003
            raise BudgetExceeded("out of funds")

    d = deliberate(make_proposal(["senate/models.py"]), SENATORS,
                   "constitution text", BrokeLLM([]), CFG)
    assert d.verdict == Verdict.ESCALATE


def test_fast_track_approval_needs_clerk_confirm():
    replies = [
        "FAST_TRACK: typo fix",   # triage
        "APPROVE\nfine",          # single reviewer
        "ESCALATE",               # clerk re-check refuses
    ]
    d = deliberate(make_proposal(["README.md"]), SENATORS,
                   "constitution text", FakeLLM(replies), CFG)
    assert d.track == Track.FAST_TRACK
    assert d.verdict == Verdict.ESCALATE


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {fn.__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
