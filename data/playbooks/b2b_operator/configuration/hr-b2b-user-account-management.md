---
id: hr-b2b-user-account-management
name: hr_b2b_user_account_management
title: B2B Partner Requests for New User Account Creation or Password Reset in RAO/PAUK Systems
description: Croatian B2B partner organizations (municipalities, enforcement agencies, parking operators) regularly submit
  tickets requesting creation of new user accounts or password resets for their employees in RAO-related systems (PaukIS,
  ParkIS, RAO, NKP). Requests involve providing employee personal data (name, OIB national ID), desired role/permissions,
  and receiving back credentials via one-time secret links or plaintext. A secondary sub-pattern involves role changes (e.g.,
  from traffic warden to community warden) requiring account reconfiguration.
category: b2b_operator/configuration
ticket_class: b2b_partner
issue_category: configuration
resolution_pattern: configuration_change
languages:
- hr
country_focus:
- hr
status: active
cluster_id: RAOS:b2b_partner|Support|duplikat:c1
project_key: RAOS
cluster_size: 50
cluster_size_dedup: 50
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 2.44
median_resolution_minutes: 87.0
p95_resolution_minutes: 8589.399999999994
cannot_reproduce_rate: 0.0
data_window_start: '2025-03-13'
data_window_end: '2026-04-15'
annual_hours_saved: 4.8
roi:
  baseline_active_hours: 16.1
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 1.2
  deflection_hours_range:
  - 0.8
  - 1.6
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 4.8
  agent_assist_hours_range:
  - 3.6
  - 6.1
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 9.7
  product_fix_hours_range:
  - 6.8
  - 12.6
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 1.6
  autonomous_resolve_hours_range:
  - 1.1
  - 2.1
  autonomous_resolve_max_safe_volume_pct: 0.2
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- RAOS-6424
- RAOS-6329
- RAOS-6640
- RAOS-2187
- RAOS-3358
- RAOS-4125
- RAOS-5233
- RAOS-6868
- RAOS-3254
- RAOS-3365
- RAOS-6493
- RAOS-3357
- RAOS-4952
- RAOS-3690
- RAOS-2822
- RAOS-2503
- RAOS-3364
- RAOS-3359
canonical_examples:
- RAOS-6424
- RAOS-5233
- RAOS-6329
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
  autonomous_resolve_max_safe_volume_pct: 0.2
  autonomous_resolve_narrow_use_case: Automated password reset only, for existing verified partner users whose identity is
    confirmed via an authenticated partner portal session
  autonomous_resolve_safety_constraints:
  - User identity must be authenticated via the partner organisation's existing login session before reset is triggered —
    no unauthenticated reset flows
  - OIB must match an existing active record in the target system; any mismatch must escalate to a human agent
  - New account creation and role changes must always involve human review due to access-rights and compliance implications
  - One-time credential links must be system-generated and never expose plaintext passwords in automated responses
  - Audit log of every autonomous action must be retained for at least 12 months per Croatian public-sector data handling
    norms
related_playbooks:
- android-ppc-device-setup-and-app-installation
- dubrovnik-pass-website-hours-notice-posting
- dubrovnik-pass-website-notice-management
- hr-b2b-case-status-and-data-correction
- hr-b2b-monthly-invoice-generation-and-fiscalization
- hr-b2b-parking-operations-support
- hr-b2b-parking-price-change-request
- hr-b2b-photo-download-enablement
- hr-b2b-sms-parking-and-ddpk-issues
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

# B2B Partner Requests for New User Account Creation or Password Reset in RAO/PAUK Systems

## What this pattern is

Croatian B2B partner organizations (municipalities, enforcement agencies, parking operators) regularly submit tickets requesting creation of new user accounts or password resets for their employees in RAO-related systems (PaukIS, ParkIS, RAO, NKP). Requests involve providing employee personal data (name, OIB national ID), desired role/permissions, and receiving back credentials via one-time secret links or plaintext. A secondary sub-pattern involves role changes (e.g., from traffic warden to community warden) requiring account reconfiguration.

## When this applies

- New employee hired by partner organization needing system access
- Existing employee forgot or lost their password
- Employee role changes requiring updated system permissions
- Employee transferred to a different department or role (e.g., traffic to community warden)
- Expired temporary password not used in time

## Typical resolution flow

1. Partner submits ticket with employee name, OIB (national ID), and desired role/permissions
2. Support agent may request missing information (e.g., OIB, signature, badge number) if not provided
3. Support agent creates new account or resets password in the relevant system
4. Credentials are delivered via one-time secret link (onetimesecret.com) or occasionally as plaintext
5. Partner is advised to copy credentials immediately (one-time visibility) and change password after first login
6. If role-based access is needed, appropriate roles are assigned matching a reference user or specified role

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Request missing employee details (OIB, role, signature/badge for wardens) | support_agent | Jira/ticket system | 5 min |
| Create new user account with appropriate role and permissions in target system | support_agent | RAO/PaukIS/ParkIS admin backend | 10 min |
| Reset existing user password | support_agent | RAO/PaukIS admin backend | 5 min |
| Deliver credentials securely via one-time secret link | support_agent | onetimesecret.com | 3 min |
| Change user role (e.g., from Prometni to Komunalni redar) and reset credentials | support_agent | RAO/PaukIS admin backend | 10 min |

## Evidence

Derived from 50 tickets in cluster `RAOS:b2b_partner|Support|duplikat:c1`. Direct quotes from 7 representative tickets:

