#!/usr/bin/env bash
set -euo pipefail
R="https://api.github.com/repos/buckZz7/interrex/issues"
H=(-H "Authorization: token $GITHUB_TOKEN" -H "Accept: application/vnd.github+json")

post() {
  curl -s "${H[@]}" -X POST "$R" -d "$(python3 - "$1" "$2" <<'PY'
import json, sys
print(json.dumps({"title": sys.argv[1], "labels": ["senate-priority"], "body": sys.argv[2]}))
PY
)" | python3 -c "import json,sys; print('issue #', json.load(sys.stdin).get('number'))"
}

post "Transfer-verification runner: grade the senate against the founding fixtures" \
"Article VI §4 gates senate autonomy on passing the founder's fixtures (evals/fixtures/founding_fixtures.json), but the benchmark harness only reads diff-based fixtures. Scenario fixtures need their own runner: present each scenario to the senate as a proposal, collect the verdict, compare to founder_ruling, report agreement % and per-fixture divergence.

Acceptance: offline tests with FakeLLM; markdown report; nonzero exit if agreement < threshold."

post "Interview engine MVP: conduct Phases 1–3 as a guided text conversation" \
"The product's core: an LLM-guided interview implementing docs/INTERVIEW_PROTOCOL.md — ramble capture (verbatim phrases), comparison questions, scenario generation, founder rulings. Output: draft CONSTITUTION.md + founding_fixtures.json.

Text-first (founder: voice 'down the line'). Must honor issue #1 (one scenario at a time, no walls of text) and Article VIII (transcript confidentiality — transcripts never leave the project)."

post "Chronicle section for the interrex site" \
"The site should grow a chronicle like jurisdiction #1's: the founding interview, first ruling (PR #3 — the senate judged its own face 3–0 against BRAND.md), Amendment I (unattended-operation language; first amendment passed in either jurisdiction). Primary sources linked, costs stated, BRAND.md-compliant (no slop)."
