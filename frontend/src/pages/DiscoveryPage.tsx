/** Discovery — corpus-wide health report.
 *
 * One read of /discovery/report rolls up every playbook YAML into:
 * hero stats (count, tickets analyzed, reliability, hours saved),
 * coverage bars by category, the five biggest patterns, gaps where
 * coverage is thin, a reliability mini-table, and per-country /
 * per-language coverage with flags.
 *
 * Everything is data-driven — no hardcoded numbers.
 */
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle, Compass } from 'lucide-react';

import { getDiscoveryReport } from '../lib/api';
import { countryLabel } from '../lib/labels';
import type {
  DiscoveryCategoryEntry,
  DiscoveryCountryEntry,
  DiscoveryGap,
  DiscoveryQuality,
  DiscoveryReport,
  DiscoveryTopPlaybook,
} from '../lib/types';


const WORKSPACE_NAME = 'bMove · Customer Support';


export function DiscoveryPage() {
  const [report, setReport] = useState<DiscoveryReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDiscoveryReport()
      .then(setReport)
      .catch((e) => setError(String(e)));
  }, []);

  return (
    <div className="h-full overflow-y-auto scrollbar-thin">
      <div className="max-w-5xl mx-auto px-8 py-8 space-y-10">
        <Header />

        {error && (
          <p className="text-[13px] text-red-600 dark:text-red-400">
            Failed to load report: {error}
          </p>
        )}

        {!report && !error && (
          <p className="text-[13px] text-ink-muted">Loading report…</p>
        )}

        {report && (
          <>
            <Hero report={report} />
            <CategoryCoverage categories={report.categories} />
            <TopPatterns playbooks={report.top_playbooks} />
            <GapsAndRisks gaps={report.gaps} />
            <QualityOverview quality={report.quality} />
            <CountryAndLanguageCoverage
              countries={report.countries}
              languages={report.languages}
            />
          </>
        )}
      </div>
    </div>
  );
}


// ---------------------------------------------------------------------------
// Header
// ---------------------------------------------------------------------------

function Header() {
  return (
    <header>
      <div className="flex items-center gap-2 text-[11px] uppercase tracking-wider text-ink-muted font-medium">
        <Compass width={12} height={12} strokeWidth={1.75} />
        {WORKSPACE_NAME}
      </div>
      <h1 className="text-xl font-semibold text-ink mt-2">Discovery Report</h1>
      <p className="text-[13px] text-ink-muted mt-1">
        Corpus-wide view of what the agent knows, where coverage is
        strong, and where it isn't.
      </p>
    </header>
  );
}


// ---------------------------------------------------------------------------
// Hero — four bare stats (same chrome as Home)
// ---------------------------------------------------------------------------

function Hero({ report }: { report: DiscoveryReport }) {
  const r = report.roi_summary;
  const savings = r.baseline_hours - r.agent_assist_hours;
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 py-6 border-b border-line-subtle">
      <Stat
        label="Total playbooks"
        value={report.total_playbooks.toString()}
        sub="active in corpus"
      />
      <Stat
        label="Tickets analyzed"
        value={report.total_tickets_covered.toLocaleString()}
        sub="across all clusters"
      />
      <Stat
        label="Avg reliability"
        value={
          report.avg_confidence != null
            ? `${Math.round(report.avg_confidence * 100)}%`
            : '—'
        }
        sub="extraction confidence"
      />
      <Stat
        label="Hours saved / year"
        value={`${Math.round(savings).toLocaleString()} h`}
        sub={`vs ${Math.round(r.baseline_hours).toLocaleString()} h baseline`}
      />
    </div>
  );
}


function Stat({
  label,
  value,
  sub,
}: {
  label: string;
  value: string;
  sub: string;
}) {
  return (
    <div>
      <div className="text-[11px] uppercase tracking-wider text-ink-muted font-medium">
        {label}
      </div>
      <div className="text-[28px] leading-none font-semibold font-mono mt-1 tabular-nums text-ink">
        {value}
      </div>
      {sub && <div className="text-[11px] text-ink-muted mt-1.5">{sub}</div>}
    </div>
  );
}


// ---------------------------------------------------------------------------
// Coverage by category — horizontal bars
// ---------------------------------------------------------------------------

function CategoryCoverage({ categories }: { categories: DiscoveryCategoryEntry[] }) {
  if (categories.length === 0) return null;
  const max = Math.max(...categories.map((c) => c.count));
  return (
    <Section title="Coverage by category">
      <ul className="space-y-2">
        {categories.map((c) => {
          const pct = Math.max(2, Math.round((c.count / max) * 100));
          return (
            <li key={c.name}>
              <Link
                to={`/knowledge?issue_category=${encodeURIComponent(c.name)}`}
                className="group block py-2 px-2 -mx-2 rounded-md hover:bg-hover transition-colors duration-150"
              >
                <div className="flex items-baseline justify-between mb-1.5">
                  <span className="text-[13px] text-ink group-hover:text-accent-fg transition-colors duration-150">
                    {humanizeCategory(c.name)}
                  </span>
                  <span className="text-[12px] font-mono tabular-nums text-ink-muted">
                    {c.count} playbook{c.count === 1 ? '' : 's'}
                  </span>
                </div>
                <div className="h-1.5 rounded-full bg-hover overflow-hidden">
                  <div
                    className="h-full bg-accent rounded-full transition-all"
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </Link>
            </li>
          );
        })}
      </ul>
    </Section>
  );
}


// ---------------------------------------------------------------------------
// Top 5 patterns
// ---------------------------------------------------------------------------

