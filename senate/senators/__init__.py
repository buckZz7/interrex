"""Senators — persona construction and opinion/vote elicitation."""
from __future__ import annotations

import re
from dataclasses import dataclass

from ..llm import ChatClient
from ..models import Proposal, SenatorOpinion, Vote

SENATOR_SYSTEM = """You are Senator {name} of the Agentic Senate, an autonomous \
body governing a code repository under a written constitution.

Your mandate: {mandate}

You must evaluate proposals against, in order:
1. The Constitution (provided below)
2. Sound engineering judgment
3. The evidence in the diff itself — never trust the PR description over the code

Be honest (Article II §3): state your true assessment even if it is unpopular.
Be specific: cite files, lines, and constitutional articles.

--- CONSTITUTION ---
{constitution}
--- END CONSTITUTION ---"""

OPINION_PROMPT = """Deliberation on the following proposal. Give your opening \
assessment in under 250 words. Identify the strongest reason to approve and the \
strongest reason to reject before stating your leaning.

{proposal}"""

REBUTTAL_PROMPT = """You previously assessed this proposal. Your fellow senators \
said the following. In under 150 words, respond: what did they see that you \
missed, or where are they wrong?

--- FELLOW OPINIONS ---
{opinions}
--- END ---"""

VOTE_PROMPT = """Cast your final vote on the proposal. First line must be exactly \
one of: APPROVE, REJECT, ABSTAIN. Then give your justification in under 100 words.

Reminder of the full deliberation so far:
{transcript}"""


@dataclass
class Senator:
    name: str
    model: str
    family: str
    mandate: str

    def _system(self, constitution: str) -> str:
        return SENATOR_SYSTEM.format(
            name=self.name, mandate=self.mandate, constitution=constitution
        )

    def opine(
        self, proposal: Proposal, constitution: str, client: ChatClient, max_tokens: int
    ) -> SenatorOpinion:
        text = client.chat(
            model=self.model,
            system=self._system(constitution),
            user=OPINION_PROMPT.format(proposal=render_proposal(proposal)),
            max_tokens=max_tokens,
        )
        return SenatorOpinion(senator=self.name, model=self.model, assessment=text)

    def rebut(
        self,
        others: list[SenatorOpinion],
        constitution: str,
        client: ChatClient,
        max_tokens: int,
    ) -> SenatorOpinion:
        rendered = "\n\n".join(f"[{o.senator}]\n{o.assessment}" for o in others)
        text = client.chat(
            model=self.model,
            system=self._system(constitution),
            user=REBUTTAL_PROMPT.format(opinions=rendered),
            max_tokens=max_tokens,
        )
        return SenatorOpinion(senator=self.name, model=self.model, assessment=text)

    def vote(
        self, transcript: str, constitution: str, client: ChatClient, max_tokens: int
    ) -> SenatorOpinion:
        text = client.chat(
            model=self.model,
            system=self._system(constitution),
            user=VOTE_PROMPT.format(transcript=transcript),
            max_tokens=max_tokens,
        )
        vote, justification = parse_vote(text)
        return SenatorOpinion(
            senator=self.name,
            model=self.model,
            assessment=text,
            vote=vote,
            justification=justification,
        )


def parse_vote(text: str) -> tuple[Vote, str]:
    """Extract the vote from the first line; malformed ballots count as ABSTAIN."""
    lines = text.strip().splitlines()
    first = lines[0].strip().upper() if lines else ""
    first = re.sub(r"[^A-Z]", "", first)
    rest = "\n".join(lines[1:]).strip()
    for v in (Vote.APPROVE, Vote.REJECT, Vote.ABSTAIN):
        if first == v.value:
            return v, rest
    return Vote.ABSTAIN, f"(malformed ballot treated as abstention)\n{text.strip()}"


def render_proposal(p: Proposal) -> str:
    kind = "CONSTITUTIONAL AMENDMENT" if p.is_amendment else "ordinary proposal"
    return (
        f"[{kind}] PR #{p.number}: {p.title}\nAuthor: {p.author}\n"
        f"Files changed: {', '.join(p.changed_files)}\n\n"
        f"Description:\n{p.body}\n\n--- DIFF (truncated) ---\n{p.diff[:16000]}"
    )
