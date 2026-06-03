# UI Manual Test Checklist

Walk through this list end-to-end in a real browser (Chrome AND Safari,
ideally) before any production rollout. Items are grouped by feature
area so the operator can do a focused re-test after a relevant change
without redoing everything.

Backend must be running with `EMBEDDING_PROVIDER=local` (or a Voyage
paid tier) so multi-turn flows aren't throttled.

## Setup

- [ ] Frontend dev server running (`cd frontend && npm run dev`) and
      backend up (`uvicorn backend.main:app --port 8000`).
- [ ] Open the chat page on `http://localhost:5173/chat`.
- [ ] Hard refresh (Cmd+Shift+R) to clear cached state.

## Thread lifecycle

- [ ] Empty state: sidebar shows "No threads yet" and the example
      chips are visible and clickable.
- [ ] Click "New thread" / send first message — thread appears in
      sidebar with auto-generated title within ~2s.
- [ ] Thread title updates from "(untitled)" to a preview of the first
      user message.
- [ ] Click a thread in the sidebar — chat history loads in order;
      every turn renders user bubble + skill timeline + answer + cost
      footer.
- [ ] Hover a sidebar row — red X (delete) appears on the right.
- [ ] Click X — thread disappears from sidebar (soft-delete is OK,
      it should not reappear on refresh).
- [ ] Delete the currently active thread — the chat pane resets to
      empty state, not a 404 / broken view.

## Streaming + interrupt

- [ ] Send a multi-plate query ("Provjeri W-55123K i ZG-1234-AB.").
- [ ] Watch the skill timeline expand live; verify the "Querying N
      sources" counter increments as skills fire.
- [ ] Verify the Stop button (square icon) appears in place of Send
      while streaming.
- [ ] Click Stop mid-stream — the turn stops within ~5-15s, shows
      "Stopped by operator." italic line.
- [ ] Press ESC anywhere on the page (not in the textarea) while
      streaming — same behavior as the Stop button.
- [ ] Verify the textarea is disabled while streaming and re-enables
      after the turn finishes.

## Compaction + cost surface

- [ ] After a turn finishes, verify the muted cost footer reads
      "X,XXX in · XXX out · $0.0X" with reasonable numbers.
- [ ] Send a 5+ turn thread on the same plate. The cost footer per
      turn should grow as context accumulates.
- [ ] Trigger compaction artificially by setting
      `CHAT_THINKING_BUDGET=0 CHAT_TURN_COST_CAP_USD=0` and forcing
      a 100k-token history; verify the "Older messages summarised
      (tier N…)" badge appears above subsequent turns.
- [ ] If cost cap fires (low CHAT_TURN_COST_CAP_USD env), the turn
      shows the amber "Cost cap reached" panel, NOT the red error
      bar.

## Extended thinking

- [ ] Verify the "Thinking (X chars)" expandable line appears above
      the response while the agent is reasoning.
- [ ] Click to expand — reasoning shows in a muted, italic, monospace
      block.
- [ ] After streaming finishes, the block auto-collapses but stays
      clickable.

## Streaming UX details

- [ ] During the gap between a tool_result and the next text stream,
      the indicator reads "Thinking (step N)…", not silent.
- [ ] Token streaming is smooth (RAF-animated) — no chunked jumps.
- [ ] Scroll position follows new turns smoothly; scrolling up while
      streaming does NOT get snapped back down (preserve operator
      reading position).

## Refresh resilience

- [ ] Mid-stream, press Cmd+R / F5 to reload the page.
- [ ] After reload, the same thread is visible and the in-flight turn
      continues to stream (replay of buffered events + live tail).
- [ ] Final answer text is identical to what would have rendered
      without the refresh.

## Citation rendering

- [ ] Citations like `[playbook-id]` render as small numbered chips
      inline in the answer.
- [ ] Hover a citation — tooltip shows playbook title + description.
- [ ] Click — the playbook viewer panel opens (or whichever surface
      we wire up) — citation is not a dead link.
- [ ] Hallucinated citations are silently dropped (self-correction
      ran) — operator never sees a broken `[fake-id]`.

## Dark mode

- [ ] Toggle dark mode (whatever control your build exposes).
- [ ] Every element retains contrast — user bubble, skill timeline
      rows, compaction badge, cost footer, thinking quote-block,
      Stop button.
- [ ] No element disappears or becomes unreadable (white text on
      white background, etc.).

## Edge cases

- [ ] Send an empty string — submit button is disabled until text
      is typed. Sending an emoji-only follow-up after a real turn
      doesn't crash.
- [ ] Paste a very long message (~5000 chars) — textarea grows up to
      its max-height, then scrolls internally. Submit still works.
- [ ] Try a message with non-Latin characters (Croatian diacritics,
      German umlauts, emoji). Renders correctly in user bubble and
      reply.

## Error states

- [ ] Disconnect the backend (kill uvicorn) mid-stream — the UI shows
      a clear network-error message, not a silent freeze. Reconnect
      the backend and refresh — thread reloads.
- [ ] Hit a 429 (rate limit) by sending 25 turns fast — UI shows
      "Rate limit: retry in Xs", does not blank-screen.
- [ ] Cost cap reached — amber panel renders, NOT the red error bar.

## Settings / preferences (if exposed)

- [ ] If there's a settings page, every toggle persists across
      refresh.
- [ ] Top-k slider changes affect the retrieval count on the next
      turn (verify by counting "sources" in the timeline).

## Performance

- [ ] Open 5 threads in quick succession via the sidebar — switching
      is instant (<200ms perceived) on a warm cache.
- [ ] No visible jank during streaming on a high-frequency message
      (e.g. one calling Graylog which returns hundreds of lines).

---

When all boxes are ticked, the UI is production-ready. Re-run the
relevant section after any frontend change before merging.
