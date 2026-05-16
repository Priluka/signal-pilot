/** Right-rail metadata sidebar for the Knowledge tab.
 *
 * Surfaces the playbook's quantitative payload: extraction confidence,
 * cluster + sample sizes, frequency/resolution time, the four ROI strategies
 * (as horizontal bars sized by hours_midpoint), every related playbook with
 * a short description, and the full evidence-tickets list.
 *
 * Every value comes from the YAML frontmatter — nothing is invented.
 */
import { Link } from 'react-router-dom';

import type {
  PlaybookDetail,
  ROIBreakdown,
  ROIStrategy,
  RelatedPlaybookOut,
} from '../lib/types';

import { ConfidenceBar, TicketChip } from './ui';


export function PlaybookSidebar({ playbook }: { playbook: PlaybookDetail }) {
  return (
    <aside className="w-[300px] shrink-0 border-l border-panel-border bg-panel-surface overflow-y-auto scrollbar-thin">
      <div className="p-4 space-y-6">
        <MetadataBlock playbook={playbook} />
        {playbook.roi && <ROIBlock roi={playbook.roi} />}
        {playbook.related_playbooks_resolved.length > 0 && (
          <RelatedBlock related={playbook.related_playbooks_resolved} />
        )}
        {playbook.evidence_tickets.length > 0 && (
          <EvidenceBlock
            tickets={playbook.evidence_tickets}
            languages={playbook.languages}
            sampleSize={playbook.sample_size_used}
            clusterSize={playbook.cluster_size}
          />
        )}
      </div>
    </aside>
  );
}


// ---------------------------------------------------------------------------
// Section: heading + cards
// ---------------------------------------------------------------------------

function SidebarHeading({ children }: { children: React.ReactNode }) {
  return (
    <h3 className="text-[10px] font-semibold tracking-wider uppercase text-slate-500 mb-2">
      {children}
    </h3>
  );
}


function StatRow({
  label,
  children,
  hint,
}: {
  label: string;
  children: React.ReactNode;
  hint?: string;
}) {
  return (
    <div className="flex items-baseline justify-between gap-3 py-1.5">
      <div className="text-[11px] text-slate-500 leading-tight">
        {label}
        {hint && <span className="block text-[10px] text-slate-400">{hint}</span>}
      </div>
      <div className="text-sm font-medium text-slate-900 font-mono tabular-nums text-right shrink-0">
        {children}
      </div>
    </div>
  );
}


// ---------------------------------------------------------------------------
// Metadata
// ---------------------------------------------------------------------------

function MetadataBlock({ playbook }: { playbook: PlaybookDetail }) {
  return (
    <section>
      <SidebarHeading>Metadata</SidebarHeading>
      <div className="bg-white border border-panel-border rounded-lg p-3">
        <div className="pb-2 mb-2 border-b border-panel-divider">
          <div className="text-[11px] text-slate-500 mb-1">Extraction confidence</div>
          <ConfidenceBar score={playbook.extraction_confidence} />
        </div>
        <div className="divide-y divide-panel-divider">
          <StatRow label="Cluster size" hint="tickets in this pattern">
            {playbook.cluster_size ?? '—'}
          </StatRow>
          <StatRow label="Sample used" hint="quoted in evidence">
            {playbook.sample_size_used ?? '—'}
          </StatRow>
          <StatRow label="Frequency" hint="tickets / month">
            {playbook.frequency_per_month != null
              ? playbook.frequency_per_month.toFixed(2)
              : '—'}
          </StatRow>
          <StatRow label="Median resolution" hint="hours">
            {playbook.median_resolution_minutes != null
              ? (playbook.median_resolution_minutes / 60).toFixed(1)
              : '—'}
          </StatRow>
        </div>
      </div>
    </section>
  );
}


// ---------------------------------------------------------------------------
// ROI bar chart
// ---------------------------------------------------------------------------

interface ROIRowDef {
  key: keyof ROIBreakdown;
  label: string;
  color: string;
  hint: string;
}

const ROI_ROWS: ROIRowDef[] = [
  { key: 'agent_assist', label: 'Agent assist', color: 'bg-blue-500', hint: 'human + AI co-write' },
  { key: 'product_fix', label: 'Product fix', color: 'bg-amber-500', hint: 'engineering removes the cause' },
  { key: 'deflection', label: 'Self-service deflection', color: 'bg-emerald-500', hint: 'help-center article' },
  { key: 'autonomous_resolve', label: 'Autonomous resolve', color: 'bg-indigo-500', hint: 'agent replies alone' },
];


