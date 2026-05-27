# Skills Catalog

_Planirani Skills za agentski sloj. Vidi `docs/AGENT_IMPLEMENTATION.md` za redoslijed gradnje._

## Implementacijski status

| Status | Skills |
|---|---|
| **Implementirano** | `jira_add_internal_comment` |
| **Planirano** (vidi AGENT_IMPLEMENTATION.md) | svi ostali u nastavku |

## Kako koristiti

1. SME odabire koje skills su dozvoljene u playbook-u
2. Copy-paste ime u `allowed_skills:` listu u YAML frontmatter-u

```yaml
allowed_skills:
  - igeus_lookup_transaction
  - jira_add_public_comment
```

## Legenda

- **R** = read-only (siguran auto-execute)
- **W** = write (mijenja state)
- **HITL** = Human In The Loop (čovjek mora odobriti)
- **AUTO** = može auto-execute ako bullet dozvoljava

---

## IGeus skills

### `igeus_lookup_transaction` — **R, AUTO**

Look up a parking transaction in IGeus by reference code or customer details.
Returns transaction code, amount, date, status, card type.

**Parametri:**
| Polje | Tip | Required | Opis |
|---|---|---|---|
| `reference` | string | yes | Transaction code, npr. `3d5p7-py22e-b25` |
| `customer_email` | string | no | Cross-reference by email |
| `amount` | number | no | Cross-reference by amount (EUR) |

**Use case:** Kupac traži kopiju računa / agent treba verificirati transakciju prije refunda.

---

### `igeus_storno_card` — **W, HITL**

Cancels (stornira) a parking card in IGeus. Irreversible action.

**Parametri:**
| Polje | Tip | Required | Opis |
|---|---|---|---|
| `transaction_code` | string | yes | IGeus transaction code |
| `reason` | enum | yes | `duplicate` / `wrong_zone` / `wrong_plate` / `customer_request` |

**Safety constraints:**
- Uvijek human approval — pogrešan storno = direktna šteta korisniku
- One card per call (ne batch)
- Audit log obavezan

**Use case:** ZGH potvrdio cancel, treba storno u IGeus-u prije refunda.

---

## Jira skills

### `jira_get_history` — **R, AUTO**

Returns full history (comments, status changes) for a Jira ticket.

**Parametri:**
| Polje | Tip | Required | Opis |
|---|---|---|---|
| `ticket_id` | string | yes | Jira key, npr. `BS-45949` |

**Use case:** Agent treba kontekst prije nego predloži akciju.

---

### `jira_add_public_comment` — **W, HITL**

Adds a public comment visible to the customer.

**Parametri:**
| Polje | Tip | Required | Opis |
|---|---|---|---|
| `ticket_id` | string | yes | Jira key |
| `body` | string | yes | Comment text |
| `template` | string | no | Template ID (overrides body) |
| `language` | enum | no | `hr` / `en` / `de` / `it` / `sl` |

**Safety constraints:**
- Uvijek HITL — ide kupcu
- Rate limit: 30 / sat per ticket

**Use case:** Slanje odgovora kupcu (draft + send).

---

### `jira_add_internal_comment` — **W, AUTO**

Adds an internal note. NOT visible to customer.

**Parametri:**
| Polje | Tip | Required | Opis |
|---|---|---|---|
| `ticket_id` | string | yes | Jira key |
| `body` | string | yes | Internal note text |
| `mention` | string | no | User to @-mention, npr. `Lidija Petricević` |

**Use case:** Tag payment colleague za refund. Tracking note. Internal handoff.

---

### `jira_add_label` — **W, AUTO**

Adds a label to a ticket.

**Parametri:**
| Polje | Tip | Required | Opis |
|---|---|---|---|
| `ticket_id` | string | yes | Jira key |
| `label` | string | yes | Label name |

**Safety constraints:**
- Allowed labels samo iz whitelista (npr. `refund-pending`, `awaiting-vendor`)

**Use case:** Markiranje za routing / filtering.

---

### `jira_transition` — **W, HITL**

Change ticket status (Open → In Progress → Resolved itd).

**Parametri:**
| Polje | Tip | Required | Opis |
|---|---|---|---|
| `ticket_id` | string | yes | Jira key |
| `target_status` | enum | yes | `In Progress` / `Waiting for vendor` / `Waiting for customer` / `Resolved` / `Closed` |
| `resolution` | enum | no | `Done` / `Won't Fix` / `Duplicate` |
| `comment` | string | no | Optional transition comment |

**Safety constraints:**
- Uvijek HITL za `Resolved` / `Closed`
- Auto OK za `In Progress` / `Waiting for ...`

**Use case:** Premjesti ticket u sljedeću fazu workflow-a.

---

### `jira_escalate` — **W, HITL**

Escalate ticket to a different team.

**Parametri:**
| Polje | Tip | Required | Opis |
|---|---|---|---|
| `ticket_id` | string | yes | Jira key |
| `target_team` | enum | yes | `Finance` / `Engineering` / `Legal` / `Tier-2` |
| `reason` | string | yes | Why escalating |

**Use case:** Kompleksan slučaj / iznad agentovih ovlasti.

---

## Što NIJE skill (i nikad neće biti)

| Akcija | Zašto ne |
|---|---|
| Bank transfer execution | Financijska — uvijek ovlašteni čovjek |
| Direct database write | Nema audit putanja — kroz Jira ide |
| Customer data export | GDPR — treba poseban consent flow |
| External vendor API write | Out of scope — vendor ima vlastiti sistem |
| Bulk operations | Risk multiplikator — radimo one-at-a-time |

---

## Brzi cheat sheet za playbook

| Trebaš... | Skill |
|---|---|
| Pronaći transakciju | `igeus_lookup_transaction` |
| Stornirati karticu | `igeus_storno_card` (HITL) |
| Vidjeti ticket history | `jira_get_history` |
| Odgovoriti kupcu | `jira_add_public_comment` (HITL) |
| Interna bilješka / tag kolegu | `jira_add_internal_comment` |
| Označiti ticket | `jira_add_label` |
| Zatvoriti / premjestiti ticket | `jira_transition` |
| Eskalirati | `jira_escalate` |

---

## Versioning

| Verzija | Datum | Promjena |
|---|---|---|
| v0.1 | 2026-05-27 | Initial catalog — 8 skills (1 implementiran, 7 planiranih) |

_Auto-regen planirano kao dio implementacije (vidi AGENT_IMPLEMENTATION.md). Trenutno ručno održavan._
