/** ActionApproval — unit tests.
 *
 * Mocks lib/api so no network is touched; covers:
 *  - empty list → renders nothing
 *  - non-empty list → one card per action, with skill name + params
 *  - clicking Approve calls approveAction(id) + re-fetches
 *  - clicking Reject calls rejectAction(id) + re-fetches
 *  - error from API surfaces via toast (no crash)
 */
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';

import { ActionApproval } from './ActionApproval';
import * as api from '../lib/api';
import { ToastProvider } from './Toast';


function renderWithToast(node: React.ReactElement) {
  return render(<ToastProvider>{node}</ToastProvider>);
}


const sampleAction = {
  id: 'pa-abc',
  ticket_id: 'KAN-99',
  playbook_id: 'pb-x',
  skill_name: 'jira_add_public_comment',
  skill_input: { ticket_id: 'KAN-99', body: 'Hello' },
  mode: 'assisted',
  iteration: 2,
  created_at: '2026-05-28T12:00:00Z',
};


describe('ActionApproval', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders nothing when there are no pending actions', async () => {
    vi.spyOn(api, 'listPendingActionsForTicket').mockResolvedValue([]);
    const { container } = renderWithToast(
      <ActionApproval ticketKey="KAN-99" />,
    );
    await waitFor(() => {
      expect(api.listPendingActionsForTicket).toHaveBeenCalledWith('KAN-99');
    });
    expect(container.querySelector('section')).toBeNull();
  });

  it('renders one card per pending action with skill name + params', async () => {
    vi.spyOn(api, 'listPendingActionsForTicket').mockResolvedValue([
      sampleAction,
    ]);
    renderWithToast(<ActionApproval ticketKey="KAN-99" />);
    expect(
      await screen.findByText(/Agent action.*awaiting approval/i),
    ).toBeInTheDocument();
    expect(screen.getByText('jira_add_public_comment')).toBeInTheDocument();
    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.getByText(/iter 2/)).toBeInTheDocument();
  });

  it('clicking Approve calls approveAction + refetches', async () => {
    const listSpy = vi
      .spyOn(api, 'listPendingActionsForTicket')
      .mockResolvedValue([sampleAction]);
    const approveSpy = vi.spyOn(api, 'approveAction').mockResolvedValue({
      status: 'done',
      pending_action_id: null,
      error: null,
      iterations: 3,
      summary: 'ok',
    });

    renderWithToast(<ActionApproval ticketKey="KAN-99" />);
    const approveBtn = await screen.findByRole('button', { name: /approve/i });
    fireEvent.click(approveBtn);

    await waitFor(() => {
      expect(approveSpy).toHaveBeenCalledWith('pa-abc');
    });
    // initial mount fetch + post-approve refetch = at least 2 calls
    expect(listSpy.mock.calls.length).toBeGreaterThanOrEqual(2);
  });

  it('clicking Reject calls rejectAction + refetches', async () => {
    const listSpy = vi
      .spyOn(api, 'listPendingActionsForTicket')
      .mockResolvedValue([sampleAction]);
    const rejectSpy = vi.spyOn(api, 'rejectAction').mockResolvedValue({
      status: 'done',
      pending_action_id: null,
      error: null,
      iterations: 3,
      summary: 'rejected',
    });

    renderWithToast(<ActionApproval ticketKey="KAN-99" />);
    const rejectBtn = await screen.findByRole('button', { name: /reject/i });
    fireEvent.click(rejectBtn);

    await waitFor(() => {
      expect(rejectSpy).toHaveBeenCalledWith(
        'pa-abc',
        expect.any(String),
      );
    });
    expect(listSpy.mock.calls.length).toBeGreaterThanOrEqual(2);
  });

  it('does not crash when API rejects approve', async () => {
    vi.spyOn(api, 'listPendingActionsForTicket').mockResolvedValue([
      sampleAction,
    ]);
    vi.spyOn(api, 'approveAction').mockRejectedValue(new Error('409 in flight'));

    renderWithToast(<ActionApproval ticketKey="KAN-99" />);
    const approveBtn = await screen.findByRole('button', { name: /approve/i });
    fireEvent.click(approveBtn);

    // Button transitions to Working then returns; component still mounted.
    await waitFor(() => {
      expect(api.approveAction).toHaveBeenCalled();
    });
    // No throw bubbles up — error becomes a toast inside the component.
    expect(screen.queryByText('jira_add_public_comment')).toBeInTheDocument();
  });
});