function ROIBlock({ roi }: { roi: ROIBreakdown }) {
  const max = Math.max(
    1,
    ...ROI_ROWS.map((r) => {
      const strat = roi[r.key] as ROIStrategy | null;
      return strat?.hours_midpoint ?? 0;
    }),
  );
  return (
    <section>
      <SidebarHeading>ROI · hours saved / year</SidebarHeading>
      <div className="bg-white border border-panel-border rounded-lg p-3">
        {roi.baseline_active_hours != null && (
          <div className="pb-2 mb-2 border-b border-panel-divider">
            <StatRow label="Baseline" hint={roi.baseline_confidence_tier ?? undefined}>
              {roi.baseline_active_hours.toFixed(1)} h
            </StatRow>
          </div>
        )}
        <ul className="space-y-3">
          {ROI_ROWS.map((r) => {
            const strat = roi[r.key] as ROIStrategy | null;
            const mid = strat?.hours_midpoint;
            return (
              <li key={r.key}>
                <div className="flex items-baseline justify-between gap-2 mb-1">
                  <div className="text-[11px] text-slate-700 leading-tight">
                    {r.label}
                    <span className="block text-[10px] text-slate-400">{r.hint}</span>
                  </div>
                  <div className="text-xs font-mono tabular-nums text-slate-900 shrink-0">
                    {mid != null ? `${mid.toFixed(1)} h` : '—'}
                  </div>
                </div>
                <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${r.color}`}
                    style={{
                      width: mid != null ? `${(mid / max) * 100}%` : '0%',
                    }}
                  />
                </div>
                {strat?.hours_range_low != null && strat?.hours_range_high != null && (
                  <div className="mt-0.5 text-[10px] text-slate-400 font-mono">
                    range {strat.hours_range_low.toFixed(1)}–{strat.hours_range_high.toFixed(1)} h
                    {strat.confidence_tier && (
                      <span className="ml-1 italic">· {strat.confidence_tier}</span>
                    )}
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      </div>
    </section>
  );
}


// ---------------------------------------------------------------------------
// Related playbooks (resolved with title + description)
// ---------------------------------------------------------------------------

function RelatedBlock({ related }: { related: RelatedPlaybookOut[] }) {
  return (
    <section>
      <SidebarHeading>Related playbooks · {related.length}</SidebarHeading>
      <ul className="space-y-2">
        {related.map((r) => (
          <li key={r.id}>
            <Link
              to={`/knowledge/${r.id}`}
              className="block bg-white border border-panel-border rounded-lg p-3 hover:border-blue-300 transition-colors"
            >
              <div className="text-xs font-medium text-slate-900 leading-snug">
                {r.title}
              </div>
              <div className="mt-0.5 text-[10px] font-mono text-slate-500 truncate">
                {r.id}
              </div>
              <p className="mt-1.5 text-[11px] text-slate-600 leading-relaxed line-clamp-2">
                {r.description}
              </p>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}


// ---------------------------------------------------------------------------
// Evidence tickets
// ---------------------------------------------------------------------------

function EvidenceBlock({
  tickets,
  languages,
  sampleSize,
  clusterSize,
}: {
  tickets: string[];
  languages: string[];
  sampleSize: number | null;
  clusterSize: number | null;
}) {
  // Group ticket IDs by project prefix (BS-1234 → BS) for a compact summary.
  const byProject = new Map<string, string[]>();
  for (const t of tickets) {
    const [prefix] = t.split('-', 1);
    const arr = byProject.get(prefix) ?? [];
    arr.push(t);
    byProject.set(prefix, arr);
  }
  return (
    <section>
      <SidebarHeading>Evidence · {tickets.length} tickets</SidebarHeading>
      <div className="bg-white border border-panel-border rounded-lg p-3">
        <div className="text-[11px] text-slate-500 mb-2">
          {sampleSize != null && clusterSize != null
            ? `${sampleSize} of ${clusterSize} tickets sampled`
            : `${tickets.length} sampled tickets`}
        </div>
        <div className="flex flex-wrap gap-1.5 mb-3">
          {languages.filter((l) => l !== 'other').map((l) => (
            <span
              key={l}
              className="inline-flex items-center px-1.5 py-0 text-[10px] rounded bg-slate-100 text-slate-700 border border-slate-200"
            >
              {l}
            </span>
          ))}
        </div>
        {Array.from(byProject.entries()).map(([proj, ids]) => (
          <div key={proj} className="mb-2 last:mb-0">
            <div className="text-[10px] font-mono text-slate-400 mb-1">
              {proj} · {ids.length}
            </div>
            <div className="flex flex-wrap gap-1">
              {ids.map((t) => (
                <TicketChip key={t} id={t} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
