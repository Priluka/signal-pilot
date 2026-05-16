---
id: italian-b2b-unsolicited-procurement-marketing-emails
name: italian_b2b_unsolicited_procurement_marketing_emails
title: Unsolicited Italian procurement/tender marketing and webinar emails landing in B2B partner support inbox
description: The Bmove support mailbox (s****@bmove.com) is repeatedly receiving unsolicited commercial email newsletters
  and promotional messages from Italian public-procurement and legal-training vendors (e.g. Infoplus, Famis, Rogaitalia, Infordat,
  ZCS/Zucchetti), advertising webinars, tender-monitoring trials, and training courses. These emails are not genuine support
  requests but are instead marketing communications misdirected or spam-addressed to the support address. The single legitimate
  support ticket in the sample (BS-10567) concerns a simple email-address change request from an Italian B2B partner.
category: b2b_operator/user_issues
ticket_class: b2b_partner
issue_category: misuse
resolution_pattern: no_action
languages:
- it
country_focus:
- it
status: active
cluster_id: BS:b2b_partner|italy|no_label:c1
project_key: BS
cluster_size: 46
cluster_size_dedup: 46
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.88
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.9
median_resolution_minutes: 970.5
p95_resolution_minutes: 1321.95
cannot_reproduce_rate: 0.0
data_window_start: '2023-07-19'
data_window_end: '2026-05-08'
annual_hours_saved: 0.6
roi:
  baseline_active_hours: 2.3
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.0
  deflection_hours_range:
  - 0.0
  - 0.0
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.6
  agent_assist_hours_range:
  - 0.4
  - 0.8
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 1.8
  product_fix_hours_range:
  - 1.3
  - 2.1
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: low
  autonomous_resolve_hours_midpoint: 0.5
  autonomous_resolve_hours_range:
  - 0.4
  - 0.7
  autonomous_resolve_max_safe_volume_pct: 0.25
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-50644
- BS-51731
- BS-51247
- BS-10567
- BS-49271
- BS-52033
- BS-51719
- BS-53219
- BS-50206
- BS-48624
- BS-53164
- BS-52028
- BS-51857
- BS-49020
- BS-49511
- BS-48922
- BS-50320
- BS-52431
canonical_examples:
- BS-50644
- BS-49271
- BS-10567
vendor_dependency:
  vendor_name: Infoplus / Famis / Rogaitalia / Infordat / ZCS Zucchetti (multiple Italian procurement/training vendors)
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: Informational — safe for agent self-service
  autonomous_resolve_max_safe_volume_pct: 0.25
  autonomous_resolve_narrow_use_case: Auto-close inbound tickets whose sender domain and subject-line match a maintained spam-vendor
    allowlist (Infoplus, Famis, Rogaitalia, Infordat, ZCS/Zucchetti known patterns), with no outbound response sent.
  autonomous_resolve_safety_constraints:
  - Only act on tickets where sender domain exactly matches a curated blocklist; no fuzzy matching without human review.
  - Never auto-respond to or unsubscribe on behalf of the sender — silent discard only, to avoid confirming inbox validity.
  - Any ticket containing an account identifier, partner ID, or email-change keyword must be routed to a human agent regardless
    of sender.
  - Maintain a quarantine log for 30 days so false positives can be recovered by a human reviewer.
  - Blocklist must be reviewed and approved by a human operator at least monthly.
related_playbooks:
- bmove-heartbeat-api-anomaly-italy__412abb
- bmove-heartbeat-api-anomaly-italy__a1951a
- bmove-production-anomaly-restoration-notification-it
- gtt-skidata-is-alive-timeout-error
- italian-b2b-invoice-billing-question
- italy-gtt-parking-stop-threshold-alert
- italy-gtt-skidata-invalid-timestamp-anomaly
- microsoft365-quarantine-notification-auto-tickets
- microsoft365-quarantine-phishing-meta-impersonation
- parking-collector-purchase-lot-exhaustion-alert
- russian-spam-suggestion-tickets
- unsolicited-spam-marketing-emails
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Unsolicited Italian procurement/tender marketing and webinar emails landing in B2B partner support inbox

