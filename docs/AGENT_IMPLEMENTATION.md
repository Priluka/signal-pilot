# Agent Implementation Guide

_v1.0 · 2026-05-27_

---

## 1. Problem

Trenutno agent samo predlaže draft teksta. Ne može izvršiti akciju u Jira-i, IGeus-u, niti igdje drugdje.

Pipeline danas:
```
ticket → classify → retrieve → draft  ← stane ovdje
```

Što fali: agent treba moći **stvarno izvršiti akciju** (poslati komentar, promijeniti status, naći transakciju), ali na način koji je:
- **siguran** (ne smije slučajno izvršiti pogrešnu akciju)
- **kontroliran** (čovjek može odobriti rizično prije execute)
- **audit-able** (svaka akcija ima trag)
- **playbook-specific** (svaki playbook dozvoljava samo svoje akcije)

---

## 2. Rješenje — koncept

**Tri komponente:**

1. **Skill** = Python klasa koja zna izvršiti jednu konkretnu akciju (npr. dodati Jira komentar). Ima `name`, `description`, `input_schema`, `execute()`. Wrapping postojeći `jira_client`.

2. **Playbook allow-list** = YAML polje `allowed_skills: [...]` koje kaže koji Skills su dozvoljeni za taj playbook. Claude fizički ne može pozvati ništa izvan liste.

3. **Agent loop** = Python petlja koja zove Anthropic API s tools, dobiva Claude-ove tool requests, validira ih, izvršava (ili pauzira za čovjeka), vraća rezultate Claude-u, ponavlja dok Claude ne kaže gotov.

**Kako Claude radi:**
- Anthropic API je **stateless**. Mi šaljemo cijelu povijest svaki put.
- Claude vraća `tool_use` blok = "želim pozvati X s parametrima Y"
- **Tvoj kod** odlučuje izvršiti, pauzirati za HITL, ili odbiti
- Vraćaš `tool_result` Claude-u, on nastavlja
- Loop traje dok Claude ne vrati `stop_reason: "end_turn"`

---

## 3. Arhitektura

```
ticket
  ↓
classify (postojeće)
  ↓
retrieve (postojeće) → matched playbook
  ↓
draft (postojeće, ostaje) → tekst odgovora
  ↓
PLANNER (novo) ─────────────────────────────────────┐
  loop:                                             │
    Claude API call (tools = allow-list iz pb)      │
    ↓                                               │
    Claude vrati tool_use                           │
    ↓                                               │
    Validator (in allow-list? schema OK? safe?)     │
    ↓                                               │
    Mode gate (shadow/assisted/autonomous)          │
    ↓                                               │
    Read   → execute auto                           │
    Write  → HITL (return AwaitingApproval)         │
    ↓                                               │
    Audit log                                       │
    ↓                                               │
    tool_result → natrag Claude-u                   │
  end_turn → done                                   │
─────────────────────────────────────────────────────┘
  ↓
ticket updated
```

---

## 4. Što već postoji

| Komponenta | Lokacija | Status |
|---|---|---|
| `Skill` ABC, registry, primjer | `core/skills/` | ✓ |
| Pipeline (classify/retrieve/draft) | `core/*.py` | ✓ |
| Jira klijent | `core/jira_client.py` | ✓ |
| Mode config (shadow/assisted/autonomous) | `core/agent_config.py` | ✓ |
| Per-playbook mode override | `core/agent_config.py:effective_mode` | ✓ |
| Test playbook s `allowed_skills` | `data/playbooks/.../test-receipt-copy-request.md` | ✓ |
| SKILLS katalog | `docs/SKILLS.md` | ✓ |

---

## 5. Što treba implementirati

| File | Što radi | Procjena |
|---|---|---|
| `core/skills/jira/get_history.py` | Read-only Jira ticket history | 0.5 dan |
| `core/skills/jira/add_public_comment.py` | Slanje odgovora kupcu (write, HITL) | 0.5 dan |
| `core/skills/jira/transition.py` | Promjena statusa (write, HITL) | 0.5 dan |
| `core/skills/jira/add_label.py` | Label (write, low-risk) | 0.25 dan |
| `core/playbook_bullets.py` | Parse `[res-XXX]` bullete iz markdown body-ja | 0.5 dan |
| `core/skills/validator.py` | Provjeri tool call prije execute | 0.5 dan |
| `core/agent_actions.py` | SQLite tablica + CRUD za audit | 0.5 dan |
| `core/planner.py` | Agent loop (srce sustava) | 2 dana |
| `backend/routers/actions.py` | HITL endpoint-i (approve/reject) | 0.5 dan |
| `frontend/.../ActionApproval.tsx` | UI panel za approval | 1.5 dan |
| Hook u `core/agent_runner.py` | Pokreni planner nakon draft-a | 0.25 dan |
| Testovi | Unit + integration + E2E | 1.5 dan |

**Ukupno: ~9 dana solo.**

