# Agent Implementation Guide

_v3.0 · 2026-05-27 · demo-focused_

> **Scope**: ovo je plan za **demo verziju**, ne produkciju. Demo prikazuje da agent može stvarno izvršiti akciju kroz HITL approval. Produkcijske dodatke (full audit, multi-playbook migration, monitoring) dodajemo poslije demo-a.

---

## 1. Problem

Agent danas samo predlaže draft. Demo mora pokazati da agent može **stvarno izvršiti akciju** (Jira comment, transition) safe-by-default (allow-list + HITL).

```
ticket → classify → retrieve → draft  ← stane ovdje
```

---

## 2. Rješenje — koncept

1. **Skill** = Python klasa (name, description, input_schema, execute). Wraps `jira_client`.
2. **`allowed_skills` u playbook YAML frontmatter-u** — popis dozvoljenih Skills. Claude fizički ne može pozvati ništa izvan liste.
3. **Agent loop** — Anthropic `tool_use` API. Claude predloži → validator → execute ili HITL → ponavlja.

**Ključni uvid**: Claude čita cijeli markdown body kao prose. **Ne parsiramo bullete.** Strogi parser ide samo na frontmatter.

---

## 3. Arhitektura

```
ticket
  ↓
classify / retrieve / draft (postojeće)
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
| **Test playbook** za demo | `data/playbooks/.../test-receipt-copy-request.md` |
| Katalog | `docs/SKILLS.md` |

---

## 5. Što treba implementirati za DEMO

| File | Što | Procjena |
|---|---|---|
| `core/skills/jira/get_history.py` | Read-only history | 0.5 dan |
| `core/skills/jira/add_public_comment.py` | Public reply (write) | 0.5 dan |
| `core/skills/jira/transition.py` | Status change (write) | 0.5 dan |
| `core/skills/validator.py` | Provjeri tool call | 0.25 dan |
| `core/pending_actions.py` | Minimal HITL state (4 polja) | 0.25 dan |
| `core/planner.py` | Agent loop | 1.5 dan |
| `backend/routers/actions.py` | HITL endpoints | 0.5 dan |
| `frontend/.../ActionApproval.tsx` | UI panel | 1.5 dan |
| Hook u `core/agent_runner.py` | Pokreni planner | 0.25 dan |
| Manual E2E test | s test playbook-om | 0.25 dan |

**Ukupno: ~5-6 dana za demo.**

> **Prije nego što kreneš s `planner.py`**: provjeri Claude Agent SDK (1 sat). Ako mapira čisto, koristi njega — ušteda 1-2 dana.

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
    description = "Change Jira ticket status."
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
- `execute()` nikad ne raise → vrati `SkillResult(ok=False, error=...)`

---

## 7. Playbook za demo

**Za demo NE migriraš nijedan produkcijski playbook. Koristiš postojeći test playbook.**

`data/playbooks/end_user/billing/test-receipt-copy-request.md` već ima:

```yaml
allowed_skills:
  - igeus_lookup_transaction
  - jira_add_public_comment
  - jira_add_internal_comment
  - jira_transition

status: draft                              # ne ide u produkciju retrieval
```

**Ne diraš nijedan postojeći playbook. Nula ručnog pisanja bullete-a.**

> **Bullete u markdown body-ju** su guidance za SME i Claude (kao prose, ne parsiramo). Postojeći test playbook ih već ima — Claude čita prirodno.

---

## 8. Planner — agent loop

> Prvo provjeri Claude Agent SDK. Ako ne, custom:

```python
# core/planner.py

MAX_ITERATIONS = 10

