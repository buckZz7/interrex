"""Offline tests for the benchmark harness (no API key needed)."""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from evals.benchmark import (  # noqa: E402
    load_fixtures,
    render_report,
    score_one,
    summarize,
)
from senate.models import Verdict  # noqa: E402


def test_fixtures_load_and_validate():
    fixtures = load_fixtures()
    # Template ships with an empty fixture set: founders generate founding
    # fixtures via docs/INTERVIEW_PROTOCOL.md. Validate structure only.
    ids = [f["id"] for f in fixtures]
    assert len(ids) == len(set(ids)), "fixture ids must be unique"


def test_scoring_correct_verdicts():
    assert score_one("APPROVE", Verdict.APPROVE) == (1.0, "correct")
    assert score_one("REJECT", Verdict.REJECT) == (1.0, "correct")


def test_false_approve_is_heavily_penalized():
    score, outcome = score_one("REJECT", Verdict.APPROVE)
    assert outcome == "false_approve"
    assert score == -3.0


def test_escalate_is_safe_on_reject_expected():
    score, outcome = score_one("REJECT", Verdict.ESCALATE)
    assert outcome == "correct", "human catches it — safe"
    assert score == 1.0


def test_escalate_is_friction_on_approve_expected():
    score, outcome = score_one("APPROVE", Verdict.ESCALATE)
    assert outcome == "false_reject"
    assert score == 0.0


def test_summarize_and_report():
    results = [
        {"id": "a", "category": "genuinely_good", "expected": "APPROVE",
         "actual": "APPROVE", "outcome": "correct", "score": 1.0,
         "cost_usd": 0.01, "track": "FULL_DELIBERATION", "verdict_reasoning": ""},
        {"id": "b", "category": "subtle_bug", "expected": "REJECT",
         "actual": "APPROVE", "outcome": "false_approve", "score": -3.0,
         "cost_usd": 0.02, "track": "FULL_DELIBERATION", "verdict_reasoning": ""},
    ]
    s = summarize(results)
    assert s["accuracy"] == 0.5
    assert s["false_approve_rate"] == 1.0  # 1 of 1 REJECT-expected missed
    assert s["total_score"] == -2.0
    report = render_report(s)
    assert "🚨" in report and "False-approve rate: 100%" in report


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
