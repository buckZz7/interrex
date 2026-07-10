"""Deliberation engine — runs the constitutional process end to end.

Article IV: fast-track (single reviewer + clerk re-check) or full deliberation
(opinions -> one rebuttal round -> votes -> tally).
Article V: amendments need a 2/3 supermajority; abstentions count against.
"""
from __future__ import annotations

from ..llm import BudgetExceeded, ChatClient
from ..models import Deliberation, Proposal, Track, Verdict, Vote
from ..senators import Senator, render_proposal
from ..triage import triage


def deliberate(
    proposal: Proposal,
    senators: list[Senator],
    constitution: str,
    client: ChatClient,
    cfg: dict,
) -> Deliberation:
    max_tokens = int(cfg["budget"]["max_tokens_per_turn"])
    d = Deliberation(
        proposal=proposal, track=Track.FULL_DELIBERATION, triage_reasoning=""
    )

    try:
        track, reasoning = triage(
            proposal,
            client,
            model=cfg["triage"]["model"],
            always_deliberate_paths=cfg["triage"]["always_deliberate_paths"],
        )
        d.track = track
        d.triage_reasoning = reasoning

        if track == Track.FAST_TRACK:
            _fast_track(d, senators[0], constitution, client, cfg, max_tokens)
        else:
            _full_deliberation(d, senators, constitution, client, cfg, max_tokens)
    except BudgetExceeded as exc:
        # Running out of budget is never silent approval (Article II §2 Safety).
        d.verdict = Verdict.ESCALATE
        d.verdict_reasoning = f"Budget exceeded mid-deliberation: {exc}"

    d.cost_usd = client.spent_usd
    return d


def _fast_track(
    d: Deliberation,
    reviewer: Senator,
    constitution: str,
    client: ChatClient,
    cfg: dict,
    max_tokens: int,
) -> None:
    opinion = reviewer.vote(
        transcript=render_proposal(d.proposal),
        constitution=constitution,
        client=client,
        max_tokens=max_tokens,
    )
    d.opinions.append(opinion)
    if opinion.vote == Vote.APPROVE:
        # Clerk re-check: cheap second look; any doubt escalates (Article IV §1).
        recheck = client.chat(
            model=cfg["triage"]["model"],
            system=(
                "You are the Triage Clerk re-checking a fast-tracked approval. "
                "Reply CONFIRM if the change is genuinely trivial and safe, "
                "or ESCALATE if it deserves full deliberation."
            ),
            user=render_proposal(d.proposal),
            max_tokens=40,
        )
        if "CONFIRM" in recheck.upper():
            d.verdict = Verdict.APPROVE
            d.verdict_reasoning = "Fast-track approval confirmed by clerk re-check."
        else:
            d.verdict = Verdict.ESCALATE
            d.verdict_reasoning = "Clerk re-check raised doubt; escalate to full senate."
    elif opinion.vote == Vote.REJECT:
        d.verdict = Verdict.REJECT
        d.verdict_reasoning = f"Fast-track rejection by {opinion.senator}."
    else:
        d.verdict = Verdict.ESCALATE
        d.verdict_reasoning = "Fast-track reviewer abstained; escalate."


def _full_deliberation(
    d: Deliberation,
    senators: list[Senator],
    constitution: str,
    client: ChatClient,
    cfg: dict,
    max_tokens: int,
) -> None:
    p = d.proposal

    # Round 1: opening assessments
    for s in senators:
        d.opinions.append(s.opine(p, constitution, client, max_tokens))

    # Round 2: one rebuttal round (Article IV §2)
    for s in senators:
        others = [o for o in d.opinions if o.senator != s.name]
        d.rebuttals.append(s.rebut(others, constitution, client, max_tokens))

    # Round 3: votes
    transcript = _transcript(d)
    votes = [
        s.vote(transcript, constitution, client, max_tokens) for s in senators
    ]
    d.opinions.extend(votes)

    approve = sum(1 for v in votes if v.vote == Vote.APPROVE)
    reject = sum(1 for v in votes if v.vote == Vote.REJECT)
    total = len(senators)

    if p.is_amendment:
        threshold = float(cfg["amendment"]["supermajority"])
        passed = (approve / total) >= threshold  # abstentions count against
        d.verdict = Verdict.APPROVE if passed else Verdict.REJECT
        d.verdict_reasoning = (
            f"Amendment vote {approve}/{total} "
            f"({'meets' if passed else 'fails'} {threshold:.0%} supermajority; "
            f"abstentions count against). Custodian approval still required "
            f"during bootstrap (Article VI)."
        )
        if passed and cfg["amendment"]["custodian_approval_required"]:
            d.verdict = Verdict.ESCALATE
            d.verdict_reasoning += " ESCALATED to Custodian."
    else:
        non_abstain = approve + reject
        if non_abstain == 0:
            d.verdict = Verdict.ESCALATE
            d.verdict_reasoning = "All senators abstained; no quorum of opinion."
        else:
            passed = approve > reject
            d.verdict = Verdict.APPROVE if passed else Verdict.REJECT
            d.verdict_reasoning = (
                f"Ordinary vote: {approve} approve / {reject} reject / "
                f"{total - non_abstain} abstain."
            )


def _transcript(d: Deliberation) -> str:
    parts = [render_proposal(d.proposal), "\n=== OPENING ASSESSMENTS ==="]
    for o in d.opinions:
        parts.append(f"\n[{o.senator}]\n{o.assessment}")
    parts.append("\n=== REBUTTALS ===")
    for o in d.rebuttals:
        parts.append(f"\n[{o.senator}]\n{o.assessment}")
    return "\n".join(parts)