def run(*, ticket, playbook, client=None, resume_action_id=None):
    mode = agent_config.effective_mode(playbook.id)
    tools = tools_for_playbook(playbook.metadata.get("allowed_skills", []))

    if resume_action_id:
        messages, iteration = pending_actions.load(resume_action_id)
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
                    continue

                if mode == "shadow":
                    print(f"[SHADOW] bi pozvao {block.name} s {block.input}")
                    results.append(_shadow_result(block.id))
                    continue

                if vr.requires_approval:
                    action_id = pending_actions.save(
                        ticket_id=ticket["key"],
                        skill_name=block.name,
                        skill_input=block.input,
                        messages=messages,
                        tool_use_id=block.id,
                    )
                    return PlannerResult(status="awaiting_approval",
                                         pending_action_id=action_id)

                skill = get_skill(block.name)
                result = skill.execute(**block.input)
                results.append(_format_result(block.id, result))

            messages.append({"role": "user", "content": results})
            continue

        return PlannerResult(status="failed", error=str(response.stop_reason))

    return PlannerResult(status="max_iterations")


def resume(action_id, *, approved, edited_input=None):
    state = pending_actions.load(action_id)
    if approved:
        skill = get_skill(state["skill_name"])
        result = skill.execute(**(edited_input or state["skill_input"]))
    pending_actions.delete(action_id)
    return run(ticket=..., playbook=..., resume_action_id=action_id)
```

---

## 9. Validator — tri provjere

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

    # 3. Treba approval?
    requires_approval = False
    if mode == "assisted" and skill.is_write:
        requires_approval = True
    if mode == "autonomous" and skill.is_write:
        if not playbook.metadata.get("agent_compatibility", {}).get("autonomous_resolve"):
            requires_approval = True

    return ValidationResult(ok=True, requires_approval=requires_approval)
```

Schema validira Anthropic SDK automatski.

---

## 10. Modes

| Mode | Read skill | Write skill |
|---|---|---|
| **shadow** | Print log, no execute | Print log, no execute |
| **assisted** | Auto-execute | **Uvijek HITL** |
| **autonomous** | Auto-execute | Auto ako `autonomous_resolve = true`, inače HITL |

Za demo pokazuješ: shadow → assisted progresija.

---

## 11. HITL state — minimalan

**Za demo ne treba puni audit log. Samo state za resume nakon ✓.**

```sql
CREATE TABLE pending_actions (
    id            TEXT PRIMARY KEY,        -- UUID
    ticket_id     TEXT NOT NULL,
    skill_name    TEXT NOT NULL,
    skill_input   TEXT NOT NULL,           -- JSON
    messages_blob TEXT NOT NULL,           -- JSON cijela povijest
    tool_use_id   TEXT NOT NULL,           -- za format_result
    iteration     INTEGER NOT NULL,
    created_at    TEXT NOT NULL
);
```

**Briše se nakon execute** (nije permanent audit trail).

> **Za produkciju kasnije**: proširi u `agent_actions` s validation/execution/decided_by/status povijesti. Za demo to nije potrebno.

---

## 12. HITL flow

```
Claude predloži write skill
       ↓
Validator OK, requires_approval=true
       ↓
pending_actions.save(...) → action_id
       ↓
Planner vrati AwaitingApproval(action_id)
       ↓
[Loop stane.]
       ↓
Frontend dohvati pending list
       ↓
UI: skill name, params, [✓] [✗] [Edit]
       ↓
User klikne ✓
       ↓
POST /api/actions/{id}/approve
       ↓
planner.resume(action_id, approved=True)
       ↓
Skill execute → tool_result → loop nastavlja
       ↓
pending_actions.delete(action_id)
```

---

## 13. Order of implementation — DEMO

```
DAY 1   Read Claude Agent SDK docs (1h) → odluka SDK ili custom
        Implementiraj jira_get_history (read-only, najsigurniji)
        Unit test
        
DAY 2   jira_add_public_comment + jira_transition
        validator.py
        pending_actions.py (4-polja tablica)
        
DAY 3   planner.py — agent loop (SDK ili custom)
        Mode gates (shadow/assisted)
        Resume mehanizam
        Manual test: skill se pokrene s mock Anthropic
        
DAY 4   backend/routers/actions.py
        Hook u core/agent_runner.py
        Test playbook ima allowed_skills (već ima)
        
DAY 5   frontend ActionApproval.tsx
        Integration u Agent Feed
        
DAY 6   E2E manual test s test playbook-om
        Polish za demo (loading states, error messages)
```

