---
id: hr-b2b-parking-operations-support
name: hr_b2b_parking_operations_support
title: Croatian B2B Partner Operational Support for Parking Management Systems (PARKIS/PAUKIS/RAO)
description: 'B2B partners (parking operators, municipalities) in Croatia submit recurring operational requests to the RAO
  support team covering a wide range of activities: monthly billing cycle closures and invoice generation, fiscalization issues
  (Croatian tax compliance), ticket/voucher stornos, hardware device configuration, and system outages in parking management
  applications (PARKIS, PAUKIS, RAO NKP). These tickets span routine administrative notifications as well as technical bugs
  and compliance problems requiring developer intervention.'
category: b2b_operator/bugs
ticket_class: b2b_partner
issue_category: bug_in_product
resolution_pattern: manual_close
languages:
- hr
country_focus:
- hr
status: active
cluster_id: RAOS:b2b_partner|Support|no_label:c4
project_key: RAOS
cluster_size: 115
cluster_size_dedup: 115
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.82
extraction_model: claude-sonnet-4-6
frequency_per_month: 5.61
median_resolution_minutes: 2704.0
p95_resolution_minutes: 55780.79999999985
cannot_reproduce_rate: 0.0
data_window_start: '2024-09-10'
data_window_end: '2026-05-06'
annual_hours_saved: 93.9
roi:
  baseline_active_hours: 521.6
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 8.7
  deflection_hours_range:
  - 6.1
  - 11.3
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 93.9
  agent_assist_hours_range:
  - 67.8
  - 120.0
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 156.5
  product_fix_hours_range:
  - 109.6
  - 203.4
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 5.6
  autonomous_resolve_hours_range:
  - 3.9
  - 7.3
  autonomous_resolve_max_safe_volume_pct: 0.1
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- RAOS-1230
- RAOS-1675
- RAOS-887
- RAOS-90
- RAOS-455
- RAOS-2062
- RAOS-3128
- RAOS-399
- RAOS-5931
- RAOS-1939
- RAOS-5712
- RAOS-6313
- RAOS-6379
- RAOS-4611
- RAOS-6941
- RAOS-1709
- RAOS-6007
- RAOS-4556
canonical_examples:
- RAOS-1675
- RAOS-1230
- RAOS-2062
vendor_dependency:
  vendor_name: Monri (payment gateway), MUP (Croatian police/traffic authority), FINA (Croatian financial agency), Bmove
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.1
  autonomous_resolve_narrow_use_case: Automated acknowledgement and structured data-collection form for month-closure billing
    trigger notifications (action 1 pre-step only)
  autonomous_resolve_safety_constraints:
  - No autonomous execution of invoice generation without explicit human-agent review and approval
  - No autonomous storno of tickets or invoices — irreversible financial action requiring human sign-off
  - No autonomous fiscalization actions — Croatian FINA compliance requires accountable human oversight
  - No autonomous hardware device configuration — physical/remote device changes risk operational outages
  - All vendor-dependent actions (Monri, MUP, FINA) must remain human-mediated
  - B2B partner identity must be verified before any automated response containing account-specific data
related_playbooks:
- dubrovnik-pass-website-hours-notice-posting
- dubrovnik-pass-website-notice-management
- hr-b2b-case-status-and-data-correction
- hr-b2b-monthly-invoice-generation-and-fiscalization
- hr-b2b-parking-price-change-request
- hr-b2b-photo-download-enablement
- hr-b2b-sms-parking-and-ddpk-issues
- hr-b2b-user-account-management
- hr-sms-parking-payment-issues
- kml-polygon-upload-correction-hr
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Croatian B2B Partner Operational Support for Parking Management Systems (PARKIS/PAUKIS/RAO)

## What this pattern is

B2B partners (parking operators, municipalities) in Croatia submit recurring operational requests to the RAO support team covering a wide range of activities: monthly billing cycle closures and invoice generation, fiscalization issues (Croatian tax compliance), ticket/voucher stornos, hardware device configuration, and system outages in parking management applications (PARKIS, PAUKIS, RAO NKP). These tickets span routine administrative notifications as well as technical bugs and compliance problems requiring developer intervention.

## When this applies

- Partner notifies support that a billing month has been closed in PARKIS or PAUKIS and requests invoice generation
- Fiscalization errors occur (delayed fiscalization, missing JIR/ZKI codes, e-invoice errors, fiskalizacija 2.0 migration issues)
- A voucher, parking ticket, or invoice needs to be cancelled (storno) due to wrong zone, wrong data, or system error
- Web shop or partner portal becomes unavailable or login fails
- Handheld/Unitech control devices require firmware installation or configuration
- System-wide outage in RAO NKP blagajna or PARKIS prevents printing or access
- Data missing in supervisory center (nadzorni centar) due to third-party (MUP) connectivity failure
- Voucher not generated after successful payment, funds already deducted

