/// <reference types="vitest" />
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

// Vitest config — kept separate from ``vite.config.ts`` so that the
// production build can use Vite's own ``defineConfig`` (which doesn't
// understand the ``test`` field) without type conflicts between the
// rolldown-flavoured Vite plugins and vitest's bundled Vite types.

// @ts-expect-error — rolldown vs rollup plugin shape mismatch between
// Vite's bundled rolldown and vitest's bundled rollup. The plugin
// works at runtime; both ecosystems agree on the public Vite plugin
// API even when the internal hook signatures disagree.
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    css: false,
  },
})
