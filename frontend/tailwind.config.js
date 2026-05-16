/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
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
          '"JetBrains Mono"',
          '"SF Mono"',
          'Menlo',
          'Consolas',
          'monospace',
        ],
      },
      colors: {
        sidebar: {
          bg: '#1a1a2e',
          surface: '#222238',
          border: '#2a2a44',
          muted: '#7a7a96',
          heading: '#5d5d7a',
          text: '#c8c8dc',
          textActive: '#ffffff',
          accent: '#3b82f6',
        },
        panel: {
          bg: '#f7f8fa',
          surface: '#ffffff',
          border: '#e5e7eb',
          divider: '#eef0f3',
        },
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
};
