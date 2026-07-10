"""Triage Clerk — decides FAST_TRACK vs FULL_DELIBERATION.

Constitutional basis: Article II §6 (Economy), Article III §3, Article V §2
(amendments always deliberate). Protected paths force full deliberation no
matter what the clerk thinks — the model is advisory, the path rules are law.
"""
from __future__ import annotations

import fnmatch

from ..llm import ChatClient
from ..models import Proposal, Track

TRIAGE_SYSTEM = """You are the Triage Clerk of an agentic senate governing a \
code repository under a written constitution. Classify the proposal as \
FAST_TRACK (trivial, low-risk: typo fixes, comment/doc tweaks, small isolated \
changes with tests) or FULL_DELIBERATION (anything touching logic, security, \
incentives, CI, dependencies, or anything you are unsure about).
When in doubt, choose FULL_DELIBERATION.
Reply with exactly one line: FAST_TRACK or FULL_DELIBERATION, then a colon, \
then one sentence of reasoning."""


def triage(
    proposal: Proposal,
    client: ChatClient,
    model: str,
    always_deliberate_paths: list[str],
) -> tuple[Track, str]:
    # Law before advice: protected paths and amendments always deliberate.
    if proposal.is_amendment:
        return Track.FULL_DELIBERATION, "Constitutional amendment (Article V §2)."
    for path in proposal.changed_files:
        for pattern in always_deliberate_paths:
            if fnmatch.fnmatch(path, pattern):
                return (
                    Track.FULL_DELIBERATION,
                    f"Protected path touched: {path} (matches {pattern}).",
                )

    reply = client.chat(
        model=model,
        system=TRIAGE_SYSTEM,
        user=_render(proposal),
        max_tokens=120,
    )
    head = reply.strip().split(":", 1)
    label = head[0].strip().upper()
    reasoning = head[1].strip() if len(head) > 1 else ""
    if label == "FAST_TRACK":
        return Track.FAST_TRACK, reasoning
    return Track.FULL_DELIBERATION, reasoning or "Clerk defaulted to deliberation."


def _render(p: Proposal) -> str:
    return (
        f"PR #{p.number}: {p.title}\nAuthor: {p.author}\n"
        f"Files: {', '.join(p.changed_files)}\n\n{p.body}\n\n"
        f"--- DIFF (truncated to 8000 chars) ---\n{p.diff[:8000]}"
    )
