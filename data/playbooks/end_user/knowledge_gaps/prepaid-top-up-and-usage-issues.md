---
id: prepaid-top-up-and-usage-issues
name: prepaid_top_up_and_usage_issues
title: End users unable to top up or use Bmove prepaid account balance for parking payments
description: End users in Croatia report difficulties either topping up their Bmove prepaid account (card transaction declined/stuck,
  card top-up feature broken in mobile app) or failing to use existing prepaid balance when purchasing parking tickets (payment
  defaults to bank card instead of prepaid account). A secondary sub-pattern involves users not knowing how to request a bank-transfer
  invoice (ponuda) to top up via internet banking.
category: end_user/knowledge_gaps
ticket_class: end_user
issue_category: knowledge_gap
resolution_pattern: user_education
languages:
- hr
- en
country_focus:
- hr
- other
status: active
cluster_id: BS:end_user|no_value|prepaid:c0
project_key: BS
cluster_size: 25
cluster_size_dedup: 25
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.88
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.49
median_resolution_minutes: 5907.0
p95_resolution_minutes: 81379.19999999995
cannot_reproduce_rate: 0.0
data_window_start: '2022-05-03'
data_window_end: '2023-03-18'
annual_hours_saved: 0.6
roi:
  baseline_active_hours: 2.2
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.5
  deflection_hours_range:
  - 0.3
  - 0.6
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.6
  agent_assist_hours_range:
  - 0.4
  - 0.7
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 1.1
  product_fix_hours_range:
  - 0.8
  - 1.4
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.1
  autonomous_resolve_hours_range:
  - 0.1
  - 0.2
  autonomous_resolve_max_safe_volume_pct: 0.15
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-802
- BS-2672
- BS-2841
- BS-488
- BS-4196
- BS-5681
- BS-5358
- BS-5481
- BS-4596
- BS-5921
- BS-5807
- BS-4589
- BS-6759
- BS-3974
- BS-6060
- BS-3665
- BS-3301
- BS-6414
canonical_examples:
- BS-802
- BS-5481
- BS-5681
vendor_dependency:
  vendor_name: CorvusPay
  involves_vendor: true
  typical_wait_days: 3
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: User education — safe for self-service deflection
  autonomous_resolve_max_safe_volume_pct: 0.15
  autonomous_resolve_narrow_use_case: Auto-send the ponuda (bank-transfer invoice) generation walkthrough to users who explicitly
    ask how to top up via internet banking, when no CorvusPay error code is present.
  autonomous_resolve_safety_constraints:
  - Must not autonomously handle tickets involving a declined card or CorvusPay payment error without agent review, as root
    cause may be a vendor-side fault.
  - Must not access or modify account balance or payment records; read-only balance lookup only.
  - Must escalate any ticket where the user reports a financial discrepancy or missing funds to a human agent.
  - Auto-resolution confirmation message must include a clear human-escalation path.
  - Vendor (CorvusPay) outage or degraded-service signals must immediately suspend autonomous resolution and queue for agent
    handling.
related_playbooks:
- app-payment-failure-parking-ticket
- bmove-app-feedback-mixed-issues__7950cd
- croatia-ticketless-best-in-parking-knowledge-gap
- croatia-ticketless-rental-car-ghost-charge
- croatian-invoice-download-request
- expired-card-deletion-ticketless-link
- hr-b2b-r1-invoice-request
- hr-open-session-after-garage-exit
- hr-parking-ticket-fine-after-paid-app
- igeus-portal-access-credential-management
- italian-ticketless-setup-and-payment-issues
- parking-fine-received-despite-valid-payment
- parking-payment-failure-end-user
- phonzie-to-bmove-credit-refund-request
- slovakia-parking-payment-failure-no-ticket
- ticketless-open-session-at-exit__d8d1ba
- ticketless-open-session-at-exit__fd04ac
- wrong-parking-ticket-purchase-redirect
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

# End users unable to top up or use Bmove prepaid account balance for parking payments

## What this pattern is

End users in Croatia report difficulties either topping up their Bmove prepaid account (card transaction declined/stuck, card top-up feature broken in mobile app) or failing to use existing prepaid balance when purchasing parking tickets (payment defaults to bank card instead of prepaid account). A secondary sub-pattern involves users not knowing how to request a bank-transfer invoice (ponuda) to top up via internet banking.

