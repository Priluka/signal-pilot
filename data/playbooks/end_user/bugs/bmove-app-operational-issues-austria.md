---
id: bmove-app-operational-issues-austria
name: bmove_app_operational_issues_austria
title: 'Bmove App Operational Issues: Open Sessions, Ticketless Setup, and General App Problems'
description: Users of the Bmove parking app report a variety of operational problems, most commonly ghost/stuck parking sessions
  that remain open after vehicle exit, preventing further app use. Secondary issues include difficulty setting up or using
  the ticketless (license plate recognition) entry system, and general app malfunctions such as crashes, missing map views,
  or failed payment setups. The majority of affected users are in Austria, with some cases from Germany and other countries.
category: end_user/bugs
ticket_class: end_user
issue_category: bug_in_product
resolution_pattern: manual_close
languages:
- de
- en
country_focus:
- at
- de
- other
status: active
cluster_id: BS:unknown|austria|no_label:c4
project_key: BS
cluster_size: 107
cluster_size_dedup: 74
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.82
extraction_model: claude-sonnet-4-6
frequency_per_month: 1.45
median_resolution_minutes: 2786.0
p95_resolution_minutes: 123990.39999999963
cannot_reproduce_rate: 0.0561
data_window_start: '2023-08-21'
data_window_end: '2026-04-30'
annual_hours_saved: 4.2
roi:
  baseline_active_hours: 18.9
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 3.4
  deflection_hours_range:
  - 2.4
  - 4.3
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 4.2
  agent_assist_hours_range:
  - 3.0
  - 5.3
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 14.2
  product_fix_hours_range:
  - 10.0
  - 18.4
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 1.9
  autonomous_resolve_hours_range:
  - 1.4
  - 2.5
  autonomous_resolve_max_safe_volume_pct: 0.2
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-50000
- BS-14174
- BS-27759
- BS-12059
- BS-15196
- BS-24799
- BS-29314
- BS-45394
- BS-46036
- BS-45369
- BS-47225
- BS-43668
- BS-46300
- BS-47034
- BS-52889
- BS-47397
- BS-46057
- BS-51227
canonical_examples:
- BS-50000
- BS-15196
- BS-52889
vendor_dependency:
  vendor_name: null
  involves_vendor: false
  typical_wait_days: 2
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.2
  autonomous_resolve_narrow_use_case: Automated ghost-session close triggered by confirmed exit event, limited to accounts
    with a single unambiguous open session and no payment dispute flag
  autonomous_resolve_safety_constraints:
  - Must not close a session that has an associated active charge dispute or unpaid balance
  - Must verify exit event from parking operator data before auto-close to avoid erroneous session termination
  - Must not auto-close sessions involving vehicles that could still be on-site (e.g., multi-day parking)
  - Requires opt-in confirmation step from user before finalizing to guard against false positives
  - Audit log of every autonomous close action must be retained for 90 days for dispute resolution
related_playbooks:
- austrian-open-session-at-exit
- austrian-ticketless-open-session-at-exit__06e3d4
- austrian-ticketless-open-session-at-exit__deee93
- b2b-partner-austria-ticketless-open-session-at-exit
- bmove-app-feedback-mixed-issues__7950cd
- bmove-app-feedback-mixed-issues__d6cf0c
- bmove-skidata-not-recognized-manual-open
- croatia-parking-payment-failure__e3b934
- croatia-ticketless-open-session-at-exit__a7c97e
- croatia-ticketless-open-session-at-exit__f25b63
- croatian-ticketless-open-session-at-exit__275624
- croatian-ticketless-open-session-at-exit__dc548a
- croatian-ticketless-open-session-at-exit__e3afed
- manual-debt-cancellation-request
- missing-parking-invoice-receipt
- open-session-at-exit-austria
- open-session-at-exit-payment-failure
- pkc-license-plate-purchase-logging
- scs-westfield-open-session-daily-check__a69ff7
- scs-westfield-open-session-daily-check__c72ee4
- ticketless-open-session-at-exit__960f17
- ticketless-open-session-at-exit__d8d1ba
- ticketless-open-session-at-exit__fd04ac
- ticketless-open-session-not-closed-at-exit
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Bmove App Operational Issues: Open Sessions, Ticketless Setup, and General App Problems

