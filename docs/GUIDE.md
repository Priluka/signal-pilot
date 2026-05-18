# Signal Pilot — Operator Guide

A working prototype of an AI triage agent for support tickets. Reads tickets,
matches them to a 122-playbook knowledge base, drafts replies, and routes the
ambiguous ones to a human inbox.

This doc covers what's actually in the app today — every endpoint listed has
been tested against the running backend, every view exists in the UI.

---

## Stack & run

- **Backend**: FastAPI + uvicorn (Python 3.12), SQLite (WAL mode), Anthropic
  SDK (Haiku 4.5 classifier, Sonnet 4.6 drafter + chat), sentence-transformers
  `BAAI/bge-m3` for local embeddings.
- **Frontend**: Vite + React 19 + TypeScript + Tailwind v3, react-router-dom
  v7, react-force-graph-2d for the knowledge graph.

Start in two terminals:

```bash
# Backend (port 8000)
.venv/bin/uvicorn backend.main:app --reload --port 8000

# Frontend (port 5173)
cd frontend && npm run dev
```

Open `http://localhost:5173`.

---

## Views

The sidebar groups views into three sections: **Knowledge**, **Agent**, and
**Suggestions**. Anything labeled *Coming soon* is a sidebar placeholder; the
sections below describe only the functional views.

### Knowledge Library — `/knowledge`

What it shows: every playbook, three panels wide.

- **Left** — filter bar (ticket class, issue category, country, source
  project) + searchable list. Filters live in the URL (`?ticket_class=...`)
  so a deep link reproduces the filtered view.
- **Center** — the open playbook: title, description, when-applies,
  resolution flow, typical actions table, risks, evidence quotes, related
  playbooks. Steps in the resolution flow have a pencil icon — click to
  propose an inline edit (it goes into the Suggestions queue).
- **Right** — metadata sidebar: cluster size, extraction confidence,
  frequency, median resolution minutes, ROI breakdown if the playbook
  declares one in its YAML `roi` block.

API behind it:

- `GET /playbooks` — list (cached, served from in-memory copy)
- `GET /playbooks/{id}` — full detail
- `GET /categories` — drives the filter dropdowns
- `POST /suggestions` — used by the pencil-icon inline editor

### Knowledge Graph — `/graph`

A force-directed graph of every playbook. Nodes sized by `cluster_size`,
edges from each playbook's `related_playbooks` list. Click a node to open
its playbook in a new tab.

API: `GET /playbooks/graph` returns `{ nodes, edges }`.

### Chat — `/chat`

Retrieval-augmented Q&A over the playbook corpus.

- Left rail: chat history. Sessions persist to SQLite; deleting one removes
  it from the rail.
- Center: ask a question, watch the answer stream in. Citations appear as
  superscript footnotes inline; hover one to preview the playbook title;
  click it to jump to that playbook.
- Streaming is checkpointed every ~250 chars to SQLite, and the generator
  runs in a daemon thread, so refreshing mid-stream resumes from where you
  left off (not from scratch).

API:

- `POST /chat/answer` — Server-Sent Events. Emits `sources`, `delta` (many),
  `done`, or `error`.
- `GET /chat/sessions/{id}/stream` — re-attach to an in-flight session
  (used on refresh).
- `GET /chat/sessions` / `GET /chat/sessions/{id}` / `DELETE /chat/sessions/{id}`
  for the history rail.

### Inbox — `/inbox`

The operator's decision queue. Tabs switch between two ticket sources:

#### Local tickets tab

Reads from `data/tickets/sample.jsonl` (50 mocked Bmove tickets). Only
tickets whose derived agent status is `needs_review` or `escalated` appear
here — everything else (`auto_resolved`, `skipped`, `approved`, `rejected`)
moves to the Activity Log.

The agent doesn't run on a timer. Click **Process pending tickets** in the
header strip to start a background batch — uvicorn keeps responding while
the daemon thread chews through the rest. Progress shows live.

Per ticket, the right pane shows:

- Timeline (classified → retrieved → drafted)
- Classification label + reason + confidence
- Matched playbook (linked)
- Draft reply (editable, with diff view)
- Decision row: **Reject / Edit / Approve & send**

Approve logs feedback locally. There's no real send for sample tickets.

#### Jira tickets tab

Live from your Jira project (set `JIRA_PROJECT` in `.env`). All tickets show,
regardless of agent state. Pick one and click **Process with agent** to run
classify → retrieve → draft on demand. Approve writes the draft as a Jira
comment AND logs feedback locally; if Jira rejects the comment, feedback is
not logged so you can retry without double-counting.

Tab choice persists across reloads via `localStorage.inboxSource`.

API:

- Local: `GET /tickets`, `GET /tickets/{key}`, `GET /agent/sessions`,
  `POST /agent/batch-process`, `GET /agent/batch-status`,
  `GET /agent/metrics`
- Jira: `GET /jira/tickets`, `GET /jira/tickets/{key}`,
  `POST /jira/process/{key}`, `POST /jira/comment`
- Both: `GET /agent/sessions/{id}`, `POST /feedback`

### Activity Log — `/activity-log`

Every agent step + every operator decision, newest first. Same left/right
shell as the Inbox, but the list is unfiltered — you see classified, drafted,
approved, rejected, skipped, auto-resolved. Use it as the audit trail.

Filter pills at the top narrow by event type. Clicking a row opens that
ticket's full session detail on the right.

API: `GET /agent/activity?limit=500`.

### Suggestions — `/suggestions`

Operator-submitted playbook edits. Each row shows the targeted playbook, the
section + step the edit applies to, the old text struck through, the new
text in green. Pending rows have Accept / Reject.

Accept rewrites the playbook markdown on disk **and** creates a git commit
against the signal-pilot repo. Reject is a status change only.

API: `GET /suggestions`, `PUT /suggestions/{id}/accept`,
`PUT /suggestions/{id}/reject`. New suggestions are created from inside
the Knowledge Library via `POST /suggestions`.

---

## User flows

### 1. Browse a playbook and propose an edit

1. Sidebar → **Knowledge**.
2. (Optional) Use the filter bar to narrow by ticket class / country / etc.
3. Click a playbook from the list.
4. In the resolution flow section, click the **pencil** next to any step.
5. Edit the text inline, click **Save suggestion**.
6. The change goes to the Suggestions queue (status: *pending*); the
   playbook on disk is unchanged until someone accepts it.

### 2. Ask the chat a question

