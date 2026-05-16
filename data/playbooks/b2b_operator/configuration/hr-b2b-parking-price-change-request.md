---
id: hr-b2b-parking-price-change-request
name: hr_b2b_parking_price_change_request
title: Croatian B2B partner requests parking price/article changes via PoP form
description: B2B parking operators in Croatia (municipalities, parking companies) submit requests to update parking tariffs,
  articles, and operating hours in the RAO system, typically triggered by new pricing decisions, seasonal tariff changes,
  or municipal ordinances. Partners submit a completed PoP (Podaci o parkiralištima) form, which the RAO support team uses
  to apply configuration changes in the parking system. Occasionally the initial request is missing required details (e.g.
  missing articles, unclear deactivations), requiring back-and-forth to clarify and complete the PoP form before changes are
  applied.
category: b2b_operator/configuration
ticket_class: b2b_partner
issue_category: configuration
resolution_pattern: configuration_change
languages:
- hr
country_focus:
- hr
status: active
cluster_id: RAOS:b2b_partner|Support|duplikat:c2
project_key: RAOS
cluster_size: 19
cluster_size_dedup: 19
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.95
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.93
median_resolution_minutes: 5735.0
p95_resolution_minutes: 22630.799999999974
cannot_reproduce_rate: 0.0
data_window_start: '2025-02-21'
data_window_end: '2026-03-31'
annual_hours_saved: 2.3
roi:
  baseline_active_hours: 9.2
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.4
  deflection_hours_range:
  - 0.3
  - 0.5
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 2.3
  agent_assist_hours_range:
  - 1.7
  - 3.0
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 1.5
  product_fix_hours_range:
  - 1.1
  - 1.9
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.5
  autonomous_resolve_hours_range:
  - 0.3
  - 0.7
  autonomous_resolve_max_safe_volume_pct: 0.1
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- RAOS-4276
- RAOS-2962
- RAOS-4960
- RAOS-2170
- RAOS-2981
- RAOS-4245
- RAOS-4765
- RAOS-5688
- RAOS-1807
- RAOS-5706
- RAOS-6679
- RAOS-4764
- RAOS-4407
- RAOS-4832
- RAOS-6305
- RAOS-5942
- RAOS-5552
- RAOS-4411
canonical_examples:
- RAOS-4276
- RAOS-2170
- RAOS-4245
vendor_dependency:
  vendor_name: null
  involves_vendor: false
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: reference_only
  claude_skill: reference_only
  agent_assist: false
  autonomous_resolve: false
  note: Admin/operator-only configuration change
  autonomous_resolve_max_safe_volume_pct: 0.1
  autonomous_resolve_narrow_use_case: Fully automated acknowledgement and completeness-check of incoming PoP form submissions,
    flagging missing fields before agent review.
  autonomous_resolve_safety_constraints:
  - No autonomous modification of live parking tariffs or system configuration without human agent review and approval
  - Partner identity and authorisation must be verified by a human before any configuration change is applied
  - Municipal ordinance references must be reviewed for regulatory compliance by a human agent
  - Any deactivation or deletion of articles requires explicit human confirmation to avoid operational disruption
  - Automated actions limited strictly to intake triage and completeness checks; zero write-access to the RAO system
related_playbooks:
- android-ppc-device-setup-and-app-installation
- dubrovnik-pass-website-hours-notice-posting
- dubrovnik-pass-website-notice-management
- hr-b2b-case-status-and-data-correction
- hr-b2b-monthly-invoice-generation-and-fiscalization
- hr-b2b-parking-operations-support
- hr-b2b-photo-download-enablement
- hr-b2b-sms-parking-and-ddpk-issues
- hr-b2b-user-account-management
- hr-internal-partner-misc-support__0cfe1d
- hr-sms-parking-payment-issues
- kml-polygon-upload-correction-hr
- periodic-table-update-lpr-a1-ht
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Croatian B2B partner requests parking price/article changes via PoP form

## What this pattern is

B2B parking operators in Croatia (municipalities, parking companies) submit requests to update parking tariffs, articles, and operating hours in the RAO system, typically triggered by new pricing decisions, seasonal tariff changes, or municipal ordinances. Partners submit a completed PoP (Podaci o parkiralištima) form, which the RAO support team uses to apply configuration changes in the parking system. Occasionally the initial request is missing required details (e.g. missing articles, unclear deactivations), requiring back-and-forth to clarify and complete the PoP form before changes are applied.

## When this applies

- New municipal or company pricing decision coming into effect on a specific date
- Seasonal tariff change (e.g. summer/winter periods)
- New parking zones or articles introduced by municipal ordinance
- Introduction or removal of privileged parking card (PPK/KPK) categories
- DPK (dnevna parkirna karta) price or rules update
- Partner submits or re-submits a PoP form proactively as a reminder

## Typical resolution flow

1. Partner sends a price-change request (often with attached PoP form or pricing document) to RAO support
2. RAO support reviews the request and, if information is incomplete, sends back a pre-filled PoP form asking partner to highlight changes in yellow
3. Partner reviews, corrects, and returns the completed PoP form
4. RAO support applies the configuration changes (prices, articles, active/inactive status, operating hours) in the system
5. RAO support confirms changes are applied and asks partner to report any irregularities

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Partner submits pricing change request with attached PoP form or pricing document | b2b_partner | RAO Help Desk / support portal | — |
| RAO support sends pre-filled PoP form to partner for review and confirmation of changes | RAO support agent | PoP form (spreadsheet attachment) | 15 min |
| Partner reviews PoP form, marks changes in yellow, and returns completed form | b2b_partner | PoP form (spreadsheet) | — |
| RAO support applies price/article/operating-hour changes in the parking system | RAO support agent | RAO NKP / ParkIS / Bmove application backend | 30 min |
| RAO support sends confirmation and asks partner to verify correctness | RAO support agent | Help Desk | 5 min |

