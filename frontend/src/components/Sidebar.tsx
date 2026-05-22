/** Linear-style sidebar: shares the app background so it blends with the
 * shell. No border on the right — visual separation comes from the
 * floating content panel sitting to its right.
 *
 * Compact 220px wide, sectioned, Lucide icons, theme toggle pinned next
 * to the user avatar at the bottom.
 */
import {
  useCallback,
  useEffect,
  useState,
  type ComponentType,
  type SVGProps,
} from 'react';
import { NavLink } from 'react-router-dom';
import {
  Activity,
  BookOpen,
  Bot,
  ChevronsUpDown,
  Inbox,
  Lightbulb,
  MessageSquare,
  Moon,
  Sun,
} from 'lucide-react';

import { getAgentMetrics, getCategories, getSuggestionStats } from '../lib/api';
import { useChatStore } from '../lib/chatStore';
import { useTheme } from '../lib/theme';


type IconType = ComponentType<SVGProps<SVGSVGElement>>;


interface NavRowProps {
  to: string;
  label: string;
  icon: IconType;
  count?: number;
}


function NavRow({ to, label, icon: Icon, count }: NavRowProps) {
  return (
    <NavLink
      to={to}
      end={to === '/'}
      className={({ isActive }) =>
        [
          'group flex items-center justify-between gap-2 h-8 px-2.5 rounded-md text-[13px] transition-colors duration-150',
          isActive
            ? 'bg-active text-ink font-medium'
            : 'text-ink-body hover:bg-hover hover:text-ink',
        ].join(' ')
      }
    >
      {({ isActive }) => (
        <>
          <span className="flex items-center gap-2.5 min-w-0">
            <Icon
              width={16}
              height={16}
              strokeWidth={1.75}
              className={`shrink-0 ${isActive ? 'text-ink' : 'text-ink-muted'}`}
            />
            <span className="truncate">{label}</span>
          </span>
          {typeof count === 'number' && count > 0 && (
            <span className="text-2xs text-ink-muted font-mono tabular-nums">
              {count}
            </span>
          )}
        </>
      )}
    </NavLink>
  );
}


function ChatNavRow() {
  const { status } = useChatStore();
  const streaming = status === 'streaming';
  return (
    <NavLink
      to="/chat"
      className={({ isActive }) =>
        [
          'group flex items-center justify-between gap-2 h-8 px-2.5 rounded-md text-[13px] transition-colors duration-150',
          isActive
            ? 'bg-active text-ink font-medium'
            : 'text-ink-body hover:bg-hover hover:text-ink',
        ].join(' ')
      }
    >
      {({ isActive }) => (
        <>
          <span className="flex items-center gap-2.5 min-w-0">
            <MessageSquare
              width={16}
              height={16}
              strokeWidth={1.75}
              className={`shrink-0 ${isActive ? 'text-ink' : 'text-ink-muted'}`}
            />
            <span className="truncate">Chat</span>
            {streaming && (
              <span
                title="Streaming…"
                className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"
              />
            )}
          </span>
          {streaming && (
            <span className="text-2xs uppercase tracking-wider text-emerald-600 font-medium">
              live
            </span>
          )}
        </>
      )}
    </NavLink>
  );
}


function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <div className="px-3 pt-4 pb-1 text-[11px] font-medium uppercase tracking-wider text-ink-muted">
      {children}
    </div>
  );
}


export function Sidebar() {
  const [playbooksCount, setPlaybooksCount] = useState<number | undefined>(undefined);
  const [suggestionsPending, setSuggestionsPending] = useState<number | undefined>(undefined);
  const [inboxCount, setInboxCount] = useState<number | undefined>(undefined);
  const { theme, toggle } = useTheme();

  const refreshPlaybooks = useCallback(() => {
    getCategories()
      .then((data) => setPlaybooksCount(data.total))
      .catch(() => setPlaybooksCount(undefined));
  }, []);

  const refreshSuggestions = useCallback(() => {
    getSuggestionStats()
      .then((stats) => setSuggestionsPending(stats.pending))
      .catch(() => setSuggestionsPending(undefined));
  }, []);

  const refreshInbox = useCallback(() => {
    getAgentMetrics()
      .then((m) => setInboxCount(m.needs_review + m.escalated))
      .catch(() => setInboxCount(undefined));
  }, []);

  useEffect(() => {
    refreshPlaybooks();
    refreshSuggestions();
    refreshInbox();
    const suggHandler = () => refreshSuggestions();
    const agentHandler = () => refreshInbox();
    window.addEventListener('suggestions-changed', suggHandler);
    window.addEventListener('agent-sessions-changed', agentHandler);
    return () => {
      window.removeEventListener('suggestions-changed', suggHandler);
      window.removeEventListener('agent-sessions-changed', agentHandler);
    };
  }, [refreshPlaybooks, refreshSuggestions, refreshInbox]);

  return (
    <aside className="w-[248px] shrink-0 flex flex-col py-3 px-2 bg-app">
      {/* Workspace selector */}
      <button
        type="button"
        className="w-full flex items-center justify-between gap-2 px-2 py-1.5 rounded-md hover:bg-hover transition-colors duration-150 text-left"
      >
        <div className="flex items-center gap-2 min-w-0">
          <div className="w-6 h-6 rounded-md bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-white font-semibold text-[11px] shrink-0">
            P
          </div>
          <div className="min-w-0">
            <div className="text-[13px] font-semibold text-ink truncate tracking-tight">
              Praxis
            </div>
            <div className="text-[10px] text-ink-muted truncate">
              bMove · Support
            </div>
          </div>
        </div>
        <ChevronsUpDown width={14} height={14} strokeWidth={1.75} className="text-ink-muted shrink-0" />
      </button>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto scrollbar-thin mt-1 -mx-2 px-2 space-y-px">
        <SectionHeading>Workspace</SectionHeading>
        <NavRow to="/knowledge" label="Playbooks" icon={BookOpen} count={playbooksCount} />
        <ChatNavRow />
        <NavRow to="/inbox" label="Inbox" icon={Inbox} count={inboxCount} />
        <NavRow to="/activity-log" label="Activity Log" icon={Activity} />

        <SectionHeading>Review</SectionHeading>
        <NavRow
          to="/suggestions"
          label="Suggestions"
          icon={Lightbulb}
          count={suggestionsPending}
        />

        <SectionHeading>System</SectionHeading>
        <NavRow to="/agents" label="Agents" icon={Bot} />
      </nav>

      {/* User + theme */}
      <div className="mt-2 pt-3 border-t border-line-subtle flex items-center gap-2 px-1">
        <div className="w-7 h-7 rounded-full bg-gradient-to-br from-emerald-400 to-teal-600 shrink-0 flex items-center justify-center text-[10px] font-semibold text-white">
          OP
        </div>
        <div className="min-w-0 flex-1">
          <div className="text-[12px] text-ink truncate font-medium">Operator</div>
          <div className="text-[10px] text-ink-muted truncate">Support · Admin</div>
        </div>
        <button
          type="button"
          onClick={toggle}
          aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          title={theme === 'dark' ? 'Light mode' : 'Dark mode'}
          className="w-7 h-7 inline-flex items-center justify-center rounded-md text-ink-muted hover:bg-hover hover:text-ink transition-colors duration-150 shrink-0"
        >
          {theme === 'dark' ? (
            <Sun width={15} height={15} strokeWidth={1.75} />
          ) : (
            <Moon width={15} height={15} strokeWidth={1.75} />
          )}
        </button>
      </div>
    </aside>
  );
}