## When this applies

- User has topped up prepaid account but parking purchase still charges their bank card
- User cannot top up prepaid account via credit card in the mobile app (CorvusPay redirect stuck or card declined)
- User does not know how to select prepaid as payment method at checkout
- User does not know how to generate a bank-transfer invoice (ponuda) for prepaid top-up
- Topped-up funds not immediately visible on account (bank processing delay)
- Prepaid voucher (bon) shows as expired or is not visible in app after purchase

## Typical resolution flow

1. User tops up or attempts to top up prepaid account
2. User encounters error or cannot locate funds / correct payment method
3. User submits support ticket via app feedback form or email
4. Support agent checks account balance and transaction status in back-end
5. Agent instructs user how to select Bmove prepaid at checkout screen, or explains top-up alternatives (web app, Tiska kiosk)
6. If CorvusPay issue, agent confirms known bug and advises workaround (use already-saved card or web app)
7. If bank-transfer ponuda needed, agent explains how to generate it via web app
8. Ticket closed once balance confirmed or user educated

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Check user account balance and recent transaction status | support_agent | Bmove back-end / admin panel | 5 min |
| Educate user on selecting Bmove prepaid as payment method before tapping 'Kupi kartu' | support_agent | email/ticket comment | 5 min |
| Advise workaround for CorvusPay mobile redirect bug (use web app or already-saved card or Tiska kiosk voucher) | support_agent | email/ticket comment | 5 min |
| Guide user to generate bank-transfer invoice (ponuda) via web app at app.bmove.com | support_agent | email/ticket comment | 5 min |
| Close ticket after confirming balance is present or issue resolved | support_agent | Jira / ticketing system | 2 min |

## Vendor dependency

- **Vendor:** CorvusPay
- **Typical wait:** 3 day(s)

## Evidence

Derived from 25 tickets in cluster `BS:end_user|no_value|prepaid:c0`. Direct quotes from 7 representative tickets:

- `BS-802` _[hr]_: "kako napraviti da mi se skidaju novci sa bona koji sam uplatila, 100kn, a NE sa bankovne kartice?"
- `BS-5481` _[hr]_: "uplatila sam 10 eur kao prepaid u aplikaciju ali mi se to ne nudi kao nacin placanja pri kupnji karte. ne mogu na nikakav nacin iskoristiti tih 10 eura."
- `BS-5681` _[hr]_: "ne mogu nadoplatiti račun, piše redirecting corvuspay i tako stoji?"
- `BS-6060` _[hr]_: "aplikacija je vrlo dobra alu zadnje vrijeme mi skida sa kartice iako imam 7.53 eura na računu"
- `BS-4196` _[hr]_: "jucer sam kupio prepaid parking bon preko web aplikacije. u web aplikaciji kada idem gledati Purchases mi za isti bon pise expired a u mobilnoj aplikaciji ga uopce ne mogu ni vidjeti."
- `BS-488` _[hr]_: "CorvusPay (naplatni servis) Vam je odbio transakciju iz nama nepoznatih razloga. Novac Vam ne bi trebao biti skinut."
- `BS-5807` _[hr]_: "trenutno je greška koju čekamo da se riješi, pa alternativno možete nadoplatiti Bmove račun sa već dodanom karticom u aplikaciji, kupovinom Bmove bona na kiosku Tiska ili nadoplatom Bmove računa novom"

## Cluster statistics

