# The Constitution of [PROJECT NAME]

> Version 0.1.0 — Founding Draft
> This document is the supreme governing intent of this repository. All code,
> deliberation, and merges in this repository exist to serve it. Changes to
> this file follow the Amendment Process (Article V).
>
> HOW TO WRITE THIS FILE: do not fill in these brackets alone. Run the
> Interview Protocol (docs/INTERVIEW_PROTOCOL.md): ramble your idea to your
> agent, answer its comparison questions, rule on the founding fixture cases
> it generates. The protocol produces this file *and* the proof it was
> understood.

## Preamble

[Why this project exists, in the founder's own words. One paragraph.
The senators will interpret ambiguity against this paragraph — make it
carry your intent, not marketing copy.]

## Article I — Mission

1. [The mission, stated as something an agent can serve — concrete enough
   to judge proposals against.]
2. [How improvement toward the mission is measured. If you cannot say,
   say what evidence of progress would look like — the founding fixtures
   are the first answer.]

## Article II — Values (in priority order)

When values conflict, the lower-numbered value prevails.
[This ordering is the most load-bearing part of the constitution. The
Interview Protocol's priority-forcing questions produce it. 4–7 values.]

1. **[Value]** — [one sentence: what serving it looks like]
2. **[Value]** — ...

## Article III — The Senate

1. The Senate consists of an odd number of Senators, no fewer than 3 and no
   more than 9. Composition is defined in `senate/config.yaml`.
2. No more than ⌈N/3⌉ Senators may be backed by the same model family.
3. A Triage Clerk classifies each proposal as FAST_TRACK or
   FULL_DELIBERATION.
4. Senators evaluate every proposal against, in order: this Constitution,
   the repository's stated engineering standards, and available evidence.

## Article IV — Ordinary Decisions

1. FAST_TRACK: one Senator reviews; approval requires no objection from the
   Triage Clerk's re-check. Any doubt escalates.
2. FULL_DELIBERATION: opening assessments; one rebuttal round; votes of
   APPROVE, REJECT, or ABSTAIN with written justification.
3. An ordinary proposal passes with a simple majority of non-abstaining votes.
4. All deliberation transcripts are public artifacts of the repository.

## Article V — Amendments

1. Any person or agent may propose an amendment via pull request.
2. Amendments always require FULL_DELIBERATION.
3. An amendment passes only with a two-thirds supermajority of the full
   Senate (abstentions count against).
4. During the bootstrap period (Article VI), a passed amendment additionally
   requires explicit approval by the human Custodian.
5. This Article's supermajority requirement may not be removed except by
   unanimous vote plus Custodian approval.

## Article VI — Bootstrap & Devolution of Power

1. **Phase 0 (founding):** the human Custodian holds merge authority; Senate
   verdicts are advisory and published on every proposal.
2. **Phase 1:** a passing Senate verdict becomes a required merge condition;
   the Custodian retains veto.
3. **Phase 2:** the Senate merges ordinary proposals autonomously; the
   Custodian retains veto over amendments only.
4. Advancement between phases is itself a constitutional amendment, and
   should cite the decision-quality record (`evals/`).
5. The Custodian at founding is [FOUNDER GITHUB HANDLE].

## Article VII — Interpretation

1. Ambiguity is resolved in the manner most consistent with the Preamble
   and the Article II priority ordering.
2. Procedural gaps are filled by `docs/GOVERNANCE.md`, subordinate to this
   Constitution.
