---
id: hr-internal-partner-misc-support__0cfe1d
name: hr_internal_partner_misc_support
title: Croatian Internal Partner Miscellaneous IT and Operational Support Requests
description: Internal partners (mostly Croatian municipal/public offices) submit a wide variety of support requests covering
  software installation, device configuration, user account management, and operational queries related to parking and cash
  register systems. Tickets are typically brief, often lacking descriptions, and cover ad-hoc issues ranging from locked user
  accounts and password resets to hardware setup and application-specific problems. The pattern is highly heterogeneous but
  consistently originates from internal Croatian partners using parking/control/cash register (blagajna) systems.
category: internal_partner/configuration
ticket_class: internal_partner
issue_category: configuration
resolution_pattern: configuration_change
languages:
- hr
country_focus:
- hr
status: draft
cluster_id: RAOS:internal_partner|Support|no_label:c1
project_key: RAOS
cluster_size: 234
cluster_size_dedup: 234
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.62
extraction_model: claude-sonnet-4-6
frequency_per_month: 11.42
median_resolution_minutes: 0.0
p95_resolution_minutes: 595.2499999999911
cannot_reproduce_rate: 0.0
data_window_start: '2024-09-16'
data_window_end: '2026-05-07'
annual_hours_saved: 98.2
roi:
  baseline_active_hours: 490.9
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 73.6
  deflection_hours_range:
  - 51.5
  - 95.7
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 98.2
  agent_assist_hours_range:
  - 68.7
  - 127.6
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 98.2
  product_fix_hours_range:
  - 68.7
  - 127.6
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 24.7
  autonomous_resolve_hours_range:
  - 17.3
  - 32.1
  autonomous_resolve_max_safe_volume_pct: 0.18
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- RAOS-2166
- RAOS-2798
- RAOS-6317
- RAOS-158
- RAOS-490
- RAOS-1410
- RAOS-3084
- RAOS-6369
- RAOS-2548
- RAOS-910
- RAOS-6855
- RAOS-1956
- RAOS-6131
- RAOS-1215
- RAOS-1279
- RAOS-4951
- RAOS-5990
- RAOS-4190
canonical_examples:
- RAOS-3084
- RAOS-6855
- RAOS-1215
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
  autonomous_resolve_max_safe_volume_pct: 0.18
  autonomous_resolve_narrow_use_case: Automated password reset and account unlock for known Croatian internal-partner user
    accounts via verified identity check
  autonomous_resolve_safety_constraints:
  - Scope strictly to password-reset and account-unlock ticket sub-type only; hardware and software configuration must remain
    agent-handled
  - Identity verification required before any credential change (e.g. email confirmation to registered municipal account)
  - All autonomous actions must be logged and auditable for GDPR compliance (Croatian personal data regulations apply)
  - Automatic escalation to agent if account belongs to privileged or admin user
  - Human review of autonomous-resolution queue at least daily during pilot period
related_playbooks:
- android-ppc-device-setup-and-app-installation
- dubrovnik-pass-website-hours-notice-posting
- dubrovnik-pass-website-notice-management
- hr-b2b-case-status-and-data-correction
- hr-b2b-parking-price-change-request
- hr-b2b-photo-download-enablement
- hr-b2b-user-account-management
- hr-internal-partner-misc-support__a37936
- hr-parking-sms-payment-visibility-issue
- periodic-table-update-lpr-a1-ht
- sac-system-hr-polygon-ddpk-issues
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Croatian Internal Partner Miscellaneous IT and Operational Support Requests

## What this pattern is

Internal partners (mostly Croatian municipal/public offices) submit a wide variety of support requests covering software installation, device configuration, user account management, and operational queries related to parking and cash register systems. Tickets are typically brief, often lacking descriptions, and cover ad-hoc issues ranging from locked user accounts and password resets to hardware setup and application-specific problems. The pattern is highly heterogeneous but consistently originates from internal Croatian partners using parking/control/cash register (blagajna) systems.

## When this applies

- New hardware or computer requiring software installation or configuration
- User account locked or requiring a password reset
- Device setup needed for a new or replacement control unit
- Operational question about reports, cash registers, or system parameters
- Application error or unexpected system behavior (e.g., negative sign not accepted in journal entry)
- Missing or incorrect data on printed documents (e.g., slip or field ticket)
- Authorization or alias configuration issue

## Typical resolution flow

1. Internal partner contacts support via ticket with brief description of issue
2. Support agent identifies the nature of the request (IT setup, user issue, software bug, etc.)
3. Agent performs or coordinates the required action (e.g., configures device, resets password, installs software)
4. Resolution is confirmed and ticket is closed

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Install or configure blagajna (cash register) software on new or replacement computer | support agent | ParkIS / blagajna system | 60 min |
| Configure and dispatch a new control device | support agent | control device / postal service | 90 min |
| Reset user password or unlock account | support agent | user administration system | 15 min |
| Correct authorization alias or system parameter | support agent | backend system | 20 min |
| Answer operational queries about reports, cash registers, or system parameters | support agent | — | 30 min |

## Evidence

Derived from 234 tickets in cluster `RAOS:internal_partner|Support|no_label:c1`. Direct quotes from 8 representative tickets:

- `RAOS-3084` _[hr]_: "Potrebno podesiti novi uređaj za kontrolu i instalirati blagajnu na zamjensko računalo"
- `RAOS-6855` _[hr]_: "Blagajna instalirana i podešena."
- `RAOS-1215` _[hr]_: "ne može se prijaviti u aplikaciju"
- `RAOS-1279` _[hr]_: "nova lozinka za usera dbrkic1"
- `RAOS-6317` _[hr]_: "Kontrolori imaju problema s tekstom koji se ispisuje na terenskom listiću pa treba vidjeti što se može napraviti po tom pitanju."
- `RAOS-4951` _[hr]_: "Jutros ne mogu unijeti negativan predznak u temeljnici pa pretpostavljam da je jučerašnja greška povezana"
- `RAOS-1956` _[hr]_: "Korigiran MUP allias"
- `RAOS-4190` _[hr]_: "Potrebno je podesiti novo računalo za pristup web sustavu."

## Cluster statistics

- **Volume:** 234 tickets total (234 unique semantic events after dedup)
- **Frequency:** 11.42 tickets/month (over data window 2024-09-16 → 2026-05-07)
- **Median resolution:** 0 min
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~490.9 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~98.2 (range [68.74, 127.6])
- **Time reduction per ticket:** ~20% (range [14%, 26%])
- **Feasibility:** 0.70
- **Rationale:** Despite high heterogeneity, many tickets follow a small set of resolution scripts (password reset, blagajna install checklist, device dispatch steps); an assist tool surfacing the right runbook and pre-filling common fields could reduce active work time by ~20%, primarily on documentation, classification, and follow-up drafting. Tickets lacking descriptions limit classification accuracy, so gains are moderate.
- **Validation:** Run a 3-week shadow-mode pilot in which the assist tool suggests resolution runbooks and draft replies for Croatian-partner tickets; measure agent acceptance rate and time-on-ticket compared with a matched control group to validate the 20% time-reduction assumption.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~6 (range [4.2, 7.8])
- **Hours eliminated per year:** ~98.2 (range [68.74, 127.6])
- **Root cause:** The pattern reflects operational lifecycle needs (new hardware deployments, account management, ad-hoc queries) rather than a fixable software defect; however, the absence of self-service account management and automated device provisioning workflows forces manual agent intervention.
- **Rationale:** Building self-service password-reset and account-unlock capabilities into the blagajna/parking portal could eliminate the ~20% of tickets that are pure credential resets without agent touch; deeper provisioning automation could address device-config tickets but carries significantly higher engineering scope. Hours eliminated are capped at the realistic addressable sub-cluster, well below the 490.9 baseline.
- **Validation:** Engineering team to scope a spike (1 sprint) estimating effort for self-service password reset in the existing portal; compare against ticket sub-type distribution to validate the addressable volume assumption.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~73.6 (range [51.52, 95.68])
- **Form:** `help_center`
- **Deflection rate:** ~15% (range [10%, 20%])
- **Feasibility:** 0.45
- **Rationale:** Tickets are highly heterogeneous, often lacking descriptions, and cover hands-on tasks (hardware setup, device dispatch) that cannot be self-served; only simpler sub-types like password resets and basic operational queries realistically deflect. A Croatian-language help centre covering common blagajna/cash-register FAQs and account-unlock procedures could capture roughly 15% of volume.
- **Validation:** Deploy a Croatian-language help-centre section covering password resets, common blagajna errors, and report queries for 6 weeks; measure ticket-submission rate from Croatian municipal partner accounts before and after to confirm deflection rate.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 18% of tickets
- **Hours saved per year:** ~24.7 (range [17.3, 32.1])
- **Narrow use case:** Automated password reset and account unlock for known Croatian internal-partner user accounts via verified identity check
- **Safety constraints:**
  - Scope strictly to password-reset and account-unlock ticket sub-type only; hardware and software configuration must remain agent-handled
  - Identity verification required before any credential change (e.g. email confirmation to registered municipal account)
  - All autonomous actions must be logged and auditable for GDPR compliance (Croatian personal data regulations apply)
  - Automatic escalation to agent if account belongs to privileged or admin user
  - Human review of autonomous-resolution queue at least daily during pilot period
- **Rationale:** Only the password-reset and account-unlock sub-type (~18% of volume, estimated) is narrow and low-risk enough to consider for autonomous resolution; all other ticket types involve physical hardware, software installation, or parameter changes that require human judgment and are unsafe to automate. Even within this sub-type, identity verification and audit requirements constrain full autonomy.
- **Validation:** Pilot autonomous password reset for a single Croatian municipal partner for 4 weeks with agent shadow-approval; measure successful resolution rate, identity-verification pass rate, and escalation frequency before expanding; accept only if escalation rate remains below 10%.

### Risks

- **Compliance concerns:**
  - Croatian and EU GDPR rules apply to any automated handling of user account credentials or personal data held in blagajna/parking systems
  - Municipal and public-sector partners may have contractual or regulatory requirements mandating human authorisation for account changes
  - Audit trails for all configuration changes to cash-register (blagajna) systems may be legally required under Croatian fiscal regulations
- **Must not automate:**
  - Hardware device dispatch and physical configuration — requires human verification of device identity and location
  - Installation or reconfiguration of blagajna (cash register) software — fiscal compliance risk if misconfigured
  - Correction of authorization aliases or system parameters — erroneous changes can disrupt parking/cash operations across multiple municipal sites
  - Any ticket from an account flagged as privileged, admin, or belonging to a system-critical role

## Agent compatibility

- **Status:** `draft` (extraction confidence 0.62)
- **Brainbox skill:** `reference_only`
- **Claude skill:** `reference_only`
- **Agent-assist:** `False`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Admin/operator-only configuration change

