import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';

import { Layout } from './components/Layout';
import { AgentPage } from './pages/AgentPage';
import { ChatPage } from './pages/ChatPage';
import { KnowledgePage } from './pages/KnowledgePage';


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Navigate to="/knowledge" replace />} />
          <Route path="/knowledge" element={<KnowledgePage />} />
          <Route path="/knowledge/:slug" element={<KnowledgePage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/agent" element={<AgentPage />} />
          <Route path="/agent/:ticketKey" element={<AgentPage />} />
          <Route path="*" element={<Navigate to="/knowledge" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
