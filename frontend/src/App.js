import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import './App.css';
import Dashboard from './components/Dashboard';
import ChatInterface from './components/ChatInterface';
import { Menu, X, BarChart3, MessageSquare } from 'lucide-react';
import { fetchPredictions } from './store/slices/predictionsSlice';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const dispatch = useDispatch();
  const { gold, silver, loading, error } = useSelector((state) => state.predictions);
  const { messages } = useSelector((state) => state.chat);

  useEffect(() => {
    // Fetch predictions if not already loaded and no error exists
    if (!gold && !silver && !loading && !error) {
      dispatch(fetchPredictions(90));
    }
    
    // Refresh predictions every 5 minutes if no active error
    const interval = setInterval(() => {
      if (!error) {
        dispatch(fetchPredictions(90));
      }
    }, 300000);
    
    return () => clearInterval(interval);
  }, [dispatch, gold, silver, loading, error]);

  const handleRefresh = () => {
    dispatch(fetchPredictions(90));
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🏅 Gold & Silver Agent System</h1>
          <nav className="nav-tabs">
            <button
              className={`nav-tab ${activeTab === 'dashboard' ? 'active' : ''}`}
              onClick={() => setActiveTab('dashboard')}
            >
              <BarChart3 size={18} />
              Dashboard
            </button>
            <button
              className={`nav-tab ${activeTab === 'chat' ? 'active' : ''}`}
              onClick={() => setActiveTab('chat')}
            >
              <MessageSquare size={18} />
              Chat Agent
            </button>
          </nav>
        </div>
      </header>

      <main className="app-main">
        {activeTab === 'dashboard' && (
          <Dashboard 
            predictions={{ gold, silver }} 
            loading={loading} 
            error={error}
            onRefresh={handleRefresh} 
          />
        )}
        {activeTab === 'chat' && <ChatInterface />}
      </main>

      <footer className="app-footer">
        <p>⚠️ This system provides market analysis only. Not financial advice.</p>
      </footer>
    </div>
  );
}

export default App;

