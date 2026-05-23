/** /settings — workspace-wide preferences for the operator.
 *
 * Premium settings-page chrome (flat sections, max-w-4xl, hairline
 * dividers — same as AgentsPage). For now hosts only the chat
 * retrieval-depth control; more sections (notifications, theme
 * granularity, etc.) will follow.
 */
import { useChatStore } from '../lib/chatStore';


export function SettingsPage() {
  const chat = useChatStore();

  return (
    <div className="h-full overflow-y-auto scrollbar-thin">
      <div className="max-w-4xl mx-auto px-8 py-8">
        <header>
          <h1 className="text-xl font-semibold text-ink">Settings</h1>
          <p className="text-[13px] text-ink-body mt-1">
            Workspace preferences. Saved per browser, no restart required.
          </p>
        </header>

        <section className="pt-6 mt-6 border-t border-line-subtle">
          <div className="flex items-center justify-between mb-1 gap-3">
            <h2 className="text-[14px] font-semibold text-ink">
              Chat retrieval depth
            </h2>
            <span className="text-[14px] font-semibold font-mono text-ink tabular-nums">
              {chat.topK}
            </span>
          </div>
          <p className="text-[12px] text-ink-body mb-4">
            How many playbooks Claude sees as grounding context for each
            chat question. More depth = richer answers on broad questions
            but slightly more tokens per call. Defaults to 5; lower it if
            you want faster, narrower answers.
          </p>

          <RetrievalSlider value={chat.topK} onChange={chat.setTopK} />

          <div className="flex justify-between text-[11px] font-mono text-ink-muted mt-2">
            <span>1</span>
            <span>3</span>
            <span>5</span>
          </div>
        </section>
      </div>
    </div>
  );
}


function RetrievalSlider({
  value,
  onChange,
}: {
  value: number;
  onChange: (v: number) => void;
}) {
  // Map 1..5 onto 0..1 for the visual fill.
  const pct = ((value - 1) / 4) * 100;
  return (
    <div className="relative h-4 flex items-center select-none">
      <div className="absolute inset-x-0 top-1/2 -translate-y-1/2 h-1.5 rounded-full bg-hover" />
      <div
        className="absolute top-1/2 -translate-y-1/2 h-1.5 rounded-full bg-accent"
        style={{ width: `${pct}%` }}
      />
      <div
        className="absolute top-1/2 w-4 h-4 rounded-full bg-white border-2 border-accent shadow-sm pointer-events-none"
        style={{
          left: `${pct}%`,
          transform: 'translate(-50%, -50%)',
        }}
      />
      <input
        type="range"
        min={1}
        max={5}
        step={1}
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value, 10))}
        className="absolute inset-0 w-full h-full appearance-none bg-transparent cursor-grab active:cursor-grabbing opacity-0"
        aria-label="Chat retrieval depth"
      />
    </div>
  );
}
