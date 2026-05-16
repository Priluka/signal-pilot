---
id: croatian-end-user-wrong-registration-storno-refund
name: croatian_end_user_wrong_registration_storno_refund
title: Croatian end-users requesting cancellation or refund after paying parking for wrong vehicle registration or wrong zone/city
description: End users in Croatia (and occasionally other countries) accidentally purchase parking tickets for the wrong licence
  plate, wrong parking zone, or wrong city via the Bmove app and subsequently request a cancellation (storno) or refund. Bmove
  support cannot technically reverse or modify purchased tickets and redirects users to the responsible local parking authority
  (koncesionar). A secondary sub-pattern involves payment confusion where users believe a payment failed but the ticket was
  actually issued successfully.
category: end_user/user_issues
ticket_class: end_user
issue_category: misuse
resolution_pattern: vendor_escalation
languages:
- hr
country_focus:
- hr
- other
status: active
cluster_id: BS:end_user|croatia|user_error:c1
project_key: BS
cluster_size: 85
cluster_size_dedup: 85
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.93
extraction_model: claude-sonnet-4-6
frequency_per_month: 1.67
median_resolution_minutes: 1693.0
p95_resolution_minutes: 36776.79999999999
cannot_reproduce_rate: 0.0
data_window_start: '2023-05-03'
data_window_end: '2026-01-21'
annual_hours_saved: 2.1
roi:
  baseline_active_hours: 6.0
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 1.5
  deflection_hours_range:
  - 1.1
  - 1.9
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 2.1
  agent_assist_hours_range:
  - 1.5
  - 2.7
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 1.2
  product_fix_hours_range:
  - 0.8
  - 1.6
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: low
  autonomous_resolve_hours_midpoint: 0.5
  autonomous_resolve_hours_range:
  - 0.3
  - 0.7
  autonomous_resolve_max_safe_volume_pct: 0.15
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-37868
- BS-25666
- BS-9162
- BS-8432
- BS-11681
- BS-13982
- BS-17901
- BS-24630
- BS-17990
- BS-40327
- BS-39967
- BS-24199
- BS-8771
- BS-20335
- BS-42791
- BS-27807
- BS-10281
- BS-10851
canonical_examples:
- BS-8432
- BS-39967
- BS-24630
vendor_dependency:
  vendor_name: Local parking authority / koncesionar (e.g. Zagrebparking, Splitparking, Malinska, Usluga Poreč, Komunalni
    servis Rovinj)
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Vendor coordination — needs human verification
  autonomous_resolve_max_safe_volume_pct: 0.15
  autonomous_resolve_narrow_use_case: 'Payment-confusion sub-pattern only: auto-confirm ticket issuance success and surface
    active ticket details when the user''s most recent transaction completed within the last 30 minutes and no actual refund
    action is possible.'
  autonomous_resolve_safety_constraints:
  - Must not promise or imply that Bmove will initiate a refund or cancellation on the user's behalf
  - Must not send the user to a local authority without confirming which authority is relevant to the purchased zone/city
  - Must escalate to human agent if the user explicitly disputes the charge or mentions a credit-card dispute
  - Must not handle cases where the ticket was purchased more than 24 hours ago (policy ambiguity increases)
  - Must comply with Croatian consumer-protection information requirements (GDPR-adjacent disclosure of transaction data)
related_playbooks:
- croatia-bmove-app-feedback-miscellaneous
- croatia-parking-fine-dispute
- croatia-parking-fine-dispute-and-payment
- croatia-parking-fine-payment-failure
- croatia-parking-payment-failure__ffdf4e
- croatia-parking-ticket-storno-user-error
- croatia-ticketless-best-in-parking-knowledge-gap
- croatia-ticketless-open-session-at-exit__f25b63
- croatia-ticketless-rental-car-ghost-charge
- croatian-invoice-download-request
- croatian-parking-debt-payment-failure
- croatian-ticketless-open-session-at-exit__275624
- croatian-ticketless-open-session-at-exit__56d2b2
- croatian-ticketless-open-session-at-exit__ab83b0
- croatian-ticketless-open-session-at-exit__dc548a
- croatian-ticketless-open-session-at-exit__e3afed
- open-session-at-exit-payment-failure
- wrong-parking-ticket-purchase-redirect
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Croatian end-users requesting cancellation or refund after paying parking for wrong vehicle registration or wrong zone/city

## What this pattern is

End users in Croatia (and occasionally other countries) accidentally purchase parking tickets for the wrong licence plate, wrong parking zone, or wrong city via the Bmove app and subsequently request a cancellation (storno) or refund. Bmove support cannot technically reverse or modify purchased tickets and redirects users to the responsible local parking authority (koncesionar). A secondary sub-pattern involves payment confusion where users believe a payment failed but the ticket was actually issued successfully.

