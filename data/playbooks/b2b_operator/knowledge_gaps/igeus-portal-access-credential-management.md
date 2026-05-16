---
id: igeus-portal-access-credential-management
name: igeus_portal_access_credential_management
title: Croatian B2B Partners Requesting IGeus Portal Access or Credential Reset
description: Croatian B2B parking concession partners (koncesionari) repeatedly contact Bmove support because they cannot
  log in to the IGeus portal, need new accounts created, or require password resets. The most common triggers are forgotten
  or expired one-time password links, new staff needing accounts, system reinstallation causing lost credentials, and shared
  accounts being replaced with individual ones. Support resolves issues by creating new accounts or generating new one-time
  password links via onetimesecret.com or password.link.
category: b2b_operator/knowledge_gaps
ticket_class: b2b_partner
issue_category: knowledge_gap
resolution_pattern: user_education
languages:
- hr
country_focus:
- hr
status: active
cluster_id: BS:b2b_partner|croatia|koncesionar:c0
project_key: BS
cluster_size: 17
cluster_size_dedup: 17
sample_size_used: 17
extraction_schema: v1.0
extraction_confidence: 0.93
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.33
median_resolution_minutes: 172.0
p95_resolution_minutes: 12796.399999999976
cannot_reproduce_rate: 0.0
data_window_start: '2023-04-29'
data_window_end: '2024-09-18'
annual_hours_saved: 0.6
roi:
  baseline_active_hours: 2.3
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.7
  deflection_hours_range:
  - 0.5
  - 0.9
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.6
  agent_assist_hours_range:
  - 0.4
  - 0.7
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 1.7
  product_fix_hours_range:
  - 1.2
  - 2.2
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.2
  autonomous_resolve_hours_range:
  - 0.2
  - 0.3
  autonomous_resolve_max_safe_volume_pct: 0.2
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-12772
- BS-15454
- BS-15564
- BS-17309
- BS-20006
- BS-23468
- BS-27062
- BS-7767
- BS-8477
- BS-17538
- BS-10117
- BS-22930
- BS-16477
- BS-10295
- BS-21010
- BS-26990
- BS-21896
canonical_examples:
- BS-15454
- BS-15454
- BS-27062
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
  autonomous_resolve_narrow_use_case: Automated one-time password link generation and delivery for existing verified accounts
    only
  autonomous_resolve_safety_constraints:
  - Must only act on verified, existing account holders — never create new accounts autonomously
  - Requester identity must be confirmed against known partner contact list before link is sent
  - One-time link must be sent only to the pre-registered email on record, not to an email supplied in the ticket
  - Permission changes (add/revoke access) must always involve a human agent
  - All autonomous actions must be logged and auditable for GDPR compliance
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
- hr-b2b-r1-invoice-request
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
---

# Croatian B2B Partners Requesting IGeus Portal Access or Credential Reset

## What this pattern is

Croatian B2B parking concession partners (koncesionari) repeatedly contact Bmove support because they cannot log in to the IGeus portal, need new accounts created, or require password resets. The most common triggers are forgotten or expired one-time password links, new staff needing accounts, system reinstallation causing lost credentials, and shared accounts being replaced with individual ones. Support resolves issues by creating new accounts or generating new one-time password links via onetimesecret.com or password.link.

## When this applies

- User cannot log in to IGeus portal (credentials not recognised)
- One-time password link has expired or already been used
- New employee needs an IGeus portal account created
- Computer reinstallation causes loss of saved credentials
- Shared account is being replaced with individual accounts
- User does not know the IGeus portal URL
- Passphrase required on onetimesecret link not understood by user
- Browser or device compatibility issue causes login spinner with no error message

## Typical resolution flow

1. B2B partner contacts support reporting inability to access IGeus portal
2. Support agent clarifies whether issue is accessing the URL or logging in with credentials
3. If login issue: support resets password and generates a new one-time secret link
4. Support sends username and one-time password link to the user via email
5. User opens the link, reveals the password, and is advised to record it immediately
6. If link fails or passphrase is required, support generates a new link or provides the password in plaintext as fallback
7. User confirms successful login and ticket is closed

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Clarify whether user cannot reach portal URL or cannot authenticate | support_agent | email | 5 min |
| Create new user account or reset existing account password | support_agent | IGeus admin portal | 10 min |
| Generate and send one-time password link (onetimesecret.com or password.link) | support_agent | onetimesecret.com / password.link | 5 min |
| Provide passphrase hint or send plaintext password as fallback if link fails | support_agent | email | 5 min |
| Add or revoke portal access permissions for specific users | support_agent | IGeus admin portal | 10 min |

## Evidence

Derived from 17 tickets in cluster `BS:b2b_partner|croatia|koncesionar:c0`. Direct quotes from 7 representative tickets:

