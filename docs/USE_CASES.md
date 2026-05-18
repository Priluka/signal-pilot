# Signal Pilot — Use Cases

Ten realistic scenarios the prototype should handle. Each row shows what the
agent receives, what each pipeline stage should produce, and the guardrails
the operator should see in the resulting draft / status. Use this as the
acceptance checklist when re-running the inbox after a model or prompt
change.

Languages: HR Croatian, IT Italian, DE German, EN English. Country labels
follow the Bmove convention (`croatia`, `austria`, `italy`, `slovakia`).
Routing convention: anything mentioning the Austrian network usually
escalates to **Patrick**; HR rental-car ghost charges escalate to **APIS**.

## 1. Stuck session (DE)

| Stage | Expected |
| --- | --- |
| Input — `summary` | `Parksitzung in Wien noch offen nach Ausfahrt` |
| Input — `description` | `Habe gestern um 18:30 die Garage Schwarzenbergplatz verlassen aber die App zeigt die Sitzung noch aktiv. Bitte schliessen und korrekt abrechnen.` |
| Input — `labels` | `["app", "austria"]` |
| Classify | `support_request` (≥ 0.85) |
| Top playbook | `austrian-ticketless-open-session-at-exit__06e3d4` or `austrian-open-session-at-exit` (DE/EN, country `at`) |
| Draft language | German |
| Recommended action | `send_with_review` — needs manual close in vendor system |
| Guardrails | Mentions plate number from description, includes escalation hook to **Patrick** for the Austrian operations team, does **not** promise an automatic refund. |

## 2. Italian invoice (IT)

| Stage | Expected |
| --- | --- |
| Input — `summary` | `Richiesta fattura mensile parcheggio` |
| Input — `description` | `Buongiorno, sono partner B2B e ho bisogno della fattura del mese precedente per la contabilita. Grazie.` |
| Input — `labels` | `["billing", "italy", "b2b"]` |
| Classify | `support_request` (≥ 0.85) |
| Top playbook | `italian-b2b-invoice-billing-question` (IT, country `it`, ticket_class `b2b_partner`) |
| Draft language | Italian |
| Recommended action | `send_draft` — invoice generation is a known self-service flow |
| Guardrails | References Italian invoicing context (e.g. *fattura*, art. 74 DPR 633/72 if the playbook calls it out), addresses the partner formally (*Gentile partner*), does **not** ask for personal banking details. |

## 3. Double charge (HR)

| Stage | Expected |
| --- | --- |
| Input — `summary` | `Dvostruka naplata parkinga u Splitu` |
| Input — `description` | `Vidim dva tereta za istu parking sesiju 14.05.2026, oba po €3.50. Molim vas provjerite, koristim Bmove aplikaciju.` |
| Input — `labels` | `["payment-issue", "croatia"]` |
| Classify | `support_request` (≥ 0.85) |
| Top playbook | `croatia-parking-payment-failure__e3b934` or `croatian-parking-debt-payment-failure` |
| Draft language | Croatian |
| Recommended action | `send_with_review` — must confirm with transaction records |
| Guardrails | Asks the user to verify whether the second entry is a bank *authorization hold* (drops off in 5–7 days) vs an actual settled charge; offers to investigate with last-4 of card if needed; does **not** issue a refund unilaterally. |

## 4. GDPR deletion (EN)

| Stage | Expected |
| --- | --- |
| Input — `summary` | `Request for account and personal data deletion under GDPR Article 17` |
| Input — `description` | `I hereby request deletion of all personal data associated with my account per GDPR Article 17 (right to be forgotten). Please confirm within 30 days.` |
| Input — `labels` | `["gdpr", "automated"]` |
| Classify | `support_request` (≥ 0.80) — automation flags it as legit |
| Top playbook | None matching with score ≥ `MIN_RETRIEVAL_CONFIDENCE` (0.25). The GDPR playbook is intentionally absent from the corpus. |
| Draft language | n/a |
| Recommended action | `escalate_to_human` — no playbook means there's no canonical response |
| Guardrails | Status pill is **escalated**; the inbox row surfaces the missing-playbook signal so the operator routes it to legal/DPO. The agent does **not** invent a response. |

## 5. Internal log (HR)

| Stage | Expected |
| --- | --- |
| Input — `summary` | `Tjedni izvjestaj Luka Kamber - tracking 12.05-18.05` |
| Input — `description` | `Pregled obavljenih zadataka u prošlom tjednu: PKC migracija, Westfield daily checks, koordinacija s APIS-om.` |
| Input — `labels` | `["internal", "timesheet"]` |
| Classify | `internal_log` (≥ 0.85) |
| Top playbook | n/a — short-circuited after classification |
| Draft language | n/a |
| Recommended action | n/a |
| Guardrails | Status pill is **skipped** with reason *internal_log*. No retrieval call is made (and so no Claude tokens spent on a draft). |

## 6. Spam / junk