## What this pattern is

Users of the Bmove parking app report a variety of operational problems, most commonly ghost/stuck parking sessions that remain open after vehicle exit, preventing further app use. Secondary issues include difficulty setting up or using the ticketless (license plate recognition) entry system, and general app malfunctions such as crashes, missing map views, or failed payment setups. The majority of affected users are in Austria, with some cases from Germany and other countries.

## When this applies

- Vehicle not recognized by license plate camera at exit, leaving session open
- User re-enters garage or rents a car that has an existing active session from previous user
- License plate not supported (e.g., non-Austrian/non-German plates) for ticketless system
- User attempts to set up ticketless parking but cannot link vehicle or payment method
- App crashes or freezes during vehicle registration or use
- Bmove system reported as non-functional by garage staff at entry
- User receives a penalty ticket despite having purchased a parking ticket via app
- User unsure whether payment or setup was completed successfully

## Typical resolution flow

1. User contacts support via app feedback form, web contact form, or email reporting the issue
2. Support agent acknowledges receipt and promises 1-2 business day response
3. Agent investigates the specific user account, license plate, and session in the backend system
4. For open sessions: agent manually closes the parking session with correct exit timestamp
5. For ticketless setup issues: agent provides step-by-step instructions or explains system limitations (e.g., unsupported foreign plates)
6. Agent confirms resolution to user and advises restarting the app if session still appears active

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Manually close open/ghost parking session in backend system | support_agent | Bmove backend/admin system | 15 min |
| Instruct user to add vehicle and configure ticketless/payment link | support_agent | email/written instruction | 10 min |
| Explain license plate recognition limitations for foreign plates | support_agent | email | 10 min |
| Investigate why vehicle was not recognized at entry/exit using logs | support_agent or technical_team | Bmove backend/admin system | 30 min |

## Evidence

Derived from 107 tickets in cluster `BS:unknown|austria|no_label:c4`. Direct quotes from 7 representative tickets:

- `BS-50000` _[de]_: "Leider sagt meine bmove app, dass ich seit zwei 22.6.2023 um 08:55 Uhr in der C&A Garage stehe, was nicht stimmt - deswegen kann ich aber die app nicht mehr verwenden."
- `BS-15196` _[de]_: "Ich habe seit 75 Tagen eine aktive Sitzung die es nicht gibt... Es ist kein gutes Gefühl welche Kosten sich da anhäufen."
- `BS-52889` _[de]_: "Auto wurde bei der Ausfahrt um ca. 22:00 nicht erkannt und somit ist das Ticket noch immer offen. Der Schranken wurde per Telefon von einem Mitarbeiter geöffnet."
- `BS-47034` _[en]_: "Unfortunately, this functionality is currently not supported for vehicle license plates from the Republic of Serbia."
- `BS-45394` _[de]_: "Leider funktioniert die Einfahrt von 10x mindestens 3x nicht und ich muss den höheren Tarif zahlen. Das ist nicht Sinn und Zweck."
- `BS-46036` _[de]_: "in meiner Bmove-App (Android, Pixel 8a) fehlt die komplette Standortliste/Kartenansicht. Ich sehe nur Ticketless, aber keine Garagenstandorte."
- `BS-51227` _[de]_: "mir bei der Einfahrt am 25.03. 22:56 vom Disponenten mitgeteilt, dass das bmove-System aktuell nicht funktionsfähig sei."

## Cluster statistics

