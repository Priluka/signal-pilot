import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { ErrorBoundary } from './components/ErrorBoundary'
import { ToastProvider } from './components/Toast'
import { ChatStoreProvider } from './lib/chatStore'
import { ThemeProvider } from './lib/theme'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider>
      <ErrorBoundary>
        <ToastProvider>
          <ChatStoreProvider>
            <App />
          </ChatStoreProvider>
        </ToastProvider>
      </ErrorBoundary>
    </ThemeProvider>
  </StrictMode>,
)
