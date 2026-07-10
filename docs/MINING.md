# Mining this repo on Gittensor

A plain-language guide for contributing to the Agentic Senate and getting paid
via [Gittensor (Bittensor subnet 74)](https://gittensor.io).

## If you're already a Gittensor miner

1. Find an open issue here — `senate-priority` labels matter most to us.
2. Comment on the issue so others know you're on it.
3. Open a PR referencing the issue (`Fixes #N` in the description).
4. The Senate will review your PR and post a public verdict; the Custodian
   merges. Read `CONSTITUTION.md` — the Senate literally judges against it.
5. Once merged, Gittensor validators score your PR in their next round
   (every ~2 hours).

### What scores well here

- **Real source code** — Gittensor scores AST tokens of source changes;
  docs/config score much lower and tests are down-weighted by the subnet.
  But note: the *Senate* values tests (Constitution, Article II §4), so
  PRs with tests are more likely to be approved and merged at all.
- **Scoped, reviewable PRs** — one issue, one PR. Giant drive-by refactors
  will likely be rejected by the Senate (Article II §2 — reversibility).
- **Credibility management** — Gittensor requires ≥3 merged PRs and ≥80%
  credibility (merged / (merged + closed)) per repo before you earn. Don't
  spray low-quality PRs: closed PRs poison your ratio and your open PRs
  carry collateral.

### What gets rejected

- Changes that weaken review, grant hidden authority, touch secrets, or game
  incentives — Senator Cincinnatus's entire mandate is hunting for these.
- Unverifiable claims: the Senate is instructed to trust the diff, not the
  PR description.
- Constitution edits without genuine justification — amendments need a 2/3
  supermajority (Article V).

## If you're new to Gittensor entirely

1. **Get a Bittensor wallet + hotkey** and register a UID on subnet 74
   (registration cost varies; check current cost first).
2. **Create a fine-grained GitHub PAT** (read-only is enough for validation).
3. **Broadcast your PAT** to validators: `gitt miner post`.
   Your GitHub identity gets permanently locked to your hotkey.
4. Contribute to any registered repo — including this one.

Full official docs: https://docs.gittensor.io — start with the
[miner guide](https://docs.gittensor.io/miner.html) and
[OSS contributions scoring](https://docs.gittensor.io/oss-contributions.html).

## FAQ

**Do I need to run a server?** No. Gittensor mining is: register once, then
submit PRs. Validators pull your merged-PR record from GitHub.

**Can the Senate merge my PR?** Not yet — bootstrap Phase 0 means a human
Custodian merges. The Senate's verdict is advisory but strongly weighted.

**Can I be a maintainer here?** Maintainer (COLLABORATOR+) PRs are *ignored*
by Gittensor scoring, so becoming a maintainer ends your mining income from
this repo. Choose wisely.