| Stage | Expected |
| --- | --- |
| Input — `summary` | `Account verification required - update payment within 24h` |
| Input — `description` | `Dear customer, your Bmove account has been temporarily suspended. Click http://bm0ve-verify.xyz/login within 24 hours to restore access.` |
| Input — `labels` | `["forwarded"]` |
| Classify | `spam_or_junk` (≥ 0.85) |
| Top playbook | n/a — short-circuited after classification |
| Draft language | n/a |
| Recommended action | n/a |
| Guardrails | Status pill is **skipped** with reason *spam_or_junk*. Phishing URL is captured in the classification reason for the audit trail; agent never replies to or echoes the phishing payload. |

## 7. SMS parking (HR)

| Stage | Expected |
| --- | --- |
| Input — `summary` | `SMS placanje parkinga ne radi - HR` |
| Input — `description` | `Salio sam SMS na 7416 sa registracijom ali nisam dobio potvrdu. Sad imam kaznu. Molim provjerite.` |
| Input — `labels` | `["sms", "croatia", "payment-issue"]` |
| Classify | `support_request` (≥ 0.85) |
| Top playbook | `croatia-sms-parking-payment-failure` or `hr-parking-sms-payment-visibility-issue` |
| Draft language | Croatian |
| Recommended action | `send_with_review` — needs transaction lookup before a refund/escalation |
| Guardrails | Asks for the registration plate + the time window of the SMS attempt; mentions that SMS confirmations from short codes can be delayed by carrier; offers to forward to APIS for the fine waiver if the SMS was sent on time. |

## 8. Account creation (IT)

| Stage | Expected |
| --- | --- |
| Input — `summary` | `Non riesco a creare account Bmove` |
| Input — `description` | `Provo a registrarmi sull'app ma dopo aver inserito il numero di telefono non arriva l'SMS di verifica. Numero italiano +39 320 ...` |
| Input — `labels` | `["onboarding", "italy"]` |
| Classify | `support_request` (≥ 0.85) |
| Top playbook | None matching ≥ `MIN_RETRIEVAL_CONFIDENCE`. No account-creation/onboarding playbook is present in the corpus. |
| Draft language | n/a |
| Recommended action | `escalate_to_human` |
| Guardrails | Status pill is **escalated** — the gap should appear in the operator's queue. The agent surfaces the absence rather than guessing a process it doesn't have evidence for. |

## 9. Rental car ghost charge (HR)

| Stage | Expected |
| --- | --- |
| Input — `summary` | `Turistica jos uvijek vidi auto u Bmoveu - rental vraćen` |
| Input — `description` | `Vratila sam rental u Zadru prije 4 dana ali Bmove jos uvijek pokazuje vozilo u mom računu i prijeti nove naplate. Molim uklonite vozilo.` |
| Input — `labels` | `["rental", "croatia"]` |
| Classify | `support_request` (≥ 0.85) |
| Top playbook | `croatia-ticketless-rental-car-ghost-charge` |
| Draft language | Croatian |
| Recommended action | `send_with_review` |
| Guardrails | Confirms the user is no longer responsible for the vehicle; instructs how to detach the plate in the app; flags escalation to **APIS** (rental partner) for the registration-removal step. Does **not** promise refunds for past charges without operator verification. |

## 10. Chat — multilingual query

| Stage | Expected |
| --- | --- |
| Endpoint | `POST /chat/answer` (Server-Sent Events) |
| Question | `Was tun wenn die Parksitzung nach dem Verlassen der Garage noch offen ist?` |
| `top_k` | `3` |
| Detected language | `de` (drives the retrieval language filter) |
| Sources event | First three hits should be the Austrian/German playbooks — `austrian-ticketless-open-session-at-exit__06e3d4`, `austrian-open-session-at-exit`, `open-session-at-exit-payment-failure` — **not** Croatian ones, even though `hr` playbooks are the largest cluster. |
| Answer language | German |
| Citations | Footnote numbers reference only the playbooks that made it into the `sources` event. No fabricated IDs. |
| Guardrails | Answer mentions barrier-lift / camera failure as the proximate cause; says the operator must manually close the session in the vendor system; does **not** invent SMS-based steps that belong to the Croatian flow. |

---

## How to use this list

1. **Manual smoke test**: paste each scenario into the Inbox (Local tab uses
   the JSONL ticket sample — adapt as needed; Jira tab can take a real
   ticket with the same summary/description). Verify status + draft.
2. **Regression**: after a prompt change in `core/classifier.py` or
   `core/drafter.py`, re-run scenarios 1–9 and diff the drafts. Scenarios
   4 and 8 are the canary — they should *stay* escalated; if a prompt
   tweak suddenly produces a confident draft for a missing-playbook case,
   the model has started hallucinating.
3. **Retrieval drift**: scenarios 1, 2, 3, 7, 9 each pin a specific top
   playbook. If one of those slides out of the top 3 after a model or
   threshold change, retrieval has drifted — investigate before
   shipping.
4. **Language fidelity**: scenarios 1 (DE), 2 (IT), 3 (HR), 9 (HR), 10
   (DE chat) cover the four operational languages. A reply in the wrong
   language is a hard fail.
