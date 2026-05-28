# Known Production Gaps

_v1.0 · 2026-05-28 · post-audit_

The Skills layer is **demo-ready and pilot-grade**: 10 hardening passes
landed (retry/backoff, claim-pattern, audit log, multi-tool snapshot,
bearer auth, planner error surfacing, per-ticket locks, polling, frontend
tests, system-prompt tightening). The list below is what's intentionally
**not** in this release and why.

---

## 1. Multi-tenancy

**Gap.** `pending_actions`, `agent_sessions`, `agent_actions_history`,
`suggestions`, `chat_sessions` all key on `(ticket_id)` or `(id)` with no
`workspace_id` column. The skills `REGISTRY` is a module-level global.

**Why deferred.** Bmove is the single tenant. Adding scoping requires:

- Schema migration on every table (workspace_id NOT NULL + index)
- Scoped registry per workspace (skills per tenant)
- Auth flow that resolves the request → workspace
- Per-tenant Jira/Anthropic credentials (currently env-global)

That's 2–3 days of work and a forward-only migration. We do it when a
second customer signs.

**Mitigation today.** Deploy is single-tenant — one signal-pilot
instance per customer. Operationally clean, just doesn't scale to SaaS.

---

## 2. Audit log retention / export

**Built.** `agent_actions_history` is append-only and never gets
deleted by application code (per `core/agent_audit.py`).

**Missing for SOC 2 / GDPR.**

- No retention policy (rows live forever — fine for compliance, bad for disk)
- No periodic export to immutable storage (S3 with object-lock)
- No "right to be forgotten" workflow (GDPR Article 17)

**Why deferred.** Both are policy decisions — when the customer's
compliance team specifies retention windows and storage targets, we
implement. Putting placeholders in now would just be guessing.

---

## 3. Authentication

**Built.** `OPERATOR_TOKEN` bearer auth on `/actions/*`.
`secrets.compare_digest` for timing safety. Frontend reads
`VITE_OPERATOR_TOKEN` and sends `Authorization: Bearer ...`.

**Missing for enterprise.**

- No OAuth/OIDC integration with the customer's IdP (Okta/Azure AD)
- Token rotation = env-var + process restart
- No per-operator audit (decided_by is the bearer token literal, not a user id)
- Other endpoints (`/agent/*`, `/jira/*`, `/chat/*`) still open

**Why deferred.** Production rollout will swap this dependency for
whatever SSO the customer already uses. The shape of the dependency
won't change — only what `require_operator` does internally.

---

## 4. Rate limiting

**Gap.** No per-IP / per-operator rate limit. A bad actor with the
token can burn Anthropic credits.

**Why deferred.** Internal tool with allow-listed operators behind
VPN — no public surface to rate-limit. Production exposure (if any)
goes behind a gateway that handles this layer.

---

## 5. Streaming planner output

**Gap.** Planner runs synchronously inside `process_ticket`. Operator
sees nothing until the loop returns or pauses.

**Workaround.** Frontend polls `/actions/pending/{ticket_id}` every 3s
so pending actions appear within that window. Not real-time but feels
live.

**Why deferred.** True streaming needs SSE or WebSocket — works behind
most proxies but adds infrastructure. 3s polling is enough for the
typical 5–15s planner cycle.

---

## 6. Long-running planner timeouts

**Gap.** A wedged Anthropic call can sit in `_loop` until the request
hits Anthropic's own 10-min timeout. The operator sees nothing.

**Why deferred.** PLANNER_MAX_ITERATIONS=10 caps the worst case
implicitly. Hard per-call timeout would need async/threading
refactor — possible but not blocking demo.

---

## 7. Skill input validation beyond JSON Schema

**Built.** Anthropic SDK validates against `input_schema` before the
tool_use reaches our planner.

**Gap.** Skills like `jira_add_public_comment` trust `body` is "safe
text". A model proposing a 100KB body or injecting Jira markup is
technically valid but problematic. No content sanitization layer.

**Why deferred.** Schema's `maxLength` caps most abuse vectors.
Content policy (forbidden phrases, PII detection) belongs in a
separate skill or middleware, not in the planner itself.

---

## 8. Frontend test coverage breadth

**Built.** ActionApproval covered by 5 Vitest scenarios.

**Gap.** Other components (DraftSection, AgentInbox, SuggestionsPage,
ChatPage) have zero coverage. The `npm test` suite would catch
ActionApproval regressions only.

**Why deferred.** ActionApproval is the only component handling
write actions to external systems — the highest-risk surface.
Other components are read/display heavy.

---

## 9. Graceful degradation when Anthropic is down

**Built.** 3-attempt exponential retry on 429/5xx.

**Gap.** After 3 failed attempts the planner returns
`PlannerResult(status='failed')` and `agent_sessions.planner_status`
goes to "failed". UI surfaces a red banner.

**Missing.** No automatic re-try-later queue. Operator must manually
re-process. For a true outage, we'd want sessions in "deferred" state
that the runner picks up when Anthropic recovers.

---

## What IS rock-solid

- Concurrency safety (per-ticket locks, atomic claim pattern, WAL SQLite)
- Audit trail (append-only, never deleted, every outcome captured)
- Authentication primitive (bearer token, timing-safe compare)
- Error surfacing (no silent planner failures)
- Resume semantics (multi-tool turns preserved, paired tool_results
  always sent)
- Test coverage on the critical path (6 backend E2E scenarios + 5
  frontend tests covering the panel)
- Retry on transient API failures
- Single source of truth UI (no duplicate approval surfaces)

This release is **safe for an internal demo with executives in the
room and for a controlled pilot with one customer.** It is NOT safe
to put behind a public URL without the items above being addressed.
