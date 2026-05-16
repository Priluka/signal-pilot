---
id: hr-internal-partner-misc-support__a37936
name: hr_internal_partner_misc_support
title: Croatian internal partner miscellaneous support requests (configuration, IT, bookkeeping, system access)
description: Internal partner organizations (Croatian municipalities and local governments) submit a wide variety of support
  tickets covering topics such as manual data entry corrections, VPN/IT access issues, PoP system configuration, bookkeeping/accounting
  queries, authorization requests, and general system usage questions. The tickets are predominantly from Croatian cities
  and towns (HR) and span operational, IT, and administrative support needs. Due to the heterogeneous nature of the requests,
  many are classified as 'other' sub-issue and require direct human intervention from support staff.
category: internal_partner/knowledge_gaps
ticket_class: internal_partner
issue_category: knowledge_gap
resolution_pattern: user_education
languages:
- hr
country_focus:
- hr
status: draft
cluster_id: RAOS:internal_partner|Support|duplikat:c1
project_key: RAOS
cluster_size: 71
cluster_size_dedup: 71
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.62
extraction_model: claude-sonnet-4-6
frequency_per_month: 3.46
median_resolution_minutes: 0.0
p95_resolution_minutes: 5062.5
cannot_reproduce_rate: 0.0
data_window_start: '2025-02-20'
data_window_end: '2026-04-13'
annual_hours_saved: 23.6
roi:
  baseline_active_hours: 117.9
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 23.6
  deflection_hours_range:
  - 16.5
  - 30.6
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 23.6
  agent_assist_hours_range:
  - 16.5
  - 30.6
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 18.0
  product_fix_hours_range:
  - 12.6
  - 23.4
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 3.5
  autonomous_resolve_hours_range:
  - 2.5
  - 4.5
  autonomous_resolve_max_safe_volume_pct: 0.1
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- RAOS-1838
- RAOS-6765
- RAOS-1853
- RAOS-1892
- RAOS-2772
- RAOS-3673
- RAOS-4782
- RAOS-6476
- RAOS-4685
- RAOS-6128
- RAOS-3396
- RAOS-4589
- RAOS-6236
- RAOS-6479
- RAOS-1878
- RAOS-1891
- RAOS-5118
- RAOS-3244
canonical_examples:
- RAOS-1838
- RAOS-1892
- RAOS-2772
vendor_dependency:
  vendor_name: null
  involves_vendor: false
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: draft
  claude_skill: draft
  agent_assist: false
  autonomous_resolve: false
  note: User education — safe for self-service deflection
  autonomous_resolve_max_safe_volume_pct: 0.1
  autonomous_resolve_narrow_use_case: Automated password reset and VPN reconnection guide delivery for AnyConnect-only tickets
    where no account exception is required
  autonomous_resolve_safety_constraints:
  - Must not autonomously modify financial or bookkeeping records; all data corrections require human authorization
  - Must not autonomously grant or revoke system authorizations (ZPK, PoP access) without supervisor approval
  - Must confirm partner identity via established authentication before any account-level action
  - Autonomous scope limited strictly to informational/self-service password reset flows; any ambiguity routes to human agent
  - All autonomous actions must be logged and auditable per Croatian public-sector data governance requirements
related_playbooks:
- android-ppc-device-setup-and-app-installation
- hr-internal-partner-misc-support__0cfe1d
- hr-parking-sms-payment-visibility-issue
- sac-system-hr-polygon-ddpk-issues
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Croatian internal partner miscellaneous support requests (configuration, IT, bookkeeping, system access)

## What this pattern is

Internal partner organizations (Croatian municipalities and local governments) submit a wide variety of support tickets covering topics such as manual data entry corrections, VPN/IT access issues, PoP system configuration, bookkeeping/accounting queries, authorization requests, and general system usage questions. The tickets are predominantly from Croatian cities and towns (HR) and span operational, IT, and administrative support needs. Due to the heterogeneous nature of the requests, many are classified as 'other' sub-issue and require direct human intervention from support staff.

## When this applies

- Internal partner (municipality) cannot perform a system action (e.g., manual entry, authorization)
- User cannot log in or connect to VPN/system
- Bookkeeping or accounting question arises (e.g., unallocated payments, court fees, DPK suspension)
- PoP system form needs review or correction
- Missing or incorrect notices/records need to be fixed
- Need for training or education on system features (e.g., enforcement, fiscalization)
- IT infrastructure issue (VPN installation, AnyConnect password)

## Typical resolution flow

1. Internal partner contacts support via ticket with a brief description or just a summary line
2. Support agent identifies the specific sub-issue (IT, accounting, system correction, education)
3. Support agent investigates or manually performs the required action (correction, configuration, installation)
4. Resolution is confirmed and ticket is closed

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Correct or adjust records/notices in the system for specified case IDs | support agent | RAOS backend system | 30 min |
| Enable manual entry (e.g., ZPK, authorization) for a partner | support agent | RAOS configuration/admin panel | 20 min |
| Assist with VPN installation or password reset for AnyConnect | IT support agent | Cisco AnyConnect / VPN infrastructure | 30 min |
| Review and correct PoP system form with partner | support agent | PoP system | 60 min |
| Provide guidance or education on accounting/bookkeeping procedures | support agent | Phone/email/ticketing | 30 min |

## Evidence

Derived from 71 tickets in cluster `RAOS:internal_partner|Support|duplikat:c1`. Direct quotes from 8 representative tickets:

