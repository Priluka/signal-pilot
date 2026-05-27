/** Right-rail metadata sidebar for the Knowledge tab.
 *
 * Dense, scannable data panel — Bloomberg/Figma-inspector feel. Shares the
 * card surface with the viewer (no gray block), with hairline separators
 * between sections instead of nested cards. Surfaces the playbook's
 * quantitative payload: extraction confidence, cluster/sample sizes,
 * frequency, median resolution time, the four ROI strategies as horizontal
 * bars sized relative to baseline, related playbooks with descriptions,
 * and every evidence ticket grouped by source/project prefix.
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
import {
  frequencyLabel,
  reliabilityTier,
  resolutionLabel,
} from '../lib/labels';


export function PlaybookSidebar({ playbook }: { playbook: PlaybookDetail }) {
  return (
    <aside className="w-[280px] shrink-0 border-l border-line-subtle bg-card overflow-y-auto scrollbar-thin">
      <div className="py-5">
        <Section>
          <MetadataBlock playbook={playbook} />
        </Section>

        {playbook.roi && (
          <Section>
            <ROIBlock roi={playbook.roi} />
          </Section>
        )}

        {playbook.related_playbooks_resolved.length > 0 && (
          <Section>
            <RelatedBlock related={playbook.related_playbooks_resolved} />
          </Section>
        )}

        {playbook.evidence_tickets.length > 0 && (
          <Section last>
            <EvidenceBlock
              tickets={playbook.evidence_tickets}
              languages={playbook.languages}
              sampleSize={playbook.sample_size_used}
              clusterSize={playbook.cluster_size}
            />
          </Section>
        )}
      </div>
    </aside>
  );
}


// ---------------------------------------------------------------------------
// Section wrapper — uniform spacing + hairline divider
// ---------------------------------------------------------------------------

function Section({ children, last }: { children: React.ReactNode; last?: boolean }) {
  return (
    <section
      className={`px-5 ${last ? '' : 'pb-5 mb-5 border-b border-line-subtle'}`}
    >
      {children}
    </section>
  );
}


function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <h3 className="text-[11px] uppercase tracking-wider font-semibold text-ink-muted mb-4">
      {children}
    </h3>
  );
}


// ---------------------------------------------------------------------------
// 1. Metadata
// ---------------------------------------------------------------------------

function MetadataBlock({ playbook }: { playbook: PlaybookDetail }) {
  const reliability = reliabilityTier(playbook.extraction_confidence);
  const reliabilityColor =
    reliability == null
      ? 'bg-ink-muted'
      : reliability.tier === 'High'
      ? 'bg-emerald-500'
      : reliability.tier === 'Medium'
      ? 'bg-amber-500'
      : 'bg-red-400';

  return (
    <>
      <SectionLabel>Metadata</SectionLabel>

      {/* Reliability — tier label + percent + progress bar */}
      <div className="mb-4">
        <div className="flex items-baseline justify-between">
          <span className="text-[12px] text-ink-body">Reliability</span>
          <span className="text-[13px] font-semibold text-ink">
            {reliability != null
              ? `${reliability.tier} (${reliability.percent}%)`
              : '—'}
          </span>
        </div>
        <div className="h-1.5 rounded-full bg-hover overflow-hidden mt-1.5">
          <div
            className={`h-full rounded-full transition-all ${reliabilityColor}`}
            style={{ width: `${reliability?.percent ?? 0}%` }}
          />
        </div>
      </div>

      {/* Quantitative rows */}
      <div>
        <MetaRow
          label="Similar tickets"
          value={
            playbook.cluster_size != null
              ? `${playbook.cluster_size}`
              : '—'
          }
        />
        <MetaRow
          label="Frequency"
          value={frequencyLabel(playbook.frequency_per_month)}
        />
        <MetaRow
          label="Avg resolution"
          value={resolutionLabel(playbook.median_resolution_minutes)}
        />
      </div>
    </>
  );
}


function MetaRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between py-2 border-b border-line-subtle last:border-0">
      <div className="text-[12px] text-ink-body">{label}</div>
      <div className="text-[13px] font-semibold text-ink text-right shrink-0">
        {value}
      </div>
    </div>
  );
}


// ---------------------------------------------------------------------------
// 2. ROI · hours saved / year
// ---------------------------------------------------------------------------

interface ROIRowDef {
  key: keyof ROIBreakdown;
  label: string;
  color: string;
}

const ROI_ROWS: ROIRowDef[] = [
  { key: 'agent_assist', label: 'With AI assist', color: 'bg-blue-500' },
  { key: 'product_fix', label: 'After fix', color: 'bg-amber-500' },
  { key: 'deflection', label: 'Self-service', color: 'bg-emerald-500' },
  { key: 'autonomous_resolve', label: 'Fully automated', color: 'bg-indigo-500' },
];