---

## 6. Skill — kako napisati

Template (jedan file = jedan skill = jedna akcija):

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
- `name` = stringski identifier, isti koji ide u playbook `allowed_skills`
- `description` = što Claude vidi i koristi za odluku
- `is_write` = `True` za bilo što side-effect-no
- `input_schema` = JSON Schema, što stroge to bolje
- `execute()` = nikad ne raise — vrati `SkillResult(ok=False, error=...)`

---

## 7. Playbook — nove promjene

### Frontmatter

```yaml
allowed_skills:
  - igeus_lookup_transaction
  - jira_add_public_comment
  - jira_transition
```

Bez ovog polja → playbook se ponaša kao i sad (samo draft). **Opt-in po playbook-u.**

### Resolution bullets

```markdown
## Resolution bullets

[res-00001] :: Lookup transakcije
  skill: igeus_lookup_transaction
  safety:
    human_approval_required: false

[res-00002] :: Pošalji odgovor kupcu
  skill: jira_add_public_comment
  safety:
    human_approval_required: true

[res-00003] :: Zatvori ticket
  skill: jira_transition
  skill_params:
    target_status: "Resolved"
  safety:
    human_approval_required: true
```

Pravila:
- **1 bullet = 1 skill** (deterministic)
- `safety.human_approval_required: true` → uvijek HITL (override-a sve modove)

---

## 8. Planner loop — srce sustava

```python
# core/planner.py
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
    """Pozove se iz backend endpoint-a nakon approval/reject."""
    state = agent_actions.load_pause_state(action_id)
    if approved:
        skill = get_skill(state["skill_name"])
        result = skill.execute(**(edited_input or state["skill_input"]))
        agent_actions.mark_executed(action_id, result, decided_by="user")
        tool_result = _format_result(state["tool_use_id"], result)
    else:
        agent_actions.mark_rejected(action_id, decided_by="user")
        tool_result = _reject(state["tool_use_id"], "user_rejected")
    
    # Nastavi loop s tim rezultatom
    return run(ticket=..., playbook=..., resume_action_id=action_id)
```

---

## 9. Modovi — kako se uklapaju

| Mode | Read skill | Write skill |
|---|---|---|
| **shadow** | Log only | Log only — Jira API se nikad ne zove |
| **assisted** | Auto-execute | **Uvijek HITL** |
| **autonomous** | Auto-execute | Auto ako: playbook dozvoljava + bullet ne traži approval + safety pass; inače HITL |

**Prioritet (od najjačeg):**
1. `bullet.safety.human_approval_required: true` — uvijek HITL
2. `playbook.autonomous_resolve: false` — write uvijek HITL
3. `mode = assisted` — write uvijek HITL
4. `mode = autonomous` + sve gore OK — auto-execute

Najrestriktivnije pobjeđuje.

---

## 10. HITL flow

```
Claude predloži write skill
       ↓
Validator pass, ali requires_approval=true
       ↓
Planner:
  • UUID action_id = generiraj
  • INSERT agent_actions (status=proposed, messages_blob=...)
  • return AwaitingApproval(action_id)
       ↓
[Loop završio. Process slobodan.]
       ↓
Frontend dohvati pending actions (poll ili WS)
       ↓
UI prikaže: skill name, params, bullet ref, [✓] [✗] [Edit]
       ↓
User klikne ✓
       ↓
POST /api/actions/{id}/approve
       ↓
Backend zove planner.resume(action_id, approved=True)
       ↓
Skill execute → audit log → tool_result
       ↓
Loop nastavlja s novom porukom Claude-u
       ↓
Sljedeća iteracija (ili end_turn)
```

**Pauza može biti sekunde ili dani — Claude ne primjećuje jer je API stateless.**

---

## 11. Audit log — SQLite tablica

```sql
CREATE TABLE agent_actions (
    id              TEXT PRIMARY KEY,           -- UUID
    ticket_id       TEXT NOT NULL,
    playbook_id     TEXT NOT NULL,
    bullet_id       TEXT,                       -- npr. 'res-00002'
    skill_name      TEXT NOT NULL,
    skill_input     TEXT NOT NULL,              -- JSON
    status          TEXT NOT NULL,              -- proposed/executed/rejected/shadow/failed
    mode            TEXT NOT NULL,
    validation      TEXT,                       -- JSON ValidationResult
    execution_result TEXT,                      -- JSON
    error           TEXT,
    proposed_at     TEXT NOT NULL,
    decided_at      TEXT,
    decided_by      TEXT,                       -- 'auto' | user_email
    executed_at     TEXT,
    -- za HITL resume:
    messages_blob   TEXT,                       -- JSON cijela povijest
    tool_use_id     TEXT,                       -- Anthropic block id
    iteration       INTEGER
);

CREATE INDEX idx_actions_status ON agent_actions(status);
CREATE INDEX idx_actions_ticket ON agent_actions(ticket_id);
```

