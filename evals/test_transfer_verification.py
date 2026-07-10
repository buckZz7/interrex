"""Offline tests for transfer verification (no API key)."""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from evals.transfer_verification import (  # noqa: E402
    judge,
    load_founding_fixtures,
    render_report,
    run,
    scenario_to_proposal,
)
from senate.models import Verdict  # noqa: E402


class FakeLLM:
    """Scripted client: returns queued replies in order."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.spent_usd = 0.0
        self.max_usd = 10.0

    def chat(self, model, system, user, max_tokens=1200):  # noqa: ANN001
        if not self.replies:
            raise AssertionError("FakeLLM exhausted")
        return self.replies.pop(0)


def test_fixtures_load():
    data = load_founding_fixtures()
    assert data["founder"] == "buckZz7"
    assert len(data["fixtures"]) == 10
    ids = [f["id"] for f in data["fixtures"]]
    assert len(set(ids)) == 10


def test_scenario_becomes_proposal():
    data = load_founding_fixtures()
    p = scenario_to_proposal(data["fixtures"][0], number=90001)
    assert "SCENARIO" in p.title
    assert p.changed_files == []
    assert not p.is_amendment


def test_judge_agreement():
    assert judge("APPROVE", Verdict.APPROVE) == (True, "agree")
    assert judge("REJECT", Verdict.REJECT) == (True, "agree")


def test_judge_escalation_asymmetry():
    ok, label = judge("REJECT", Verdict.ESCALATE)
    assert ok and label == "agree_via_escalation"
    ok, label = judge("APPROVE", Verdict.ESCALATE)
    assert not ok and label == "diverge_escalated_on_approve"


def test_full_run_with_fake_senate():
    """3 senators, full deliberation each fixture: triage + 3 opinions +
    3 rebuttals + 3 votes = 10 replies per fixture."""
    data = load_founding_fixtures()
    two = data["fixtures"][:2]
    data = {**data, "fixtures": two}

    # Fixture 1 (founder APPROVE): senate votes APPROVE -> agree
    # Fixture 2 (founder REJECT): senate votes APPROVE -> diverge
    per_fixture_1 = ["FULL_DELIBERATION: governance scenario"] + \
        ["assessment"] * 3 + ["rebuttal"] * 3 + ["APPROVE\nyes"] * 3
    per_fixture_2 = ["FULL_DELIBERATION: governance scenario"] + \
        ["assessment"] * 3 + ["rebuttal"] * 3 + ["APPROVE\nyes"] * 3

    from senate.senators import Senator
    senators = [Senator(name=n, model="fake", family=f, mandate="m")
                for n, f in (("A", "fa"), ("B", "fb"), ("C", "fc"))]
    cfg = {
        "triage": {"model": "fake", "always_deliberate_paths": []},
        "budget": {"max_tokens_per_turn": 100},
        "amendment": {"supermajority": 0.6667,
                      "custodian_approval_required": True},
    }
    client = FakeLLM(per_fixture_1 + per_fixture_2)
    summary = run(client, senators, "constitution", cfg, data)

    assert summary["n"] == 2
    assert summary["results"][0]["agreement"] is True   # F1: APPROVE/APPROVE
    assert summary["results"][1]["agreement"] is False  # F2: REJECT/APPROVE
    assert summary["agreement_rate"] == 0.5
    report = render_report(summary)
    assert "Divergences" in report and "50%" in report


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
