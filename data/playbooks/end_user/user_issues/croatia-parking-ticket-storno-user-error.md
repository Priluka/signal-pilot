---
id: croatia-parking-ticket-storno-user-error
name: croatia_parking_ticket_storno_user_error
title: Croatian end-users requesting cancellation/refund of wrongly purchased parking tickets
description: End users in Croatia (predominantly) purchased parking tickets via the Bmove app by mistake — entering the wrong
  licence plate, selecting the wrong parking zone, wrong vehicle, wrong duration, or accidentally triggering a duplicate purchase.
  They contact Bmove support requesting a cancellation (storno) or refund, but Bmove redirects them to the relevant local
  parking concessionaires as those entities hold jurisdiction over issued tickets.
category: end_user/user_issues
ticket_class: end_user
issue_category: misuse
resolution_pattern: vendor_escalation
languages:
- hr
- en
country_focus:
- hr
status: active
cluster_id: BS:end_user|croatia|user_error:c0
project_key: BS
cluster_size: 38
cluster_size_dedup: 37
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.73
median_resolution_minutes: 506.5
p95_resolution_minutes: 28053.949999999975
cannot_reproduce_rate: 0.0
data_window_start: '2023-05-23'
data_window_end: '2026-01-19'
annual_hours_saved: 0.3
roi:
  baseline_active_hours: 1.0
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.3
  deflection_hours_range:
  - 0.2
  - 0.4
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.3
  agent_assist_hours_range:
  - 0.2
  - 0.4
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 0.3
  product_fix_hours_range:
  - 0.2
  - 0.4
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.2
  autonomous_resolve_hours_range:
  - 0.1
  - 0.3
  autonomous_resolve_max_safe_volume_pct: 0.2
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-18281
- BS-29511
- BS-10059
- BS-9711
- BS-13338
- BS-14703
- BS-18849
- BS-34451
- BS-35611
- BS-17210
- BS-40364
- BS-37763
- BS-36916
- BS-18329
- BS-12245
- BS-39303
- BS-18573
- BS-16405
canonical_examples:
- BS-18281
- BS-29511
- BS-9711
vendor_dependency:
  vendor_name: Local parking concessionaires (e.g. Zagrebparking/ZGH, Rijeka-plus, BestInParking Varaždin, Split Parking,
    Vukovar parking)
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: Vendor coordination — needs human verification
  autonomous_resolve_max_safe_volume_pct: 0.2
  autonomous_resolve_narrow_use_case: Auto-send templated redirect reply when ticket metadata unambiguously identifies the
    city and concessionaire, and the request contains no refund-amount dispute or escalation signal.
  autonomous_resolve_safety_constraints:
  - Must not attempt to initiate or promise a refund on behalf of any concessionaire — Bmove has no authority to issue refunds.
  - Must not handle tickets where the user indicates they received a parking fine or penalty; these require human review.
  - Must not auto-close tickets where city or concessionaire cannot be confidently resolved from metadata alone.
  - Must include a human-review fallback if the user replies dissatisfied after the automated redirect.
  - Automation must be disclosed to the user (transparency requirement).
related_playbooks:
- croatia-bmove-app-feedback-miscellaneous
- croatia-parking-fine-dispute
- croatia-parking-fine-dispute-and-payment
- croatia-parking-fine-payment-failure
- croatia-parking-payment-failure__ffdf4e
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
- open-session-at-exit-payment-failure
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

# Croatian end-users requesting cancellation/refund of wrongly purchased parking tickets

## What this pattern is

End users in Croatia (predominantly) purchased parking tickets via the Bmove app by mistake — entering the wrong licence plate, selecting the wrong parking zone, wrong vehicle, wrong duration, or accidentally triggering a duplicate purchase. They contact Bmove support requesting a cancellation (storno) or refund, but Bmove redirects them to the relevant local parking concessionaires as those entities hold jurisdiction over issued tickets.

## When this applies

- User selected wrong licence plate from saved vehicle list
- User selected wrong parking zone
- User selected wrong parking duration (e.g. weekly instead of monthly, semi-annual instead of monthly)
- App froze or auto-completed purchase unexpectedly
- User accidentally swiped/tapped wrong option
- Duplicate payment made after user self-corrected an error

## Typical resolution flow

1. User makes a purchase error in the Bmove app
2. User often corrects the error by purchasing the correct ticket immediately after
3. User contacts Bmove support via email requesting storno or refund
4. Bmove support agent identifies the responsible parking concessionaire for the city in question
5. Agent redirects user to the appropriate parking concessionaire's contact (email/phone/website)
6. Case is closed by Bmove with no further action on their side

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Receive storno/refund request from end user | support_agent | email/ticketing system | 2 min |
| Identify the city and responsible parking concessionaire from ticket details | support_agent | internal knowledge / ticket content | 2 min |
| Reply to user redirecting them to the parking concessionaire with contact details | support_agent | email | 3 min |

## Vendor dependency

- **Vendor:** Local parking concessionaires (e.g. Zagrebparking/ZGH, Rijeka-plus, BestInParking Varaždin, Split Parking, Vukovar parking)

## Evidence

Derived from 38 tickets in cluster `BS:end_user|croatia|user_error:c0`. Direct quotes from 7 representative tickets:

