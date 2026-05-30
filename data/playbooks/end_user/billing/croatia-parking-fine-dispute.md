---
id: croatia-parking-fine-dispute
name: croatia_parking_fine_dispute
title: Croatian end-users disputing parking fines despite claiming payment via bmove app
description: End users in Croatia receive a parking fine (dnevna parkirna karta / kazna) after paying or attempting to pay
  via the bmove app or connected channels. Users contact bmove support expecting the fine to be cancelled or the situation
  explained, often believing the app malfunction or a mistake on the part of the parking authority is to blame. The majority
  of cases involve mismatched licence plate numbers, wrong zones selected, timing issues, or occasional app errors, with bmove's
  role limited to being the payment channel while enforcement remains with local parking concessionaires.
category: end_user/billing
ticket_class: end_user
issue_category: billing
resolution_pattern: vendor_escalation
languages:
- hr
country_focus:
- hr
status: active
cluster_id: BS:end_user|croatia|dpk:c0
project_key: BS
cluster_size: 17
cluster_size_dedup: 17
sample_size_used: 17
extraction_schema: v1.0
extraction_confidence: 0.91
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.33
median_resolution_minutes: 239.0
p95_resolution_minutes: 13821.599999999971
cannot_reproduce_rate: 0.0
data_window_start: '2023-07-08'
data_window_end: '2025-12-11'
annual_hours_saved: 0.5
roi:
  baseline_active_hours: 2.0
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.4
  deflection_hours_range:
  - 0.3
  - 0.5
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.5
  agent_assist_hours_range:
  - 0.4
  - 0.7
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 0.4
  product_fix_hours_range:
  - 0.3
  - 0.5
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.1
  autonomous_resolve_hours_range:
  - 0.1
  - 0.1
  autonomous_resolve_max_safe_volume_pct: 0.1
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-23339
- BS-25755
- BS-27865
- BS-28288
- BS-31231
- BS-32577
- BS-40312
- BS-40351
- BS-43776
- BS-46302
- BS-19164
- BS-34299
- BS-35031
- BS-38807
- BS-35100
- BS-10067
- BS-26471
canonical_examples:
- BS-28288
- BS-31231
- BS-40312
vendor_dependency:
  vendor_name: Local parking concessionaires (e.g. Best in Parking / Varaždin, Split parking, Komunalno Kostrena, Komunalac
    Fažana, Zaprešić komunalno)
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: Vendor coordination — needs human verification
  autonomous_resolve_max_safe_volume_pct: 0.1
  autonomous_resolve_narrow_use_case: Auto-send transaction confirmation (plate, zone, timestamp) to user when ticket is a
    clear 'proof of payment' request with no concessionaire escalation required
  autonomous_resolve_safety_constraints:
  - Must not make any commitment to cancel, dispute, or influence a fine on behalf of the user — this authority lies solely
    with the local parking concessionaire
  - Must not autonomously contact or represent bmove to any external parking authority
  - Must route any case involving a potential app malfunction or disputed charge to a human agent
  - Must apply only when the transaction lookup is unambiguous (single matching record for the reported plate/zone/time)
  - Must not handle emotionally escalated or legally sensitive cases autonomously
related_playbooks:
- croatia-bmove-app-feedback-miscellaneous
- croatia-parking-fine-dispute-and-payment
- croatia-parking-fine-payment-failure
- croatia-parking-payment-failure__ffdf4e
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

# Croatian end-users disputing parking fines despite claiming payment via bmove app

## What this pattern is

End users in Croatia receive a parking fine (dnevna parkirna karta / kazna) after paying or attempting to pay via the bmove app or connected channels. Users contact bmove support expecting the fine to be cancelled or the situation explained, often believing the app malfunction or a mistake on the part of the parking authority is to blame. The majority of cases involve mismatched licence plate numbers, wrong zones selected, timing issues, or occasional app errors, with bmove's role limited to being the payment channel while enforcement remains with local parking concessionaires.

## When this applies

