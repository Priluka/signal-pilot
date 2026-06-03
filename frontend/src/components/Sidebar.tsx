/** Linear-style sidebar: shares the app background so it blends with the
 * shell. No border on the right — visual separation comes from the
 * floating content panel sitting to its right.
 *
 * Top: user dropdown (theme toggle + settings link, more to come).
 * Middle: Workspace / Review / Teams / System nav sections.
 * Bottom: nothing for now — the old "OP / Operator" tile moved into
 * the dropdown header so the rail itself stays quiet.
 */
import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type ComponentType,
  type SVGProps,
} from 'react';
import { Link, NavLink } from 'react-router-dom';
import {
  Activity,
  BookOpen,
  Bot,
  ChevronsUpDown,
  Compass,
  Home,
  Inbox,
  Lightbulb,
  MessageSquare,
  Moon,
  Settings as SettingsIcon,
  Sun,
  Users,
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
  // Drive the nav-row spinner from streamingTurnId — any non-null
  // value means a turn is currently being generated.
  const { streamingTurnId } = useChatStore();
  const streaming = streamingTurnId != null;
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


function InactiveRow({ label, icon: Icon }: { label: string; icon: IconType }) {
  return (
    <div className="flex items-center gap-2.5 h-8 px-2.5 rounded-md text-[13px] text-ink-body hover:bg-hover hover:text-ink transition-colors duration-150 cursor-pointer">
      <Icon
        width={16}
        height={16}
        strokeWidth={1.75}
        className="shrink-0 text-ink-muted"
      />
      <span className="truncate">{label}</span>
    </div>
  );
}


function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <div className="px-3 pt-4 pb-1 text-[11px] font-medium uppercase tracking-wider text-ink-muted">
      {children}
    </div>
  );
}


// ---------------------------------------------------------------------------
// Sidebar
// ---------------------------------------------------------------------------

export function Sidebar() {
  const [playbooksCount, setPlaybooksCount] = useState<number | undefined>(undefined);
  const [suggestionsPending, setSuggestionsPending] = useState<number | undefined>(undefined);
  const [inboxCount, setInboxCount] = useState<number | undefined>(undefined);

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
      <UserDropdown />

      <nav className="flex-1 overflow-y-auto scrollbar-thin mt-1 -mx-2 px-2 space-y-px">
        <SectionHeading>Workspace</SectionHeading>
        <NavRow to="/" label="Home" icon={Home} />
        <NavRow to="/knowledge" label="Playbooks" icon={BookOpen} count={playbooksCount} />
        <NavRow to="/discovery" label="Discovery" icon={Compass} />
        <ChatNavRow />
        <NavRow to="/inbox" label="Inbox" icon={Inbox} count={inboxCount} />
        <NavRow to="/activity-log" label="History" icon={Activity} />

        <SectionHeading>Review</SectionHeading>
        <NavRow
          to="/suggestions"
          label="Suggestions"
          icon={Lightbulb}
          count={suggestionsPending}
        />

        <SectionHeading>Teams</SectionHeading>
        <InactiveRow label="Support" icon={Users} />

        <SectionHeading>System</SectionHeading>
        <NavRow to="/agents" label="Agents" icon={Bot} />
      </nav>
    </aside>
  );
}


// ---------------------------------------------------------------------------
// User dropdown — replaces the old workspace selector
// ---------------------------------------------------------------------------

function UserDropdown() {
  const { theme, toggle } = useTheme();
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!open) return;
    function onClickAway(e: MouseEvent) {
      const target = e.target as Node | null;
      if (target && rootRef.current && !rootRef.current.contains(target)) {
        setOpen(false);
      }
    }
    function onEsc(e: KeyboardEvent) {
      if (e.key === 'Escape') setOpen(false);
    }
    document.addEventListener('mousedown', onClickAway);
    document.addEventListener('keydown', onEsc);
    return () => {
      document.removeEventListener('mousedown', onClickAway);
      document.removeEventListener('keydown', onEsc);
    };
  }, [open]);

  return (
    <div ref={rootRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between gap-2 px-2 py-1.5 rounded-md hover:bg-hover transition-colors duration-150 text-left"
      >
        <div className="flex items-center gap-2 min-w-0">
          <div className="w-6 h-6 rounded-md bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center text-white font-semibold text-[10px] shrink-0">
            OP
          </div>
          <div className="min-w-0">
            <div className="text-[13px] font-semibold text-ink truncate tracking-tight">
              Operator
            </div>
            <div className="text-[10px] text-ink-muted truncate">
              Support · Admin
            </div>
          </div>
        </div>
        <ChevronsUpDown
          width={14}
          height={14}
          strokeWidth={1.75}
          className="text-ink-muted shrink-0"
        />
      </button>

      {open && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-card border border-line rounded-md shadow-md py-1 z-30">
          <button
            type="button"
            onClick={() => {
              toggle();
              setOpen(false);
            }}
            className="w-full flex items-center justify-between px-3 py-1.5 text-[13px] text-ink-body hover:bg-hover hover:text-ink transition-colors duration-150"
          >
            <span className="flex items-center gap-2">
              {theme === 'dark' ? (
                <Sun width={14} height={14} strokeWidth={1.75} />
              ) : (
                <Moon width={14} height={14} strokeWidth={1.75} />
              )}
              Theme
            </span>
            <span className="text-[11px] text-ink-muted capitalize">{theme}</span>
          </button>

          <Link
            to="/settings"
            onClick={() => setOpen(false)}
            className="w-full flex items-center gap-2 px-3 py-1.5 text-[13px] text-ink-body hover:bg-hover hover:text-ink transition-colors duration-150"
          >
            <SettingsIcon width={14} height={14} strokeWidth={1.75} />
            Settings
          </Link>
        </div>
      )}
    </div>
  );
}
