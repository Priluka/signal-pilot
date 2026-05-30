/** AgentTimeline — unit tests.
 *
 * Mocks lib/api so no network. Covers:
 *  - Classified / Retrieved / Draft always render
 *  - Skills branch renders Planner started + history + pending + outcome
 *  - Legacy branch renders Awaiting review with Approve/Edit/Reject
 *  - Once feedback_status is set, legacy collapses to a decided step
 *  - Approve & run click bubbles up via onApproveAction
 */
import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

import { AgentTimeline, type AgentTimelineProps } from './AgentTimeline';
import { ThemeProvider } from '../lib/theme';
import type {
  AgentSessionDetail,
  AuditEntry,
  PendingAction,
} from '../lib/types';


// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

function makeSession(
  overrides: Partial<AgentSessionDetail> = {},
): AgentSessionDetail {
  return {
    ticket_id: 'KAN-99',
    classification: {
      label: 'support_request',
      confidence: 0.95,
      reason: 'User asks about parking receipt.',
    },
    retrieval: {
      hits: [
        {
          playbook_id: 'pb-parking',
          title: 'Parking fine playbook',
          description: '',
          score: 0.62,
          rank: 0,
          ticket_class: 'end_user',
          issue_category: 'billing',
          country_focus: ['hr'],
          languages: ['hr'],
          status: 'active',
          extraction_confidence: 0.95,
          project_keys: ['BS'],
        },
      ],
      detected_language: 'hr',
      detected_country: 'hr',
    },
    draft: {
      draft: 'Pozdrav, evo vaše potvrde…',
      recommended_action: 'send_with_review',
      rationale: 'Verify before sending.',
    },
    draft_playbook_id: 'pb-parking',
    edited_text: null,
    feedback_status: null,
    derived_status: 'needs_review',
    updated_at: '2026-05-28T10:00:00Z',
    started_at: '2026-05-28T09:59:00Z',
    classified_at: '2026-05-28T09:59:30Z',
    retrieved_at: '2026-05-28T09:59:40Z',
    drafted_at: '2026-05-28T09:59:55Z',
    feedback_at: null,
    auto_posted_at: null,
    processed_mode: 'assisted',
    jira_browse_url: null,
    planner_status: null,
    planner_error: null,
    planner_updated_at: null,
    ...overrides,
  } as AgentSessionDetail;
}


function baseProps(
  session: AgentSessionDetail | null,
  overrides: Partial<AgentTimelineProps> = {},
): AgentTimelineProps {
  return {
    session,
    source: 'jira',
    pendingActions: [],
    history: [],
    busyActionId: null,
    onApproveAction: vi.fn(),
    onRejectAction: vi.fn(),
    processing: false,
    processError: null,
    onProcess: vi.fn(),
    streamError: null,
    editing: false,
    editedText: session?.draft?.draft ?? '',
    hasEdits: false,
    submitting: false,
    submitError: null,
    isActionable: true,
    onStartEdit: vi.fn(),
    onCancelEdit: vi.fn(),
    onEditedTextChange: vi.fn(),
    onDraftApprove: vi.fn(),
    onDraftReject: vi.fn(),
    ...overrides,
  };
}


function renderRouted(node: React.ReactElement) {
  return render(
    <ThemeProvider>
      <MemoryRouter>{node}</MemoryRouter>
    </ThemeProvider>,
  );
}


// ---------------------------------------------------------------------------
// Cases
// ---------------------------------------------------------------------------

