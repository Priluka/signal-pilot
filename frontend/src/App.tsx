import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';

import { Layout } from './components/Layout';
import { ActivityLogPage } from './pages/ActivityLogPage';
import { AgentsPage } from './pages/AgentsPage';
import { ChatPage } from './pages/ChatPage';
import { GraphPage } from './pages/GraphPage';
import { InboxPage } from './pages/InboxPage';
import { KnowledgePage } from './pages/KnowledgePage';
import { SuggestionsPage } from './pages/SuggestionsPage';


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
          <Route path="/inbox" element={<InboxPage />} />
          <Route path="/inbox/:ticketKey" element={<InboxPage />} />
          <Route path="/activity-log" element={<ActivityLogPage />} />
          <Route path="/activity-log/:ticketKey" element={<ActivityLogPage />} />
          {/* Old /agent routes redirect to the new Inbox. */}
          <Route path="/agent" element={<Navigate to="/inbox" replace />} />
          <Route path="/agent/:ticketKey" element={<Navigate to="/inbox" replace />} />
          <Route path="/suggestions" element={<SuggestionsPage />} />
          <Route path="/agents" element={<AgentsPage />} />
          {/* Old 'Coming soon' sub-routes now land on the Agents page. */}
          <Route path="/agents/deployed" element={<Navigate to="/agents" replace />} />
          <Route path="/agents/shadow" element={<Navigate to="/agents" replace />} />
          <Route path="/agents/performance" element={<Navigate to="/agents" replace />} />
          <Route path="*" element={<Navigate to="/knowledge" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