**Pravilo**: audit row se piše **prije** execute, ne nakon. Ako execute pukne, ima trag.

---

## 12. Validator — što provjerava

```python
def validate(tool_call, playbook, mode) -> ValidationResult:
    # 1. Skill u registry?
    skill = get_skill(tool_call.name)
    if skill is None:
        return ValidationResult(ok=False, reason="unknown_skill")

    # 2. Allow-list iz playbook frontmatter-a?
    if tool_call.name not in playbook.allowed_skills:
        return ValidationResult(ok=False, reason="not_allowed")

    # 3. Schema (Anthropic SDK već validirao — defensive recheck)

    # 4. Bullet match + safety
    bullet = find_bullet_for_skill(playbook, tool_call.name)
    requires_approval = bullet.safety.get("human_approval_required", False)

    # 5. Mode gate
    if mode == "assisted" and skill.is_write:
        requires_approval = True
    if mode == "autonomous" and skill.is_write:
        if not playbook.metadata["agent_compatibility"].get("autonomous_resolve"):
            requires_approval = True

    return ValidationResult(ok=True, requires_approval=requires_approval,
                            matched_bullet_id=bullet.id if bullet else None)
```

---

## 13. Order of implementation

Striktni redoslijed — svaki korak ovisi o prethodnom.

```
DAY 1   jira_get_history (read-only) + jira_add_label
        Unit testovi
        
DAY 2   jira_add_public_comment + jira_transition
        validator.py + unit testovi
        Acceptance: registry ima 5 skills, validator radi
        
DAY 3   playbook_bullets.py parser
        agent_actions.py + SQLite migration
        Tests
        
DAY 4-5 planner.py — agent loop
        Mode gates (shadow/assisted/autonomous)
        Resume mehanizam
        Integration testovi (mock Anthropic)
        Acceptance: full loop radi s mock-om, sve modovi rade
        
DAY 6   backend/routers/actions.py
        Hook u core/agent_runner.py
        Update test playbook s allowed_skills
        
DAY 7-8 frontend ActionApproval.tsx
        Integration u Agent Feed
        E2E manual test
        
DAY 9   Buffer + metrike u UI
```

**Total: ~9 dana.**

---

## 14. Acceptance kriteriji

### Po fazi:

**Skills (Day 1-2)**
- [ ] 5+ skills u REGISTRY
- [ ] Svi JSON schemas valid
- [ ] Validator odbija unknown / not-allowed skills

**Parser + audit (Day 3)**
- [ ] Parser ekstraktira bullete s `skill:`, `safety:`, `skill_params:`
- [ ] Audit log INSERT/SELECT radi

**Planner (Day 4-5)**
- [ ] E2E s mock Anthropic pass
- [ ] Shadow mode logira, ne izvršava
- [ ] Assisted mode pauzira write skills
- [ ] Autonomous mode respektira playbook + bullet
- [ ] `MAX_ITERATIONS` zaštita radi
- [ ] Resume nakon pauze nastavi correctly

**UI + integration (Day 6-9)**
- [ ] Predložene akcije vidljive u UI
- [ ] Approve / Reject / Edit gumbi rade
- [ ] Test playbook prolazi full flow s HITL approval
- [ ] Audit log sadrži sve akcije

---

## 15. Failure modes — najkritičnije

| Risk | Mitigation |
|---|---|
| Claude bira krivi tool | HITL gate za write + jasni descriptions |
| Tool izvan allow-liste | Validator hard reject |
| Infinite loop | `MAX_ITERATIONS = 10` u planner-u |
| Race condition (dupli approve) | `action_id` kao idempotency key |
| Schema invalid input | Anthropic SDK validira pre-poziva |
| Skill execute crash | try/except → `SkillResult(ok=False)`, ne raise |
| Long pause + API outage | Retry s backoff; state je u DB, ne in-memory |

---

## 16. Što NIJE u scope-u (eksplicitno odgođeno)

- MCP server exposure (only direct Anthropic API)
- Bullet counters / ACE-style learning (Sprint 8+)
- Multi-tenant isolation
- Claude Agent SDK migration
- Parallel tool execution
- Auto-generated SKILLS.md
- Migration svih 122 postojećih playbookova (opt-in samo)

---

## 17. Bottom line

```
Što gradimo:
  Playbook s allowed_skills + bullete (markdown)
  ↓
  Skills (Python klase) registered u REGISTRY
  ↓
  Planner agent loop s Anthropic tool_use
  ↓
  Validator (allow-list + schema + safety + mode)
  ↓
  Read auto / Write HITL
  ↓
  Audit log + UI approval

Što ne mijenjamo:
  Postojeće classify / retrieve / draft
  Postojeća 3-mode arhitektura
  Postojećih 122 playbookova (opt-in migration)

Cilj:
  Agent koji stvarno izvršava akcije,
  safe-by-default,
  audit-able,
  s clear path-om za rizično (HITL).
```
