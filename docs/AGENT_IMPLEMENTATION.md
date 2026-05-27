# Agent Implementation Guide

_v2.0 · 2026-05-27 · pojednostavljeno_

---

## 1. Problem

Trenutno agent samo predlaže draft teksta. Ne može izvršiti akciju u Jira-i, IGeus-u, niti igdje drugdje.

```
ticket → classify → retrieve → draft  ← stane ovdje
```

Treba: agent koji **stvarno izvršava akcije**, ali **safe-by-default** (allow-list + HITL za rizično + audit).

---

## 2. Rješenje — koncept

**Tri stvari:**

1. **Skill** = Python klasa (name, description, input_schema, execute). Wraps `jira_client` itd.
2. **`allowed_skills` u playbook YAML frontmatter-u** — popis dozvoljenih Skills za taj playbook. Claude fizički ne može pozvati ništa izvan liste.
3. **Agent loop** — koristi Anthropic `tool_use` API. Claude predloži → validator → execute ili HITL → audit log → ponavlja dok ne kaže gotov.

**Ključni uvid**: Claude čita cijeli markdown body kao prose. **Ne trebamo parsirati bullete.** Strogi parser ide samo na frontmatter (allow-list).

---

## 3. Arhitektura

```
ticket
  ↓
classify (postojeće)
  ↓
retrieve (postojeće) → matched playbook
  ↓
draft (postojeće) → tekst odgovora
  ↓
PLANNER (novo)
  loop:
    Claude API call (tools = allow-list iz frontmatter-a)
    ↓
    Claude vrati tool_use blok
    ↓
    Validator: in allow-list? schema OK? mode allows?
    ↓
    Read auto / Write HITL (po mode + skill.is_write)
    ↓
    Audit log
    ↓
    tool_result → natrag Claude-u
  end_turn → done
```

---

## 4. Već postoji

| Komponenta | Lokacija |
|---|---|
| Pipeline (classify/retrieve/draft) | `core/*.py` |
| Jira client | `core/jira_client.py` |
| Modes (shadow/assisted/autonomous) | `core/agent_config.py` |
| Skill ABC, registry | `core/skills/` |
| Prvi primjer skill | `core/skills/jira/add_internal_comment.py` |
| Test playbook | `data/playbooks/.../test-receipt-copy-request.md` |
| Katalog | `docs/SKILLS.md` |

---

## 5. Što treba implementirati

| File | Što | Procjena |
|---|---|---|
| `core/skills/jira/get_history.py` | Read-only history | 0.5 dan |
| `core/skills/jira/add_public_comment.py` | Public reply (write) | 0.5 dan |
| `core/skills/jira/transition.py` | Status change (write) | 0.5 dan |
| `core/skills/jira/add_label.py` | Label (write, low-risk) | 0.25 dan |
| `core/skills/validator.py` | Provjeri tool call | 0.25 dan |
| `core/agent_actions.py` | SQLite audit + CRUD | 0.5 dan |
| `core/planner.py` | Agent loop | 1.5 dan |
| `backend/routers/actions.py` | HITL endpoints | 0.5 dan |
| `frontend/.../ActionApproval.tsx` | UI panel | 1.5 dan |
| Hook u `core/agent_runner.py` | Pokreni planner | 0.25 dan |
| Testovi | Unit + E2E | 1 dan |

**Ukupno: ~7 dana.**

> **Prije nego što kreneš s `planner.py`**: provjeri Claude Agent SDK (1 sat čitanja docs-a). Ako mapira čisto na ovu arhitekturu, koristi njega — uštedjet ćeš 1-2 dana i smanjit broj bug-ova.

---

## 6. Skill — kako napisati

```python
# core/skills/jira/transition.py
from core import jira_client
from core.skills.base import Skill, SkillResult
from core.skills.registry import register


@register
class JiraTransition(Skill):
    name = "jira_transition"
    description = "Change Jira ticket status. Use to move through workflow."
    is_write = True

    input_schema = {
        "type": "object",
        "properties": {
            "ticket_id": {"type": "string"},
            "target_status": {
                "type": "string",
                "enum": ["In Progress", "Waiting for vendor",
                         "Waiting for customer", "Resolved", "Closed"]
            },
        },
        "required": ["ticket_id", "target_status"],
        "additionalProperties": False
    }

    def execute(self, **params) -> SkillResult:
        try:
            jira_client.transition(params["ticket_id"], params["target_status"])
            return SkillResult(ok=True, data={"status": params["target_status"]})
        except Exception as e:
            return SkillResult(ok=False, error=str(e))
```

Pravila:
- `is_write = True` za bilo što side-effect-no
- `input_schema` što stroge to bolje
- `execute()` nikad ne raise → vrati `SkillResult(ok=False, error=...)`

---

## 7. Playbook — promjene

### Frontmatter (strogi YAML, parser ovo ekstraktira)