## When this applies

- User purchased a parking ticket for an incorrect vehicle registration plate
- User purchased a parking ticket for the wrong parking zone
- User purchased a parking ticket for the wrong city or location
- User received a fine despite believing they had paid correctly
- User wants to cancel an active or recently purchased parking ticket
- User confused by 'payment time not available' message and unsure if payment succeeded
- User unaware of Ticketless auto-charge for a vehicle they no longer use

## Typical resolution flow

1. User submits feedback via Bmove app describing the erroneous purchase or payment issue
2. Ticket is created in Jira as end_user sub_issue (storno_request, refund_request, or payment_failure)
3. Support agent reviews the user's purchase history in the system
4. Support agent confirms that purchased tickets cannot be modified or cancelled by Bmove
5. Support agent redirects user to the relevant local parking authority (koncesionar) with contact details
6. If payment confusion, support agent explains what a successful purchase looks like (active ticket visible, email notification, charge applied)
7. Ticket is closed; resolution depends on the local parking authority

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Review user's purchase history and identify the erroneous ticket | support_agent | Jira / Bmove back-office | 5 min |
| Inform user that Bmove cannot technically cancel or modify purchased tickets | support_agent | Jira comment / email | 5 min |
| Redirect user to local parking authority with contact details (email/phone/website) | support_agent | Jira comment / email | 5 min |
| Explain payment success criteria (active ticket on home screen, email notification, card charge) | support_agent | Jira comment / email | 3 min |

## Vendor dependency

- **Vendor:** Local parking authority / koncesionar (e.g. Zagrebparking, Splitparking, Malinska, Usluga Poreč, Komunalni servis Rovinj)

## Evidence

Derived from 85 tickets in cluster `BS:end_user|croatia|user_error:c1`. Direct quotes from 8 representative tickets:

- `BS-8432` _[hr]_: "zabunom sam kupio kartu za pogresno vozilo. Mozete li stornirati kartu za ZG****?"
- `BS-39967` _[hr]_: "tehnički nismo u mogućnosti promijniti registraciju za kupljenu kartu. Sve kupljene karte su u nadležnosti parking službi"
- `BS-24630` _[hr]_: "Slucajno sam uplatio parking za krivu registracijsku oznaku. Da li je moguce dobiti povrat novca?"
- `BS-42791` _[hr]_: "naplatio mi se Poreč 2 zona . molim vas da mi napravite povrat sredstava jer je to definitivno greška aplikacije"
- `BS-27807` _[hr]_: "platio sam parking ali mi nije došla potvrda na mail, a nije mi ni skinulo sa kartice. pisalo je da je kupnja uspješna"
- `BS-10281` _[hr]_: "Greškom sam uplatio za zonu 2 a auto nam u zoni tri tako da smo dobili opomenu na autu"
- `BS-10851` _[hr]_: "slučajno sam uplatila parking za registraciju ZG**** umjesto za ZG****. Možete li ikako stornirati račun"
- `BS-11681` _[hr]_: "po lokaciji platila sam parking, a dočekala me kazna pod brisačem. Parkirala sam kod Arene, a aplikacija mi je naplatila kartu na drugom kraju grada"

## Cluster statistics

- **Volume:** 85 tickets total (85 unique semantic events after dedup)
- **Frequency:** 1.67 tickets/month (over data window 2023-05-03 → 2026-01-21)
- **Median resolution:** 1.2 days
- **Languages:** hr
- **Country focus:** hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~6 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~2.1 (range [1.5, 2.7])
- **Time reduction per ticket:** ~35% (range [25%, 45%])
- **Feasibility:** 0.85
- **Rationale:** This pattern follows a highly predictable resolution script (look up ticket, explain no-cancel policy, provide authority contact); an agent-assist tool can auto-retrieve the purchase record and pre-populate a templated response with the correct local authority contact details, significantly reducing active handle time. The 3–5 min lookup and redirect steps are the strongest candidates for automation assistance.
- **Validation:** Run agent-assist in shadow mode for 2 weeks on this cluster, measuring auto-draft acceptance rate and handle-time delta versus a manually handled control group; target ≥75% draft acceptance before full rollout.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `low`
  - Sprints estimate: ~1.5 (range [1.1, 1.9])