## What this pattern is

The Bmove support mailbox (s****@bmove.com) is repeatedly receiving unsolicited commercial email newsletters and promotional messages from Italian public-procurement and legal-training vendors (e.g. Infoplus, Famis, Rogaitalia, Infordat, ZCS/Zucchetti), advertising webinars, tender-monitoring trials, and training courses. These emails are not genuine support requests but are instead marketing communications misdirected or spam-addressed to the support address. The single legitimate support ticket in the sample (BS-10567) concerns a simple email-address change request from an Italian B2B partner.

## When this applies

- Third-party Italian procurement/legal marketing platforms send bulk newsletter emails to s****@bmove.com
- s****@bmove.com is registered (intentionally or accidentally) on Italian tender-monitoring and training vendor mailing lists
- Automated promotional campaigns from vendors such as Infoplus/Famis, Rogaitalia, Infordat, ZCS dispatch emails that create tickets in the helpdesk
- Occasional genuine B2B partner email (e.g. email-change request) arrives in the same channel

## Typical resolution flow

1. Marketing or newsletter email is sent to s****@bmove.com by an Italian third-party vendor
2. Helpdesk system auto-creates a ticket classified as b2b_partner / other
3. Ticket sits unresolved or is manually closed with no action taken
4. Pattern repeats at high frequency across multiple vendor campaigns

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Review incoming ticket and identify it as unsolicited marketing/spam email | support agent | helpdesk ticketing system | 2 min |
| Close or discard ticket without customer response | support agent | helpdesk ticketing system | 1 min |
| For genuine email-change requests (e.g. BS-10567), update partner email in the system | support agent | CRM / partner management system | 10 min |

## Vendor dependency

- **Vendor:** Infoplus / Famis / Rogaitalia / Infordat / ZCS Zucchetti (multiple Italian procurement/training vendors)

## Evidence

Derived from 46 tickets in cluster `BS:b2b_partner|italy|no_label:c1`. Direct quotes from 6 representative tickets:

- `BS-50644` _[it]_: "La verifica dell'anomalia dell'offerta - Webinar 19 Marzo 📆 Aspetti legali e tecnico-operativi con simulazioni pratiche. Scopri come partecipare gratuitamente."
- `BS-49271` _[it]_: "✅ Solo gli appalti che contano davvero: prova gratis per 7 giorni — Ogni giorno, solo gare coerenti con il tuo profilo"
- `BS-10567` _[it]_: "chiedo che la e-mail sia sostituita con la seguente b****@cantierecreattivo.it"
- `BS-51857` _[it]_: "La prova gratuita che ti abbiamo riservato come omaggio per la tua azienda è terminata... ma non è ancora troppo tardi per approfittarne!"
- `BS-48624` _[it]_: "Gare d'appalto: scopri quelle del tuo settore — Tutte le gare d'Italia sono in un'unica dashboard: smetti di cercare su MEPA e portali regionali"
- `BS-52431` _[it]_: "Formazione Gare d'appalto di Servizi e Forniture: preparazione operativa alla luce del nuovo Bando Tipo - 12 Maggio"

## Cluster statistics

- **Volume:** 46 tickets total (46 unique semantic events after dedup)
- **Frequency:** 0.9 tickets/month (over data window 2023-07-19 → 2026-05-08)
- **Median resolution:** 16.2 hours
- **Languages:** it
- **Country focus:** it

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~2.3 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.6 (range [0.41, 0.754])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.70
- **Rationale:** An AI classifier surfacing a 'Spam – close immediately' recommendation would reduce agent review time for spam tickets from ~3 min to ~1 min, yielding modest but real savings; the genuine email-change tickets (like BS-10567) could also benefit from a pre-filled action template. Given the very low annual volume, absolute savings are small.
- **Validation:** Run classifier in shadow mode for 3 weeks, measuring precision/recall against agent ground-truth labels; accept if precision ≥ 0.95 and recall ≥ 0.90 before activating recommendations.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `low`
  - Sprints estimate: ~0.5 (range [0.3, 0.7])