```yaml
allowed_skills:
  - igeus_lookup_transaction
  - jira_add_public_comment
  - jira_transition

agent_compatibility:
  autonomous_resolve: false        # postojeće — gateira write skills u autonomous modu
```

Bez `allowed_skills` polja → playbook ostaje draft-only (current behavior).

### Markdown body (Claude čita kao prose, parser ignorira)

```markdown
## Resolution bullets

[res-00001] Lookup transakcije u IGeus-u
  → koristi igeus_lookup_transaction
  → auto (read-only)

[res-00002] Storno karte
  → koristi igeus_storno_card
  → uvijek odobrenje (financijski rizik)
```

**Bullete su guidance za SME i za Claude. Nismo strogo parsiramo.** Format je opušten.

---

## 8. Planner — agent loop

> **Prvo provjeri Claude Agent SDK** — možda ti daje cijeli loop. Ako ne, custom:

```python
# core/planner.py

MAX_ITERATIONS = 10

def run(*, ticket, playbook, client=None, resume_action_id=None):
    mode = agent_config.effective_mode(playbook.id)
    tools = tools_for_playbook(playbook.metadata.get("allowed_skills", []))

    if resume_action_id:
        messages, iteration = agent_actions.load_pause_state(resume_action_id)
    else:
        messages = [_build_initial(ticket, playbook)]
        iteration = 0

    while iteration < MAX_ITERATIONS:
        iteration += 1
        response = client.messages.create(
            model=config.DRAFTER_MODEL,
            tools=tools,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            return PlannerResult(status="done")

        if response.stop_reason == "tool_use":
            results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue

                vr = validate(block, playbook, mode)
                if not vr.ok:
                    results.append(_reject(block.id, vr.reason))
                    audit(block, status="rejected", validation=vr)
                    continue

                if mode == "shadow":
                    audit(block, status="shadow")
                    results.append(_shadow_result(block.id))
                    continue

                if vr.requires_approval:
                    action_id = audit(block, status="proposed",
                                      messages=messages, iteration=iteration)
                    return PlannerResult(status="awaiting_approval",
                                         pending_action_id=action_id)

                skill = get_skill(block.name)
                result = skill.execute(**block.input)
                audit(block, status="executed" if result.ok else "failed",
                      execution_result=result.data, error=result.error)
                results.append(_format_result(block.id, result))

            messages.append({"role": "user", "content": results})
            continue

        return PlannerResult(status="failed",
                             error=f"unexpected: {response.stop_reason}")

    return PlannerResult(status="max_iterations")


def resume(action_id, *, approved, edited_input=None):
    state = agent_actions.load_pause_state(action_id)
    if approved:
        skill = get_skill(state["skill_name"])
        result = skill.execute(**(edited_input or state["skill_input"]))
        agent_actions.mark_executed(action_id, result, decided_by="user")
    else:
        agent_actions.mark_rejected(action_id, decided_by="user")
    return run(ticket=..., playbook=..., resume_action_id=action_id)
```

---

## 9. Validator — što provjerava

**Samo tri stvari:**

```python
def validate(tool_call, playbook, mode) -> ValidationResult:
    # 1. Skill u allow-list iz frontmatter-a?
    allowed = playbook.metadata.get("allowed_skills", [])
    if tool_call.name not in allowed:
        return ValidationResult(ok=False, reason="not_allowed")

    # 2. Skill postoji u registry-u?
    skill = get_skill(tool_call.name)
    if skill is None:
        return ValidationResult(ok=False, reason="unknown_skill")

    # 3. Mode + is_write → treba approval?
    requires_approval = False
    if mode == "assisted" and skill.is_write:
        requires_approval = True
    if mode == "autonomous" and skill.is_write:
        if not playbook.metadata["agent_compatibility"].get("autonomous_resolve"):
            requires_approval = True

    # Schema već validira Anthropic SDK
    return ValidationResult(ok=True, requires_approval=requires_approval)
```

**Nema bullet parsiranja. Nema bullet-level safety constraints. Sve safety dolazi iz:**
- `allowed_skills` frontmatter (whitelist)
- `skill.is_write` (Python class flag)
- `playbook.autonomous_resolve` (frontmatter)
- `mode` (shadow/assisted/autonomous)

---

## 10. Modes

| Mode | Read skill | Write skill |
|---|---|---|
| **shadow** | Log only | Log only — Jira API se nikad ne zove |
| **assisted** | Auto-execute | **Uvijek HITL** |
| **autonomous** | Auto-execute | Auto ako `playbook.autonomous_resolve = true`, inače HITL |

---

## 11. HITL flow