## Typical resolution flow

1. Partner submits ticket describing the operational issue or routine notification
2. RAO support agent acknowledges and investigates the root cause
3. If monthly closure: support generates monthly invoices in the background and confirms to partner
4. If fiscalization issue: support checks fiscal status, adjusts parameters or escalates to development team
5. If storno requested: support performs cancellation in the system and advises partner on refund process
6. If hardware: devices are shipped to RAO, configured, and returned to partner
7. If third-party dependency (MUP, Monri, financial provider): partner is informed and issue is escalated externally
8. Ticket is closed once action is confirmed or partner acknowledges resolution

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Generate monthly invoices after partner confirms month closure in PARKIS/PAUKIS | RAO support agent | ParkIS / PaukIS backend | 30 min |
| Investigate and resolve fiscalization errors (delayed sending, missing fiscal codes, e-invoice issues) | RAO developer / support agent | Fiscalization system / FiskAplikacija | 120 min |
| Perform storno of incorrectly issued parking ticket or invoice | RAO support agent | RAO NKP / ParkIS backend | 15 min |
| Configure handheld Unitech parking control devices and return to partner | RAO technical staff | Unitech devices / RAO internal tooling | 240 min |
| Investigate missing voucher after payment and recommend refund | RAO support agent | Monri payment gateway / web shop backend | 60 min |
| Escalate supervisory center data gap to MUP and monitor resolution | RAO support agent | RAO.up IS / MUP integration | — |

## Vendor dependency

- **Vendor:** Monri (payment gateway), MUP (Croatian police/traffic authority), FINA (Croatian financial agency), Bmove

## Evidence

Derived from 115 tickets in cluster `RAOS:b2b_partner|Support|no_label:c4`. Direct quotes from 8 representative tickets:

- `RAOS-1675` _[hr]_: "Obavještavam Vas da je mjesec SIJEČANJ 2025. zaključen u aplikaciji PARKIS."
- `RAOS-1230` _[hr]_: "Navedena karta je stornirana. Molimo da se obratite Bmove za povrat sredstava."
- `RAOS-2062` _[hr]_: "trenutno ne postoji opcija da blagajnik može ručno slati takve račune na ponovnu fiskalizaciju te da bi isto mogli napraviti potrebna je ozbiljna nadogradnja sustava"
- `RAOS-5712` _[hr]_: "Radi fiskalizacije 2.0 generiranje računa je trenutno onemogućeno."
- `RAOS-6313` _[hr]_: "Problem je do MUP-a pa čekamo da se riješi problem s njihove strane."
- `RAOS-3128` _[hr]_: "Nakon analize zahtjeva voucher se nije kreirao prilikom kupnje na web shopu. Nakon provjere sa kolegama preproučeno je da se napravi povrat sredstava korisniku."
- `RAOS-399` _[hr]_: "Uređaji su podešeni i spremni za rad."
- `RAOS-6379` _[hr]_: "fiskalizirano odobrenje 54/URED/102 u FiskAplikaciji porezne uprave označeno je greškom G014 ( greška reference prethodnog računa )"

## Cluster statistics

