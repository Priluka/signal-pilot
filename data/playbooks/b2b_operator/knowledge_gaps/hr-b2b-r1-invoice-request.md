---
id: hr-b2b-r1-invoice-request
name: hr_b2b_r1_invoice_request
title: Croatian B2B partners requesting R1 (VAT) invoices for Bmove parking payments
description: Croatian business users and B2B partners repeatedly contact support asking how to obtain R1 (VAT-compliant) invoices
  for parking payments made via the Bmove application. A significant sub-pattern involves requests to retroactively convert
  already-issued invoices to R1 format, which is not legally permissible. Resolution typically involves educating users about
  registering as a business account or configuring their personal account to receive monthly consolidated R1 invoices.
category: b2b_operator/knowledge_gaps
ticket_class: b2b_partner
issue_category: knowledge_gap
resolution_pattern: user_education
languages:
- hr
country_focus:
- hr
status: active
cluster_id: BS:b2b_partner|croatia|no_label:c0
project_key: BS
cluster_size: 50
cluster_size_dedup: 50
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.95
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.98
median_resolution_minutes: 634.5
p95_resolution_minutes: 17448.299999999992
cannot_reproduce_rate: 0.0
data_window_start: '2023-07-10'
data_window_end: '2026-04-22'
annual_hours_saved: 2.2
roi:
  baseline_active_hours: 7.5
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 3.0
  deflection_hours_range:
  - 2.1
  - 3.9
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 2.2
  agent_assist_hours_range:
  - 1.6
  - 2.9
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 2.2
  product_fix_hours_range:
  - 1.5
  - 2.9
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: low
  autonomous_resolve_hours_midpoint: 0.5
  autonomous_resolve_hours_range:
  - 0.3
  - 0.7
  autonomous_resolve_max_safe_volume_pct: 0.2
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-44318
- BS-37424
- BS-37042
- BS-10158
- BS-19550
- BS-21807
- BS-24544
- BS-17269
- BS-26492
- BS-42480
- BS-50297
- BS-42612
- BS-13807
- BS-10350
- BS-45868
- BS-17662
- BS-51266
- BS-49055
canonical_examples:
- BS-44318
- BS-10350
- BS-50297
vendor_dependency:
  vendor_name: null
  involves_vendor: false
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: User education — safe for self-service deflection
  autonomous_resolve_max_safe_volume_pct: 0.2
  autonomous_resolve_narrow_use_case: Automated reply to users asking only how to register a business account and receive
    R1 invoices going forward (no retroactive conversion request, no backend account investigation required).
  autonomous_resolve_safety_constraints:
  - Never autonomously confirm or deny that a retroactive invoice conversion has been or can be processed — legal and compliance
    risk.
  - Exclude tickets where backend prepaid balance or invoice delivery status verification is required (action 4).
  - Require human review for any ticket where the user disputes a legal policy or expresses dissatisfaction.
  - Limit autonomous resolution to informational replies; do not trigger account-type changes automatically.
  - Scope to Croatian-language tickets only to avoid misrouting in other locales.
related_playbooks:
- croatia-b2b-parking-card-refund-request
- croatia-sms-parking-payment-failure
- croatia-ticketless-best-in-parking-knowledge-gap
- croatia-ticketless-rental-car-ghost-charge
- croatian-b2b-parking-ticket-storno-refund
- croatian-b2b-parking-ticket-storno-request
- croatian-invoice-download-request
- expired-card-deletion-ticketless-link
- hr-b2b-parking-card-cancellation-refund
- hr-b2b-parking-card-storno-refund
- hr-b2b-parking-ticket-storno-refund
- igeus-portal-access-credential-management
- italian-ticketless-setup-and-payment-issues
- phonzie-to-bmove-credit-refund-request
- prepaid-top-up-and-usage-issues
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
# Skills enabled — reads auto-execute, writes are HITL.
allowed_skills:
  - graylog_search
  - parkis_lookup
  - skidata_session_lookup
  - bmove_user_lookup
  - datatrans_transaction
  - jira_get_history
  - jira_add_internal_comment
  - jira_add_public_comment
  - jira_transition