- **Volume:** 25 tickets total (25 unique semantic events after dedup)
- **Frequency:** 0.49 tickets/month (over data window 2022-05-03 → 2023-03-18)
- **Median resolution:** 4.1 days
- **Languages:** hr, en
- **Country focus:** hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~2.2 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.6 (range [0.4, 0.7])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.80
- **Rationale:** The resolution pattern is highly templatable: agents follow a consistent four-step diagnostic and education flow with stable scripted workarounds, making response drafting and balance-check lookup strong candidates for assist automation. Time savings accrue mainly from auto-populating the account balance status and pre-drafting the ponuda and CorvusPay workaround instructions, reducing active work per ticket by roughly one step.
- **Validation:** Run agent-assist in shadow mode for 3 weeks, measuring draft acceptance rate and time-to-send per ticket; a ≥70% draft acceptance rate with no quality regressions would validate the feasibility score and time-reduction estimate.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~1.1 (range [0.77, 1.43])
- **Root cause:** CorvusPay mobile-redirect bug causes card top-up to fail or become stuck in the mobile app; a separate UX gap means the prepaid-balance payment option is not prominently surfaced before the 'Kupi kartu' action, causing users to default to their bank card unintentionally.
- **Rationale:** Fixing the CorvusPay redirect requires coordination with a third-party vendor (3-day typical wait per escalation cycle), adding schedule uncertainty; surfacing prepaid balance as the default or first-presented payment option is a lower-effort UX change but must be verified against the vendor's payment-flow API. A complete fix of both issues could eliminate the majority of tickets, but vendor dependency means elimination is partial and slower than pure internal fixes.
- **Validation:** Engineering should scope the CorvusPay integration fix by reviewing vendor API documentation and running a sandbox reproduction; a 2-sprint spike with CorvusPay's technical team would yield a firmer effort estimate before committing to a full fix.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.5 (range [0.32, 0.58])
- **Form:** `help_center`
- **Deflection rate:** ~35% (range [25%, 45%])
- **Feasibility:** 0.72
- **Rationale:** The two most common sub-patterns — selecting prepaid balance before purchase and generating a bank-transfer invoice — are step-by-step procedural questions well-suited to an illustrated help-center article or in-app tooltip. However, CorvusPay redirect bugs and declined-card scenarios require live diagnosis and cannot be deflected by documentation alone, capping the deflection ceiling.
- **Validation:** Publish a targeted FAQ/help-center article covering the three known flows (payment method selection, ponuda generation, CorvusPay workaround) and instrument article views vs. ticket opens over a 6-week window; target ≥25% reduction in inbound volume to validate the midpoint estimate.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 15% of tickets
- **Hours saved per year:** ~0.1 (range [0.098, 0.182])
- **Narrow use case:** Auto-send the ponuda (bank-transfer invoice) generation walkthrough to users who explicitly ask how to top up via internet banking, when no CorvusPay error code is present.
- **Safety constraints:**
  - Must not autonomously handle tickets involving a declined card or CorvusPay payment error without agent review, as root cause may be a vendor-side fault.
  - Must not access or modify account balance or payment records; read-only balance lookup only.
  - Must escalate any ticket where the user reports a financial discrepancy or missing funds to a human agent.
  - Auto-resolution confirmation message must include a clear human-escalation path.
  - Vendor (CorvusPay) outage or degraded-service signals must immediately suspend autonomous resolution and queue for agent handling.
- **Rationale:** Autonomous resolution is only viable for the narrow, low-risk knowledge-gap sub-pattern (how to generate a ponuda); tickets involving payment failures, declined cards, or CorvusPay errors carry financial-impact risk and vendor uncertainty that make full automation unsafe. The low annual frequency further limits absolute hours saved.
- **Validation:** Pilot over 8 weeks on explicitly tagged 'ponuda inquiry' tickets only (confirmed by keyword and absence of error codes); measure CSAT, re-open rate, and false-positive escalation rate; accept only if re-open rate is <10% and CSAT is neutral or positive.

### Risks

- **Compliance concerns:**
  - Any automated action touching payment method selection or balance display must comply with applicable Croatian and EU payment services regulations (PSD2); agent or bot must not store or log card credentials.
  - GDPR: automated ticket handling must minimise personal data access; balance lookups should return only what is necessary to resolve the inquiry.
- **Must not automate:**
  - Investigation or resolution of missing or incorrect account balance amounts (financial dispute risk).
  - Any step that modifies a user's payment method, account settings, or transaction records.
  - CorvusPay error escalations that may indicate a systemic vendor outage affecting multiple users.
- **Vendor dependencies blocking automation:**
  - CorvusPay mobile-redirect bug fix is blocked on vendor cooperation and their release cycle (typical wait ≥3 days per escalation); autonomous or product-side resolution of top-up failures cannot proceed without vendor confirmation.
  - Any change to the payment flow API surface (e.g., defaulting to prepaid balance) must be validated against CorvusPay's integration contract to avoid breaking existing payment sessions.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.88)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `True`
- **RAG-consumable:** `True`
- **Note:** User education — safe for self-service deflection