## Evidence

Derived from 19 tickets in cluster `RAOS:b2b_partner|Support|duplikat:c2`. Direct quotes from 7 representative tickets:

- `RAOS-4276` _[hr]_: "Ponovo šaljem ispunjen PoP obrazac."
- `RAOS-2170` _[hr]_: "promjene su izvršene prema PoP obrascu"
- `RAOS-4245` _[hr]_: "Molimo Vas da pregledate dostavljene informacije, izvršite potrebne izmjene te upišete aktualne cijene. Sve izmijenjene stavke ljubazno Vas molimo da označite žutom bojom."
- `RAOS-2981` _[hr]_: "ispričavamo se na propustu, navedeno je ispravljeno odmah po prijavi"
- `RAOS-6305` _[hr]_: "Ljubazno Vas molimo, ukoliko je moguće, da nam barem tjedan dana ranije pošaljete podsjetnik za promjenu cijena."
- `RAOS-4960` _[hr]_: "Od 1.12. 2025. godine na snagu stupa novi Cjenik parkirnih karti."
- `RAOS-5688` _[hr]_: "molim da u skladu sa priloženim cjenikom parkirališta, koji je stupio na snagu 01.01.2026., izvršite izmjenu cijena artikala."

## Cluster statistics

- **Volume:** 19 tickets total (19 unique semantic events after dedup)
- **Frequency:** 0.93 tickets/month (over data window 2025-02-21 → 2026-03-31)
- **Median resolution:** 4.0 days
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~9.2 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~2.3 (range [1.7, 2.99])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.75
- **Rationale:** The workflow is highly templated: agents send a pre-filled PoP form, apply changes, and send a confirmation — all steps suitable for AI-drafted templates and checklist prompts that pre-populate standard fields from prior partner configurations. Time savings primarily target steps 2 and 5, reducing drafting and lookup effort.
- **Validation:** Run a 4-week shadow-mode pilot where the assist tool drafts the pre-filled PoP email and confirmation message; compare agent edit time and ticket handle time before and after to validate the 25% reduction estimate.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~4 (range [3, 5])
- **Hours eliminated per year:** ~1.5 (range [1.05, 1.95])
- **Root cause:** Not a bug; the pattern is a legitimate operational workflow where B2B partners periodically submit pricing/tariff decisions for manual configuration in the RAO system. Incomplete PoP forms cause rework, which could be reduced with a validated digital intake form, but the core configuration work would remain.
- **Rationale:** A structured digital PoP submission portal with mandatory field validation could eliminate incomplete-form back-and-forth (estimated ~15–20% of active effort) but cannot eliminate the configuration application step itself. Full elimination of the cluster is not feasible without self-service configuration access for partners.
- **Validation:** Engineering team estimates effort via a spike sprint scoping a validated web form against the RAO API; validate hours-eliminated by tracking rework tickets before and after pilot deployment.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.4 (range [0.28, 0.5])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.15
- **Rationale:** These requests are B2B partner-initiated configuration changes that inherently require RAO-side system access to fulfil; no FAQ or self-service article can replace the hands-on configuration work. A structured intake guide could marginally reduce incomplete-form submissions but cannot deflect the core request.
- **Validation:** Publish a detailed PoP form checklist and intake guide for 8 weeks; measure the share of tickets arriving with all required fields complete versus baseline to quantify only the rework-reduction benefit.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 10% of tickets
- **Hours saved per year:** ~0.5 (range [0.35, 0.65])
- **Narrow use case:** Fully automated acknowledgement and completeness-check of incoming PoP form submissions, flagging missing fields before agent review.
- **Safety constraints:**
  - No autonomous modification of live parking tariffs or system configuration without human agent review and approval
  - Partner identity and authorisation must be verified by a human before any configuration change is applied
  - Municipal ordinance references must be reviewed for regulatory compliance by a human agent
  - Any deactivation or deletion of articles requires explicit human confirmation to avoid operational disruption
  - Automated actions limited strictly to intake triage and completeness checks; zero write-access to the RAO system
- **Rationale:** Autonomous resolution of parking configuration changes carries significant operational and regulatory risk; even narrow automation is limited to pre-processing (completeness checks, auto-acknowledgement). The hands-on RAO system configuration must remain human-controlled given its direct impact on live B2B partner operations and potential municipal compliance obligations.
- **Validation:** Pilot an automated intake bot for 6 weeks that only checks PoP form completeness and sends a structured missing-field reply; measure reduction in back-and-forth rounds per ticket and confirm zero false approvals before expanding scope.

### Risks

- **Compliance concerns:**
  - Parking tariff changes may be governed by Croatian municipal ordinances or public procurement rules, requiring documented human approval chains before system changes are applied.
  - Incorrect configuration of pricing articles could expose B2B partners to regulatory or contractual liability, necessitating audit trails for all changes.
  - Data accuracy obligations under Croatian consumer-protection and transport regulations mean errors in tariff configuration must be traceable to a responsible human agent.
- **Must not automate:**
  - Applying any price, tariff, or operating-hour change directly to the RAO production system without human review and partner-confirmed PoP form.
  - Deactivating or deleting parking articles, even when requested, without explicit dual confirmation from both partner and RAO agent.
  - Accepting partner identity or authorisation claims without human verification, especially for municipalities with formal signatory requirements.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.95)
- **Brainbox skill:** `reference_only`
- **Claude skill:** `reference_only`
- **Agent-assist:** `False`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Admin/operator-only configuration change

