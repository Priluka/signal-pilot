import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';

import { Layout } from './components/Layout';
import { AgentPage } from './pages/AgentPage';
import { ChatPage } from './pages/ChatPage';
import { ComingSoonPage } from './pages/ComingSoonPage';
import { GraphPage } from './pages/GraphPage';
import { KnowledgePage } from './pages/KnowledgePage';


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Navigate to="/knowledge" replace />} />
          <Route path="/knowledge" element={<KnowledgePage />} />
          <Route path="/knowledge/:slug" element={<KnowledgePage />} />
          <Route path="/graph" element={<GraphPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/agent" element={<AgentPage />} />
          <Route path="/agent/:ticketKey" element={<AgentPage />} />
          <Route
            path="/suggestions"
            element={
              <ComingSoonPage
                title="Suggestions"
                description="Operator-submitted edits to playbooks land here for review before being merged. Wiring pending."
              />
            }
          />
          <Route
            path="/agents/deployed"
            element={
              <ComingSoonPage
                title="Deployed agents"
                description="Inventory of agents running in production with their assigned playbook scopes."
              />
            }
          />
          <Route
            path="/agents/shadow"
            element={
              <ComingSoonPage
                title="Shadow mode"
                description="Tickets where the agent generated a draft but a human reviewed before sending — for pilot tracking."
              />
            }
          />
          <Route
            path="/agents/performance"
            element={
              <ComingSoonPage
                title="Performance"
                description="Approve / edit / reject rates over time, by playbook and by classifier confidence band."
              />
            }
          />
          <Route path="*" element={<Navigate to="/knowledge" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
