---
id: croatia-parking-payment-failure__ffdf4e
name: croatia_parking_payment_failure
title: End-user unable to complete parking payment in Bmove app (Croatia)
description: Users in Croatia (and some neighbouring countries) report being unable to pay for parking tickets — including
  hourly, monthly, and privileged/resident cards — through the Bmove mobile app. Failures manifest as generic error messages
  ('sustav nije u mogućnosti obraditi zahtjev', 'pokušajte kasnije', greyed-out payment button), card registration/expiry
  issues, or purchased tickets not being recorded. The pattern spans transient technical faults, card management problems,
  and privilege-card purchase flows that require escalation to local parking operators or the development team.
category: end_user/bugs
ticket_class: end_user
issue_category: bug_in_product
resolution_pattern: product_fix_required
languages:
- hr
- en
- other
country_focus:
- hr
- other
status: active
cluster_id: BS:end_user|croatia|no_label:c3
project_key: BS
cluster_size: 137
cluster_size_dedup: 134
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.92
extraction_model: claude-sonnet-4-6
frequency_per_month: 2.63
median_resolution_minutes: 1500.0
p95_resolution_minutes: 43424.399999999994
cannot_reproduce_rate: 0.0
data_window_start: '2023-04-14'
data_window_end: '2026-05-04'
annual_hours_saved: 3.9
roi:
  baseline_active_hours: 15.8
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 1.2
  deflection_hours_range:
  - 0.8
  - 1.6
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 3.9
  agent_assist_hours_range:
  - 2.8
  - 5.1
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 10.5
  product_fix_hours_range:
  - 7.3
  - 13.7
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 1.2
  autonomous_resolve_hours_range:
  - 0.8
  - 1.6
  autonomous_resolve_max_safe_volume_pct: 0.15
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-46618
- BS-42390
- BS-34132
- BS-9604
- BS-9892
- BS-16911
- BS-17288
- BS-23689
- BS-21427
- BS-23403
- BS-42909
- BS-50862
- BS-18523
- BS-46381
- BS-13829
- BS-36781
- BS-25483
- BS-17191
canonical_examples:
- BS-16911
- BS-17288
- BS-17191
vendor_dependency:
  vendor_name: Local parking operators (e.g. Gradski parking Šibenik, TD Baška, Parking Opatija, Dubrovnik parking)
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: reference_only
  claude_skill: reference_only
  agent_assist: false
  autonomous_resolve: true
  note: Engineering backlog — not for runtime agents
  autonomous_resolve_max_safe_volume_pct: 0.15
  autonomous_resolve_narrow_use_case: Auto-verify backend purchase recording and send a 'purchase confirmed — please retry'
    notification when the ticket was silently recorded despite the error message
  autonomous_resolve_safety_constraints:
  - Must only close ticket autonomously when backend API confirms purchase recorded with no ambiguity; any uncertain state
    routes to agent
  - No autonomous handling of privileged-card or resident-card flows, which require dev-team escalation
  - No autonomous payment card modifications or deletions on behalf of users
  - Must never interact with local parking operators or vendor systems autonomously
  - All autonomous actions must be logged and reviewable for 90 days for dispute purposes
  - User must receive a clear notification that the action was automated with an opt-out to human review
related_playbooks:
- b2b-outstanding-payment-failure-app
- croatia-bmove-app-feedback-miscellaneous
- croatia-parking-fine-dispute
- croatia-parking-fine-dispute-and-payment
- croatia-parking-fine-payment-failure
- croatia-parking-ticket-storno-user-error
- croatia-ticketless-best-in-parking-knowledge-gap
- croatia-ticketless-open-session-at-exit__f25b63
- croatia-ticketless-rental-car-ghost-charge
- croatian-end-user-wrong-registration-storno-refund
- croatian-invoice-download-request
- croatian-parking-debt-payment-failure
- croatian-ticketless-open-session-at-exit__275624
- croatian-ticketless-open-session-at-exit__56d2b2
- croatian-ticketless-open-session-at-exit__ab83b0
- croatian-ticketless-open-session-at-exit__dc548a
- croatian-ticketless-open-session-at-exit__e3afed
- hr-open-session-after-garage-exit
- open-session-at-exit-payment-failure
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

# End-user unable to complete parking payment in Bmove app (Croatia)

## What this pattern is

