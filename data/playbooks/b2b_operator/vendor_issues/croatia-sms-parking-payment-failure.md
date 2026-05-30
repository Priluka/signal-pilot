---
id: croatia-sms-parking-payment-failure
name: croatia_sms_parking_payment_failure
title: Croatian B2B Partner SMS Parking Payment Service Outages
description: 'B2B partners (parking operators, airports, venues) in Croatia report recurring failures of SMS-based parking
  payment services. Outages are typically caused by connectivity issues: lost connections to the Hostcom (HC) gateway, mobile
  operator network problems (HT, Telemach), ISP infrastructure failures (e.g. Cogent backbone), or brief system interruptions
  on the Bmove platform side. Partners report that multiple end-users are unable to complete SMS parking payments during these
  periods.'
category: b2b_operator/vendor_issues
ticket_class: b2b_partner
issue_category: vendor_failure
resolution_pattern: vendor_escalation
languages:
- hr
country_focus:
- hr
status: active
cluster_id: BS:b2b_partner|croatia|no_label:c1
project_key: BS
cluster_size: 38
cluster_size_dedup: 38
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.93
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.74
median_resolution_minutes: 1068.5
p95_resolution_minutes: 9943.549999999988
cannot_reproduce_rate: 0.0
data_window_start: '2023-04-07'
data_window_end: '2026-04-27'
annual_hours_saved: 2.2
roi:
  baseline_active_hours: 8.9
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.1
  deflection_hours_range:
  - 0.1
  - 0.1
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 2.2
  agent_assist_hours_range:
  - 1.6
  - 2.8
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 2.7
  product_fix_hours_range:
  - 1.9
  - 3.5
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.6
  autonomous_resolve_hours_range:
  - 0.4
  - 0.8
  autonomous_resolve_max_safe_volume_pct: 0.1
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-32622
- BS-51942
- BS-7312
- BS-8083
- BS-13295
- BS-14377
- BS-17248
- BS-23847
- BS-50957
- BS-43592
- BS-50496
- BS-50904
- BS-50981
- BS-49012
- BS-50847
- BS-35713
- BS-23261
- BS-52550
canonical_examples:
- BS-7312
- BS-51942
- BS-17248
vendor_dependency:
  vendor_name: Hostcom / Mobile operators (HT, Telemach) / Cogent ISP
  involves_vendor: true
  typical_wait_days: 0
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: Vendor coordination — needs human verification
  autonomous_resolve_max_safe_volume_pct: 0.1
  autonomous_resolve_narrow_use_case: Automated service restart and status notification to partner when Hostcom gateway reconnection
    is confirmed without human verification needed
  autonomous_resolve_safety_constraints:
  - Autonomous restart must only trigger after confirmed gateway disconnection signal, not on ambiguous errors, to avoid false
    restarts during live transactions
  - Partner must receive automated notification before and after any automated restart action
  - Human engineer must review and approve any action that cannot be automatically verified as resolved within 5 minutes
  - Autonomous path must not proceed when root cause is identified as mobile operator or ISP-side (not Bmove-side), as no
    remediation is possible
  - Full audit log of every automated action required for B2B partner SLA accountability
related_playbooks:
- app-payment-failure-parking-ticket
- croatia-b2b-parking-card-refund-request
- croatian-b2b-parking-ticket-storno-refund
- croatian-b2b-parking-ticket-storno-request
- hr-b2b-parking-card-cancellation-refund
- hr-b2b-parking-card-storno-refund
- hr-b2b-parking-ticket-storno-refund
- hr-b2b-r1-invoice-request
- igeus-portal-access-credential-management
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

# Croatian B2B Partner SMS Parking Payment Service Outages

## What this pattern is

B2B partners (parking operators, airports, venues) in Croatia report recurring failures of SMS-based parking payment services. Outages are typically caused by connectivity issues: lost connections to the Hostcom (HC) gateway, mobile operator network problems (HT, Telemach), ISP infrastructure failures (e.g. Cogent backbone), or brief system interruptions on the Bmove platform side. Partners report that multiple end-users are unable to complete SMS parking payments during these periods.

