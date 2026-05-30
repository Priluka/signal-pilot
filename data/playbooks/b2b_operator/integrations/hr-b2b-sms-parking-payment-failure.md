---
id: hr-b2b-sms-parking-payment-failure
name: hr_b2b_sms_parking_payment_failure
title: B2B Partner Reports SMS/App Parking Payment Failures in Croatia
description: Croatian B2B parking operators (primarily Rijeka Plus, Komunalac Sisak, and others) report that end-users cannot
  complete parking payments via SMS or the Bmove app. Failures are caused by a mix of teleoperator-side processing issues
  (HT, A1), system-side technical outages, user errors (incorrect SMS format, unfinished prior transactions), and third-party
  integration problems (SKIDATA, RAO). The B2B partner acts as an intermediary, escalating end-user complaints to Bmove Support
  for investigation and resolution.
category: b2b_operator/integrations
ticket_class: b2b_partner
issue_category: integration_issue
resolution_pattern: vendor_escalation
languages:
- hr
country_focus:
- hr
status: active
cluster_id: BS:b2b_partner|no_value|koncesionar:c0
project_key: BS
cluster_size: 57
cluster_size_dedup: 57
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.91
extraction_model: claude-sonnet-4-6
frequency_per_month: 1.12
median_resolution_minutes: 1245.0
p95_resolution_minutes: 15529.999999999976
cannot_reproduce_rate: 0.0
data_window_start: '2022-02-14'
data_window_end: '2023-04-21'
annual_hours_saved: 3.2
roi:
  baseline_active_hours: 14.5
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 2.6
  deflection_hours_range:
  - 1.9
  - 3.4
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 3.2
  agent_assist_hours_range:
  - 2.3
  - 4.2
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 4.4
  product_fix_hours_range:
  - 3.1
  - 5.7
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 1.1
  autonomous_resolve_hours_range:
  - 0.8
  - 1.4
  autonomous_resolve_max_safe_volume_pct: 0.15
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-4890
- BS-3056
- BS-4859
- BS-40
- BS-782
- BS-1358
- BS-4154
- BS-2015
- BS-80
- BS-1817
- BS-1278
- BS-438
- BS-2139
- BS-2596
- BS-187
- BS-7254
- BS-988
- BS-5536
canonical_examples:
- BS-4890
- BS-2596
- BS-80
vendor_dependency:
  vendor_name: HT (T-COM/Simpa), A1, RAO, SKIDATA
  involves_vendor: true
  typical_wait_days: 1
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: Vendor coordination — needs human verification
  autonomous_resolve_max_safe_volume_pct: 0.15
  autonomous_resolve_narrow_use_case: Auto-diagnose and reply to B2B partner for confirmed user-error sub-types (wrong SMS
    format or open prior session) using transaction log lookup with no vendor escalation required.
  autonomous_resolve_safety_constraints:
  - Must not autonomously close tickets requiring vendor escalation (RAO, SKIDATA, HT, A1)
  - Must not autonomously confirm outage resolution without human verification
  - Must not send advisory responses if transaction log lookup is inconclusive
  - Must route all B2B partner tickets with unresolved payment failures to a human agent
  - Autonomous actions must be logged and reviewable by a human supervisor within 24 hours
related_playbooks:
- b2b-parking-invoice-payment-issues
- b2b-partner-parking-card-storno-refund
- b2b-ticketless-open-session-and-permit-conflict
- gtt-skidata-is-alive-timeout-error
- hr-b2b-partner-billing-payment-storno
- italy-gtt-parking-stop-threshold-alert
- italy-gtt-skidata-invalid-timestamp-anomaly
- parking-fine-received-despite-valid-payment
- skidata-hosted-services-maintenance-notification
- zagreb-parking-cancelled-ticket-refund
- zagrebparking-b2b-storno-refund-request
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

# B2B Partner Reports SMS/App Parking Payment Failures in Croatia

## What this pattern is

Croatian B2B parking operators (primarily Rijeka Plus, Komunalac Sisak, and others) report that end-users cannot complete parking payments via SMS or the Bmove app. Failures are caused by a mix of teleoperator-side processing issues (HT, A1), system-side technical outages, user errors (incorrect SMS format, unfinished prior transactions), and third-party integration problems (SKIDATA, RAO). The B2B partner acts as an intermediary, escalating end-user complaints to Bmove Support for investigation and resolution.

