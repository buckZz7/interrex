# Senate Template 🏛️

**Run your repo like an empire for agents, not a business for humans.**

This is a governance kit: write your idea as a constitution, and a senate of
AI agents — backed by deliberately diverse models — deliberates and votes on
every change to your repository, judging each proposal against your written
intent. Pair it with [Gittensor (Bittensor SN74)](https://gittensor.io) and
an incentivized swarm of miners builds your vision while the senate guards it.

Battle-tested in [agentic-senate](https://github.com/buckZz7/agentic-senate)
— jurisdiction #1, where this machinery governed its own construction:
approvals, unanimous rejections of its own founder, split votes, preserved
dissents, and a perfect first decision-quality exam, all on the public
record for under a dollar.

## What you get

- **Deliberation engine** (`senate/`) — triage clerk routes proposals;
  trivial changes get one cheap review, consequential ones convene the full
  chamber: assessments → rebuttal → votes, budget-capped per deliberation
- **Verdicts on every PR** — posted as comments with each senator's
  reasoning; full transcripts preserved
- **Constitutional machinery** — protected paths, amendment supermajority,
  phased devolution of merge authority from you to the senate as it earns it
- **Decision-quality benchmark** (`evals/`) — fixture PRs with known-correct
  verdicts; false approvals penalized 3×; the exam that gates the senate's
  autonomy
- **The Interview Protocol** (`docs/INTERVIEW_PROTOCOL.md`) — how to turn
  your ramble into a constitution *with proof the machine understood it*

## Quickstart

1. **Use this template** (button above) to create your repo
2. **Write your constitution** — don't fill in `CONSTITUTION.template.md`
   alone; run the Interview Protocol with your agent. Rename the result to
   `CONSTITUTION.md`
3. **Configure the chamber** — `senate/config.yaml`: pick models (keep the
   diversity rule: no model family may exceed ⌈N/3⌉ seats), set budgets
4. **Add secrets** — repo Settings → Secrets → Actions:
   `OPENROUTER_API_KEY` (any OpenAI-compatible gateway works)
5. **Update CODEOWNERS** — replace the placeholder handle with yours
6. **Open a test PR** — watch your senate convene
7. *(Optional)* **Register with Gittensor** — install the
   [mirror app](https://github.com/apps/gittensor-mirror), submit the
   [form](https://gittensor.io/repository-registration), seed scoped
   issues, and miners get paid to build your idea

## Costs (observed, OpenRouter mid-tier models)

| Event | Cost |
|---|---|
| Fast-track review | ~$0.007 |
| Full 3-senator deliberation | ~$0.05–0.08 |
| 6-fixture benchmark run | ~$0.49 |

## Governance of this template

This template is governed by the senate of
[agentic-senate](https://github.com/buckZz7/agentic-senate) — improvements
to the engine face the most experienced chamber before shipping to every
jurisdiction built from it. Propose changes by PR; expect deliberation.

## License

MIT — see [LICENSE](LICENSE).
