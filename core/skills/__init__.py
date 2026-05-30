"""Skills layer: typed, audited wrappers around external system calls.

Each Skill is a single Python class that exposes:
- A name + description Claude sees through the Anthropic ``tool_use`` API
- An ``input_schema`` (JSON Schema) for parameter validation
- An ``execute`` method that performs the actual side effect

Skills are registered in ``REGISTRY`` and looked up by name at runtime. The
planner sends only skills allow-listed by the matched playbook, so Claude
physically cannot call anything outside the playbook's whitelist.
"""
from core.skills.base import Skill, SkillResult
from core.skills.registry import REGISTRY, get_skill, tools_for_playbook

# Eagerly import every skill sub-package so the @register side effects
# fire when ANY consumer touches core.skills.registry — without this the
# planner sees an empty REGISTRY and silently exits at iteration 0.
from core.skills import external, jira  # noqa: E402, F401  — side-effect: register skills

__all__ = ["Skill", "SkillResult", "REGISTRY", "get_skill", "tools_for_playbook"]
