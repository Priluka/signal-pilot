"""Validator — gatekeeper between Claude's tool_use call and execution.

Three checks per ``docs/AGENT_IMPLEMENTATION.md``:

1. **Allow-list**  — the skill name must appear in the matched playbook's
   ``allowed_skills`` frontmatter list. Claude can't reach anything else.
2. **Registry**    — the skill must be registered (typo in a playbook =>
   not-implemented => reject; do not crash).
3. **Approval**    — based on agent mode + skill.is_write + playbook's
   ``agent_compatibility.autonomous_resolve``. Returns
   ``requires_approval=True`` to put the call in the HITL queue.

The validator is intentionally narrow — input-schema validation is done
by the Anthropic SDK before the call ever reaches us, so we don't need
to re-validate types here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.skills.registry import REGISTRY


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of validating one tool_use block.

    When ``ok`` is False the ``reason`` is fed back to Claude as the
    tool_result content so the model can recover (try a different
    skill, fix params, etc.). When ``ok`` is True, ``requires_approval``
    drives the planner's branch — auto-execute vs save-pending-action.
    """

    ok: bool
    reason: str = ""
    requires_approval: bool = False


def validate(
    tool_name: str,
    playbook_metadata: dict[str, Any],
    mode: str,
) -> ValidationResult:
    """Validate a single Claude tool_use call against playbook + mode.

    Parameters
    ----------
    tool_name
        The ``name`` field from the Anthropic ``tool_use`` block.
    playbook_metadata
        The matched playbook's YAML frontmatter dict (``pb.metadata``).
    mode
        ``"shadow"`` | ``"assisted"`` | ``"autonomous"``.
    """
    # 1. Allow-list check ---------------------------------------------------
    allowed = playbook_metadata.get("allowed_skills") or []
    if not isinstance(allowed, list):
        return ValidationResult(
            ok=False,
            reason="playbook_misconfigured: allowed_skills is not a list",
        )
    if tool_name not in allowed:
        return ValidationResult(
            ok=False,
            reason=(
                f"not_allowed: {tool_name!r} is not in this playbook's "
                f"allowed_skills (have: {allowed})"
            ),
        )

    # 2. Registry check -----------------------------------------------------
    cls = REGISTRY.get(tool_name)
    if cls is None:
        return ValidationResult(
            ok=False,
            reason=(
                f"unknown_skill: {tool_name!r} is allow-listed but not "
                f"implemented yet"
            ),
        )

    # 3. Approval policy ----------------------------------------------------
    # Read skills never require approval — they're side-effect-free.
    if not cls.is_write:
        return ValidationResult(ok=True, requires_approval=False)

    # Write skills:
    #   - shadow    → never executes anyway (planner logs and skips)
    #   - assisted  → always HITL for write
    #   - autonomous→ auto-execute iff playbook explicitly opted in via
    #                 agent_compatibility.autonomous_resolve = true
    if mode == "shadow":
        return ValidationResult(ok=True, requires_approval=False)
    if mode == "assisted":
        return ValidationResult(ok=True, requires_approval=True)
    if mode == "autonomous":
        compat = playbook_metadata.get("agent_compatibility") or {}
        if compat.get("autonomous_resolve"):
            return ValidationResult(ok=True, requires_approval=False)
        return ValidationResult(ok=True, requires_approval=True)

    # Unknown mode — treat as the strictest option.
    return ValidationResult(
        ok=False,
        reason=f"unknown_mode: {mode!r}",
    )