## When this applies

- End-users report inability to pay parking via SMS to the B2B partner (parking operator)
- End-users report inability to pay via Bmove app (garage or parking lot)
- Users receive unexpected error messages or cancellation notices after apparent successful payment
- Parking inspectors issue fines to users who claim they paid via SMS/app
- Multiple users affected simultaneously, suggesting a systemic outage
- Individual user error (wrong SMS format, expired card, incorrect vehicle registration entry)

## Typical resolution flow

1. B2B partner receives end-user complaint about failed SMS or app payment
2. B2B partner forwards complaint to Bmove Support via email, requesting investigation
3. Bmove Support checks transaction logs and system (Parkis, IGeus) for the reported registration plate or time window
4. Bmove Support determines root cause: teleoperator-side failure, system outage, user error, or third-party (RAO/SKIDATA) issue
5. If teleoperator at fault, Bmove Support informs partner and may advise user to contact their teleoperator
6. If system outage confirmed, Bmove Support reports the affected time window and confirms restoration
7. If user error identified, Bmove Support explains the specific mistake to the B2B partner
8. If third-party (RAO/SKIDATA) involved, Bmove Support escalates or coordinates with that vendor
9. B2B partner communicates resolution back to end-user; fines may be annulled if appropriate

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Check transaction logs for reported registration plate and time window | Bmove Support agent | ParkIS / IGeus | 15 min |
| Confirm whether teleoperator processed the SMS request correctly | Bmove Support agent | Internal logs | 10 min |
| Advise B2B partner on user error (wrong SMS format, unfinished prior session, expired card, swapped registration fields) | Bmove Support agent | email | 10 min |
| Escalate to RAO or SKIDATA if third-party integration is at fault | Bmove Support agent | email (h****@rao.hr or SKIDATA contact) | 20 min |
| Report system outage window and confirm service restoration to B2B partner | Bmove Support agent | email | 10 min |

## Vendor dependency

- **Vendor:** HT (T-COM/Simpa), A1, RAO, SKIDATA
- **Typical wait:** 1 day(s)

## Evidence

Derived from 57 tickets in cluster `BS:b2b_partner|no_value|koncesionar:c0`. Direct quotes from 7 representative tickets:

- `BS-4890` _[hr]_: "HT sms parking usluga nije radila danas od 13:38 do 14:11."
- `BS-2596` _[hr]_: "na usluzi su bili tehnički problemi jučer popodne i tijekom noći. Sada bi sve trebalo uredno raditi od jutra."
- `BS-80` _[hr]_: "problem je vezan za poteškoće sa Googleovim aplikacijama za slanje SMS poruka gdje se kod korisnika koji imaju njihovu Messages aplikaciju događa to da poruke na kratki broj ili ne odlaze ili odlaze n"
- `BS-1817` _[hr]_: "korisnik je napravio grešku i zamijenio ta dva polja. U opis je unio svoju reg. oznaku, a u polje za reg. oznaku je unio ono što je htio unijeti pod opis"
- `BS-5536` _[hr]_: "teleoperater nije obradio zahtjev u zadanom roku i transakcija je proglašena neuspješnom. Razlog tome ne znamo, ali na strani teleoperatera je sigurno jer od njih nismo niti u jednom trenu zaprimili z"
- `BS-1278` _[hr]_: "je pokušao slati SMS koji nije prošao zbog prijašnje inicijalizacije parkirne karte koja traje 15 minuta"
- `BS-40` _[hr]_: "umjesto da je samo napisao reg. oznaku, korisnik je napisao prije toga 'm-parking' čime je probio limit znakova standarne registracijske oznake"

## Cluster statistics

