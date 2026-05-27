---
id: test-receipt-copy-request
name: test_receipt_copy_request
title: TEST — End User Requests Copy of Parking Receipt
description: Test playbook za demonstraciju Skills+bullet arhitekture. Krajnji korisnik traži kopiju računa za već plaćenu parking
  kartu (ima referencu transakcije ili broj kartice). Sigurno za testiranje — sve akcije su low-risk.
category: end_user/billing
ticket_class: end_user
issue_category: billing
resolution_pattern: receipt_sent
languages:
- hr
- en
country_focus:
- hr
status: draft
extraction_confidence: 1.0

# ============================================================
# NOVO — Skills allow-list. Claude smije zvati SAMO ove tools.
# Sve što nije ovdje navedeno je fizički nemoguće.
# ============================================================
allowed_skills:
  - igeus_lookup_transaction       # read-only, auto-execute OK
  - jira_add_public_comment        # write, HITL obavezno
  - jira_add_internal_comment      # write, low-risk, može auto
  - jira_transition                # write, HITL obavezno

agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Test playbook — sve write akcije HITL u prvoj fazi
---

# TEST — End User Requests Copy of Parking Receipt

## What this pattern is

Krajnji korisnik traži kopiju računa za parking transakciju koju je već platio. Obično ima referencu transakcije, datum, ili
broj kartice. Pattern je low-risk i pogodan za testiranje Skills mehanizma jer nema financijskih akcija.

## When this applies

- Korisnik šalje email/ticket s pitanjem "trebam račun za parking od ..."
- Korisnik ima referencu transakcije ili dovoljno podataka za lookup
- Nema spora oko iznosa — samo treba kopiju računa

## Resolution bullets

```
[res-00001] :: Stigao zahtjev za kopiju računa, treba lookup transakcije
  when: status="new" and intent="receipt_copy_request"
  skill: igeus_lookup_transaction
  skill_params:
    reference: "{extracted_reference}"
    customer_email: "{ticket.reporter_email}"
  safety:
    human_approval_required: false       # read-only, sigurno
    rate_limit_per_hour: 60

[res-00002] :: Transakcija nađena, pošalji račun korisniku
  when: igeus_lookup.found == true
  skill: jira_add_public_comment
  skill_params:
    template: "receipt-found-hr"
    fields:
      transaction_code: "{igeus_lookup.code}"
      amount: "{igeus_lookup.amount}"
      date: "{igeus_lookup.date}"
      attach_pdf: true
  safety:
    human_approval_required: true        # ide kupcu — uvijek čovjek odobri
    rate_limit_per_hour: 30

[res-00003] :: Transakcija NIJE nađena, javi korisniku da treba više podataka
  when: igeus_lookup.found == false
  skill: jira_add_public_comment
  skill_params:
    template: "receipt-not-found-hr"
  safety:
    human_approval_required: true

[res-00004] :: Račun poslan, dodaj internal note za tracking
  when: previous_skill == "jira_add_public_comment" and previous_status == "executed"
  skill: jira_add_internal_comment
  skill_params:
    text: "Račun automatski poslan korisniku. Transaction: {igeus_lookup.code}"
  safety:
    human_approval_required: false       # internal note, low-risk

[res-00005] :: Zatvori ticket nakon slanja računa
  when: receipt_sent == true
  skill: jira_transition
  skill_params:
    target_status: "Resolved"
    resolution: "Done"
  safety:
    human_approval_required: true        # closing ticket — uvijek čovjek
```

## Must not automate

- **Slanje računa za pogrešnu transakciju** — bullet [res-00002] traži human approval
- **Zatvaranje ticketa bez potvrde** — bullet [res-00005] traži human approval
- **Bilo kakva financijska akcija** — nema skill u allowed_skills za to, fizički nemoguće

## Test scenariji za QA

| Scenarij | Očekivano ponašanje |
|---|---|
| Korisnik šalje referencu transakcije, lookup uspješan | [res-00001] auto → [res-00002] HITL → [res-00004] auto → [res-00005] HITL |
| Korisnik šalje referencu, lookup neuspješan | [res-00001] auto → [res-00003] HITL |
| Korisnik šalje bez reference | Classifier ne match-a ovaj playbook, fallback na ljudsku obradu |
| Pokušaj zvati skill koji nije u allowed_skills | Validator reject prije execute |
| Pokušaj poslati račun bez approval | Validator queue za approval, ne execute |

## Evidence

Ovo je TEST playbook — nema real evidence tickets. Koristi se za:
- Unit test Skills registry
- Integration test planner-a
- E2E test approval UI

## Agent compatibility

- **Status:** `draft` — TEST playbook, ne ide u produkciju
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False` — sve write akcije HITL
- **Note:** Sigurno za testiranje, low-risk akcije, jasne safety gates