- **Hours eliminated per year:** ~1.2 (range [0.84, 1.56])
- **Root cause:** Root cause is user error (wrong plate, zone, or city) combined with a non-reversible transaction model imposed by third-party parking authorities; the secondary payment-confusion sub-pattern is addressable by improving purchase confirmation UX (e.g. persistent confirmation banner, immediate push notification, clearer email receipt). Neither issue is a software defect, but UX improvements could reduce error frequency.
- **Rationale:** Adding a pre-purchase confirmation screen (plate + zone + city review step) and a clearer post-purchase success state could reduce wrong-purchase incidents and payment-confusion contacts; it cannot eliminate the cluster because some users will still proceed through the confirmation without reading it. Hours eliminated are capped well below the 6.0-hour baseline.
- **Validation:** A/B test the confirmation step with 50% of Croatian users for 6 weeks; measure wrong-purchase contact rate per thousand purchases in treatment vs. control to estimate incident reduction.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~1.5 (range [1.1, 1.9])
- **Form:** `in_app_help`
- **Deflection rate:** ~25% (range [18%, 32%])
- **Feasibility:** 0.65
- **Rationale:** A prominent in-app help article explaining that Bmove cannot cancel/modify tickets and directing users immediately to the relevant local authority could prevent a meaningful share of tickets from ever reaching support; however, users who have already paid for the wrong plate or zone are often distressed and may still seek human confirmation, limiting deflection ceiling. Payment-confusion sub-pattern is more amenable to deflection via clear in-app confirmation screens.
- **Validation:** Deploy a contextual in-app help banner on the purchase-confirmation screen plus a searchable FAQ page for 4 weeks; measure ratio of contacts-per-purchase in the treatment cohort versus a matched control cohort to validate deflection rate.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 15% of tickets
- **Hours saved per year:** ~0.5 (range [0.35, 0.65])
- **Narrow use case:** Payment-confusion sub-pattern only: auto-confirm ticket issuance success and surface active ticket details when the user's most recent transaction completed within the last 30 minutes and no actual refund action is possible.
- **Safety constraints:**
  - Must not promise or imply that Bmove will initiate a refund or cancellation on the user's behalf
  - Must not send the user to a local authority without confirming which authority is relevant to the purchased zone/city
  - Must escalate to human agent if the user explicitly disputes the charge or mentions a credit-card dispute
  - Must not handle cases where the ticket was purchased more than 24 hours ago (policy ambiguity increases)
  - Must comply with Croatian consumer-protection information requirements (GDPR-adjacent disclosure of transaction data)
- **Rationale:** Full autonomous resolution is unsafe because the core action is vendor escalation to a municipality-specific authority requiring accurate, up-to-date contact details and no financial commitment from Bmove; the automation risk of mis-routing users or implying a refund is high. Only the narrow payment-confusion sub-pattern (confirming a ticket was issued) is safely automatable, and that sub-pattern represents a small fraction of the cluster.
- **Validation:** Pilot autonomous confirmation replies on payment-confusion tickets (identifiable by keywords: 'plaćanje nije prošlo', 'payment failed', 'nema tiketa') for 4 weeks with a human review queue for all auto-replies; measure containment rate and escalation-to-dispute rate as acceptance criteria.

### Risks

- **Compliance concerns:**
  - Croatian Consumer Protection Act and EU Consumer Rights Directive may require explicit disclosure of refund rights and the responsible party (parking authority vs. app operator); automated messages must not inadvertently misrepresent Bmove's legal obligations.
  - GDPR: auto-retrieval and display of purchase history in agent-assist or autonomous flows must be scoped to the authenticated user's own data only.
  - Parking ticket validity is time-sensitive; incorrect or delayed information about the responsible authority could cause the user to miss a valid appeal window, creating liability exposure for Bmove.
- **Must not automate:**
  - Any response that implies Bmove will process a refund or cancellation on behalf of the user
  - Determination of which local parking authority is responsible when zone or city is ambiguous — requires human verification
  - Escalations where the user has initiated or threatened a credit-card chargeback or formal complaint
  - Responses to tickets older than 24 hours where appeal windows at local authorities may have expired
- **Vendor dependencies blocking automation:**
  - All actual refund or cancellation actions are exclusively controlled by the local parking authority (e.g. Zagrebparking, Splitparking, Usluga Poreč); Bmove has no technical API or contractual mechanism to reverse transactions, so no automation can promise resolution.
  - Contact details and escalation procedures for each municipal authority must be maintained in a curated, up-to-date knowledge base; stale data would cause mis-routing and undermine any assist or autonomous tool.
  - If any future integration with parking authorities' systems were negotiated, the entire ROI model for autonomous resolve would need to be re-evaluated.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.93)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Vendor coordination — needs human verification

