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
  const conf = playbook.extraction_confidence;
  const confColor =
    conf == null
      ? 'bg-ink-muted'
      : conf >= 0.8
      ? 'bg-emerald-500'
      : conf >= 0.6
      ? 'bg-amber-500'
      : 'bg-red-400';

  return (
    <>
      <SectionLabel>Metadata</SectionLabel>

      {/* Extraction confidence — special row with progress bar */}
      <div className="mb-4">
        <div className="flex items-baseline justify-between">
          <span className="text-[12px] text-ink-body">Extraction confidence</span>
          <span className="text-[13px] font-semibold font-mono text-ink">
            {conf != null ? conf.toFixed(2) : '—'}
          </span>
        </div>
        <div className="h-1.5 rounded-full bg-hover overflow-hidden mt-1.5">
          <div
            className={`h-full rounded-full transition-all ${confColor}`}
            style={{ width: `${Math.round((conf ?? 0) * 100)}%` }}
          />
        </div>
      </div>

      {/* Quantitative rows */}
      <div>
        <MetaRow
          label="Cluster size"
          sublabel="tickets in this pattern"
          value={playbook.cluster_size != null ? playbook.cluster_size.toString() : '—'}
          unit="tickets"
        />
        <MetaRow
          label="Sample used"
          sublabel="quoted in evidence"
          value={
            playbook.sample_size_used != null
              ? playbook.sample_size_used.toString()
              : '—'
          }
          unit="tickets"
        />
        <MetaRow
          label="Frequency"
          value={
            playbook.frequency_per_month != null
              ? playbook.frequency_per_month.toFixed(2)
              : '—'
          }
          unit="tickets / month"
        />
        <MetaRow
          label="Median resolution"
          value={
            playbook.median_resolution_minutes != null
              ? (playbook.median_resolution_minutes / 60).toFixed(1)
              : '—'
          }
          unit="hours"
        />
      </div>
    </>
  );
}


function MetaRow({
  label,
  sublabel,
  value,
  unit,
}: {
  label: string;
  sublabel?: string;
  value: string;
  unit?: string;
}) {
  return (
    <div className="flex items-baseline justify-between py-2 border-b border-line-subtle last:border-0">
      <div className="min-w-0">
        <div className="text-[12px] text-ink-body">{label}</div>
        {sublabel && (
          <div className="text-[10px] text-ink-muted">{sublabel}</div>
        )}
      </div>
      <div className="text-right shrink-0">
        <div className="text-[14px] font-semibold font-mono text-ink tabular-nums">
          {value}
        </div>
        {unit && (
          <div className="text-[10px] text-ink-muted">{unit}</div>
        )}
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
  hint: string;
}

const ROI_ROWS: ROIRowDef[] = [
  { key: 'agent_assist', label: 'Agent assist', color: 'bg-blue-500', hint: 'human + AI co-write' },
  { key: 'product_fix', label: 'Product fix', color: 'bg-amber-500', hint: 'engineering removes the cause' },
  { key: 'deflection', label: 'Self-service deflection', color: 'bg-emerald-500', hint: 'help-center article' },
  { key: 'autonomous_resolve', label: 'Autonomous resolve', color: 'bg-indigo-500', hint: 'agent replies alone' },
];


function ROIBlock({ roi }: { roi: ROIBreakdown }) {
  const baseline = roi.baseline_active_hours;
  // Bars are scaled relative to the baseline so the four strategies read as
  // "how much of the baseline does this strategy reclaim". If baseline is
  // missing we fall back to the largest strategy.
  const scaleMax = Math.max(
    1,
    baseline ?? 0,
    ...ROI_ROWS.map((r) => (roi[r.key] as ROIStrategy | null)?.hours_midpoint ?? 0),
  );

  return (
    <>
      <SectionLabel>ROI · hours saved / year</SectionLabel>

      {baseline != null && (
        <div className="py-3 border-b border-line-subtle">
          <div className="flex items-baseline justify-between">
            <span className="text-[12px] font-medium text-ink">Baseline</span>
            <span className="text-[14px] font-semibold font-mono text-ink tabular-nums">
              {baseline.toFixed(1)} h
            </span>
          </div>
          {roi.baseline_confidence_tier && (
            <div className="text-[10px] text-ink-muted mt-0.5">
              {roi.baseline_confidence_tier}
            </div>
          )}
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
                {mid != null ? `${mid.toFixed(1)} h` : '—'}
              </span>
            </div>
            <div className="text-[10px] text-ink-muted mt-0.5">{r.hint}</div>
            <div className="h-1 rounded-full bg-hover overflow-hidden mt-2 w-full">
              <div
                className={`h-full rounded-full ${r.color}`}
                style={{ width: `${pct}%` }}
              />
            </div>
            {strat?.hours_range_low != null && strat?.hours_range_high != null && (
              <div className="text-[10px] font-mono text-ink-muted mt-1">
                range {strat.hours_range_low.toFixed(1)}–
                {strat.hours_range_high.toFixed(1)} h
                {strat.confidence_tier && (
                  <span className="ml-1">· {strat.confidence_tier}</span>
                )}
              </div>
            )}
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
