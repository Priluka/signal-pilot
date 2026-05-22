/** Catches render errors so the whole app doesn't blank out — instead the
 * operator sees the message + a Reload button. */
import { Component, type ReactNode } from 'react';


interface Props {
  children: ReactNode;
}

interface State {
  error: Error | null;
}


export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: { componentStack?: string }) {
    // eslint-disable-next-line no-console
    console.error('[ErrorBoundary]', error, info);
  }

  render(): ReactNode {
    if (this.state.error) {
      return (
        <div className="h-full flex items-center justify-center bg-hover p-8">
          <div className="max-w-xl bg-card border border-red-200 rounded-md p-6 shadow-sm">
            <h1 className="text-base font-semibold text-red-700">
              Something went wrong rendering the UI
            </h1>
            <pre className="mt-3 text-xs text-ink-body bg-hover border border-line rounded p-3 overflow-auto max-h-64">
              {this.state.error.message}
              {this.state.error.stack && '\n\n' + this.state.error.stack}
            </pre>
            <div className="mt-4 flex items-center gap-2">
              <button
                type="button"
                onClick={() => {
                  this.setState({ error: null });
                }}
                className="px-3 py-1.5 text-sm border border-line rounded hover:bg-hover"
              >
                Retry
              </button>
              <button
                type="button"
                onClick={() => window.location.reload()}
                className="px-3 py-1.5 text-sm font-medium text-white bg-accent rounded hover:bg-accent-hover"
              >
                Reload page
              </button>
              <button
                type="button"
                onClick={() => {
                  try {
                    localStorage.clear();
                  } catch {
                    /* ignore */
                  }
                  window.location.reload();
                }}
                className="px-3 py-1.5 text-sm border border-amber-200 text-amber-700 rounded hover:bg-amber-50"
              >
                Clear local data &amp; reload
              </button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