---

# Croatian B2B partners requesting R1 (VAT) invoices for Bmove parking payments

## What this pattern is

Croatian business users and B2B partners repeatedly contact support asking how to obtain R1 (VAT-compliant) invoices for parking payments made via the Bmove application. A significant sub-pattern involves requests to retroactively convert already-issued invoices to R1 format, which is not legally permissible. Resolution typically involves educating users about registering as a business account or configuring their personal account to receive monthly consolidated R1 invoices.

## When this applies

- User wants R1 invoice for parking payment but has not registered as a business user
- User requests retroactive conversion of existing invoice to R1 format
- User cannot download or access R1 invoice in the app
- User asks whether Bmove supports e-račun (eInvoice / Fiscalization 2.0) for public procurement obligations
- User has registered as individual (fizička osoba) instead of legal entity (pravna osoba)
- User confused about prepaid top-up confirmation vs. monthly R1 invoice
- User changes phone and needs to re-link business account

## Typical resolution flow

1. User submits ticket via app feedback, email, or forwarded partner request asking about R1 invoices
2. Support checks whether user is registered as business (pravna osoba) or individual (fizička osoba)
3. If not registered as business: support provides registration link (https://app.bmove.com/registracija/pravna-osoba/) and PDF instructions
4. If already registered as individual: support instructs user to update billing details in web app (app.bmove.com) under account settings
5. If requesting retroactive R1: support explains this is legally not possible for already fiscalized invoices
6. If asking about e-račun/Fiscalization 2.0: support clarifies prepaid top-up VAT exemption and monthly consolidated R1 invoice delivery mechanism
7. Support provides instructions link (https://app.bmove.com/downloads/upute-poslovni.pdf) and closes ticket

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Provide business registration link and PDF usage instructions | support_agent | email/ticket system | 5 min |
| Explain retroactive R1 invoice conversion is legally not possible | support_agent | email/ticket system | 5 min |
| Clarify prepaid top-up VAT exemption and monthly consolidated R1 invoice process | support_agent | email/ticket system | 10 min |
| Verify internal Django/backend prepaid balance and invoice delivery status | support_agent | Django admin backend | 15 min |
| Instruct user to enable file access permissions for Bmove app on mobile device | support_agent | email/ticket system | 3 min |

## Evidence

Derived from 50 tickets in cluster `BS:b2b_partner|croatia|no_label:c0`. Direct quotes from 6 representative tickets:

- `BS-44318` _[hr]_: "Zanima me da li putem Vaše aplikacije korisnici mogu plaćati i dobivati R1 račun?"
- `BS-10350` _[hr]_: "mogućnost prebacivanja već izdanih i fiskaliziranih računa u R1 nije moguće"
- `BS-50297` _[hr]_: "nadoplata Bmove prepaida je bez PDV-a jer je to višenamjenski vrijednosni kupon koji je oslobođen PDV-a temeljem čl. 11 Zakona o porezu na dodanu vrijednost"
- `BS-49055` _[hr]_: "Mi smo javni naručitelj i imamo obvezu zaprimanja e-računa. Da li možete ispostavljati e-račun?"
- `BS-17269` _[hr]_: "korisnički račun po mail adresi y****@yahoo.com je registriran kao fizička osoba, ne kao pravna osoba"
- `BS-37042` _[hr]_: "svakog 10. u mjesecu stiže zbirni račun gdje su sve prepaid kupovine za poslovne korisnike od prethodnog mjeseca"

## Cluster statistics

- **Volume:** 50 tickets total (50 unique semantic events after dedup)
- **Frequency:** 0.98 tickets/month (over data window 2023-07-10 → 2026-04-22)
- **Median resolution:** 10.6 hours
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~7.5 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~2.2 (range [1.6, 2.9])
- **Time reduction per ticket:** ~30% (range [21%, 39%])
- **Feasibility:** 0.90
- **Rationale:** All five resolution actions are templatable: the business registration link, the legal explanation of retroactive conversion, the VAT exemption/monthly invoice clarification, the backend verification steps, and the mobile permissions instruction are consistent across tickets. An agent-assist tool can surface the correct response block within seconds, reducing active minutes by roughly 30% per ticket.
- **Validation:** Run a 3-week shadow-mode pilot where the assist tool suggests pre-drafted response blocks for R1 tickets; measure agent acceptance rate (target ≥70%) and average active-minutes-per-ticket versus the 38-minute baseline.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `low`
  - Sprints estimate: ~1.5 (range [1.1, 1.9])
- **Hours eliminated per year:** ~2.2 (range [1.54, 2.86])
- **Root cause:** There is no bug; the pattern arises from insufficient in-app guidance for Croatian B2B users at the point of payment and account setup — users are not informed proactively that R1 invoices require prior business account registration and that retroactive conversion is legally prohibited.
- **Rationale:** Adding a proactive in-app prompt at account creation and at first payment — explaining B2B registration, R1 invoice eligibility, and the legal constraint on retroactive conversion — would eliminate the uninformed-user sub-pattern. Full elimination is unlikely because some users will ignore prompts or have edge-case questions about their specific situation.
- **Validation:** Product team scopes the in-app tooltip/banner change in a sprint planning session; after release, compare R1-cluster ticket volume over a 90-day window against the prior 12-month rate to validate hours eliminated.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~3 (range [2.1, 3.9])
- **Form:** `help_center`
- **Deflection rate:** ~40% (range [28%, 52%])
- **Feasibility:** 0.80
- **Rationale:** The pattern is almost entirely knowledge-gap/user-education with stable, rule-based answers (business registration steps, legal impossibility of retroactive R1 conversion, VAT exemption explanation), making it well-suited for a structured help-center article or in-app FAQ. However, some users may still contact support due to language nuance or personal account configuration needs, capping deflection below 50%.
- **Validation:** Deploy a Croatian-language help-center article covering R1 invoice registration, retroactive conversion policy, and monthly consolidated invoice setup; track ticket inflow for the R1 cluster over 6 weeks pre/post and measure deflection rate against baseline of 11.8/year.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~0.5 (range [0.35, 0.65])
- **Narrow use case:** Automated reply to users asking only how to register a business account and receive R1 invoices going forward (no retroactive conversion request, no backend account investigation required).
- **Safety constraints:**
  - Never autonomously confirm or deny that a retroactive invoice conversion has been or can be processed — legal and compliance risk.
  - Exclude tickets where backend prepaid balance or invoice delivery status verification is required (action 4).
  - Require human review for any ticket where the user disputes a legal policy or expresses dissatisfaction.
  - Limit autonomous resolution to informational replies; do not trigger account-type changes automatically.
  - Scope to Croatian-language tickets only to avoid misrouting in other locales.
- **Rationale:** Low ticket volume (11.8/year) and mixed complexity — especially the legally sensitive retroactive-conversion sub-pattern — make full autonomous resolution risky and low ROI; the narrow safe scope (pure registration-guidance tickets) is estimated at ~20% of the cluster, yielding modest savings. The primary value of automation here is consistency and faster response time, not hours saved.
- **Validation:** Pilot autonomous replies on the narrowest classification (intent = 'how to get R1 invoices going forward' with no retroactive flag) for 8 weeks; accept only if CSAT for auto-resolved tickets is ≥ CSAT baseline and zero escalations result from incorrect legal statements.

### Risks

- **Compliance concerns:**
  - Croatian VAT/fiscalization law prohibits retroactive invoice conversion to R1 format; any automation that implies otherwise creates legal exposure for Bmove.
  - Automated communications about VAT invoice eligibility must reflect current Croatian tax regulation; changes in law require prompt update of all automated content.
  - Prepaid top-up VAT exemption rules must be accurately represented; incorrect statements could mislead B2B partners about deductible expenses.
- **Must not automate:**
  - Confirmation or processing of retroactive R1 invoice conversion requests.
  - Backend prepaid balance verification or invoice delivery status investigation (requires authenticated internal system access and human judgment).
  - Any response that could be construed as legal or tax advice beyond factual policy description.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.95)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `True`
- **RAG-consumable:** `True`
- **Note:** User education — safe for self-service deflection