- **Hours eliminated per year:** ~1.8 (range [1.3, 2.1])
- **Root cause:** The support inbox address (s****@bmove.com) has been harvested or guessed by Italian procurement/training spam lists. This is an external abuse pattern, not a product defect. Mitigation options include inbox-level spam filtering rules, SPF/DKIM/DMARC enforcement, and potentially changing or obfuscating the support address.
- **Rationale:** Configuring server-side or MX-level spam filter rules targeting known sender domains (Infoplus, Famis, Rogaitalia, Infordat, ZCS/Zucchetti) and known subject-line patterns could auto-discard or quarantine ~75–90% of these tickets before they reach agents, eliminating most of the active-work hours. This does not require product engineering in the traditional sense but is an ops/infrastructure task.
- **Validation:** Engineering or IT ops team implements filter rules in staging email environment for 2 weeks, measuring false-positive rate on legitimate partner emails before promoting to production.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0 (range [0.01, 0.013])
- **Form:** `none`
- **Deflection rate:** ~3% (range [2%, 4%])
- **Feasibility:** 0.05
- **Rationale:** Unsolicited spam emails are sent by external marketing vendors, not by support-seeking users, so a self-service FAQ or help-center article cannot intercept or deflect them. The tiny residual deflection estimate reflects the marginal case where a legitimate partner (like BS-10567) might self-serve an email-change request.
- **Validation:** Deploy a help-center article on email-address changes for 4 weeks and measure whether any email-change tickets cease to arrive; expect near-zero impact on spam volume.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 25% of tickets
- **Hours saved per year:** ~0.5 (range [0.37, 0.676])
- **Narrow use case:** Auto-close inbound tickets whose sender domain and subject-line match a maintained spam-vendor allowlist (Infoplus, Famis, Rogaitalia, Infordat, ZCS/Zucchetti known patterns), with no outbound response sent.
- **Safety constraints:**
  - Only act on tickets where sender domain exactly matches a curated blocklist; no fuzzy matching without human review.
  - Never auto-respond to or unsubscribe on behalf of the sender — silent discard only, to avoid confirming inbox validity.
  - Any ticket containing an account identifier, partner ID, or email-change keyword must be routed to a human agent regardless of sender.
  - Maintain a quarantine log for 30 days so false positives can be recovered by a human reviewer.
  - Blocklist must be reviewed and approved by a human operator at least monthly.
- **Rationale:** Autonomous silent-close of confirmed spam from known vendor domains is low-risk and well-scoped; capping at 25% of volume accounts for uncertainty in blocklist completeness and the need to preserve human oversight for any borderline or novel senders. Absolute hours saved remain modest given the low annual frequency.
- **Validation:** Pilot for 4 weeks with auto-close in shadow mode (tickets flagged but still routed to agent); accept automation if false-positive rate is < 2% of flagged tickets after human review of the quarantine log.

### Risks

- **Compliance concerns:**
  - Auto-discarding inbound email without logging may conflict with email-retention or audit policies; quarantine logs should be retained per company data-retention rules.
  - GDPR consideration: sender email addresses are personal data; blocklist and quarantine logs must be handled in accordance with applicable data-protection policies.
  - Silent auto-close must never trigger any outbound communication (e.g. auto-unsubscribe or bounce) that would confirm the inbox address to spammers.
- **Must not automate:**
  - Any ticket that contains a partner account identifier, contract number, or explicit request to change account details — these must always reach a human agent.
  - Tickets from sender domains not on the confirmed blocklist, even if they appear promotional, to avoid false positives with legitimate Italian partners.
  - Any action that sends an outbound reply to a suspected spam sender.
- **Vendor dependencies blocking automation:**
  - No Bmove product vendor dependency blocks these automations; however, the spam-filter implementation depends on the email infrastructure provider (MX/ESP) supporting custom rule configuration.
  - The external spam vendors (Infoplus, Famis, Rogaitalia, Infordat, ZCS/Zucchetti) cannot be compelled to stop sending; blocklist maintenance is an ongoing operational cost with no SLA guarantee of completeness.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.88)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `True`
- **RAG-consumable:** `True`
- **Note:** Informational — safe for agent self-service

