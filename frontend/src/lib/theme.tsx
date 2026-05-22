/** Theme provider + hook for the light/dark toggle.
 *
 * The actual class is applied to ``<html>`` in index.html before React
 * mounts (avoids FOUC). This provider just keeps the React state in sync
 * with the DOM + localStorage and exposes a setter.
 */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';


export type Theme = 'light' | 'dark';

interface ThemeContextValue {
  theme: Theme;
  setTheme: (next: Theme) => void;
  toggle: () => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);


function readInitial(): Theme {
  if (typeof window === 'undefined') return 'light';
  const stored = window.localStorage.getItem('theme');
  return stored === 'dark' ? 'dark' : 'light';
}


export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(readInitial);

  const apply = useCallback((next: Theme) => {
    const html = document.documentElement;
    html.classList.remove('light', 'dark');
    html.classList.add(next);
    html.style.colorScheme = next;
    try {
      window.localStorage.setItem('theme', next);
    } catch {
      /* private mode */
    }
    setThemeState(next);
  }, []);

  // Make sure DOM class matches React state on mount — if the inline
  // script in index.html ran with a different stored value than our
  // initial state, this reconciles.
  useEffect(() => {
    apply(theme);
    // Only run once on mount; further updates go through setTheme/toggle.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const value = useMemo<ThemeContextValue>(
    () => ({
      theme,
      setTheme: apply,
      toggle: () => apply(theme === 'dark' ? 'light' : 'dark'),
    }),
    [theme, apply],
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}


export function useTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used inside <ThemeProvider>');
  return ctx;
}