1. Sidebar → **Chat**.
2. Type a question (e.g. *"How do we handle ticketless parking sessions that
   stay open after exit?"*) and hit Ask.
3. The **Sources** event arrives first — top playbooks the retriever picked.
4. The answer streams in. Citations render as small superscript numbers
   inline; hover one for the playbook title, click to open.
5. Past sessions live in the left rail — click any to re-open.
6. If you refresh during a stream, the session re-attaches and finishes
   without losing the answer.

### 3. Process a local ticket end-to-end

1. Sidebar → **Inbox**. Confirm the **Local tickets** tab is active.
2. If the agent hasn't processed anything yet, click **Process pending
   tickets** in the header. Wait — progress shows X / 50.
3. Once the batch finishes, the inbox lists tickets where the agent wants a
   human (status `needs_review` or `escalated`).
4. Click a ticket. The right pane shows timeline + classification + matched
   playbook + draft.
5. **Reject** if the draft is wrong; **Edit** to tweak it (diff view shows
   your changes); **Approve & send** to log the (edited or original) draft
   as the final reply.
6. The ticket leaves the inbox immediately. It now appears in the Activity
   Log under its final status.

### 4. Process a Jira ticket and post the comment back

1. Sidebar → **Inbox**. Switch to the **Jira tickets** tab.
2. The list shows every issue in your configured Jira project, newest first.
3. Pick a ticket. The right pane shows the description and the empty-state
   panel: *"This Jira ticket hasn't been processed by the agent yet."*
4. Click **Process with agent**. The pipeline runs synchronously — usually
   2–4 s for a single ticket (classifier + retriever + drafter call).
5. When it returns, you see the same timeline + classification + draft as
   for local tickets.
6. **Approve & send** posts the draft as a Jira comment on the issue, then
   logs feedback. Open the issue in Jira to confirm.
7. If Jira returns an error (auth, permissions, malformed body), the error
   surfaces on the decision row and **no** feedback is logged — you can fix
   the issue and retry without double-counting.

### 5. Browse the Activity Log

1. Sidebar → **Activity Log**.
2. The center column is one row per event, newest first.
3. Use the filter pills above the list (`all / classified / retrieved /
   drafted / approved / edited / rejected / skipped`) to narrow.
4. Click any row to open that ticket's full session on the right —
   classification reason, retrieval hits with scores, the draft, the
   decision (if any).

### 6. Review a suggestion

1. Sidebar → **Suggestions**.
2. Filter pills at the top: *all / pending / accepted / rejected*. New
   suggestions land in *pending*.
3. Each card shows the playbook title (clickable), the section + step
   number, the diff (red minus / green plus), author, timestamp.
4. **Reject** if the edit is wrong — status flips to *rejected*, the
   playbook on disk is untouched.
5. **Accept** rewrites the markdown on disk and commits the change. The
   commit lands on the current branch of the signal-pilot repo, authored as
   the operator (set `SUGGESTION_AUTHOR` env if you want a custom string).

---

## API reference

Base URL: `http://localhost:8000`. All payloads are JSON unless noted.

### Playbooks

| Method | Path | Description |
| --- | --- | --- |
| GET | `/playbooks` | List all playbooks. Optional query: `ticket_class`, `issue_category`, `country`, `language`, `q`. |
| GET | `/playbooks/graph` | Nodes + edges for the knowledge graph. |
| GET | `/playbooks/{id}` | Full detail (resolution flow, evidence, ROI block, related). |

Example response (truncated):

```json
{
  "id": "open-session-at-exit-payment-failure",
  "title": "Parking session remains open after exit due to barrier lift...",
  "ticket_class": "end_user",
  "issue_category": "bug_in_product",
  "languages": ["hr", "en"],
  "country_focus": ["hr", "at", "other"],
  "cluster_size": 14,
  "extraction_confidence": 0.97,
  "resolution_steps": ["...", "..."],
  "evidence_quotes": [{"ticket_id": "BS-1234", "language": "hr", "quote": "..."}],
  "roi": {
    "baseline_active_hours": 120,
    "agent_assist": {"hours_midpoint": 60, "confidence_tier": "high"}
  }
}
```

### Categories

| Method | Path | Description |
| --- | --- | --- |
| GET | `/categories` | Counts for ticket classes + issue categories, plus the `by_ticket_class` mapping. |

### Tickets (local sample)

| Method | Path | Description |
| --- | --- | --- |
| GET | `/tickets` | All 50 local sample tickets. |
| GET | `/tickets/{key}` | One ticket — adds description, assignee, project_key, issue_type. |

### Agent

| Method | Path | Description |
| --- | --- | --- |
| POST | `/agent/classify?ticket_id=` | One-shot classify; persists into the session if `ticket_id` is set. |
| POST | `/agent/retrieve?ticket_id=` | Top-K playbook retrieval. |
| POST | `/agent/draft?ticket_id=` | Generate a reply against `playbook_id`. |
| POST | `/agent/batch-process` | Start the background daemon over all local tickets. Idempotent — won't restart if already running. |
| GET | `/agent/batch-status` | `{ running, processed, total, current_ticket, errors }`. |
| GET | `/agent/sessions` | All per-ticket session summaries (light shape). |
| GET | `/agent/sessions/{ticket_id}` | Full session: classification, retrieval, draft, decision. `null` if none. |
| DELETE | `/agent/sessions/{ticket_id}` | Drop the session so the ticket re-processes from scratch. |
| GET | `/agent/metrics` | Counts by derived status + approval rate + avg confidence. |
| GET | `/agent/activity?limit=500` | Flat event stream for the Activity Log. |

Example: `POST /agent/classify?ticket_id=BS-1234`

```json
// request
{ "summary": "Session still open after exit", "description": "...", "labels": ["app"] }

// response
{
  "label": "support_request",
  "confidence": 0.95,
  "reason": "User reports unresolved parking session and asks for manual closure."
}
```

### Jira

| Method | Path | Description |
| --- | --- | --- |
| GET | `/jira/tickets?limit=100` | Issues from the configured project, newest first. |
| GET | `/jira/tickets/{key}` | One issue with ADF-flattened description. |
| POST | `/jira/process/{key}` | Fetch the issue + run classify → retrieve → draft. Returns the resulting session keyed by the Jira key. |
| POST | `/jira/comment` | Body: `{ "issue_key": "KAN-4", "body": "Hello, ..." }`. Wraps the text in ADF and posts. |

`/jira/process/{key}` returns the same shape as `/agent/sessions/{id}`.

### Feedback

| Method | Path | Description |
| --- | --- | --- |
| POST | `/feedback` | Log an operator decision. Body: `{ ticket_id, playbook_id, draft_text, final_text?, status }` where status ∈ `approved \| edited \| rejected`. |
| GET | `/feedback` | All feedback rows. |
| GET | `/feedback/stats` | Aggregate counts. |

### Suggestions

| Method | Path | Description |
| --- | --- | --- |
| POST | `/suggestions` | Create a pending suggestion. Body: `{ playbook_id, section, step_number?, old_text, new_text, author? }`. |
| GET | `/suggestions?playbook_id=` | List, optionally filtered. |
| PUT | `/suggestions/{id}/accept` | Rewrite the markdown + git commit. |
| PUT | `/suggestions/{id}/reject` | Status change only. |
| GET | `/suggestions/stats` | Counts by status. |

### Chat

| Method | Path | Description |
| --- | --- | --- |
| POST | `/chat/answer` | SSE stream. Body: `{ question, top_k }`. Events: `sources`, `delta`, `done`, `error`. |
| GET | `/chat/sessions/{id}/stream` | Re-attach to a streaming session — used on browser refresh. |
| GET | `/chat/sessions` | History rail. |
| GET | `/chat/sessions/{id}` | One full session. |
| DELETE | `/chat/sessions/{id}` | Drop from history. |

SSE wire format (one event per blank-line-delimited block):

```
event: sources
data: {"hits": [...], "session_id": 42}

event: delta
data: {"text": "Hello, thank you "}

event: done
data: {"answer": "...", "cited_ids": ["pb-1"], "session_id": 42}
```

### Meta

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health` | `{ status, playbooks_loaded, tickets_loaded, index_built }`. |

---

## Configuration

All env vars are read from `.env` at the repo root (gitignored). Defaults in
`config.py`.

### Required

| Var | Used by | Notes |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | classifier, drafter, chat answerer | No fallback — these features fail loudly without it. |

### Jira (only if you use the Jira tab)

| Var | Notes |
| --- | --- |
| `JIRA_URL` | e.g. `https://teamoraapp.atlassian.net` (no trailing slash). |
| `JIRA_EMAIL` | The Atlassian account email — must match the token owner. |
| `JIRA_TOKEN` | Create at https://id.atlassian.com/manage-profile/security/api-tokens |
| `JIRA_PROJECT` | Project key (e.g. `KAN`). Search scope is hard-coded to this project. |

If any of the four are missing, `/jira/*` endpoints return `503` with a
config error message and the Jira tab surfaces it in the inbox panel.

### Embeddings

| Var | Default | Notes |
| --- | --- | --- |
| `EMBEDDING_PROVIDER` | `local` | `local` (sentence-transformers) or `voyage` (Voyage AI API). |
| `EMBEDDING_MODEL_LOCAL` | `BAAI/bge-m3` | Any sentence-transformers-compatible model. First run downloads ~2 GB to the HuggingFace cache. |
| `EMBEDDING_MODEL_VOYAGE` | `voyage-3` | Requires `VOYAGE_API_KEY`. |
| `EMBEDDING_DEVICE` | `cpu` | Set to `mps` on Apple Silicon for a 3-4× speedup, or `cuda` if you have a GPU. |

Embeddings are cached to `data/cache/playbook_embeddings.npz` — first build
takes 30–60 s on CPU, then near-instant. To swap models, delete the `.npz`
and restart; the next request rebuilds.

### Models

| Var | Default | Notes |
| --- | --- | --- |
| `CLASSIFIER_MODEL` | `claude-haiku-4-5-20251001` | Cheap + fast; latency-sensitive. |
| `DRAFTER_MODEL` | `claude-sonnet-4-6` | Used for both drafts and chat answers. |
| `TOP_K_RETRIEVAL` | `3` | How many playbooks the retriever returns. |
| `MIN_RETRIEVAL_CONFIDENCE` | `0.25` | Below this, the drafter escalates instead of replying. |

### Wiring Jira from scratch

1. Generate a token at https://id.atlassian.com/manage-profile/security/api-tokens.
2. Add to `.env`:

   ```
   JIRA_URL=https://your-workspace.atlassian.net
   JIRA_EMAIL=you@example.com
   JIRA_TOKEN=ATATT3...
   JIRA_PROJECT=KAN
   ```

3. Restart the backend (`.env` is loaded at boot).
4. Sanity check: `curl -s http://localhost:8000/jira/tickets | jq 'length'`
   should return a number.
5. Open the Inbox in the UI and switch to the **Jira tickets** tab.

### Changing the embedding model

For an English-only corpus, `BAAI/bge-base-en-v1.5` is smaller (~440 MB) and
roughly as good for English. For multilingual, the default `bge-m3` is the
right pick.

```
EMBEDDING_MODEL_LOCAL=BAAI/bge-base-en-v1.5
```

Then delete `data/cache/playbook_embeddings.npz` and restart. Note that the
cached vectors are tied to the model — mixing dimensions corrupts retrieval.

---

## Known limits

What works:

- 122 playbooks load + index from `data/playbooks/`.
- Classifier → retriever → drafter pipeline on the 50-ticket local sample.
- Per-ticket workflow state persists across restarts (SQLite).
- Chat with citations, streaming, daemon-thread persistence, refresh resume.
- Inline edit suggestions with diff view, on-disk rewrite, git commit on
  accept.
- Knowledge graph rendering with react-force-graph-2d.
- Jira: list, fetch, process, post comment — tested against
  `teamoraapp.atlassian.net`.

What's a placeholder / coming later:

- **`/agents/deployed` / `/agents/shadow` / `/agents/performance`** — sidebar
  links exist, but the pages render the *Coming soon* shell. No data behind
  them yet.
- **Mode graduation** — every playbook reports as `shadow` mode at the API
  level. There's no DB column for mode yet; promotion to `assisted` /
  `autonomous` is not wired.
- **Approve & send for local tickets** — logs feedback only; there's no
  actual outbound mail / Zendesk / Intercom adapter. Jira tickets do post a
  real comment.
- **Auto-batching on Jira** — there's no equivalent of
  `/agent/batch-process` for Jira. You process one ticket at a time via the
  UI button.
- **Pagination in `/jira/tickets`** — capped at 100 results, no paging UI.
  Increase via `?limit=N` if needed.

What's intentionally out of scope:

- Multi-user auth — there's one operator. The repo has no login flow.
- Webhooks — the Jira integration is poll-only. No live notification when
  a new ticket arrives.
- Outbound sending channels other than Jira comments.

What's known to break:

- If you delete `feedback.sqlite3` while uvicorn is running, all in-flight
  chat sessions error on the next checkpoint. Stop the backend first.
- Concurrent first-time embedding builds used to race; we now eager-build at
  startup and lock the cached path, so this should be fixed. If you see
  *index not ready* errors, check the backend logs and restart.
- The agent batch runs in a daemon thread that dies with the process. If
  uvicorn is killed mid-batch, the partial sessions stay in the DB and the
  inbox shows them as `in_progress` — re-run the batch to finish.
