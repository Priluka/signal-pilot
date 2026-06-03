# Operations Runbook

Pragmatic playbook for keeping signal-pilot healthy in production.
Every section answers: *what does this signal look like, what does
it mean, what do I do?*

## Health endpoints

| Endpoint         | Use                                              | 200 ⇒                    | 503 ⇒ |
|------------------|--------------------------------------------------|--------------------------|-------|
| `/health/live`   | Container liveness probe (k8s, ECS, systemd)     | Process is up            | Restart |
| `/health/ready`  | Load-balancer readiness, monitoring              | Every dep is healthy     | Pull from rotation, investigate `checks.*.error` |
| `/health`        | Legacy, only checks playbook/index counts        | Backwards-compat shim    | n/a   |

Hit `/health/ready` — the JSON body tells you exactly which dependency
failed:

```bash
curl -s http://signal-pilot/health/ready | jq
```

- `checks.db.ok == false` → SQLite file unreachable. Check disk +
  `data/feedback.db` permissions.
- `checks.disk.ok == false` → free space below `HEALTH_DISK_MIN_FREE_RATIO`
  (default 10%). Run a backup, then prune.
- `checks.anthropic.ok == false` → Anthropic API unreachable or auth
  failure. Verify `ANTHROPIC_API_KEY` not expired/depleted.
- `checks.playbook_index.ok == false` → embedding build failed. Check
  Voyage key, or switch `EMBEDDING_PROVIDER=local` / `chain`.

## Metrics

Scrape `/metrics` (Prometheus exposition format). Key signals:

| Metric                                | What it means                                | Alert threshold |
|---------------------------------------|----------------------------------------------|-----------------|
| `chat_turns_total{status="error"}`    | Failed turns                                 | rate > 5/min sustained |
| `chat_turns_total{status="capped"}`   | Cost-cap aborts                              | rate > 1/min — operator may be hitting expensive queries |
| `chat_turn_duration_seconds` p95      | End-to-end latency                           | p95 > 60s — investigate Anthropic latency or skill timeouts |
| `chat_turn_cost_usd` p95              | Per-turn spend                               | p95 > $0.30 — review prompt + skill payload sizes |
| `chat_skill_duration_seconds{ok="false"}` | Failing skill rate                       | rate > 0.5/min for any skill |
| `chat_rate_limit_hits_total`          | 429s served                                  | > 0 — investigate offending IP |
| `chat_anthropic_retries_total`        | SDK retries triggered                        | rate > 1/min — Anthropic-side degradation |
| `chat_compaction_hits_total{tier="3"}` | LLM summarisation fires                     | rare; sustained > 1/min ⇒ thread too long, review retention |

## Common incidents

### Anthropic credit exhausted
Symptom: every new turn ends with `error_message` starting with
`Error code: 400` + "credit balance".

1. Check Anthropic Console → Billing.
2. Top up balance OR rotate the `ANTHROPIC_API_KEY` to a fresh
   account.
3. Update `.env` and restart the backend (no zero-downtime reload yet).
4. Run `scripts/spend_watcher.py --hours 24` to see whether the
   exhaustion was abnormal usage vs a stuck loop.

### Voyage rate-limited
Symptom: backend logs `Voyage embed failed: 429`. The frontend gets
500s on every turn that needs retrieval.

1. Set `EMBEDDING_PROVIDER=chain` in `.env`. Backend now falls back
   to local on every Voyage 429.
2. Restart the backend.
3. Confirm the failure rate drops in `/metrics`.
4. Either upgrade Voyage tier or stay on `chain` permanently.

### Disk filling up
Symptom: `/health/ready` returns 503 with `disk.ok=false`.

1. Run a backup: `python scripts/backup_db.py --keep 7`.
2. Purge old threads: `curl -X POST http://signal-pilot/chat/admin/threads/purge`
3. Check `backups/` directory size; rotate to S3 / off-host storage.

### Database locked
Symptom: backend logs `sqlite3.OperationalError: database is locked`.

1. Should not happen — WAL + busy_timeout=10s is configured. If it
   does, the host is under extreme I/O contention.
2. Check `iostat`. Move DB to faster disk if needed.
3. If persistent: increase `busy_timeout` in `core/chat_threads._connect`.

### Stuck "streaming" turns
Symptom: UI shows a turn spinning forever after a crash/restart.

1. Restart the backend — startup migration marks orphan
   `status='streaming'` rows as `error`.
2. If the operator wants to retry: delete the offending thread
   (soft-delete) and start a new one.

### Cost cap repeatedly trips
Symptom: `chat_cost_cap_hits_total` climbs steadily.

1. Look at the offending threads via the spend watcher:
   `python scripts/spend_watcher.py --hours 6`.
2. If queries are legitimate: raise `CHAT_TURN_COST_CAP_USD` for
   that deployment.
3. If queries are looping: investigate prompt / playbook content —
   may be triggering the agent into a loop. Check
   `chat_skill_duration_seconds` for one skill firing repeatedly.

### Frontend can't connect
Symptom: operator UI shows network errors on every action.

1. Check CORS — `CORS_ALLOWED_ORIGINS` must include the frontend
   origin exactly (scheme + host + port).
2. Check the backend health endpoints from the frontend host.
3. Inspect browser console — a `CORS error` differs from a `502`.

## Daily operations checklist

- [ ] `scripts/spend_watcher.py --hours 24` → review top threads
- [ ] `/health/ready` returns 200
- [ ] `chat_turns_total{status="error"}` rate over 24h < 1%
- [ ] Latest backup written within last 24h (cron-friendly script
      writes to `backups/`)
- [ ] `df -h` on host shows >20% free

## Deployment notes

- **Zero-downtime reload**: not yet supported. Plan a brief window.
- **DB migrations**: run via `init_db` on backend startup. Versioned
  via `schema_versions` table. No manual ALTER needed when bumping
  `_MIGRATIONS` in `core/chat_threads.py`.
- **Key rotation**: edit `.env`, restart backend, verify
  `/health/ready` checks Anthropic OK.
- **Secrets**: `.env` only; mount via container secrets manager in
  production (AWS SSM, Vault, etc.).

## Escalation

If none of the above resolves a sustained issue:

1. Capture `tail -1000 uvicorn.log | grep -E "ERROR|WARNING"` and any
   relevant `chat_turns.error_message` rows.
2. Check `/metrics` snapshot.
3. Page the on-call engineer with the request_id of the failing
   request (visible in every log line as `[rid=XXX]` and in the
   `X-Request-ID` response header).
