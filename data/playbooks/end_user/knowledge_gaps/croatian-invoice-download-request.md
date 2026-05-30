---
id: croatian-invoice-download-request
name: croatian_invoice_download_request
title: End users requesting invoice/receipt download or R1 fiscal invoice for parking payments
description: 'Bmove app end users (primarily in Croatia) contact support because they cannot find, download, or receive invoices
  for their parking purchases, or they need R1 fiscal invoices issued to their company. The tickets span three sub-patterns:
  users who don''t know where to find invoices in the app, users who experience a technical failure when trying to download,
  and users who want invoices issued to a business entity rather than a private person.'
category: end_user/knowledge_gaps
ticket_class: end_user
issue_category: knowledge_gap
resolution_pattern: user_education
languages:
- hr
country_focus:
- hr
- other
status: active
cluster_id: BS:end_user|croatia|no_label:c0
project_key: BS
cluster_size: 54
cluster_size_dedup: 54
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.93
extraction_model: claude-sonnet-4-6
frequency_per_month: 1.06
median_resolution_minutes: 1190.5
p95_resolution_minutes: 40475.4
cannot_reproduce_rate: 0.0
data_window_start: '2023-05-04'
data_window_end: '2026-04-26'
annual_hours_saved: 1.9
roi:
  baseline_active_hours: 6.3
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 2.8
  deflection_hours_range:
  - 2.0
  - 3.7
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 1.9
  agent_assist_hours_range:
  - 1.3
  - 2.5
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 1.9
  product_fix_hours_range:
  - 1.3
  - 2.5
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: low
  autonomous_resolve_hours_midpoint: 0.9
  autonomous_resolve_hours_range:
  - 0.7
  - 1.2
  autonomous_resolve_max_safe_volume_pct: 0.25
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-48156
- BS-52618
- BS-10098
- BS-7904
- BS-13679
- BS-15979
- BS-19505
- BS-26158
- BS-41186
- BS-26490
- BS-40982
- BS-51196
- BS-22711
- BS-28766
- BS-34174
- BS-32666
- BS-18932
- BS-26740
canonical_examples:
- BS-15979
- BS-13679
- BS-52618
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
  note: User education — safe for self-service deflection
  autonomous_resolve_max_safe_volume_pct: 0.25
  autonomous_resolve_narrow_use_case: Auto-respond to users asking where to find invoices in-app by sending the standard 'Povijest
    kupovina' navigation guide and a link to the help article, without any account data access.
  autonomous_resolve_safety_constraints:
  - Must not autonomously issue or modify R1 fiscal invoices — these carry legal/tax implications requiring human verification
  - Must not access or expose payment or billing records without authenticated agent oversight
  - Must escalate any ticket indicating a technical error or download failure rather than a simple navigation question
  - Bot must clearly identify itself as automated and provide a human escalation path
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
- croatian-end-user-wrong-registration-storno-refund
- croatian-parking-debt-payment-failure
- croatian-ticketless-open-session-at-exit__275624
- croatian-ticketless-open-session-at-exit__56d2b2
- croatian-ticketless-open-session-at-exit__ab83b0
- croatian-ticketless-open-session-at-exit__dc548a
- croatian-ticketless-open-session-at-exit__e3afed
- expired-card-deletion-ticketless-link
- hr-b2b-r1-invoice-request
- igeus-portal-access-credential-management
- italian-ticketless-setup-and-payment-issues
- open-session-at-exit-payment-failure
- phonzie-to-bmove-credit-refund-request
- prepaid-top-up-and-usage-issues
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

# End users requesting invoice/receipt download or R1 fiscal invoice for parking payments

## What this pattern is

Bmove app end users (primarily in Croatia) contact support because they cannot find, download, or receive invoices for their parking purchases, or they need R1 fiscal invoices issued to their company. The tickets span three sub-patterns: users who don't know where to find invoices in the app, users who experience a technical failure when trying to download, and users who want invoices issued to a business entity rather than a private person.

## When this applies

- User cannot locate invoice/receipt after a parking purchase
- User needs to justify travel expenses and requires a formal receipt
- User wants invoice issued to their company (R1 fiscal invoice) instead of personal details
- User cannot download invoice from app (button unresponsive or file access permission denied)
- User wants monthly consolidated invoice or report
- User wants electronic invoices sent by email automatically

## Typical resolution flow

1. User submits feedback via Bmove app under category 'Preuzimanje računa' (Invoice Download)
2. Support identifies whether the issue is: (a) not knowing where invoices are, (b) technical download failure, or (c) need for business/R1 invoice
3. For location questions: Support directs user to 'Povijest kupovina' (Purchase History) in the main menu of the Bmove app or app.bmove.com
4. For R1/business invoice: Support directs user to register as a business user at app.bmove.com/registracija/pravna-osoba/ or update company details in their existing profile
5. For download technical issues: Support advises granting file access permissions in phone settings, or re-running onboarding wizard via Help menu
6. For prepaid/monthly billing: Support explains that monthly consolidated R1 invoices are sent on the 10th of each month for business prepaid users
7. If invoice still unavailable, support manually resends invoices to user's email

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Instruct user to find invoices in 'Povijest kupovina' section of Bmove app or web portal | support_agent | Jira Service Management / email | 5 min |
| Provide instructions to register as business user or add company OIB/VAT data for R1 invoices | support_agent | email with link to https://app.Bmove.com/registracija/pravna-osoba/ and PDF… | 5 min |
| Advise user to grant file storage permissions to Bmove app or re-run onboarding wizard | support_agent | email | 5 min |
| Manually resend invoices to user's registered email address | support_agent | Bmove back-office system | 10 min |
| Explain prepaid billing model and monthly consolidated invoice schedule | support_agent | email with link to PDF guide | 5 min |