function ROIBlock({ roi }: { roi: ROIBreakdown }) {
  const baseline = roi.baseline_active_hours;
  const scaleMax = Math.max(
    1,
    baseline ?? 0,
    ...ROI_ROWS.map((r) => (roi[r.key] as ROIStrategy | null)?.hours_midpoint ?? 0),
  );

  return (
    <>
      <SectionLabel>Hours saved per year</SectionLabel>

      {baseline != null && (
        <div className="py-3 border-b border-line-subtle">
          <div className="flex items-baseline justify-between">
            <span className="text-[12px] font-medium text-ink">Without AI</span>
            <span className="text-[14px] font-semibold font-mono text-ink tabular-nums">
              {Math.round(baseline)} h
            </span>
          </div>
        </div>
      )}

      {ROI_ROWS.map((r, i) => {
        const strat = roi[r.key] as ROIStrategy | null;
        const mid = strat?.hours_midpoint;
        const pct = mid != null ? Math.min(100, (mid / scaleMax) * 100) : 0;
        const isLast = i === ROI_ROWS.length - 1;
        return (
          <div
            key={r.key}
            className={`py-3 ${isLast ? '' : 'border-b border-line-subtle'}`}
          >
            <div className="flex items-baseline justify-between">
              <span className="text-[12px] font-medium text-ink">{r.label}</span>
              <span className="text-[14px] font-semibold font-mono text-ink tabular-nums">
                {mid != null ? `${Math.round(mid)} h` : '—'}
              </span>
            </div>
            <div className="h-1 rounded-full bg-hover overflow-hidden mt-2 w-full">
              <div
                className={`h-full rounded-full ${r.color}`}
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
        );
      })}
    </>
  );
}


// ---------------------------------------------------------------------------
// 3. Related playbooks
// ---------------------------------------------------------------------------

function RelatedBlock({ related }: { related: RelatedPlaybookOut[] }) {
  return (
    <>
      <h3 className="text-[11px] uppercase tracking-wider font-semibold text-ink-muted mb-3">
        Related playbooks <span className="text-ink-muted">· {related.length}</span>
      </h3>
      <ul className="space-y-2">
        {related.map((r) => (
          <li key={r.id}>
            <Link
              to={`/knowledge/${r.id}`}
              className="block border border-line rounded-lg p-3 hover:bg-hover transition-colors duration-150"
            >
              <div className="text-[12px] font-medium text-ink leading-snug">
                {r.title}
              </div>
              <div className="text-[10px] font-mono text-ink-muted mt-1 truncate">
                {r.id}
              </div>
              <p className="text-[11px] text-ink-body mt-1.5 line-clamp-2 leading-relaxed">
                {r.description}
              </p>
            </Link>
          </li>
        ))}
      </ul>
    </>
  );
}


// ---------------------------------------------------------------------------
// 4. Evidence · tickets
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
  // Group ticket IDs by project prefix (BS-1234 → BS) so the operator can
  // see at a glance which products the evidence spans.
  const byProject = new Map<string, string[]>();
  for (const t of tickets) {
    const [prefix] = t.split('-', 1);
    const arr = byProject.get(prefix) ?? [];
    arr.push(t);
    byProject.set(prefix, arr);
  }
  const visibleLanguages = languages.filter((l) => l !== 'other');

  return (
    <>
      <h3 className="text-[11px] uppercase tracking-wider font-semibold text-ink-muted mb-3">
        Evidence <span className="text-ink-muted">· tickets</span>
      </h3>

      <div className="text-[11px] text-ink-muted mb-2">
        {sampleSize != null && clusterSize != null
          ? `${sampleSize} of ${clusterSize} tickets sampled`
          : `${tickets.length} sampled tickets`}
      </div>

      {visibleLanguages.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {visibleLanguages.map((l) => (
            <span
              key={l}
              className="text-[10px] font-mono bg-app border border-line rounded px-1 py-0.5 text-ink-muted"
            >
              {l}
            </span>
          ))}
        </div>
      )}

      <div className="space-y-3">
        {Array.from(byProject.entries()).map(([proj, ids]) => (
          <div key={proj}>
            <div className="text-[11px] font-medium text-ink-body mb-1.5">
              {proj} <span className="text-ink-muted">· {ids.length}</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {ids.map((t) => (
                <Link
                  key={t}
                  to={`/inbox/${t}`}
                  className="text-[10px] font-mono bg-app border border-line rounded px-1.5 py-0.5 text-ink-body hover:bg-hover hover:text-ink transition-colors duration-150"
                >
                  {t}
                </Link>
              ))}
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