- User pays or attempts to pay parking via bmove app but still receives a fine
- User enters incorrect licence plate number, resulting in fine for unpaid vehicle
- User selects wrong parking zone, causing mismatch with enforced zone
- App displays 'already paid' message preventing new purchase, leading to unpaid period
- Timing mismatch: fine issued before payment is completed
- Parking concession system does not register the bmove payment
- User requests storno (cancellation) of the issued daily parking card

## Typical resolution flow

1. User parks vehicle and pays (or attempts to pay) via bmove or connected app
2. Parking controller issues a fine (dnevna parkirna karta) on the vehicle
3. User notices fine and contacts bmove support via email/ticket with proof of payment
4. bmove support agent reviews transaction and identifies root cause (wrong plate, wrong zone, timing, app error)
5. Agent explains that fine issuance is the responsibility of the local parking concessionaire
6. Agent redirects user to the relevant parking authority with contact details
7. In some cases, internal escalation to bmove staff to contact parking authority directly

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Review transaction record to verify what was paid (plate, zone, time) | bmove support agent | Jira / internal transaction system | 10 min |
| Inform user that fine issuance is outside bmove's jurisdiction and redirect to parking concessionaire | bmove support agent | Jira comment / email | 5 min |
| Internally escalate to bmove staff member to contact parking authority on user's behalf | bmove support agent | Jira mention / internal escalation | 15 min |

## Vendor dependency

- **Vendor:** Local parking concessionaires (e.g. Best in Parking / Varaždin, Split parking, Komunalno Kostrena, Komunalac Fažana, Zaprešić komunalno)

## Evidence

Derived from 17 tickets in cluster `BS:end_user|croatia|dpk:c0`. Direct quotes from 6 representative tickets:

- `BS-28288` _[hr]_: "platili ste parking za vozilo ČL838KJ, a kazna je izdana za vozilo ČK838KJ"
- `BS-31231` _[hr]_: "kaznu izdaju djelatnici parking službe grada Varaždina pa Vas molimo da se za navedeno javite njima"
- `BS-40312` _[hr]_: "platili ste parking za ZH6710J0, a kazna je izdana na ZG****. Dakle pogriješili ste H umjesto G i na kraju nula umjesto slovo O"
- `BS-23339` _[hr]_: "Vaš prvi pokušaj plaćanja parkinga je bio u 9:38, a kazna je izdana u 9:31"
- `BS-26471` _[hr]_: "Izgleda da je neka greška gdje se naplaćuju kazne u Varaždinu kada netko napiše VZ umjesto VŽ"
- `BS-35100` _[hr]_: "Konstantno javlja poruku da je parking već plaćen za navedeno vozilo iako nije"

## Cluster statistics