function TopPatterns({ playbooks }: { playbooks: DiscoveryTopPlaybook[] }) {
  if (playbooks.length === 0) return null;
  return (
    <Section title="Top 5 patterns">
      <ul>
        {playbooks.map((p, i) => (
          <li key={p.id}>
            <Link
              to={`/knowledge/${p.id}`}
              className="flex items-center h-10 px-2 -mx-2 rounded-md hover:bg-hover transition-colors duration-150"
            >
              <span className="text-[11px] font-mono tabular-nums text-ink-muted w-6 flex-shrink-0">
                #{i + 1}
              </span>
              <span className="text-[13px] text-ink truncate flex-1">
                {p.title}
              </span>
              <span className="text-[12px] font-mono tabular-nums text-ink-muted flex-shrink-0 ml-3">
                {p.cluster_size} ticket{p.cluster_size === 1 ? '' : 's'}
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </Section>
  );
}


// ---------------------------------------------------------------------------
// Gaps & risks
// ---------------------------------------------------------------------------

function GapsAndRisks({ gaps }: { gaps: DiscoveryGap[] }) {
  if (gaps.length === 0) {
    return (
      <Section title="Gaps &amp; risks">
        <p className="text-[12px] text-ink-muted py-2">
          Every category has at least three playbooks. No coverage gaps detected.
        </p>
      </Section>
    );
  }
  return (
    <Section title="Gaps &amp; risks">
      <ul className="space-y-2">
        {gaps.map((g) => (
          <li
            key={g.category}
            className="flex items-start gap-3 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 rounded-md px-3 py-2.5"
          >
            <AlertTriangle
              width={14}
              height={14}
              strokeWidth={1.75}
              className="text-amber-600 dark:text-amber-400 mt-0.5 shrink-0"
            />
            <div className="text-[12px] text-amber-700 dark:text-amber-300 leading-snug">
              Only {g.count} playbook{g.count === 1 ? '' : 's'} cover
              {g.count === 1 ? 's' : ''}{' '}
              <span className="font-semibold">{humanizeCategory(g.category)}</span>
              {' '}— consider expanding coverage.
            </div>
          </li>
        ))}
      </ul>
    </Section>
  );
}


// ---------------------------------------------------------------------------
// Quality overview
// ---------------------------------------------------------------------------

function QualityOverview({ quality }: { quality: DiscoveryQuality }) {
  return (
    <Section title="Quality overview">
      <div className="grid grid-cols-3 gap-8 py-4 border-t border-b border-line-subtle">
        <QualityStat label="Min" value={fmtPct(quality.min)} />
        <QualityStat label="Avg" value={fmtPct(quality.avg)} />
        <QualityStat label="Max" value={fmtPct(quality.max)} />
      </div>
      {quality.low_confidence_count > 0 && (
        <div className="flex items-start gap-3 mt-3 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 rounded-md px-3 py-2.5">
          <AlertTriangle
            width={14}
            height={14}
            strokeWidth={1.75}
            className="text-amber-600 dark:text-amber-400 mt-0.5 shrink-0"
          />
          <div className="text-[12px] text-amber-700 dark:text-amber-300 leading-snug">
            <span className="font-semibold">
              {quality.low_confidence_count} playbook
              {quality.low_confidence_count === 1 ? '' : 's'}
            </span>{' '}
            sit below the 75% reliability threshold — worth a manual pass.
          </div>
        </div>
      )}
    </Section>
  );
}


function QualityStat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-[11px] uppercase tracking-wider text-ink-muted font-medium">
        {label}
      </div>
      <div className="text-[20px] font-semibold font-mono tabular-nums text-ink mt-1">
        {value}
      </div>
    </div>
  );
}


// ---------------------------------------------------------------------------
// Country & language coverage
// ---------------------------------------------------------------------------

function CountryAndLanguageCoverage({
  countries,
  languages,
}: {
  countries: DiscoveryCountryEntry[];
  languages: { name: string; count: number }[];
}) {
  return (
    <Section title="Country &amp; language coverage">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
        <div>
          <h3 className="text-[11px] uppercase tracking-wider text-ink-muted font-medium mb-3">
            Countries
          </h3>
          {countries.length === 0 ? (
            <p className="text-[12px] text-ink-muted">No country data.</p>
          ) : (
            <ul className="space-y-1.5">
              {countries.map((c) => {
                const { flag, name } = countryLabel(c.code);
                return (
                  <li
                    key={c.code}
                    className="flex items-center justify-between text-[13px]"
                  >
                    <span className="text-ink">
                      {flag && <span className="mr-2">{flag}</span>}
                      {name}
                    </span>
                    <span className="font-mono tabular-nums text-ink-muted text-[12px]">
                      {c.count} playbook{c.count === 1 ? '' : 's'}
                    </span>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
        <div>
          <h3 className="text-[11px] uppercase tracking-wider text-ink-muted font-medium mb-3">
            Languages
          </h3>
          {languages.length === 0 ? (
            <p className="text-[12px] text-ink-muted">No language data.</p>
          ) : (
            <ul className="space-y-1.5">
              {languages.map((l) => (
                <li
                  key={l.name}
                  className="flex items-center justify-between text-[13px]"
                >
                  <span className="text-ink uppercase font-mono tracking-wider text-[12px]">
                    {l.name}
                  </span>
                  <span className="font-mono tabular-nums text-ink-muted text-[12px]">
                    {l.count} playbook{l.count === 1 ? '' : 's'}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </Section>
  );
}


// ---------------------------------------------------------------------------
// Shared chrome
// ---------------------------------------------------------------------------

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section>
      <h2 className="text-[14px] font-semibold text-ink mb-3">{title}</h2>
      {children}
    </section>
  );
}


// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function humanizeCategory(name: string): string {
  return name
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
}


function fmtPct(v: number | null): string {
  if (v == null) return '—';
  return `${Math.round(v * 100)}%`;
}