- **Volume:** 107 tickets total (74 unique semantic events after dedup)
- **Frequency:** 1.45 tickets/month (over data window 2023-08-21 → 2026-04-30)
- **Median resolution:** 1.9 days
- **Cannot Reproduce rate:** 5.6%
- **Languages:** de, en
- **Country focus:** at, de, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~18.9 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~4.2 (range [3, 5.3])
- **Time reduction per ticket:** ~22% (range [16%, 28%])
- **Feasibility:** 0.75
- **Rationale:** Agent-assist can provide pre-populated backend deep-links for session closure, templated setup instructions for ticketless configuration, and a log-lookup prompt to reduce the 30-min investigation step; the structured resolution pattern makes drafting reliable. Time savings are modest because the dominant work (manual backend session close) still requires agent execution.
- **Validation:** Run a 3-week shadow-mode pilot where the assist tool surfaces the session-close shortcut and response templates alongside live tickets; compare average handle time vs. the preceding 3-week baseline.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~4 (range [3, 5])
- **Hours eliminated per year:** ~14.2 (range [10, 18.4])
- **Root cause:** The app fails to reliably close parking sessions on vehicle exit, likely due to missed exit events from the license plate recognition system or a session-state sync failure between the app client and backend. Foreign plate recognition failures suggest a secondary gap in the LPR model's coverage.
- **Rationale:** A reliable automatic session-close mechanism and improved exit-event detection would eliminate the dominant resolution action (~15 min/ticket manual close) for the majority of tickets; hours eliminated are capped at the 18.9 h baseline. Residual edge cases and foreign-plate issues would persist, moderating the upper bound.
- **Validation:** Engineering team should instrument session-close event logging to quantify the miss-rate, then run a canary release of the fix on a subset of Austrian garages for 4 weeks, comparing ghost-session ticket rates pre/post.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~3.4 (range [2.4, 4.3])
- **Form:** `help_center`
- **Deflection rate:** ~18% (range [13%, 23%])
- **Feasibility:** 0.50
- **Rationale:** Ghost session issues and ticketless setup instructions are partially self-serviceable via a help center article, but many users will still need backend action (session close) that cannot be self-served. Deflection potential is therefore limited to the subset of informational and setup queries.
- **Validation:** Deploy a targeted help center article covering ghost session FAQs and ticketless setup steps; measure ticket volume and contact reason over a 6-week period before/after to isolate deflection rate.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~1.9 (range [1.4, 2.47])
- **Narrow use case:** Automated ghost-session close triggered by confirmed exit event, limited to accounts with a single unambiguous open session and no payment dispute flag
- **Safety constraints:**
  - Must not close a session that has an associated active charge dispute or unpaid balance
  - Must verify exit event from parking operator data before auto-close to avoid erroneous session termination
  - Must not auto-close sessions involving vehicles that could still be on-site (e.g., multi-day parking)
  - Requires opt-in confirmation step from user before finalizing to guard against false positives
  - Audit log of every autonomous close action must be retained for 90 days for dispute resolution
- **Rationale:** Full autonomous resolution carries financial and data-accuracy risk (incorrect session close could incorrectly terminate a live session or waive fees), so the safe volume is capped at 20% of tickets meeting strict eligibility criteria. Hours savings are limited given the low annual frequency and conservative scope.
- **Validation:** Pilot over 8 weeks on Austrian accounts only with all safety constraints enforced; acceptance criteria include zero erroneous closes on sessions later found to be active, and agent review of a random 20% sample to validate decision quality.

### Risks

- **Compliance concerns:**
  - Automated session closure affects billing records; any error could result in incorrect charges or unwarranted refunds, requiring clear audit trails under applicable consumer protection and payment regulations (e.g., Austrian ZaDiG, EU PSD2).
  - Retention and processing of license plate data for recognition logging may fall under GDPR; ensure data minimisation and deletion schedules are documented.
- **Must not automate:**
  - Session closes where a payment dispute or chargeback is in progress
  - Cases involving foreign plates where recognition confidence is low and manual log review is needed
  - Any action that modifies a user's payment method or billing details without explicit user consent

## Agent compatibility

- **Status:** `active` (extraction confidence 0.82)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

