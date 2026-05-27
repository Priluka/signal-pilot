/** Friendly user-facing labels for raw enum/code values.
 *
 * The data layer keeps the raw machine codes (`internal_partner`, `RAOS`,
 * `hr`, …) so URL params, filters and API contracts stay stable. The UI
 * funnels everything through these helpers so support agents and ops
 * managers never see snake_case or 4-letter project keys.
 */

// ---------------------------------------------------------------------------
// Ticket class
// ---------------------------------------------------------------------------

const TICKET_CLASS: Record<string, string> = {
  internal_partner: 'Internal',
  end_user: 'End User',
  b2b_partner: 'B2B Partner',
};

export function ticketClassLabel(key: string): string {
  return TICKET_CLASS[key] ?? key;
}


// ---------------------------------------------------------------------------
// Source / project_key
// ---------------------------------------------------------------------------

const SOURCE: Record<string, string> = {
  RAOS: 'RAO Support',
};

export function sourceLabel(key: string): string {
  return SOURCE[key] ?? key;
}


// ---------------------------------------------------------------------------
// Country
// ---------------------------------------------------------------------------

const COUNTRY: Record<string, { flag: string; name: string }> = {
  hr: { flag: '🇭🇷', name: 'Croatia' },
  it: { flag: '🇮🇹', name: 'Italy' },
  at: { flag: '🇦🇹', name: 'Austria' },
  de: { flag: '🇩🇪', name: 'Germany' },
  si: { flag: '🇸🇮', name: 'Slovenia' },
  sk: { flag: '🇸🇰', name: 'Slovakia' },
  hu: { flag: '🇭🇺', name: 'Hungary' },
  cz: { flag: '🇨🇿', name: 'Czechia' },
  pl: { flag: '🇵🇱', name: 'Poland' },
  rs: { flag: '🇷🇸', name: 'Serbia' },
  ba: { flag: '🇧🇦', name: 'Bosnia and Herzegovina' },
  me: { flag: '🇲🇪', name: 'Montenegro' },
  mk: { flag: '🇲🇰', name: 'North Macedonia' },
};

export function countryLabel(code: string): { flag: string; name: string } {
  return COUNTRY[code.toLowerCase()] ?? { flag: '', name: code.toUpperCase() };
}


// ---------------------------------------------------------------------------
// Reliability (extraction_confidence → user-friendly tier)
// ---------------------------------------------------------------------------

export type ReliabilityTier = 'High' | 'Medium' | 'Low';

export function reliabilityTier(
  score: number | null,
): { tier: ReliabilityTier; percent: number } | null {
  if (score == null) return null;
  const percent = Math.round(score * 100);
  if (score >= 0.9) return { tier: 'High', percent };
  if (score >= 0.75) return { tier: 'Medium', percent };
  return { tier: 'Low', percent };
}


// ---------------------------------------------------------------------------
// Frequency / resolution time
// ---------------------------------------------------------------------------

/** "0.78 tickets/month" → "~1 ticket per month". Sub-monthly snaps to 1. */
export function frequencyLabel(perMonth: number | null): string {
  if (perMonth == null) return '—';
  const n = Math.max(1, Math.round(perMonth));
  return `~${n} ticket${n === 1 ? '' : 's'} per month`;
}

/** "1.0 hours" → "~1 hour"; "0.4 hours" → "<1 hour". */
export function resolutionLabel(minutes: number | null): string {
  if (minutes == null) return '—';
  const hours = minutes / 60;
  if (hours < 1) return '<1 hour';
  const n = Math.round(hours);
  return `~${n} hour${n === 1 ? '' : 's'}`;
}