- `RAOS-6424` _[hr]_: "molimo reset lozinke za korisnika mhrga"
- `RAOS-5233` _[hr]_: "molim Vas izradite korisničko ime i lozinku za rad na terenu (kontrolor)"
- `RAOS-6329` _[hr]_: "Molimo Vas kad otvorite link sa podacima da iste odmah kopirate jer su vidljivi samo jednom"
- `RAOS-3358` _[hr]_: "Kolegi je promijenjena rola iz Prometnog u Komunalni redar te napravljen reset podataka."
- `RAOS-3254` _[hr]_: "trebalo bi otvoriti novo korisničko ime za novog djelatnika na pauku kao što već ima korisnik dhodzic"
- `RAOS-3364` _[hr]_: "Za dodavanje kolege potreban je potpis, pečat te broj značke."
- `RAOS-6640` _[hr]_: "trenutna lozinka istekla, pa Vas molim da pošaljete novu kako bi danas/sutra to rješili"

## Cluster statistics

- **Volume:** 50 tickets total (50 unique semantic events after dedup)
- **Frequency:** 2.44 tickets/month (over data window 2025-03-13 → 2026-04-15)
- **Median resolution:** 1.4 hours
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~16.1 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~4.8 (range [3.6, 6.1])
- **Time reduction per ticket:** ~30% (range [22%, 38%])
- **Feasibility:** 0.80
- **Rationale:** Templated workflows that pre-fill account-creation forms from parsed ticket data (OIB, role, system) and auto-generate one-time secret delivery messages can meaningfully reduce per-ticket active time, particularly the credential-delivery and clarification steps which are highly repetitive.
- **Validation:** Run shadow-mode assist tool for 2 weeks on incoming tickets of this cluster type; measure average active minutes with vs. without assist to validate the 30% reduction assumption before rollout.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~8 (range [6, 10])
- **Hours eliminated per year:** ~9.7 (range [6.8, 12.6])
- **Root cause:** No self-service user-management capability exists for partner organisations within RAO/PaukIS/ParkIS/NKP systems; all account lifecycle operations are gated on a support agent with system access, creating a structural dependency rather than a defect.
- **Rationale:** Building a partner-admin portal with delegated user management (create/reset/role-change) scoped to the partner's own org could eliminate the majority of this ticket cluster, but requires RBAC redesign across multiple systems and OIB identity verification integration. Effort is high and cross-system scope introduces coordination risk.
- **Validation:** Engineering team should spike against PaukIS and RAO APIs to confirm delegated-admin endpoints are feasible within 1 sprint before committing to full build; compare estimated sprint count against actual after spike.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~1.2 (range [0.84, 1.56])
- **Form:** `in_app_help`
- **Deflection rate:** ~15% (range [10%, 20%])
- **Feasibility:** 0.45
- **Rationale:** B2B partner admins could self-serve routine password resets via a portal, but new account creation requires OIB validation and role assignment that unlikely survives fully unguided; deflection ceiling is low without a proper partner admin console. A structured intake form would reduce back-and-forth on missing details even if it doesn't fully deflect.
- **Validation:** Deploy a guided web form pre-collecting OIB, role, and signature for 4 weeks; measure reduction in clarification round-trips and compare ticket-close time vs. baseline period.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~1.6 (range [1.12, 2.08])
- **Narrow use case:** Automated password reset only, for existing verified partner users whose identity is confirmed via an authenticated partner portal session
- **Safety constraints:**
  - User identity must be authenticated via the partner organisation's existing login session before reset is triggered — no unauthenticated reset flows
  - OIB must match an existing active record in the target system; any mismatch must escalate to a human agent
  - New account creation and role changes must always involve human review due to access-rights and compliance implications
  - One-time credential links must be system-generated and never expose plaintext passwords in automated responses
  - Audit log of every autonomous action must be retained for at least 12 months per Croatian public-sector data handling norms
- **Rationale:** Only the password-reset sub-pattern (estimated ~40% of tickets) is narrow and low-risk enough to consider for autonomous handling, and only with strong identity pre-authentication; new account creation and role changes carry access-control and legal-identity risks that require human oversight. Even in the reset case, the low annual volume caps absolute savings.
- **Validation:** Pilot authenticated self-service password reset for a single partner organisation for 8 weeks; acceptance criteria: zero credential-delivery errors, 100% audit log coverage, and partner satisfaction score ≥ pre-pilot baseline.

### Risks

- **Compliance concerns:**
  - OIB (Croatian national personal ID number) is personally identifiable data subject to GDPR and Croatian personal-data-protection law; any automated processing must have a documented lawful basis and data-minimisation controls
  - Credentials delivered via one-time secret links must not be logged in plaintext in ticket systems; automated flows must enforce this
  - Public-sector partner systems (municipalities, enforcement agencies) may have additional access-control audit requirements under Croatian e-government regulations
  - Role assignments for traffic and community wardens carry legal authority implications; erroneous role grants could have regulatory consequences
- **Must not automate:**
  - New account creation without human review of OIB, role appropriateness, and organisational authorisation
  - Role changes (e.g., Prometni to Komunalni redar) without explicit human sign-off due to differing legal authority scopes
  - Any credential delivery that stores or transmits plaintext passwords
  - Account creation for users whose OIB cannot be verified against a trusted identity source

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `reference_only`
- **Claude skill:** `reference_only`
- **Agent-assist:** `False`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Admin/operator-only configuration change

