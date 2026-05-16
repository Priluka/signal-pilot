---
id: russian-spam-suggestion-tickets
name: russian_spam_suggestion_tickets
title: Repeated Russian-language spam tickets claiming to have 'suggestions' for site management with attached files
description: A large cluster of near-identical tickets submitted in Russian (with English translation appended) claiming the
  sender has 'suggestions' for the site owner and asking support staff to forward their contact details and attached files
  to management. The messages follow a fixed template with only minor wording variations and always include 4 attached files
  of similar size (16–19 kB). Several tickets use seasonal subject lines ('С Новым Годом', 'С Наступающим') while the body
  text remains unchanged, indicating automated or bulk submission behaviour.
category: end_user/user_issues
ticket_class: end_user
issue_category: misuse
resolution_pattern: no_action
languages:
- other
- en
country_focus:
- other
status: active
cluster_id: BS:unknown|no_value|no_label:c0
project_key: BS
cluster_size: 29
cluster_size_dedup: 29
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.57
median_resolution_minutes: 1414.0
p95_resolution_minutes: 6873.4
cannot_reproduce_rate: 0.0
data_window_start: '2022-10-15'
data_window_end: '2023-01-04'
annual_hours_saved: 0.1
roi:
  baseline_active_hours: 0.3
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.0
  deflection_hours_range:
  - 0.0
  - 0.0
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.1
  agent_assist_hours_range:
  - 0.1
  - 0.1
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 0.3
  product_fix_hours_range:
  - 0.2
  - 0.3
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: low
  autonomous_resolve_hours_midpoint: 0.1
  autonomous_resolve_hours_range:
  - 0.1
  - 0.1
  autonomous_resolve_max_safe_volume_pct: 0.25
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-3832
- BS-4525
- BS-4065
- BS-4468
- BS-4616
- BS-3742
- BS-4492
- BS-3436
- BS-3413
- BS-3577
- BS-2646
- BS-4471
- BS-3728
- BS-3751
- BS-4466
- BS-3815
- BS-4603
- BS-3489
canonical_examples:
- BS-3832
- BS-4525
- BS-4065
vendor_dependency:
  vendor_name: null
  involves_vendor: false
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: Informational — safe for agent self-service
  autonomous_resolve_max_safe_volume_pct: 0.25
  autonomous_resolve_narrow_use_case: Auto-close tickets matching the fixed Russian-language 'suggestions' spam template (language
    = Russian, attachment count = 4, attachment size 16–19 kB each, body fingerprint match) with no response sent.
  autonomous_resolve_safety_constraints:
  - Fingerprint match must require ALL criteria simultaneously (language, attachment count, size band, keyword match) to minimise
    false positives.
  - Auto-closed tickets must be retained in audit log for 90 days for manual review on appeal.
  - A human agent must review a random 10% sample weekly during any pilot period.
  - Auto-closure must never send a reply to the submitter to avoid confirming a live address.
  - Scope must not expand beyond this exact template pattern without re-evaluation.
related_playbooks:
- bmove-app-feedback-mixed-issues__d6cf0c
- hr-parking-transaction-reconciliation-discrepancy
- italian-b2b-unsolicited-procurement-marketing-emails
- microsoft365-quarantine-notification-auto-tickets
- microsoft365-quarantine-phishing-meta-impersonation
- test-and-junk-tickets
- unsolicited-spam-marketing-emails
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Repeated Russian-language spam tickets claiming to have 'suggestions' for site management with attached files

## What this pattern is

A large cluster of near-identical tickets submitted in Russian (with English translation appended) claiming the sender has 'suggestions' for the site owner and asking support staff to forward their contact details and attached files to management. The messages follow a fixed template with only minor wording variations and always include 4 attached files of similar size (16–19 kB). Several tickets use seasonal subject lines ('С Новым Годом', 'С Наступающим') while the body text remains unchanged, indicating automated or bulk submission behaviour.

## When this applies

- Submission of a support ticket with the subject 'Предложение' (Suggestion) or a seasonal greeting variant
- Boilerplate Russian/English body text requesting forwarding of suggestions and contact details to management
- Attachment of 4 files of approximately 16–19 kB each

## Typical resolution flow

1. External actor submits ticket via support portal using near-identical templated message
2. Ticket is logged with class=unknown, sub_issue=other, country=OTHER
3. No legitimate support need is identified
4. Ticket is closed with no action taken

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Review incoming ticket and identify it as part of known spam/bulk submission pattern | support_agent | Jira Service Management | 2 min |
| Close ticket without response or action | support_agent | Jira Service Management | 1 min |

## Evidence

Derived from 29 tickets in cluster `BS:unknown|no_value|no_label:c0`. Direct quotes from 3 representative tickets:

- `BS-3832` _[other]_: "Здравствуйтe. У мeня eсть прeдложeния для владeльца сайта. Пeрeдайте пожалуйста мои прeдложeния и контакты руководству, которыe указаны в прикреплeнных файлах."
- `BS-4525` _[en]_: "Hello. I have suggestions for the site owner. Please pass on my suggestions and contacts to the management, which are indicated in the attached files."
- `BS-4065` _[en]_: "Please pass on my suggestions that I sent in a letter for your guidance. Please contact me at the contacts indicated in the offer."

## Cluster statistics

- **Volume:** 29 tickets total (29 unique semantic events after dedup)
- **Frequency:** 0.57 tickets/month (over data window 2022-10-15 → 2023-01-04)
- **Median resolution:** 23.6 hours
- **Languages:** other, en
- **Country focus:** other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~0.3 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.1 (range [0.056, 0.1])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.55
- **Rationale:** An assist tool that surfaces a 'known spam — close without action' banner on pattern match could shave roughly 1 minute off the 3-minute handling cycle (identification step), but absolute savings are negligible given the low annual volume.
- **Validation:** Run assist banner in shadow mode for 2 weeks; measure whether agents act on suggestion within 30 seconds versus baseline identification time to confirm time reduction.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `low`
  - Sprints estimate: ~1 (range [0.7, 1.3])
- **Hours eliminated per year:** ~0.3 (range [0.19, 0.3])
- **Root cause:** Tickets originate from external spammers exploiting an open ticket-submission endpoint; this is misuse rather than a product defect. Submission-side controls (CAPTCHA, rate-limiting, language/template fingerprinting at ingestion) could block or auto-discard matching submissions before they reach the queue.
- **Rationale:** A lightweight ingestion filter matching the known fixed template (language, attachment count/size band, keyword fingerprint) could eliminate effectively all tickets in this cluster before agent touch. Hours eliminated are capped at the 0.30 h baseline.
- **Validation:** Engineering should shadow-deploy the filter in log-only mode for 4 weeks, measuring false-positive rate on legitimate Russian-language tickets before enabling auto-discard.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0 (range [0.01, 0.01])
- **Form:** `none`
- **Deflection rate:** ~3% (range [2%, 4%])
- **Feasibility:** 0.05
- **Rationale:** These are bulk spam submissions following a fixed template, not genuine users seeking help; self-service content cannot deter or deflect automated or bad-faith senders. No realistic deflection path exists through help centre or FAQ.
- **Validation:** Not recommended for pilot; effort in building self-service content would exceed any plausible hours saved given the minimal annual volume.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 25% of tickets
- **Hours saved per year:** ~0.1 (range [0.052, 0.098])
- **Narrow use case:** Auto-close tickets matching the fixed Russian-language 'suggestions' spam template (language = Russian, attachment count = 4, attachment size 16–19 kB each, body fingerprint match) with no response sent.
- **Safety constraints:**
  - Fingerprint match must require ALL criteria simultaneously (language, attachment count, size band, keyword match) to minimise false positives.
  - Auto-closed tickets must be retained in audit log for 90 days for manual review on appeal.
  - A human agent must review a random 10% sample weekly during any pilot period.
  - Auto-closure must never send a reply to the submitter to avoid confirming a live address.
  - Scope must not expand beyond this exact template pattern without re-evaluation.
- **Rationale:** The highly stereotyped, no-action resolution pattern is well-suited to autonomous closure; however, absolute hours saved are very small (under 0.1 h/year) meaning ROI depends on the pattern scaling or the filter also serving a broader spam-blocking function. Over-investing in automation for this cluster alone is not warranted.
- **Validation:** Pilot for 8 weeks with max_safe_volume_pct = 0.20; acceptance criteria are zero false-positive closures of legitimate tickets and ≥ 90% of matching spam tickets auto-closed without agent touch.

### Risks

- **Compliance concerns:**
  - Attached files (16–19 kB each) should not be opened or forwarded; potential malware vector — auto-close rules must ensure attachments are never executed by any automated process.
  - Retaining spam tickets with potentially malicious attachments requires a defined data-retention and secure-deletion policy.
  - If the submitter is ever identified as a legitimate user who mistakenly used a similar template, wrongful auto-closure could harm the relationship — audit log retention is essential.
- **Must not automate:**
  - Do not auto-reply to the submitter in any form — this confirms a live support address and may increase spam volume.
  - Do not forward or open the attached files under any automation path.
  - Do not auto-block submitter email addresses without human review, as source addresses may be spoofed or belong to innocent third parties.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `True`
- **RAG-consumable:** `True`
- **Note:** Informational — safe for agent self-service