## When this applies

- End-users report inability to pay parking via SMS
- B2B partner notices SMS payment requests not reaching the service
- Mobile operator network disruption (HT, Telemach, etc.)
- Loss of Hostcom (HC) gateway connection
- ISP backbone outage (e.g. Cogent AS174)
- Power outage or infrastructure maintenance at partner site affecting connectivity
- System restart or upgrade activity (e.g. parking system upgrade by ECCOS)

## Typical resolution flow

1. oov je samo testB2B partner (parking operator or intermediary) submits ticket reporting SMS payment not working
2. Bmove support checks system logs and connectivity to Hostcom or operator network
3. Support identifies root cause: lost HC connection, operator-side issue, or system downtime
4. Support restarts relevant service or process, or waits for upstream vendor to restore
5. Support confirms with partner whether service is restored
6. Partner confirms end-user payments are going through again
7. Ticket closed; recurring issues sometimes escalated for enhanced monitoring

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Check system logs and connectivity to Hostcom gateway | Bmove support engineer | Internal monitoring/log system | 15 min |
| Restart the SMS payment service or process | Bmove support engineer | Server/service management tools | 10 min |
| Verify with partner that SMS payments are working again | Bmove support engineer | email/ticket system | 5 min |
| Check mobile operator or ISP status for network-side disruptions | Bmove support engineer | Network monitoring tools | 10 min |
| Escalate to enhanced system monitoring or technical contact at partner | Bmove support engineer | email | 20 min |

## Vendor dependency

- **Vendor:** Hostcom / Mobile operators (HT, Telemach) / Cogent ISP
- **Typical wait:** 0 day(s)

## Evidence

Derived from 38 tickets in cluster `BS:b2b_partner|croatia|no_label:c1`. Direct quotes from 7 representative tickets:

- `BS-7312` _[hr]_: "Iz logova izgleda da je bio problem u komunikaciji s hostcom-om."
- `BS-51942` _[hr]_: "Dana 08.04.2026. i 10.04.2026. god. zabilježen je prekid mrežne povezanosti uzrokovan ispadom na infrastrukturi globalnog ISP-a Cogent (AS174)"
- `BS-17248` _[hr]_: "Pretpostavljam da ste izgubili HC konekciju pa molim da provjerite i povratno javite."
- `BS-35713` _[hr]_: "u navedenom vremenu bilo je problema na strani Telemach mreže."
- `BS-50847` _[hr]_: "u periodu od 08:57-09:04 je bio prekid u radu sustava / poteškoće stoga navedeni pokušaji plaćanja nisu bili uspješni."
- `BS-32622` _[hr]_: "Pojačanim nadzorom sustava primjećujemo poteškoće u mrežnoj konekciji koji uzrokuju probleme i za aplikativni dio."
- `BS-14377` _[hr]_: "čini se da je garažni server nedostupan. Pokušavamo se spojiti na 10.81.0.1:10202, ali ne dobivamo odgovor od servera."

## Cluster statistics

