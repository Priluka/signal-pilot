"""Smoke check for Ivan's Skills scaffold.

Verifies that what he's shipped actually loads, registers, and (if
asked) can call the live Jira via the one implemented skill. Standalone
script — no pytest harness, just print-and-go so the output is readable.

Run from the project root:
    .venv/bin/python tests/skills_smoke.py
    .venv/bin/python tests/skills_smoke.py --live   # also posts a real comment
"""
from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(_PROJECT_ROOT / ".env")


def line(title: str) -> None:
    print(f"\n--- {title} " + "-" * (60 - len(title)))


def main() -> int:
    live = "--live" in sys.argv

    line("STEP 1 · Skill imports and self-registers")
    from core.skills import jira  # noqa: F401  — side-effect imports
    from core.skills.registry import REGISTRY, get_skill, tools_for_playbook

    if "jira_add_internal_comment" not in REGISTRY:
        print("FAIL · jira_add_internal_comment NOT in REGISTRY")
        print(f"       registry keys = {list(REGISTRY.keys())}")
        return 1
    print(f"PASS · REGISTRY has {len(REGISTRY)} skill(s): {list(REGISTRY.keys())}")

    skill = get_skill("jira_add_internal_comment")
    print(f"       get_skill() → {skill.__class__.__name__}")
    print(f"       is_write    = {skill.is_write}")

    line("STEP 2 · Test playbook loads with allowed_skills")
    from core.retrieval import load_playbook

    pb_path = (
        _PROJECT_ROOT
        / "data/playbooks/end_user/billing/test-receipt-copy-request.md"
    )
    pb = load_playbook(pb_path)
    allowed = pb.metadata.get("allowed_skills") or []
    print(f"PASS · playbook id        = {pb.id}")
    print(f"       allowed_skills     = {allowed}")
    print(f"       ticket_class       = {pb.ticket_class}")
    print(f"       status             = {pb.metadata.get('status')}")

    line("STEP 3 · tools_for_playbook() builds Claude tool_use spec")
    specs = tools_for_playbook(allowed)
    print(f"PASS · {len(specs)} of {len(allowed)} requested skills resolve to specs")
    for spec in specs:
        print(f"       • {spec['name']}")
        print(f"         desc: {spec['description'][:80]}…")
        required = spec["input_schema"].get("required", [])
        print(f"         required params: {required}")
    missing = [s for s in allowed if s not in REGISTRY]
    if missing:
        print(f"NOTE · {len(missing)} planned skill(s) not yet implemented: {missing}")

    line("STEP 4 · JiraAddInternalComment.execute() against live Jira")
    if not live:
        print("SKIP · re-run with --live to actually post a comment to KAN-34")
        print("       (will be an obvious test message; harmless to delete after)")
        return 0

    target = "KAN-34"
    body = (
        "[automated test] signal-pilot Skills smoke check — verifies "
        "Ivan's JiraAddInternalComment execute() reaches Jira API. "
        "Safe to delete."
    )
    print(f"     · posting internal comment to {target}…")
    result = skill.execute(ticket_id=target, body=body)
    print(f"     · ok          = {result.ok}")
    print(f"     · data        = {result.data}")
    print(f"     · error       = {result.error}")
    if not result.ok:
        print("FAIL · execute() did not return ok=True")
        return 2
    print("PASS · Jira API accepted the comment")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