- **Volume:** 57 tickets total (57 unique semantic events after dedup)
- **Frequency:** 1.12 tickets/month (over data window 2022-02-14 → 2023-04-21)
- **Median resolution:** 20.8 hours
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~14.5 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~3.2 (range [2.3, 4.16])
- **Time reduction per ticket:** ~22% (range [16%, 29%])
- **Feasibility:** 0.75
- **Rationale:** Agent assist tooling can accelerate log lookup (step 1), pre-populate teleoperator check checklists (step 2), and surface the correct user-error advisory text (step 3), reducing active time per ticket; steps 4–5 involve vendor escalation workflows that are harder to template and will see smaller gains.
- **Validation:** Run a 3-week shadow-mode pilot where the assist tool surfaces suggested log queries and advisory templates alongside live tickets; measure pre/post active-handle-time difference with at least 10 tickets per condition to validate the time reduction estimate.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~6 (range [4.2, 7.8])
- **Hours eliminated per year:** ~4.4 (range [3.1, 5.7])
- **Root cause:** Failures stem from a mix of system-side outages, third-party integration instability (SKIDATA, RAO), and insufficient real-time feedback to end-users on failure reasons—some of which are addressable through improved error handling, retry logic, and integration monitoring on the Bmove platform side.
- **Rationale:** A product fix addressing better integration health monitoring, automated outage detection/notification, and improved user-facing error messages could eliminate the system-outage and integration-fault ticket sub-types; however, teleoperator-side failures (HT, A1) remain outside Bmove's control and will persist regardless of internal fixes.
- **Validation:** Engineering team should instrument integration endpoints (RAO, SKIDATA) with alerting and review the last 12 months of transaction logs to quantify the share of tickets attributable to each root cause; spike estimate in a 2-sprint discovery before committing to full effort range.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~2.6 (range [1.9, 3.38])
- **Form:** `help_center`
- **Deflection rate:** ~18% (range [13%, 23%])
- **Feasibility:** 0.45
- **Rationale:** A subset of tickets—user errors such as wrong SMS format, unfinished prior sessions, or expired cards—are potentially self-resolvable via a structured help center article or FAQ. However, the B2B intermediary nature of escalations and the high proportion of vendor/system-side failures significantly limit pure self-service deflection.
- **Validation:** Deploy a targeted help center article covering the top three user-error sub-types (wrong SMS format, prior session open, field swap) and measure ticket-open rate change over a 6-week pilot; deflection confirmed if partner-reported user-error tickets drop by ≥15%.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 15% of tickets
- **Hours saved per year:** ~1.1 (range [0.77, 1.4])
- **Narrow use case:** Auto-diagnose and reply to B2B partner for confirmed user-error sub-types (wrong SMS format or open prior session) using transaction log lookup with no vendor escalation required.
- **Safety constraints:**
  - Must not autonomously close tickets requiring vendor escalation (RAO, SKIDATA, HT, A1)
  - Must not autonomously confirm outage resolution without human verification
  - Must not send advisory responses if transaction log lookup is inconclusive
  - Must route all B2B partner tickets with unresolved payment failures to a human agent
  - Autonomous actions must be logged and reviewable by a human supervisor within 24 hours
- **Rationale:** Only a narrow slice of tickets—clear-cut user errors verifiable entirely from transaction logs—are safe to resolve autonomously; the majority involve vendor dependencies or system-outage confirmation that require human judgment and external coordination, capping safe autonomous volume well below 30%.
- **Validation:** Pilot for 8 weeks on user-error sub-type tickets only (estimated ~15% of annual volume); acceptance criteria: zero false-positive autonomous closures, partner satisfaction score maintained, and human review confirms ≥90% of auto-responses were accurate before expanding scope.

### Risks

- **Compliance concerns:**
  - B2B partner SLA obligations may require human acknowledgement of escalations; autonomous responses must not be mistaken for SLA-binding commitments
  - Payment failure records may be subject to data retention and audit requirements under Croatian financial or telecom regulations
- **Must not automate:**
  - Vendor escalation initiation to RAO or SKIDATA without human review
  - Outage confirmation or service restoration announcements to B2B partners
  - Any response where transaction log data is ambiguous or unavailable
  - Tickets where the end-user's payment may have been partially processed
- **Vendor dependencies blocking automation:**
  - HT (T-COM/Simpa) and A1 teleoperator processing delays (typical 1-day wait) block autonomous resolution of SMS-side failures
  - RAO and SKIDATA third-party integration issues require vendor-side investigation and cannot be resolved or confirmed by Bmove automation alone
  - Lack of real-time API status feeds from vendors prevents automated outage detection and auto-resolution

## Agent compatibility

- **Status:** `active` (extraction confidence 0.91)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Vendor coordination — needs human verification