- **Volume:** 38 tickets total (38 unique semantic events after dedup)
- **Frequency:** 0.74 tickets/month (over data window 2023-04-07 → 2026-04-27)
- **Median resolution:** 17.8 hours
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~8.9 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~2.2 (range [1.6, 2.8])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.75
- **Rationale:** A runbook assistant could surface the standard diagnostic checklist (log locations, HC gateway status URL, operator status pages, service restart command) immediately on ticket open, reducing time spent on steps 1, 4, and 5 by roughly 15 minutes per ticket. Partner-verification and escalation steps still require human judgment and cannot be fully assisted.
- **Validation:** Run shadow-mode agent-assist for 4 weeks on incoming SMS-outage tickets; measure actual time-to-resolution compared to the 60-minute baseline and rate agent acceptance of suggested runbook steps.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~2.7 (range [1.89, 3.51])
- **Root cause:** Root cause is external: connectivity failures to the Hostcom HC gateway, mobile operator (HT, Telemach) network disruptions, or Cogent ISP backbone outages. The Bmove platform itself is not the origin of the fault, though lack of automated reconnection, circuit-breaker logic, or proactive monitoring could be addressed to reduce mean time to detection.
- **Rationale:** Adding automated gateway health checks, alerting, and auto-restart logic (circuit breaker) could eliminate the manual log-check and restart steps (approx. 25 of 60 active minutes per ticket), but cannot eliminate tickets that require partner verification or vendor escalation steps. Estimated ~40% of active minutes are automatable via monitoring improvements.
- **Validation:** Engineering team to spike automated Hostcom connectivity monitor in one sprint; measure reduction in time-to-detect and whether support engineer manual log-check step is skipped in subsequent incidents.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.1 (range [0.049, 0.091])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.10
- **Rationale:** These are B2B partner-reported infrastructure outages caused by third-party vendor or network failures; end-users cannot self-serve their way past a genuine SMS gateway or ISP outage, making FAQ or help-center deflection nearly irrelevant. The only marginal deflection value would be a status page telling partners the outage is already known, reducing duplicate tickets.
- **Validation:** Deploy a real-time SMS service status page for 8 weeks and measure whether repeat tickets per incident drop; track ticket-open rate during declared outages vs. baseline.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 10% of tickets
- **Hours saved per year:** ~0.6 (range [0.42, 0.78])
- **Narrow use case:** Automated service restart and status notification to partner when Hostcom gateway reconnection is confirmed without human verification needed
- **Safety constraints:**
  - Autonomous restart must only trigger after confirmed gateway disconnection signal, not on ambiguous errors, to avoid false restarts during live transactions
  - Partner must receive automated notification before and after any automated restart action
  - Human engineer must review and approve any action that cannot be automatically verified as resolved within 5 minutes
  - Autonomous path must not proceed when root cause is identified as mobile operator or ISP-side (not Bmove-side), as no remediation is possible
  - Full audit log of every automated action required for B2B partner SLA accountability
- **Rationale:** The narrow window for autonomous action is limited to the service-restart step when a clear Bmove-side disconnection is detected and auto-verified; most incidents involve external vendor faults that cannot be autonomously remediated and still require human escalation. At a 10% safe volume cap the hours saved are modest given low annual frequency.
- **Validation:** Pilot automated restart on exactly 1 incident type (confirmed HC gateway drop with clean reconnect signal) for 12 weeks; acceptance criteria: zero false-positive restarts, partner confirmation rate ≥ 90%, no SLA breach attributable to automated action.

### Risks

- **Compliance concerns:**
  - B2B partner SLA agreements may require human acknowledgment and communication during outages; automated responses must not substitute for contractual notifications
  - SMS payment infrastructure in Croatia may be subject to financial-services or telecommunications regulatory requirements that restrict unattended automated interventions
- **Must not automate:**
  - Escalation decisions to mobile operators (HT, Telemach) or Cogent ISP — these require human judgment about severity and vendor relationship management
  - Partner-facing communication confirming resolution — must be human-verified before closing the incident with a B2B partner
  - Any action taken when root cause is ambiguous or multi-vendor, to avoid masking a deeper ongoing failure
- **Vendor dependencies blocking automation:**
  - Hostcom HC gateway does not currently expose a machine-readable health/status API; automated detection of gateway-side failures depends on Hostcom providing such an interface
  - Mobile operator (HT, Telemach) and Cogent ISP outage status is not programmatically accessible in real time, limiting automated root-cause attribution
  - All meaningful remediation for operator- or ISP-caused outages depends entirely on third-party resolution timelines outside Bmove control

## Agent compatibility

- **Status:** `active` (extraction confidence 0.93)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Vendor coordination — needs human verification

