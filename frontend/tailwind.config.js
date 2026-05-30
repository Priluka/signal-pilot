/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  // Light is the default; ``class="dark"`` on <html> flips every token via
  // CSS custom properties in index.css.
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: [
          '"Inter Variable"',
          'Inter',
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          'sans-serif',
        ],
        mono: [
          '"JetBrains Mono Variable"',
          '"JetBrains Mono"',
          '"SF Mono"',
          'Menlo',
          'Consolas',
          'monospace',
        ],
      },
      fontSize: {
        // Linear runs tight — page title 18, section 14, body 13.
        '2xs': ['11px', { lineHeight: '1.4' }],
        xs: ['12px', { lineHeight: '1.4' }],
        sm: ['13px', { lineHeight: '1.5' }],
        base: ['14px', { lineHeight: '1.5' }],
        lg: ['18px', { lineHeight: '1.35', letterSpacing: '-0.01em' }],
        xl: ['20px', { lineHeight: '1.3', letterSpacing: '-0.015em' }],
        '2xl': ['24px', { lineHeight: '1.3', letterSpacing: '-0.015em' }],
      },
      colors: {
        // Surfaces
        app: 'rgb(var(--c-app) / <alpha-value>)',
        card: 'rgb(var(--c-card) / <alpha-value>)',
        elevated: 'rgb(var(--c-elevated) / <alpha-value>)',
        hover: 'rgb(var(--c-hover) / <alpha-value>)',
        active: 'rgb(var(--c-active) / <alpha-value>)',

        // Borders — line is the default, line-strong is the heavier outline
        // used on the floating content panel.
        line: 'rgb(var(--c-line) / <alpha-value>)',
        'line-subtle': 'rgb(var(--c-line-subtle) / <alpha-value>)',
        'line-strong': 'rgb(var(--c-line-strong) / <alpha-value>)',

        // Accent — indigo. Reserved for links, sidebar active state,
        // slider fills, focus rings. Primary CTAs use 'btn-primary'.
        accent: {
          DEFAULT: 'rgb(var(--c-accent) / <alpha-value>)',
          hover: 'rgb(var(--c-accent-hover) / <alpha-value>)',
          subtle: 'rgb(var(--c-accent-subtle) / <alpha-value>)',
          fg: 'rgb(var(--c-accent-fg) / <alpha-value>)',
        },

        // Primary CTA — near-black in light, near-white in dark.
        'btn-primary': {
          DEFAULT: 'rgb(var(--c-btn-primary) / <alpha-value>)',
          fg: 'rgb(var(--c-btn-primary-fg) / <alpha-value>)',
          hover: 'rgb(var(--c-btn-primary-hover) / <alpha-value>)',
        },

        // Text
        ink: {
          DEFAULT: 'rgb(var(--c-ink) / <alpha-value>)',
          body: 'rgb(var(--c-body) / <alpha-value>)',
          muted: 'rgb(var(--c-muted) / <alpha-value>)',
          faint: 'rgb(var(--c-faint) / <alpha-value>)',
        },

        // Backwards-compat panel-* aliases so legacy components keep working.
        panel: {
          bg: 'rgb(var(--c-app) / <alpha-value>)',
          surface: 'rgb(var(--c-card) / <alpha-value>)',
          border: 'rgb(var(--c-line) / <alpha-value>)',
          divider: 'rgb(var(--c-line-subtle) / <alpha-value>)',
        },

        // Sidebar aliases — sidebar now shares the app surface, but the
        // legacy class names (bg-sidebar-bg, text-sidebar-textActive…)
        // still need to compile. Map them through.
        sidebar: {
          bg: 'rgb(var(--c-app) / <alpha-value>)',
          surface: 'rgb(var(--c-hover) / <alpha-value>)',
          border: 'rgb(var(--c-line-subtle) / <alpha-value>)',
          muted: 'rgb(var(--c-muted) / <alpha-value>)',
          heading: 'rgb(var(--c-muted) / <alpha-value>)',
          text: 'rgb(var(--c-body) / <alpha-value>)',
          textActive: 'rgb(var(--c-ink) / <alpha-value>)',
          accent: 'rgb(var(--c-accent) / <alpha-value>)',
        },
      },
      borderRadius: {
        DEFAULT: '4px',
        md: '6px',
        lg: '8px',
        xl: '12px',
      },
      boxShadow: {
        // Linear uses borders, not shadows. Keep the named ones near-flat.
        sm: '0 1px 2px rgba(0,0,0,0.04)',
        DEFAULT: '0 1px 2px rgba(0,0,0,0.04)',
        md: '0 4px 12px rgba(0,0,0,0.06)',
        lg: '0 8px 24px rgba(0,0,0,0.08)',
      },
      transitionDuration: {
        DEFAULT: '150ms',
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
};