```
Claude predloži write skill
       ↓
Validator OK ali requires_approval=true
       ↓
Planner:
  • UUID action_id
  • INSERT agent_actions (status=proposed, messages_blob=...)
  • return AwaitingApproval(action_id)
       ↓
[Loop stane. Process slobodan.]
       ↓
Frontend dohvati pending actions
       ↓
UI prikaže: skill name, params, [✓] [✗] [Edit]
       ↓
User klikne ✓
       ↓
POST /api/actions/{id}/approve
       ↓
planner.resume(action_id, approved=True)
       ↓
Skill execute → audit log → tool_result
       ↓
Loop nastavlja
```

**Pauza može biti sekunde ili dani — Claude ne primjećuje, API je stateless.**

---

## 12. Audit log — SQLite

```sql
CREATE TABLE agent_actions (
    id              TEXT PRIMARY KEY,           -- UUID
    ticket_id       TEXT NOT NULL,
    playbook_id     TEXT NOT NULL,
    skill_name      TEXT NOT NULL,
    skill_input     TEXT NOT NULL,              -- JSON
    status          TEXT NOT NULL,              -- proposed/executed/rejected/shadow/failed
    mode            TEXT NOT NULL,
    execution_result TEXT,                      -- JSON
    error           TEXT,
    proposed_at     TEXT NOT NULL,
    decided_at      TEXT,
    decided_by      TEXT,                       -- 'auto' | user_email
    -- za HITL resume:
    messages_blob   TEXT,                       -- JSON cijela povijest
    tool_use_id     TEXT,
    iteration       INTEGER
);

CREATE INDEX idx_actions_status ON agent_actions(status);
CREATE INDEX idx_actions_ticket ON agent_actions(ticket_id);
```

**Pravilo**: audit row se piše **prije** execute.

---

## 13. Order of implementation

```
DAY 1   Read Claude Agent SDK docs (1h)
        → odluči: SDK ili custom loop?
        
        Implementiraj jira_get_history + jira_add_label
        Unit testovi
        
DAY 2   jira_add_public_comment + jira_transition
        validator.py
        
DAY 3   agent_actions.py (SQLite + CRUD)
        SDK setup ili početak custom planner-a
        
DAY 4   planner.py finalize (SDK ili custom)
        Mode gates + resume mehanizam
        Integration testovi
        
DAY 5   backend/routers/actions.py
        Hook u core/agent_runner.py
        Update test playbook s allowed_skills (ako nije)
        
DAY 6-7 frontend ActionApproval.tsx
        E2E manual test (full flow s HITL)

DAY 8   Buffer
```

**Total: 7 dana (5-6 s SDK, 7-8 custom).**

---

## 14. Acceptance kriteriji

**Skills (Day 1-2)**
- [ ] 5+ skills u REGISTRY
- [ ] Sve JSON schemas valid (Anthropic SDK ne baca grešku)

**Validator + Audit (Day 3)**
- [ ] Validator odbija unknown / not-allowed
- [ ] Audit log INSERT/SELECT radi

**Planner (Day 4)**
- [ ] E2E s mock Anthropic pass
- [ ] Shadow mode logira, ne izvršava
- [ ] Assisted mode pauzira write skills
- [ ] Autonomous mode respektira `autonomous_resolve`
- [ ] Resume nakon pauze nastavi correctly

**UI + integration (Day 5-7)**
- [ ] Pending actions vidljive u UI
- [ ] Approve / Reject / Edit rade
- [ ] Test playbook prolazi full flow

---

## 15. Failure modes

| Risk | Mitigation |
|---|---|
| Claude bira krivi tool | HITL gate za write + jasni descriptions |
| Tool izvan allow-liste | Validator hard reject (frontmatter) |
| Infinite loop | `MAX_ITERATIONS = 10` |
| Race condition (dupli approve) | `action_id` kao idempotency key |
| Schema invalid | Anthropic SDK validira pre-call |
| Skill crash | try/except → `SkillResult(ok=False)` |
| API outage | Retry s backoff |

---

## 16. Što NIJE u scope-u

- MCP server exposure
- Bullet parsing iz markdown body-ja (Claude reads naturally)
- Bullet-level safety constraints
- ACE-style counter learning (Sprint 8+)
- Multi-tenant
- Migracija svih 122 playbookova (opt-in samo)
- Parallel tool execution
- Streaming responses

---

## 17. Bottom line

```
Što gradimo:
  • Skills (Python klase) — name, description, schema, execute
  • allowed_skills u YAML frontmatter (allow-list)
  • Agent loop (probaj Claude Agent SDK prvo)
  • Validator: allow-list + schema + mode
  • HITL: skill.is_write + mode = pauza
  • Audit log: agent_actions SQLite

Što NE gradimo:
  • Bullet parser (Claude reads markdown naturally)
  • Bullet-level safety (frontmatter + skill.is_write dovoljno)
  • MCP server
  • Custom message helpers (SDK ili plain Anthropic SDK)

Postojeće NE ruši:
  • classify / retrieve / draft ostaje
  • 3-mode arhitektura ostaje
  • 122 playbooka rade bez izmjena (opt-in migration)

Total: 7 dana solo (5-6 s SDK).
```