- **Volume:** 17 tickets total (17 unique semantic events after dedup)
- **Frequency:** 0.33 tickets/month (over data window 2023-07-08 → 2025-12-11)
- **Median resolution:** 4.0 hours
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~2 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.5 (range [0.36, 0.65])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.75
- **Rationale:** Each ticket follows a consistent two-step pattern: verify the transaction record and communicate the jurisdictional boundary. An agent-assist tool that automatically retrieves the relevant transaction record (plate, zone, timestamp) and pre-populates a templated response referencing the correct concessionaire could meaningfully cut active handle time per ticket. The variability is low enough that draft quality targets are achievable.
- **Validation:** Run shadow-mode for 2 weeks: the assist tool retrieves transaction data and drafts a response alongside the agent's normal workflow; measure draft acceptance rate and time-to-send versus the baseline 30-minute average to confirm time savings before full rollout.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~2 (range [1.4, 2.6])
- **Hours eliminated per year:** ~0.4 (range [0.28, 0.52])
- **Root cause:** The dominant causes are user input errors (wrong plate, wrong zone, timing gaps) and a structural jurisdictional mismatch — bmove processes payment but has no authority over fine issuance or cancellation by local parking concessionaires. Occasional app errors are a minority sub-cause. There is no single product bug; the issue is partly UX (confirmation clarity) and partly an inherent third-party enforcement dependency.
- **Rationale:** Improving in-app UX — such as prominent plate/zone confirmation screens, real-time feedback on session start, and post-payment receipts clearly timestamped — could reduce user input errors and confusion, eliminating a share of these tickets. Full elimination is not achievable because enforcement authority remains external to bmove regardless of UX improvements.
- **Validation:** Engineering team should audit the share of tickets attributable to confirmed user input error (plate/zone mismatch) vs. app malfunction in a sample of 10 tickets; this ratio calibrates how much volume is addressable by UX fixes before committing sprint capacity.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.4 (range [0.28, 0.52])
- **Form:** `help_center`
- **Deflection rate:** ~20% (range [14%, 26%])
- **Feasibility:** 0.55
- **Rationale:** Most users contact support because they don't understand that bmove is only the payment channel and enforcement authority lies with the local concessionaire; a clear help-center article explaining jurisdiction split and directing users to the correct authority could deflect a portion of these tickets. However, deflection is limited because many users have emotionally charged disputes and seek personal validation of their transaction, requiring agent confirmation.
- **Validation:** Deploy a targeted help-center article and in-app FAQ entry for 4 weeks; measure ticket creation rate for this cluster before/after, and tag deflected contacts via a post-article survey asking whether the user's issue was resolved without contacting support.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 10% of tickets
- **Hours saved per year:** ~0.1 (range [0.07, 0.13])
- **Narrow use case:** Auto-send transaction confirmation (plate, zone, timestamp) to user when ticket is a clear 'proof of payment' request with no concessionaire escalation required
- **Safety constraints:**
  - Must not make any commitment to cancel, dispute, or influence a fine on behalf of the user — this authority lies solely with the local parking concessionaire
  - Must not autonomously contact or represent bmove to any external parking authority
  - Must route any case involving a potential app malfunction or disputed charge to a human agent
  - Must apply only when the transaction lookup is unambiguous (single matching record for the reported plate/zone/time)
  - Must not handle emotionally escalated or legally sensitive cases autonomously
- **Rationale:** Autonomous resolution is tightly constrained because bmove has no authority over fine outcomes and any incorrect automated communication could create legal or reputational liability with Croatian municipal concessionaires. Only the narrow sub-case of sending a verified payment receipt without any dispute claim or escalation is safe to automate.
- **Validation:** Pilot over 8 weeks with a maximum of 10% of cluster volume; acceptance criteria: zero cases where the autonomous response is interpreted by the user as a promise of fine cancellation, and zero unintended contacts with parking concessionaires; review all resolved tickets manually before scaling.

### Risks

- **Compliance concerns:**
  - bmove must not misrepresent its authority or imply it can cancel parking fines, which could constitute misleading commercial communication under Croatian consumer protection law
  - Transaction data shared in automated responses must comply with GDPR — confirm lawful basis for automated retrieval and disclosure of payment records
  - Any automated outreach to external parking concessionaires on behalf of users would require explicit authorisation and clear data-sharing agreements
- **Must not automate:**
  - Any commitment to dispute, cancel, or influence a parking fine with a local concessionaire
  - Cases involving suspected app malfunction or platform error that may have caused the fine
  - Communications to external parking authorities — these require human judgment and accountability
  - Escalated or legally threatened cases (user mentions legal action or formal complaint)
- **Vendor dependencies blocking automation:**
  - No API or data exchange exists with local Croatian parking concessionaires (Best in Parking / Varaždin, Split parking, Komunalno Kostrena, Komunalac Fažana, Zaprešić komunalno), making automated fine status lookup or cancellation technically infeasible
  - Typical wait days for vendor responses are unknown, making SLA-based automation unreliable
  - Each concessionaire has independent processes and contact channels, preventing a unified escalation workflow

## Agent compatibility

- **Status:** `active` (extraction confidence 0.91)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Vendor coordination — needs human verification