## Evidence

Derived from 54 tickets in cluster `BS:end_user|croatia|no_label:c0`. Direct quotes from 8 representative tickets:

- `BS-15979` _[hr]_: "kada platim parking, kako mogu preuzeti račun? potrebno mi je zbog pravdanja putnih troškova"
- `BS-13679` _[hr]_: "kako je moguce postaviti izdavanje r1 racuna kako bih mogao placati parking karticom od firme?"
- `BS-52618` _[hr]_: "račun bi mi trebao da ima naziv i OIB ustanove u kojoj radim"
- `BS-10098` _[hr]_: "nemogu preuzeti račun"
- `BS-22711` _[hr]_: "ako gumb 'Preuzmi' ne reagira, tada morate u postavkama Vašeg telefona odobriti pristup datotekama za Bmove aplikaciju"
- `BS-48156` _[hr]_: "imate li mogućnost slanja elektroničkih računa?"
- `BS-34174` _[hr]_: "molim vas da mi posaljete dva racuna od parkinga od 27.02. iz makarske.i dalje ih ne mogu preuzeti niti mi dolaze na mail"
- `BS-51196` _[hr]_: "Molim vas da mi šaljete mjesečne izvještaje sa navedenim iznosima koji su vezani uz vaše račune. Ova usluga mi treba radi knjigovodstva."

## Cluster statistics

- **Volume:** 54 tickets total (54 unique semantic events after dedup)
- **Frequency:** 1.06 tickets/month (over data window 2023-05-04 → 2026-04-26)
- **Median resolution:** 19.8 hours
- **Languages:** hr
- **Country focus:** hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~6.3 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~1.9 (range [1.323, 2.457])
- **Time reduction per ticket:** ~30% (range [21%, 39%])
- **Feasibility:** 0.88
- **Rationale:** Tickets in this cluster are highly templated — agents repeatedly send the same navigation instructions, R1 setup steps, or permission fix guidance — making them excellent candidates for suggested-reply macros or a one-click resend tool, reducing active time per ticket by roughly 30%.
- **Validation:** Run shadow-mode macro suggestions for two weeks across this ticket category, measuring agent accept rate and actual handle-time delta versus the 30-minute baseline before enabling live suggestions.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `low`
  - Sprints estimate: ~1.5 (range [1.1, 1.9])
- **Hours eliminated per year:** ~1.9 (range [1.33, 2.47])
- **Root cause:** A sub-segment of tickets involves technical failure when downloading invoices (e.g. missing file-storage permissions, broken download flow), representing a genuine product defect alongside the knowledge-gap issues. Fixing the download reliability and surfacing inline invoice discoverability in the app UI would eliminate both the bug-driven and navigation-confusion sub-patterns.
- **Rationale:** Fixing the download-failure bug and adding a prominent invoice section with guided onboarding wizard check for permissions would eliminate the technical sub-pattern and reduce navigation-confusion tickets; estimated impact covers roughly 30% of the cluster. This cannot exceed the 6.3 h baseline.
- **Validation:** Engineering team to instrument download-attempt success/failure rates in app analytics pre- and post-fix; sprint estimate should be validated against backlog grooming with the mobile platform team.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~2.8 (range [2.02, 3.66])
- **Form:** `in_app_help`
- **Deflection rate:** ~45% (range [32%, 58%])
- **Feasibility:** 0.82
- **Rationale:** The majority of tickets stem from users simply not knowing where to find invoices or how to set up business billing — classic knowledge-gap issues that a contextual in-app help article or FAQ can resolve without agent involvement. However, technical download failures and manual email resend cases require some agent action and reduce the ceiling.
- **Validation:** Deploy a targeted in-app help article linked from the 'Povijest kupovina' screen and a business-user registration guide; measure ticket volume reduction over a 4-week window, comparing deflected sessions against pre-launch baseline rate.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 25% of tickets
- **Hours saved per year:** ~0.9 (range [0.665, 1.235])
- **Narrow use case:** Auto-respond to users asking where to find invoices in-app by sending the standard 'Povijest kupovina' navigation guide and a link to the help article, without any account data access.
- **Safety constraints:**
  - Must not autonomously issue or modify R1 fiscal invoices — these carry legal/tax implications requiring human verification
  - Must not access or expose payment or billing records without authenticated agent oversight
  - Must escalate any ticket indicating a technical error or download failure rather than a simple navigation question
  - Bot must clearly identify itself as automated and provide a human escalation path
- **Rationale:** Only the pure navigation-question sub-type (estimated ~25% of volume) is safe for autonomous resolution; R1 invoice issuance and technical failures involve legal or system-state complexity that requires a human agent. Volume and savings are deliberately conservative.
- **Validation:** Pilot autonomous reply for navigation-only intents (classified by keyword/intent model) over 4 weeks with human review of 100% of bot responses; acceptance criterion is ≥90% appropriate resolution and zero mis-handled fiscal invoice requests.

### Risks

- **Compliance concerns:**
  - R1 fiscal invoices are legal tax documents under Croatian VAT law (Zakon o PDV-u); incorrect issuance or modification constitutes a compliance violation
  - Any automated handling of OIB (personal identification numbers) or VAT IDs must comply with GDPR data minimisation and purpose-limitation principles
  - Invoice records may be subject to Croatian mandatory retention periods (minimum 11 years); automation must not alter or delete them
- **Must not automate:**
  - Issuance, amendment, or cancellation of R1 fiscal invoices to business entities
  - Any action that modifies a user's billing profile or VAT registration data
  - Manual email resend of invoices where user identity or email address has not been verified by a human agent

## Agent compatibility

- **Status:** `active` (extraction confidence 0.93)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `True`
- **RAG-consumable:** `True`
- **Note:** User education — safe for self-service deflection