- `BS-18281` _[hr]_: "Aplikacija se smrznula i kupljena je kriva karta."
- `BS-29511` _[hr]_: "Zabunom sam kupio tjednu kartu za drugu umjesto prve zone."
- `BS-9711` _[hr]_: "kupio sam kartu za krivo vozilo ZG****, a trebao sam za ZG****"
- `BS-40364` _[hr]_: "sve kupljene karte su u nadležnosti parking službi, pa Vas za ovaj problem molimo da im se javite direktno"
- `BS-39303` _[hr]_: "platio sam parking za cijeli dan dva puta, s time da sam prvi put upisao krivu tablicu"
- `BS-13338` _[hr]_: "Zabunom sam kupio polugodišnju parkirnu kartu s početkom od 18.09. Htio sam kupiti mjesečnu kartu."
- `BS-37763` _[hr]_: "u popisu vozila sam omaškom kliznula prstom i očito odabrala pogrešno vozilo"

## Cluster statistics

- **Volume:** 38 tickets total (37 unique semantic events after dedup)
- **Frequency:** 0.73 tickets/month (over data window 2023-05-23 → 2026-01-19)
- **Median resolution:** 8.4 hours
- **Languages:** hr, en
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~1 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.3 (range [0.21, 0.39])
- **Time reduction per ticket:** ~30% (range [21%, 39%])
- **Feasibility:** 0.85
- **Rationale:** The resolution workflow is highly templated: identify the city from ticket details and insert the corresponding concessionaire contact. An agent-assist tool can auto-detect the relevant concessionaire from ticket metadata and pre-populate a draft reply, meaningfully cutting the lookup and composition steps (steps 2–3, totalling ~5 min). The remaining ~2 min for review and send is largely irreducible.
- **Validation:** Run the assist tool in shadow mode for 3 weeks, measuring draft-acceptance rate and agent edit-distance; target ≥85% acceptance with minimal edits before enabling for live use.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~0.3 (range [0.21, 0.39])
- **Root cause:** Errors stem from end-user mistakes at purchase time (wrong plate, zone, vehicle, duration, or accidental duplicate) rather than a software defect. A UX improvement — such as a prominent purchase-confirmation screen with all selected parameters and a short cancellation window — could reduce incident frequency, but does not fix a bug.
- **Rationale:** Adding a confirmation step with a short in-app self-cancellation window (subject to concessionaire policy) could prevent a portion of mistaken purchases from ever reaching support; the actual reduction depends heavily on concessionaire willingness to honour app-initiated cancellations, which is outside Bmove's direct control. Hours eliminated are capped at the 1.0 h baseline.
- **Validation:** Prototype a confirmation/review screen in a feature branch; conduct usability testing with 10–15 Croatian users and measure accidental-purchase rates in a 4-week staged rollout before estimating full-year impact.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.3 (range [0.25, 0.44])
- **Form:** `help_center`
- **Deflection rate:** ~35% (range [25%, 45%])
- **Feasibility:** 0.70
- **Rationale:** A clear help-center article listing each Croatian concessionaire's contact details by city could allow a meaningful share of users to self-redirect without opening a ticket; however, users who have already made a mistaken purchase are often distressed and may still prefer human confirmation. The redirection information is stable and city-specific, making it well-suited to a structured FAQ page.
- **Validation:** Publish a dedicated 'Wrong parking ticket in Croatia?' help-center page with per-city concessionaire contacts, then measure ticket-open rate for this cluster over 8 weeks vs. the prior 8-week baseline to estimate deflection rate.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~0.2 (range [0.14, 0.26])
- **Narrow use case:** Auto-send templated redirect reply when ticket metadata unambiguously identifies the city and concessionaire, and the request contains no refund-amount dispute or escalation signal.
- **Safety constraints:**
  - Must not attempt to initiate or promise a refund on behalf of any concessionaire — Bmove has no authority to issue refunds.
  - Must not handle tickets where the user indicates they received a parking fine or penalty; these require human review.
  - Must not auto-close tickets where city or concessionaire cannot be confidently resolved from metadata alone.
  - Must include a human-review fallback if the user replies dissatisfied after the automated redirect.
  - Automation must be disclosed to the user (transparency requirement).
- **Rationale:** Because the only action taken is a redirect — never a financial transaction or policy decision — a narrow autonomous flow is feasible for clear-cut cases; however, low annual volume (8.7 tickets/year) means absolute savings are very small, and the effort to build and maintain the automation may not be justified on ROI grounds alone. Vendor dependency on concessionaire policies makes fully automated resolution inappropriate.
- **Validation:** Pilot automated redirect for 10% of incoming tickets over 8 weeks with mandatory human spot-check of every auto-sent response; accept if CSAT on these tickets equals or exceeds agent-handled baseline before expanding to 20%.

### Risks

- **Compliance concerns:**
  - Refund and cancellation authority rests solely with local parking concessionaires; any communication implying Bmove can issue refunds could create legal or contractual liability.
  - Croatian consumer-protection regulations may require specific disclosures when redirecting users to third-party entities; legal review of redirect template is advisable.
  - GDPR: ticket metadata (licence plate, location) is personal data — automated processing must be covered by an appropriate lawful basis and documented in the data-processing register.
- **Must not automate:**
  - Any action that implies or initiates a financial refund or credit on behalf of a concessionaire.
  - Handling of tickets where a parking enforcement action (fine/penalty) has already been issued — these require human judgment.
  - Escalations where the user disputes the concessionaire's decision or threatens legal action.
- **Vendor dependencies blocking automation:**
  - None of the concessionaires (Zagrebparking/ZGH, Rijeka-plus, BestInParking Varaždin, Split Parking, Vukovar parking) have an API or structured intake — all cancellation/refund processing is fully outside Bmove's systems, blocking any end-to-end automated resolution.
  - Concessionaire contact details and policies may change without notice; any automated redirect content requires a maintenance process to stay accurate.
  - A self-cancellation window in-app would require formal policy agreements with each concessionaire before launch, which may not be achievable in the near term.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Vendor coordination — needs human verification

