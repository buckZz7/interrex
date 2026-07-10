"""Merge gate — CLI entrypoint that reviews a PR and publishes the verdict.

Usage (normally invoked by .github/workflows/senate-review.yml):
    python -m senate.merge_gate --pr 42

Reads PR metadata + diff via the GitHub API, runs the constitutional
deliberation, writes the transcript to deliberations/, posts the verdict as a
PR comment, and exits 0 (APPROVE) / 1 (REJECT) / 2 (ESCALATE) so the check
status reflects the Senate's will. Phase 0: this check is advisory.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import urllib.request

import yaml

from .deliberation import deliberate
from .llm import LLMClient
from .models import Deliberation, Proposal, Verdict
from .senators import Senator

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROTECTED = ("CONSTITUTION.md",)


def _gh(url: str, token: str, accept: str = "application/vnd.github+json") -> bytes:
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}", "Accept": accept},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def load_proposal(repo: str, pr_number: int, token: str) -> Proposal:
    base = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    meta = json.loads(_gh(base, token))
    diff = _gh(base, token, accept="application/vnd.github.v3.diff").decode(
        errors="replace"
    )
    files = json.loads(_gh(f"{base}/files?per_page=100", token))
    changed = [f["filename"] for f in files]
    return Proposal(
        number=pr_number,
        title=meta["title"],
        author=meta["user"]["login"],
        body=meta.get("body") or "",
        diff=diff,
        changed_files=changed,
        is_amendment=any(f in PROTECTED for f in changed),
    )


def post_comment(repo: str, pr_number: int, token: str, body: str) -> None:
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    req = urllib.request.Request(
        url,
        data=json.dumps({"body": body}).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        },
    )
    urllib.request.urlopen(req, timeout=60)


def render_verdict(d: Deliberation) -> str:
    verdict = d.verdict or Verdict.ESCALATE
    emoji = {"APPROVE": "✅", "REJECT": "❌", "ESCALATE": "⚖️"}[verdict.value]
    lines = [
        f"## {emoji} Senate Verdict: {verdict.value}",
        "",
        f"**Track:** {d.track.value} — {d.triage_reasoning}",
        f"**Reasoning:** {d.verdict_reasoning}",
        f"**Deliberation cost:** ${d.cost_usd:.4f}",
        "",
    ]
    votes = [o for o in d.opinions if o.vote is not None]
    if votes:
        lines.append("| Senator | Vote | Justification |")
        lines.append("|---|---|---|")
        for v in votes:
            just = v.justification.replace("\n", " ")[:200]
            lines.append(f"| {v.senator} | {v.vote.value} | {just} |")
    lines.append("")
    lines.append(
        "<sub>Advisory verdict — bootstrap Phase 0 (Constitution, Article VI). "
        "Full transcript committed to `deliberations/`.</sub>"
    )
    return "\n".join(lines)


def save_transcript(d: Deliberation) -> pathlib.Path:
    out_dir = ROOT / "deliberations"
    out_dir.mkdir(exist_ok=True)
    path = out_dir / f"pr-{d.proposal.number}.md"
    parts = [
        f"# Deliberation — PR #{d.proposal.number}: {d.proposal.title}",
        f"- Track: {d.track.value} ({d.triage_reasoning})",
        f"- Verdict: {(d.verdict or Verdict.ESCALATE).value} — {d.verdict_reasoning}",
        f"- Cost: ${d.cost_usd:.4f}",
        "\n## Opinions\n",
    ]
    for o in d.opinions:
        parts.append(f"### {o.senator} ({o.model})\n\n{o.assessment}\n")
    if d.rebuttals:
        parts.append("## Rebuttals\n")
        for o in d.rebuttals:
            parts.append(f"### {o.senator}\n\n{o.assessment}\n")
    path.write_text("\n".join(parts))
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--no-comment", action="store_true")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN", "")
    if not token or not args.repo:
        print("GITHUB_TOKEN and --repo (or GITHUB_REPOSITORY) are required")
        return 2

    cfg = yaml.safe_load((ROOT / "senate" / "config.yaml").read_text())
    constitution = (ROOT / "CONSTITUTION.md").read_text()
    senators = [Senator(**s) for s in cfg["senate"]["senators"]]

    client = LLMClient(
        base_url=cfg["llm"]["base_url"],
        api_key_env=cfg["llm"]["api_key_env"],
        max_usd=float(cfg["budget"]["max_usd_per_deliberation"]),
    )

    proposal = load_proposal(args.repo, args.pr, token)
    d = deliberate(proposal, senators, constitution, client, cfg)

    save_transcript(d)
    body = render_verdict(d)
    print(body)
    if not args.no_comment:
        post_comment(args.repo, args.pr, token, body)

    return {"APPROVE": 0, "REJECT": 1, "ESCALATE": 2}[(d.verdict or Verdict.ESCALATE).value]


if __name__ == "__main__":
    sys.exit(main())