- `RAOS-1838` _[hr]_: "pomoć oko knjiženja temeljnica i neraspoređenih uplata i zatvaranja predmeta sa statusom SUD odbačeno"
- `RAOS-1892` _[hr]_: "omogućavanje ručnog unosa ZPK"
- `RAOS-2772` _[hr]_: "insatalacija VPN-a"
- `RAOS-3244` _[hr]_: "ne mogu se spojiti na VPN sa novom lozinkom"
- `RAOS-6479` _[hr]_: "pregled i ispravak cijelog PoP obrasca sa radnim ulicama i sa PPK ulicama"
- `RAOS-3396` _[hr]_: "Na jednoj lokaciji korisnik nije u mogućnosti napraviti prijavu na blagajnu jer mu izbacuje grešku pri obradi starih podataka."
- `RAOS-1853` _[hr]_: "predmeti koji trebaju ispravak : 918475 i 842153"
- `RAOS-3673` _[hr]_: "potrebno obustaviti DPK koje su u inozemnoj naplati i iste nije moguće naplatiti"

## Cluster statistics

- **Volume:** 71 tickets total (71 unique semantic events after dedup)
- **Frequency:** 3.46 tickets/month (over data window 2025-02-20 → 2026-04-13)
- **Median resolution:** 0 min
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~117.9 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~23.6 (range [16.52, 30.6])
- **Time reduction per ticket:** ~20% (range [14%, 26%])
- **Feasibility:** 0.70
- **Rationale:** Agent-assist tooling (pre-populated response templates in Croatian, guided resolution checklists per sub-issue type, quick-access links to system actions for authorization or manual entry) can reduce the lookup and drafting overhead per ticket; however, the heterogeneous nature of these tickets limits standardization gains, and the 60-minute PoP form review sessions require real-time collaboration that tooling cannot shorten substantially.
- **Validation:** Deploy shadow-mode agent-assist with pre-built Croatian response snippets and step-by-step resolution checklists for 3 weeks; measure average handle time before and after for each of the five resolution action types and confirm ≥15% AHT reduction before full rollout.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~4 (range [3, 5])
- **Hours eliminated per year:** ~18 (range [12.6, 23.4])
- **Root cause:** The root cause is a knowledge gap combined with UX friction: the PoP system configuration, authorization flows, and manual-entry enablement processes are not intuitive for Croatian municipal partners, leading to repeated guided interventions. This is a usability and onboarding gap rather than a software defect.
- **Rationale:** Improving in-product guidance (contextual tooltips, guided onboarding flows for PoP configuration, and self-service authorization request buttons) could eliminate a portion of configuration and authorization tickets without requiring agent intervention; record/data correction tickets cannot be product-fixed as they require human judgment. Estimated elimination applies only to the addressable subset (~15% of annual hours).
- **Validation:** Engineering team should map the PoP configuration and authorization request flows against the five resolution actions, estimate story points per flow improvement in a design spike, then validate with a 2-sprint prototype tested by 3–5 Croatian municipal partners before committing to full build.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~23.6 (range [16.52, 30.6])
- **Form:** `help_center`
- **Deflection rate:** ~20% (range [14%, 26%])
- **Feasibility:** 0.55
- **Rationale:** A subset of tickets (accounting queries, general system usage questions, VPN setup steps) are procedural and could be partially addressed by a structured Croatian-language help center; however, the heterogeneous 'other' classification and the need for case-specific data corrections limit deflection potential significantly. Many tickets require agent access to internal systems, making pure self-service insufficient for a large share.
- **Validation:** Publish a Croatian-language help center covering the five most common sub-issues (VPN/AnyConnect setup, ZPK authorization request process, bookkeeping FAQs, PoP form guidance, and password reset). Run a 6-week pilot tracking ticket volume and whether users who visited the help center still opened a ticket; target ≥15% reduction in new tickets before scaling.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 10% of tickets
- **Hours saved per year:** ~3.5 (range [2.45, 4.5])
- **Narrow use case:** Automated password reset and VPN reconnection guide delivery for AnyConnect-only tickets where no account exception is required
- **Safety constraints:**
  - Must not autonomously modify financial or bookkeeping records; all data corrections require human authorization
  - Must not autonomously grant or revoke system authorizations (ZPK, PoP access) without supervisor approval
  - Must confirm partner identity via established authentication before any account-level action
  - Autonomous scope limited strictly to informational/self-service password reset flows; any ambiguity routes to human agent
  - All autonomous actions must be logged and auditable per Croatian public-sector data governance requirements
- **Rationale:** Only the VPN/AnyConnect password reset sub-type is safe and simple enough for autonomous handling via a verified self-service bot; this represents a small fraction (~10%) of annual volume. All other ticket types involve financial records, authorization changes, or complex system configuration that carry regulatory and data integrity risks incompatible with autonomous resolution.
- **Validation:** Pilot a chatbot-driven AnyConnect password reset flow with Croatian-language prompts for 8 weeks, capping at 10% of IT tickets; acceptance criteria are zero escalations due to incorrect autonomous actions and partner satisfaction ≥4/5 on post-resolution survey before any scope expansion.

### Risks

- **Compliance concerns:**
  - Croatian public-sector data governance rules may restrict automated handling of municipal financial records and personal data under GDPR and Croatian implementation law
  - Authorization and access changes for government partners may require documented human approval trails for audit purposes
  - Bookkeeping and accounting corrections may carry legal liability if made in error by automated systems
- **Must not automate:**
  - Manual data entry corrections and record adjustments for case IDs (risk of erroneous financial/legal record changes)
  - ZPK and system authorization grants or revocations (requires human accountability and audit trail)
  - PoP system form reviews involving partner-specific configuration (too variable and consequential for autonomous action)
  - Accounting and bookkeeping guidance that could constitute regulated financial advice

## Agent compatibility

- **Status:** `draft` (extraction confidence 0.62)
- **Brainbox skill:** `draft`
- **Claude skill:** `draft`
- **Agent-assist:** `False`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** User education — safe for self-service deflection

