# The Interview Protocol

> Version 0.1.0 — subordinate to CONSTITUTION.md (Article VII §2).
> How a human idea becomes a machine-executable constitution — and how we
> prove the transfer actually happened.

## The problem this solves

Every agent-maintainer system assumes the maintainer already understands the
idea it is maintaining. That assumption is the weakest link: humans do not
naturally speak in specifications, and agents do not naturally ask the right
questions. The result is drift — a repo that runs well toward the wrong thing.

This protocol treats **idea transfer as a measurable engineering step**, not
a vibe. Its output is two artifacts, and the second one is the point:

1. `CONSTITUTION.md` — the idea, written as governing law
2. **Founding fixtures** — concrete cases the *founder* ruled on, forming an
   exam that proves whether the senate judges as the founder would

An idea has been transferred when the machine and the human grade the same
cases the same way. Not when the machine can paraphrase the idea — when it
can *rule* with it.

## Phase 1 — The Ramble (founder talks, interviewer listens)

The founder describes the idea in whatever words come naturally. The
interviewer's only jobs:

- Do not interrupt with structure. Rambles contain priorities in the order
  excitement surfaces them — that ordering is data.
- Capture verbatim phrases. Founders coin their own load-bearing terms
  ("empires for agents"); the constitution should speak the founder's
  language, not consultant-ese.

## Phase 2 — Comparison-driven elicitation (never ask for specifications)

Humans cannot reliably specify what they want, but they can reliably judge
instances. So never ask "what are your quality standards?" Ask instead:

- **Pole questions**: "Here are two versions of X — which is more your idea,
  and what's wrong with the loser?"
- **Boundary probes**: "Would the project still be itself if it did Y?"
  (finds the constitutional vs. incidental features)
- **Priority forcing**: "Situation where value A and value B conflict —
  which one bends?" (produces the Article II priority ordering, the single
  most load-bearing part of any constitution)
- **Veto discovery**: "Describe something a contributor could do that would
  make you kill the project rather than accept it." (finds Article-level
  prohibitions)

Five to ten questions is usually enough. The interviewer drafts articles
*during* the conversation and reads them back: "I'm going to write down:
'X outranks Y when they conflict.' True?"

## Phase 3 — Fixtures at founding (the exam is written before the senate sits)

Before the constitution is finalized, the interviewer generates **8–15
concrete scenario cases**: realistic proposals/PRs/decisions the project
might face. For each, the founder rules APPROVE or REJECT and says why,
in one or two sentences.

Rules:

- Cases must span the trap categories (genuinely good, subtle violation,
  plausible-but-misaligned, values-in-conflict, scope creep, gaming).
- The founder's one-line rationales get captured verbatim — they become the
  fixtures' `rationale` fields and often reveal missing articles.
- **Disagreement is the product working**: when the founder's ruling
  contradicts the draft constitution, either the constitution gains an
  article or the founder discovers their idea was fuzzier than they thought.
  Both outcomes are the protocol succeeding.

## Phase 4 — Transfer verification (graded, public, repeatable)

Seat the senate. Run the founding fixtures through the real deliberation
engine (`evals/benchmark.py` pattern). Score it.

- **High agreement** → the idea transferred; the score is the certificate.
- **Divergence on specific fixtures** → the constitution is ambiguous
  exactly there; amend before launch, not after drift.
- The founding score is the project's birth certificate: recorded in the
  chronicle, cited in every future "has the senate drifted?" audit.

## Phase 5 — Drift audits (transfer is not a one-time event)

Re-run the founding fixtures on a schedule (quarterly, or after any senator
change). Divergence from the founder's rulings means one of:

1. The senate's judgment decayed → fix the senate (senator succession,
   prompt work), or
2. The project legitimately evolved past its founding intent → the
   constitution needs amendment, with the founder's participation.

Either way the divergence *triggers a governance conversation instead of
silent drift*. This is the continuous answer to "how do we measure
improvement": improvement is movement toward the constitution, and the
fixtures are the constitution made measurable.

## Founder's promise

This protocol asks roughly one hour of a founder's time and no technical
knowledge whatsoever. Everything the founder produces is in their own words:
a ramble, some this-or-that judgments, and rulings on concrete cases. The
machinery translates; the founder never has to.
