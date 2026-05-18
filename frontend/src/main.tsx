import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { ToastProvider } from './components/Toast'
import { ChatStoreProvider } from './lib/chatStore'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ToastProvider>
      <ChatStoreProvider>
        <App />
      </ChatStoreProvider>
    </ToastProvider>
  </StrictMode>,
)
