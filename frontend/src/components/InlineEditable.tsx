/** A piece of playbook text that the operator can edit inline.
 *
 * Read state: shows ``displayText`` with a pencil icon that fades in on
 * row hover.
 * Edit state: textarea (blue border) pre-filled with ``displayText`` and
 * Submit / Cancel buttons. The parent supplies an async ``onSubmit`` that
 * receives the edited string; this component never speaks to the API
 * directly so the parent can shape the old_text/new_text payload (adding
 * step-number or bullet prefixes if needed).
 */
import { useEffect, useRef, useState } from 'react';


function PencilIcon() {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 20h9" />
      <path d="M16.5 3.5a2.121 2.121 0 1 1 3 3L7 19l-4 1 1-4Z" />
    </svg>
  );
}


interface Props {
  /** Text shown read-only and pre-loaded into the textarea on edit. */
  displayText: string;
  /** Async submitter — receives the new text. Throws on error. */
  onSubmit: (newText: string) => Promise<void>;
  /** Sized for short cells ("inline") vs full step paragraphs ("block"). */
  variant?: 'inline' | 'block';
  /** Optional aria-label suffix (e.g. "step 3"). */
  ariaLabel?: string;
}


export function InlineEditable({
  displayText,
  onSubmit,
  variant = 'block',
  ariaLabel,
}: Props) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(displayText);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  // Reset draft when the source text changes (e.g. playbook reloaded after accept).
  useEffect(() => {
    if (!editing) setDraft(displayText);
  }, [displayText, editing]);

  useEffect(() => {
    if (editing && textareaRef.current) {
      textareaRef.current.focus();
      textareaRef.current.setSelectionRange(textareaRef.current.value.length, textareaRef.current.value.length);
    }
  }, [editing]);

  function startEdit() {
    setDraft(displayText);
    setError(null);
    setEditing(true);
  }

  function cancel() {
    setEditing(false);
    setDraft(displayText);
    setError(null);
  }

  async function submit() {
    const trimmed = draft.trim();
    if (!trimmed || trimmed === displayText.trim()) {
      cancel();
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await onSubmit(draft);
      setEditing(false);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  if (!editing) {
    if (variant === 'inline') {
      return (
        <span className="group/edit inline-flex items-baseline gap-1">
          <span>{displayText}</span>
          <button
            type="button"
            onClick={startEdit}
            aria-label={`Edit ${ariaLabel ?? ''}`.trim()}
            className="opacity-0 group-hover/edit:opacity-100 transition-opacity text-slate-400 hover:text-blue-600 shrink-0"
          >
            <PencilIcon />
          </button>
        </span>
      );
    }
    return (
      <div className="group/edit flex items-start gap-2">
        <div className="flex-1">{displayText}</div>
        <button
          type="button"
          onClick={startEdit}
          aria-label={`Edit ${ariaLabel ?? ''}`.trim()}
          className="opacity-0 group-hover/edit:opacity-100 transition-opacity text-slate-400 hover:text-blue-600 shrink-0 mt-1"
        >
          <PencilIcon />
        </button>
      </div>
    );
  }

  const rows = variant === 'inline' ? 2 : Math.max(2, Math.min(8, draft.split('\n').length + 1));
  return (
    <div className="w-full">
      <textarea
        ref={textareaRef}
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Escape') cancel();
          if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) submit();
        }}
        rows={rows}
        disabled={submitting}
        className="w-full px-2 py-1.5 text-sm bg-white border-2 border-blue-400 rounded focus:outline-none focus:ring-2 focus:ring-blue-500/15 resize-y font-sans leading-relaxed"
      />
      {error && <div className="mt-1 text-[11px] text-red-600">{error}</div>}
      <div className="mt-1.5 flex items-center justify-end gap-2">
        <button
          type="button"
          onClick={cancel}
          disabled={submitting}
          className="px-2.5 py-1 text-xs text-slate-600 rounded hover:bg-slate-100"
        >
          Cancel
        </button>
        <button
          type="button"
          onClick={submit}
          disabled={submitting || !draft.trim()}
          className="px-3 py-1 text-xs font-medium text-white bg-blue-600 rounded hover:bg-blue-700 disabled:bg-slate-200 disabled:text-slate-400"
        >
          {submitting ? 'Submitting…' : 'Submit suggestion'}
        </button>
      </div>
    </div>
  );
}