describe('AgentTimeline', () => {
  it('renders Ready-to-process step when session is null on Jira source', () => {
    const onProcess = vi.fn();
    renderRouted(
      <AgentTimeline
        {...baseProps(null, { source: 'jira', onProcess })}
      />,
    );
    expect(screen.getByText('Ready to process')).toBeInTheDocument();
    const btn = screen.getByRole('button', { name: /process with agent/i });
    fireEvent.click(btn);
    expect(onProcess).toHaveBeenCalled();
  });

  it('renders Queued-for-batch step without button on local source', () => {
    renderRouted(
      <AgentTimeline {...baseProps(null, { source: 'local' })} />,
    );
    expect(screen.getByText('Queued for batch')).toBeInTheDocument();
    expect(
      screen.queryByRole('button', { name: /process with agent/i }),
    ).toBeNull();
  });

  it('renders Classified / Retrieved / Draft for a basic session', () => {
    const session = makeSession();
    renderRouted(<AgentTimeline {...baseProps(session)} />);
    expect(screen.getByText('Classified')).toBeInTheDocument();
    expect(screen.getByText('Retrieved playbook')).toBeInTheDocument();
    expect(screen.getByText('Draft generated')).toBeInTheDocument();
    // Legacy branch awaiting-review step appears because no skills active.
    expect(screen.getByText('Awaiting review')).toBeInTheDocument();
  });

  it('shows Approve & send button on the legacy branch when actionable', () => {
    const session = makeSession();
    const onApprove = vi.fn();
    renderRouted(
      <AgentTimeline
        {...baseProps(session, { onDraftApprove: onApprove })}
      />,
    );
    const btn = screen.getByRole('button', { name: /approve & send/i });
    fireEvent.click(btn);
    expect(onApprove).toHaveBeenCalled();
  });

  it('collapses to a decided step once feedback_status is set', () => {
    const session = makeSession({
      feedback_status: 'approved',
      feedback_at: '2026-05-28T10:01:00Z',
      derived_status: 'approved',
    });
    renderRouted(
      <AgentTimeline {...baseProps(session, { isActionable: false })} />,
    );
    expect(screen.getByText('Reviewer approved')).toBeInTheDocument();
    expect(
      screen.queryByRole('button', { name: /approve & send/i }),
    ).toBeNull();
  });

  it('renders Skills branch when pending action exists', () => {
    const session = makeSession({ planner_status: 'awaiting_approval' });
    const pending: PendingAction[] = [
      {
        id: 'pa-1',
        ticket_id: 'KAN-99',
        playbook_id: 'pb-parking',
        skill_name: 'jira_add_public_comment',
        skill_input: { ticket_id: 'KAN-99', body: 'Hello from agent' },
        mode: 'assisted',
        iteration: 2,
        created_at: '2026-05-28T10:00:30Z',
      },
    ];
    const onApprove = vi.fn();
    renderRouted(
      <AgentTimeline
        {...baseProps(session, {
          pendingActions: pending,
          onApproveAction: onApprove,
        })}
      />,
    );
    expect(screen.getByText('Planner started')).toBeInTheDocument();
    expect(screen.getByText('jira_add_public_comment')).toBeInTheDocument();
    expect(screen.getByText('Hello from agent')).toBeInTheDocument();
    const approveBtn = screen.getByRole('button', { name: /approve & run/i });
    fireEvent.click(approveBtn);
    expect(onApprove).toHaveBeenCalledWith('pa-1');
  });

  it('renders Agent finished after history + planner_status=done', () => {
    const session = makeSession({ planner_status: 'done' });
    const history: AuditEntry[] = [
      {
        id: 1,
        ticket_id: 'KAN-99',
        playbook_id: 'pb-parking',
        skill_name: 'jira_add_public_comment',
        skill_input: { ticket_id: 'KAN-99', body: 'Hello' },
        outcome: 'approved',
        ok: true,
        result_data: { comment_id: '10082' },
        error: null,
        decided_by: 'op-1',
        mode: 'assisted',
        iteration: 2,
        decided_at: '2026-05-28T10:00:35Z',
      },
    ];
    renderRouted(
      <AgentTimeline {...baseProps(session, { history })} />,
    );
    expect(screen.getByText(/Planner started/)).toBeInTheDocument();
    expect(
      screen.getByText('Jira comment posted'),
    ).toBeInTheDocument();
    expect(screen.getByText('Agent finished')).toBeInTheDocument();
    expect(screen.getByText(/1 action executed/)).toBeInTheDocument();
  });

  it('renders shadow audit rows distinctly — no "executed", gray dot', () => {
    const session = makeSession({ planner_status: 'done' });
    const history: AuditEntry[] = [
      {
        id: 7,
        ticket_id: 'KAN-99',
        playbook_id: 'pb-parking',
        skill_name: 'jira_add_public_comment',
        skill_input: { ticket_id: 'KAN-99', body: 'Hello' },
        outcome: 'shadow',
        ok: true,
        result_data: null,
        error: null,
        decided_by: null,
        mode: 'shadow',
        iteration: 1,
        decided_at: '2026-05-28T10:00:35Z',
      },
    ];
    renderRouted(<AgentTimeline {...baseProps(session, { history })} />);
    // The "executed" wording must be absent for shadow rows.
    expect(
      screen.getByText(/jira_add_public_comment · shadow — no effect/),
    ).toBeInTheDocument();
    expect(
      screen.queryByText(/Jira comment posted/),
    ).toBeNull();
    // Agent finished summary must not count this shadow row as executed.
    expect(screen.getByText(/0 actions executed/)).toBeInTheDocument();
    expect(screen.getByText(/1 shadow/)).toBeInTheDocument();
  });

  it('marks auto-executed read skill as "executed (auto)"', () => {
    const session = makeSession({ planner_status: 'done' });
    const history: AuditEntry[] = [
      {
        id: 8,
        ticket_id: 'KAN-99',
        playbook_id: 'pb-parking',
        skill_name: 'jira_get_history',
        skill_input: { ticket_id: 'KAN-99' },
        outcome: 'auto',
        ok: true,
        result_data: { comment_count: 3 },
        error: null,
        decided_by: null,
        mode: 'assisted',
        iteration: 1,
        decided_at: '2026-05-28T10:00:30Z',
      },
    ];
    renderRouted(<AgentTimeline {...baseProps(session, { history })} />);
    expect(
      screen.getByText(/jira_get_history executed \(auto\)/),
    ).toBeInTheDocument();
  });

  it('renders red Agent-failed-at node when streamError is set mid-session', () => {
    const session = makeSession();
    renderRouted(
      <AgentTimeline
        {...baseProps(session, {
          streamError: { step: 'draft', message: 'JSON parse error' },
        })}
      />,
    );
    expect(screen.getByText('Agent failed at draft')).toBeInTheDocument();
    expect(screen.getByText(/JSON parse error/)).toBeInTheDocument();
    // The legacy/skills branch must NOT render under an error.
    expect(
      screen.queryByRole('button', { name: /approve & send/i }),
    ).toBeNull();
  });

  it('renders streamError standalone when no session has formed yet', () => {
    renderRouted(
      <AgentTimeline
        {...baseProps(null, {
          processing: false,
          source: 'jira',
          streamError: { step: 'classify', message: 'Anthropic 502' },
        })}
      />,
    );
    expect(screen.getByText('Agent failed at classify')).toBeInTheDocument();
    // Ready-to-process must not also render — operator should re-process
    // explicitly to clear the error.
    expect(
      screen.queryByRole('button', { name: /process with agent/i }),
    ).toBeNull();
  });

  it('renders red Agent loop failed step when planner_status=failed', () => {
    const session = makeSession({
      planner_status: 'failed',
      planner_error: 'anthropic_error: 503 service unavailable',
    });
    renderRouted(<AgentTimeline {...baseProps(session)} />);
    expect(screen.getByText('Agent loop failed')).toBeInTheDocument();
    expect(
      screen.getByText(/503 service unavailable/),
    ).toBeInTheDocument();
  });
});