Users in Croatia (and some neighbouring countries) report being unable to pay for parking tickets — including hourly, monthly, and privileged/resident cards — through the Bmove mobile app. Failures manifest as generic error messages ('sustav nije u mogućnosti obraditi zahtjev', 'pokušajte kasnije', greyed-out payment button), card registration/expiry issues, or purchased tickets not being recorded. The pattern spans transient technical faults, card management problems, and privilege-card purchase flows that require escalation to local parking operators or the development team.

## When this applies

- User attempts to purchase a parking ticket (hourly, monthly, or privileged/resident card) via the Bmove mobile app
- App displays an error such as 'sustav nije u mogućnosti obraditi zahtjev' or 'pokušajte kasnije'
- Payment is processed but ticket/purchase is not recorded in the app
- User's saved payment card has expired or the app reports the card as expired
- User selects wrong vehicle registration before payment and cannot correct it
- Privileged-card payment button is greyed out or non-functional
- User cannot add funds to the in-app wallet or pay by card for an extended period

## Typical resolution flow

1. User submits feedback via Bmove app reporting payment failure
2. Support ticket is created automatically in Bmove Support project
3. Support agent reviews ticket and checks whether purchase was eventually completed in the system
4. If transient technical issue: agent confirms system has been corrected and asks user to retry
5. If privileged/resident card issue: agent redirects user to web app (app.bmove.com) as a workaround and reports bug to development team
6. If expired/new card issue: agent instructs user to add new card via Main Menu > Payments > Cards and delete the old card
7. If ticket belongs to parking operator's domain: agent redirects user to the relevant parking operator contact
8. If issue persists: agent suggests alternative payment channels (SMS, parking meter, Tisak kiosks)

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Verify in backend whether the user's purchase was ultimately recorded despite the error | support_agent | Bmove back-office system | 5 min |
| Notify user that the technical issue is resolved and ask them to retry | support_agent | Bmove support ticketing | 5 min |
| Escalate privileged-card payment bug to development team and provide web-app workaround link | support_agent | Internal escalation / email | 10 min |
| Guide user to add/update payment card (Main Menu > Payments > Cards) and remove expired card | support_agent | Bmove support ticketing | 5 min |
| Redirect user to parking operator for ticket-ownership or privileged-card issues outside Bmove's control | support_agent | Bmove support ticketing | 5 min |

## Vendor dependency

- **Vendor:** Local parking operators (e.g. Gradski parking Šibenik, TD Baška, Parking Opatija, Dubrovnik parking)

## Evidence

Derived from 137 tickets in cluster `BS:end_user|croatia|no_label:c3`. Direct quotes from 8 representative tickets:

- `BS-16911` _[hr]_: "kad pokušam izvršiti uplatu aplikacija kaže "pokušajte kasnije""
- `BS-17288` _[hr]_: "Ne može se izvršiti plaćanje povlaštene karte za jednu godinu Grad Dubrovnik"
- `BS-17191` _[hr]_: "greška je prijavljena u naš razvojni tim. Molimo Vas da kupovinu povlaštene karte napravite putem naše web aplikacije dok problem ne bude riješen."
- `BS-50862` _[hr]_: "Zbog privremene tehničke poteškoće u komunikaciji s operaterom, došlo je do pogreške pri naplati parkirne karte."
- `BS-46381` _[hr]_: "već nekoliko dana ne mogu putem vaše aplikacije kupiti novu povlaštenu stanarsku kartu. Uvijek ista poruka: "Aplikacija trenutno nije u mogućnosti obraditi zahtjev.""
- `BS-18523` _[hr]_: "u aplikaciji se nemoze platiti karticom vec mjesec dana niti se moze nadopunit novcanik niti se parking moze platiti karticom"
- `BS-34132` _[hr]_: "Aplikacija mi javlja da mi je kartica istekla 28/02/2025, ja sam danas obnovljenu karticu ponovo prijavio u sustav"
- `BS-9892` _[hr]_: "nakon provedenog plaćanja nije evidentirana kupljena karta"

## Cluster statistics

