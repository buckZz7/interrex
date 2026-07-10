# Governance Procedures

This document fills procedural gaps under CONSTITUTION.md Article VII §2.
It is subordinate to the Constitution: where they conflict, the Constitution wins.

## Roles

- **Custodian** — @buckZz7. Holds merge authority in bootstrap Phase 0,
  veto in later phases (Article VI).
- **Senators** — defined in `senate/config.yaml`. Currently: Solon
  (constitutional fidelity), Hypatia (engineering quality), Cincinnatus
  (safety & power concentration).
- **Triage Clerk** — a lightweight model that routes proposals.
- **Contributors** — anyone: Gittensor miners, humans, other agents.

## Ordinary change lifecycle

1. Contributor opens a PR (ideally referencing an open issue).
2. CI convenes the Senate (`senate-review.yml`); verdict is posted as a comment
   and the transcript is written to `deliberations/`.
3. Phase 0: the Custodian reads the verdict and merges or closes. The Custodian
   should follow Senate verdicts absent strong reason not to, and must note the
   reason on the PR when overriding.

## Amendment lifecycle (changes to CONSTITUTION.md)

1. PR touching `CONSTITUTION.md` is automatically classed as an amendment.
2. Full deliberation always (Article V §2); 2/3 supermajority required;
   abstentions count against.
3. If passed, verdict is ESCALATE: the Custodian gives or withholds final
   approval (Phase 0). CODEOWNERS enforces Custodian review at the GitHub layer.

## Protected paths

Changes to these always require full deliberation and Custodian review:

- `CONSTITUTION.md`
- `senate/config.yaml` (composition — Article III limits apply)
- `.github/` (the machinery that convenes the Senate)
- `senate/deliberation/` (the process engine)

## Senator misconduct

If a senator (model) is found to systematically violate Article II §3
(Honesty) — e.g. sycophantic approval, hallucinated citations — any
contributor may open an issue tagged `senator-conduct`. Replacing a senator
is a change to `senate/config.yaml` (protected path, full deliberation).

## Phase advancement

Moving from Phase 0 → 1 → 2 is itself a constitutional amendment (Article VI
§4). Expected evidence for advancement: a track record in `deliberations/`
showing Senate verdicts aligning with good outcomes, plus decision-quality
evals in `evals/`.

## Glossary

- **Verdict** — the Senate's collective decision on a proposal: APPROVE, REJECT, or ESCALATE (to the Custodian).
- **Transcript** — the full public record of a deliberation, committed under `deliberations/`.
