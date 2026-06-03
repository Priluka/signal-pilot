import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
// Test configuration lives in vitest.config.ts so the production
// ``vite build`` doesn't drag vitest's type definitions into the
// compile and trigger plugin-shape conflicts.
export default defineConfig({
  plugins: [react()],
})