- **Volume:** 137 tickets total (134 unique semantic events after dedup)
- **Frequency:** 2.63 tickets/month (over data window 2023-04-14 → 2026-05-04)
- **Median resolution:** 1.0 days
- **Languages:** hr, en, other
- **Country focus:** hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~15.8 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~3.9 (range [2.8, 5.07])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.80
- **Rationale:** The resolution workflow is well-structured with five discrete, documented steps, making it highly suitable for an assist tool that can surface backend purchase-verification results, pre-populate the correct workaround link, and draft triage messages. Time savings come primarily from reducing lookup and message-drafting time, not from eliminating judgment on escalation routing.
- **Validation:** Run assist tool in shadow mode for 2 weeks alongside live agents on this ticket cluster; measure average handle time with vs. without suggestions and acceptance rate of drafted responses to validate the 25% time-reduction midpoint.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~5 (range [3.5, 6.5])
- **Hours eliminated per year:** ~10.5 (range [7.35, 13.65])
- **Root cause:** Multiple interacting bugs: (1) payment-gateway integration returns unhandled error states that surface as generic Croatian error messages instead of actionable codes; (2) privileged/resident-card purchase flow has a known unresolved defect requiring dev-team escalation; (3) purchased-ticket recording is non-atomic, causing tickets to appear absent despite successful backend state. Vendor API reliability from local parking operators is an additional external factor.
- **Rationale:** A comprehensive fix touching payment-gateway error handling, privileged-card flow, and idempotent ticket recording could eliminate the majority of these contacts, but vendor-dependent issues (operator-side ticket ownership) would persist regardless of app improvements. The 67% elimination estimate reflects the portion of tickets attributable to fixable app-side bugs.
- **Validation:** Engineering team should instrument the payment flow end-to-end in a staging environment, reproduce each failure mode against sandbox operator APIs, and track post-release contact-rate reduction over a 6-week window to calibrate the actual elimination rate.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~1.2 (range [0.84, 1.56])
- **Form:** `help_center`
- **Deflection rate:** ~15% (range [10%, 20%])
- **Feasibility:** 0.45
- **Rationale:** A subset of tickets (card management and retry-after-fix scenarios) could be addressed by a help-center article with step-by-step card update instructions and a status page link, but many failures require backend verification or vendor escalation that no self-service page can replace. Deflection potential is therefore modest and limited to the simpler card-management sub-pattern.
- **Validation:** Deploy a targeted help-center article plus an in-app contextual link for 4 weeks; measure ticket creation rate before and after and tag deflected contacts via article feedback ('did this solve your issue?') to validate the 15% midpoint.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 15% of tickets
- **Hours saved per year:** ~1.2 (range [0.84, 1.56])
- **Narrow use case:** Auto-verify backend purchase recording and send a 'purchase confirmed — please retry' notification when the ticket was silently recorded despite the error message
- **Safety constraints:**
  - Must only close ticket autonomously when backend API confirms purchase recorded with no ambiguity; any uncertain state routes to agent
  - No autonomous handling of privileged-card or resident-card flows, which require dev-team escalation
  - No autonomous payment card modifications or deletions on behalf of users
  - Must never interact with local parking operators or vendor systems autonomously
  - All autonomous actions must be logged and reviewable for 90 days for dispute purposes
  - User must receive a clear notification that the action was automated with an opt-out to human review
- **Rationale:** Only the narrow sub-case of a silently-recorded-but-error-displayed ticket is safe to resolve autonomously, because it requires only a read from the backend and a notification — no payment action or vendor coordination. This likely represents at most 15% of tickets, capping potential savings.
- **Validation:** Pilot with 4-week supervised automation on the purchase-verification sub-case only; acceptance criteria: zero false-positive closures (ticket closed but purchase not actually recorded), measured by post-closure user re-contact rate below 5%.

### Risks

- **Compliance concerns:**
  - Payment data handling must comply with Croatian and EU financial regulations (PSD2, GDPR); any automation touching payment state must be auditable
  - Automated closure of payment-related tickets without explicit user confirmation may create consumer-protection exposure under Croatian consumer law
- **Must not automate:**
  - Privileged/resident-card purchase escalations — these require human judgment and development-team coordination
  - Decisions to redirect users to external parking operators, as incorrect routing could leave users without valid parking tickets and expose them to fines
  - Any action that modifies, deletes, or charges a user's payment card
  - Escalation decisions involving suspected fraud or disputed charges
- **Vendor dependencies blocking automation:**
  - Local parking operators (Gradski parking Šibenik, TD Baška, Parking Opatija, Dubrovnik parking) control ticket-ownership records and privileged-card eligibility; their APIs and manual processes cannot be automated by Bmove unilaterally
  - Operator API reliability and response SLAs are outside Bmove's control, limiting the effectiveness of both product fixes and automation until vendor agreements or fallback mechanisms are in place

## Agent compatibility

- **Status:** `active` (extraction confidence 0.92)
- **Brainbox skill:** `reference_only`
- **Claude skill:** `reference_only`
- **Agent-assist:** `False`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Engineering backlog — not for runtime agents