- `BS-15454` _[hr]_: "Problem je sa prijavom, kao da ne prepoznaje više sve elemente prijave i lozinku."
- `BS-15454` _[hr]_: "postavili smo Vam novu lozinku, u nastavku šaljemo podatke za prijavu... link za lozinku je jednokratan. Kada ga otvorite, odmah si zapišite lozinku."
- `BS-27062` _[hr]_: "Ne radi link za lozinku. Molim da ponovite"
- `BS-26990` _[hr]_: "traži mi da upišem PASSPHRASE? To je mveza? Nakon sta to upišem kaze da postoji greška"
- `BS-7767` _[hr]_: "molim vas kreiranje korisničkog imena i lozinke za pristup na iGeus portal za korisnika BENEDIKT BLAGDAN"
- `BS-15564` _[hr]_: "na računalu samo mi se krug na ekranu zavrti i izbriše sve podatke koje sam upisao, i ne napiše nikakvu poruku ni da mi je username kriv ni lozinka."
- `BS-21010` _[hr]_: "molim Vas da mi dodijelite novo korisničko ime i lozinku, obzirom da je napravljana nova instalacija na računalu, a nemam prethodnih podataka."

## Cluster statistics

- **Volume:** 17 tickets total (17 unique semantic events after dedup)
- **Frequency:** 0.33 tickets/month (over data window 2023-04-29 → 2024-09-18)
- **Median resolution:** 2.9 hours
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~2.3 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.6 (range [0.41, 0.74])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.75
- **Rationale:** A canned-response template plus a guided checklist (URL reachable? existing account? new staff?) would reduce the clarification and drafting steps, shaving roughly 8–9 minutes per ticket primarily from actions 1, 3, and 4. The account-creation and permission steps still require manual portal access.
- **Validation:** Run shadow-mode assist (pre-filled response drafts and a decision-tree checklist shown to agents) for 3 weeks on incoming tickets in this cluster; measure average handle time before and after to validate reduction estimate.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~1.7 (range [1.211, 2.249])
- **Root cause:** There is no self-service account creation or password-reset flow in the IGeus portal; partners have no mechanism to recover access without contacting Bmove support. The issue is a missing product capability rather than a bug.
- **Rationale:** Adding a self-service password-reset flow and an admin-facing account-creation form within the IGeus portal would eliminate the majority of agent actions; however, permission management and edge cases (system reinstall, shared-to-individual account migration) would still occasionally require support contact.
- **Validation:** Engineering team should scope against existing IGeus identity management APIs or SSO integration options, produce a spike estimate in sprint planning, and validate by measuring support tickets in the cluster for two quarters post-launch.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.7 (range [0.483, 0.897])
- **Form:** `help_center`
- **Deflection rate:** ~30% (range [21%, 39%])
- **Feasibility:** 0.65
- **Rationale:** A step-by-step help center article covering portal URL confirmation, self-service password reset, and one-time link expiry could resolve a subset of simpler cases without agent contact. However, many triggers involve new-account creation or permission changes that inherently require agent action, limiting deflection ceiling.
- **Validation:** Publish a targeted help article and track ticket volume for this cluster over 8 weeks; compare pre/post monthly ticket rate to estimate actual deflection.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~0.2 (range [0.161, 0.299])
- **Narrow use case:** Automated one-time password link generation and delivery for existing verified accounts only
- **Safety constraints:**
  - Must only act on verified, existing account holders — never create new accounts autonomously
  - Requester identity must be confirmed against known partner contact list before link is sent
  - One-time link must be sent only to the pre-registered email on record, not to an email supplied in the ticket
  - Permission changes (add/revoke access) must always involve a human agent
  - All autonomous actions must be logged and auditable for GDPR compliance
- **Rationale:** Autonomous resolution is narrowly viable only for the password-reset sub-case where the account already exists and the requester's identity can be verified programmatically; account creation, permission management, and fallback plaintext password scenarios all carry too much risk for full automation. The low annual frequency (4 tickets/year) means the absolute hours saved are minimal even in an optimistic scenario.
- **Validation:** Pilot with a supervised automation that proposes the one-time link action to an agent for one-click approval for 6 weeks; escalate to fully autonomous only if zero identity-verification errors are observed and GDPR review is completed.

### Risks

- **Compliance concerns:**
  - GDPR (EU/Croatian law): credentials and account data belong to B2B partners; any automated handling of password-reset links must ensure data is sent only to verified, registered contacts and not stored beyond necessity
  - Sending plaintext passwords (action 4 fallback) is a security anti-pattern and should be eliminated regardless of automation strategy
  - One-time secret links (onetimesecret.com, password.link) rely on third-party services; their data-processing terms should be reviewed for GDPR adequacy
- **Must not automate:**
  - New account creation for unverified or unrecognised requesters
  - Addition or revocation of portal access permissions
  - Sending credentials to any email address other than the pre-registered contact on file
  - Plaintext password transmission via any channel

## Agent compatibility

- **Status:** `active` (extraction confidence 0.93)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `True`
- **RAG-consumable:** `True`
- **Note:** User education — safe for self-service deflection