- **Volume:** 115 tickets total (115 unique semantic events after dedup)
- **Frequency:** 5.61 tickets/month (over data window 2024-09-10 → 2026-05-06)
- **Median resolution:** 1.9 days
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~521.6 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~93.9 (range [67.8, 120])
- **Time reduction per ticket:** ~18% (range [13%, 23%])
- **Feasibility:** 0.65
- **Rationale:** Agent assist can meaningfully reduce time on invoice generation (pre-populated templates, partner closure confirmation checklists), storno workflows (guided decision trees, pre-filled storno forms), and voucher investigations (automated transaction lookup), but fiscalization debugging and device configuration require deep technical judgment that AI drafts cannot reliably replace. A 18% time reduction is conservative given the high proportion of technically complex tickets.
- **Validation:** Run a 3-week shadow-mode pilot where the assist tool surfaces invoice templates, storno checklists, and transaction lookup results alongside the agent's existing workflow; measure average handle-time delta between assisted and unassisted tickets, targeting ≥10% reduction before full rollout.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~6 (range [4.2, 7.8])
- **Hours eliminated per year:** ~156.5 (range [109.6, 203.45])
- **Root cause:** Recurring fiscalization errors (delayed sending, missing fiscal codes, e-invoice failures) and missing vouchers after payment indicate integration fragility between PARKIS/PAUKIS and FINA/Monri APIs; these are systemic bugs rather than one-off user errors, and likely share root causes around error-handling, retry logic, and reconciliation gaps.
- **Rationale:** Fiscalization and missing-voucher incidents together account for the two longest resolution actions (120 min and 60 min respectively) and likely represent 30–40% of ticket volume; robust retry/reconciliation logic and automated fiscal-code recovery could substantially eliminate those tickets, but external dependencies on FINA and Monri API stability add uncertainty. Hours eliminated are capped at the fiscalization+voucher share of the 521.6-hour baseline.
- **Validation:** Engineering team should instrument current FINA and Monri API call failure rates in staging, run a spike (1 sprint) to scope retry/reconciliation work, then validate that a canary release reduces fiscalization-error ticket submissions by ≥50% over a 6-week post-deploy observation window.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~8.7 (range [6.1, 11.3])
- **Form:** `help_center`
- **Deflection rate:** ~10% (range [7%, 13%])
- **Feasibility:** 0.35
- **Rationale:** Most tickets require direct system access, developer intervention, or vendor coordination (Monri, MUP, FINA), making self-service deflection very limited; only routine month-closure notifications or storno request pre-checks could plausibly be redirected to a structured help-center guide. The B2B partner context means users are professionals who may follow step-by-step guides, but the underlying actions still require RAO agent execution.
- **Validation:** Deploy a help-center article covering the monthly billing closure checklist and storno request prerequisites for 4 weeks; measure whether ticket volume for those sub-types drops and whether partners arrive with complete information, reducing active handle time.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 10% of tickets
- **Hours saved per year:** ~5.6 (range [3.92, 7.28])
- **Narrow use case:** Automated acknowledgement and structured data-collection form for month-closure billing trigger notifications (action 1 pre-step only)
- **Safety constraints:**
  - No autonomous execution of invoice generation without explicit human-agent review and approval
  - No autonomous storno of tickets or invoices — irreversible financial action requiring human sign-off
  - No autonomous fiscalization actions — Croatian FINA compliance requires accountable human oversight
  - No autonomous hardware device configuration — physical/remote device changes risk operational outages
  - All vendor-dependent actions (Monri, MUP, FINA) must remain human-mediated
  - B2B partner identity must be verified before any automated response containing account-specific data
- **Rationale:** The overwhelming majority of this cluster involves financial, compliance, and hardware actions that carry significant legal or operational risk if automated without human review; the only safely automatable slice is intake triage — confirming receipt, collecting structured closure confirmation data, and routing — which saves minimal active time but reduces agent context-switching. Even this narrow scope requires careful identity verification given B2B Croatian tax compliance obligations.
- **Validation:** Pilot an automated intake bot for month-closure notifications only over 6 weeks: measure whether structured data collection reduces the agent's active intake time on those tickets by ≥5 minutes per ticket, with zero instances of incorrect routing or data leakage as the acceptance gate.

### Risks

- **Compliance concerns:**
  - Croatian fiscalization law (Zakon o fiskalizaciji) requires that fiscal codes and e-invoices be issued with full human accountability — any automation touching fiscal document generation or correction must be audited and legally defensible
  - FINA e-invoicing regulations mandate specific data integrity and timing requirements; automated retries or corrections could create duplicate or invalid fiscal records
  - MUP (traffic authority) data submissions for supervisory center gaps carry regulatory obligations; autonomous escalation without human review is not permissible
  - B2B partner data processed under GDPR must not be exposed in automated responses without verified partner identity
- **Must not automate:**
  - Storno of parking tickets or invoices (irreversible financial action, requires human authorization)
  - Fiscalization error resolution or re-sending of fiscal documents (legal compliance risk)
  - Handheld Unitech device configuration and dispatch (physical asset risk, requires technical staff verification)
  - MUP supervisory center escalations (regulatory/authority communication must be human-initiated)
  - Invoice generation and issuance (financial document with legal standing under Croatian law)
  - Refund recommendations for missing vouchers (financial decision requiring human judgement)
- **Vendor dependencies blocking automation:**
  - Monri payment gateway: API reliability and error-response quality directly affect voucher and fiscalization ticket volume; improvements require vendor coordination and cannot be fully addressed internally
  - FINA (Croatian financial agency): fiscalization API stability, e-invoice schema changes, and processing delays are outside RAO control and limit both product-fix and automation scope
  - MUP (Croatian police/traffic authority): supervisory center data gap resolution depends entirely on MUP response timelines and data access, making this ticket sub-type non-automatable
  - Bmove: dependency scope unclear from available data; any automation touching Bmove-integrated workflows requires vendor API documentation and change-notification agreements

## Agent compatibility

- **Status:** `active` (extraction confidence 0.82)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