**Total: 5-6 dana.**

---

## 14. Acceptance kriteriji — DEMO

**Skills (Day 1-2)**
- [ ] 3 skills u REGISTRY (`get_history`, `add_public_comment`, `transition`)
- [ ] JSON schemas valid

**Validator + state (Day 2-3)**
- [ ] Validator odbija unknown / not-allowed
- [ ] `pending_actions` save/load/delete radi

**Planner (Day 3)**
- [ ] Shadow mode logira, ne izvršava
- [ ] Assisted mode pauzira write skills
- [ ] Resume nakon ✓ nastavi correctly
- [ ] `MAX_ITERATIONS = 10` ne dopušta runaway

**UI (Day 4-6)**
- [ ] Pending actions vidljive u UI
- [ ] Approve gumb radi end-to-end
- [ ] Reject gumb šalje Claude-u rejection
- [ ] Test playbook prolazi full flow (shadow → assisted s approval)

---

## 15. Što NIJE u demo (odgođeno za produkciju)

| Što | Kad |
|---|---|
| Full audit log (13 polja, history, analytics) | Kad ide u produkciju |
| Migration produkcijskih playbookova | Postupno nakon demo-a |
| Detaljne metrike / dashboard | Kad imamo volume |
| Streaming responses | Optimizacija nakon demo-a |
| Parallel tool execution | Kad treba |
| MCP server exposure | Kad customer želi vlastitog agenta |
| Hooks / subagents | Kad treba |
| Rate limiting | Kad imamo realan volume |

---

## 16. Failure modes — najkritičnije za demo

| Risk | Mitigation |
|---|---|
| Claude bira krivi tool | HITL gate + jasni descriptions |
| Tool izvan allow-liste | Validator hard reject |
| Infinite loop | `MAX_ITERATIONS = 10` |
| Schema invalid | Anthropic SDK validira pre-call |
| Skill crash | try/except → `SkillResult(ok=False)` |
| Demo dan: API outage | Pripremi snimku/screenshot kao backup |

---

## 17. Demo scenario — što pokazuješ

```
1. Otvori test ticket: "Trebam kopiju računa za parking, ref 3d5p7"

2. Mode = shadow
   → Agent processira ticket
   → UI prikaže "bi pozvao jira_add_public_comment, igeus_lookup, ..."
   → Ništa se ne izvršava
   → POKAŽEŠ: agent zna što napraviti, ali ne dira

3. Switch na mode = assisted
   → Agent processira isti ticket
   → Read skill auto-executes (igeus_lookup)
   → Write skill čeka odobrenje
   → UI: "jira_add_public_comment, body='...', [✓] [✗]"
   → POKAŽEŠ: HITL gate

4. Klikneš ✓
   → Akcija se izvrši (mock ili pravi Jira)
   → Loop nastavlja (sljedeća akcija ili end_turn)
   → POKAŽEŠ: end-to-end agent execution

5. Pokaži pending_actions tablicu
   → Vidi se record, briše se nakon execute
   → POKAŽEŠ: state management za pauzu
```

**5-minutna demo. Pokazuje cijeli koncept.**

---

## 18. Bottom line

```
DEMO verzija (5-6 dana):
  • 3 Skills (get_history, add_public_comment, transition)
  • Validator (3 provjere)
  • pending_actions tablica (4 polja)
  • Planner loop (SDK ili custom)
  • Frontend approval UI
  • E2E s test playbook-om

NE u demo-u:
  • Full audit log
  • Migration produkcijskih playbookova
  • Ručno pisanje bullete-a
  • Metrike / dashboard

Postojeće ostaje:
  • classify / retrieve / draft
  • 3-mode arhitektura (shadow/assisted/autonomous)
  • 122 playbooka rade bez izmjena

Produkcijski upgrade nakon demo-a:
  • pending_actions → agent_actions (full audit)
  • Postupno opt-in migration playbookova
  • Monitoring i metrike
  • Auto-generation SKILLS.md
```
