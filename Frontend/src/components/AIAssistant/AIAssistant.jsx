import { useState, useRef, useEffect } from 'react';
import Sidebar from '../Sidebar/Sidebar';
import TopBar from '../TopBar/TopBar';
import {
  startSession,
  sendMessage,
  approveAction,
  getHistory,
  refreshSchema,
} from '../../api/chatbotApi';
import './AIAssistant.css';

function AIAssistant() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [thinkingPreview, setThinkingPreview] = useState('');
  const [pendingAction, setPendingAction] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [error, setError] = useState('');
  const [schemaStatus, setSchemaStatus] = useState('');
  const [schemaRefreshing, setSchemaRefreshing] = useState(false);
  const bottomRef = useRef(null);

    const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const toggleSidebar = () => {
    setIsSidebarOpen(prev => !prev);
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, thinkingPreview, pendingAction]);

  useEffect(() => {
    const restore = async () => {
      const stored = localStorage.getItem('chatSessionId');
      if (!stored) return;
      setSessionId(stored);
      try {
        console.log('[chat] loading history', { sessionId: stored });
        const history = await getHistory(stored);
        console.log('[chat] history response', history);
        const mapped = history.messages.map((msg, index) => ({
          id: `history-${index}`,
          role: msg.role,
          text: msg.content,
          time: new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }));
        setMessages(mapped);
      } catch (err) {
        console.error(err);
      }
    };

    restore();
  }, []);

  useEffect(() => {
    if (sessionId) {
      localStorage.setItem('chatSessionId', sessionId);
    }
  }, [sessionId]);

  const ensureSession = async () => {
    if (sessionId) return sessionId;
    console.log('[chat] starting new session');
    const started = await startSession();
    console.log('[chat] session created', started);
    setSessionId(started.session_id);
    return started.session_id;
  };

  const handleSend = async () => {
    const text = input.trim();
    if (!text) return;

    const userMsg = {
      id: Date.now(),
      role: 'user',
      text,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);
    setError('');

    try {
      const activeSession = await ensureSession();
      console.log('[chat] sending message', { sessionId: activeSession, message: text });
      const response = await sendMessage({ sessionId: activeSession, message: text });
      console.log('[chat] message response', response);

      setThinkingPreview(response.thinking_preview || '');

      if (response.pending_action) {
        console.log('[chat] pending action received', response.pending_action);
        setPendingAction(response.pending_action);
      } else if (response.assistant_message) {
        console.log('[chat] assistant message received');
        const aiMsg = {
          id: Date.now() + 1,
          role: 'ai',
          text: response.assistant_message,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };
        setMessages((prev) => [...prev, aiMsg]);
        setThinkingPreview('');
      }
    } catch (err) {
      console.error(err);
      setError('Unable to reach the chatbot service.');
    } finally {
      setLoading(false);
    }
  };

  const handleDecision = async (decision) => {
    if (!pendingAction) return;
    setLoading(true);
    setError('');

    try {
      console.log('[chat] decision submit', { actionId: pendingAction.id, decision });
      const response = await approveAction({
        actionId: pendingAction.id,
        decision,
      });
      console.log('[chat] decision response', response);
      const aiMsg = {
        id: Date.now() + 2,
        role: 'ai',
        text: response.assistant_message || 'No response returned.',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, aiMsg]);
      setThinkingPreview('');
      setPendingAction(null);
    } catch (err) {
      console.error(err);
      setError('Approval request failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    setThinkingPreview('');
    setPendingAction(null);
    setError('');
    setSchemaStatus('');
    localStorage.removeItem('chatSessionId');
    setSessionId(null);
  };

  const handleRefreshSchema = async () => {
    setSchemaRefreshing(true);
    setSchemaStatus('Refreshing schema...');
    setError('');

    try {
      const response = await refreshSchema();
      const count = response?.table_count ?? 0;
      setSchemaStatus(`Schema refreshed. Tables: ${count}.`);
    } catch (err) {
      console.error(err);
      setSchemaStatus('');
      setError('Schema refresh failed.');
    } finally {
      setSchemaRefreshing(false);
    }
  };

  return (
    <div className="app-layout">
      <Sidebar isOpen={isSidebarOpen} />
      <div className={`app-content ${isSidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
        <TopBar toggleSidebar={toggleSidebar} />
        <main className="ai-main">
          <div className="ai-chat-wrapper">
            {/* Chat Header */}
            <div className="ai-chat-header">
              <div className="ai-header-left">
                <div className="ai-bot-avatar">🤖</div>
                <div>
                  <h3 className="ai-title">AI Recruitment Assistant</h3>
                  <p className="ai-subtitle">Ask me anything about candidates.</p>
                </div>
              </div>
              <div className="ai-header-actions">
                <button
                  className="btn-refresh-schema"
                  onClick={handleRefreshSchema}
                  disabled={schemaRefreshing}
                >
                  {schemaRefreshing ? 'Refreshing...' : 'Refresh Schema'}
                </button>
                <button className="btn-clear-chat" onClick={handleClearChat}>
                  Clear Chat
                </button>
              </div>
            </div>

            {/* Messages */}
            <div className="ai-messages">
              {messages.map((msg) => (
                <div key={msg.id} className={`message-row ${msg.role}`}>
                  {msg.role === 'ai' && (
                    <div className="ai-msg-avatar">🤖</div>
                  )}
                  <div className={`message-bubble ${msg.role}`}>
                    <>
                      <p className="msg-text">{msg.text}</p>
                      <span className="msg-time">{msg.time}</span>
                    </>
                  </div>
                </div>
              ))}

              {thinkingPreview && (
                <div className="message-row ai">
                  <div className="ai-msg-avatar">🤖</div>
                  <div className="message-bubble ai thinking">
                    <p className="msg-text">{thinkingPreview}</p>
                    <span className="msg-time">processing</span>
                  </div>
                </div>
              )}

              {loading && (
                <div className="message-row ai">
                  <div className="ai-msg-avatar">🤖</div>
                  <div className="message-bubble ai typing-indicator">
                    <span></span><span></span><span></span>
                  </div>
                </div>
              )}

              <div ref={bottomRef} />
            </div>

            {pendingAction && (
              <div className="approval-card">
                <div className="approval-title">Approval required</div>
                <div className="approval-subtitle">SQL query</div>
                <pre className="approval-sql">
                  {pendingAction.tool_args?.query || 'No query provided'}
                </pre>
                <div className="approval-actions">
                  <button
                    className="approval-btn approve"
                    onClick={() => handleDecision('approve')}
                    disabled={loading}
                  >
                    Approve
                  </button>
                  <button
                    className="approval-btn deny"
                    onClick={() => handleDecision('deny')}
                    disabled={loading}
                  >
                    Deny
                  </button>
                </div>
              </div>
            )}

            {error && (
              <div className="approval-error">{error}</div>
            )}

            {schemaStatus && !error && (
              <div className="schema-status">{schemaStatus}</div>
            )}

            {/* Input Area */}
            <div className="ai-input-area">
              <div className="ai-input-row">
                <input
                  type="text"
                  className="ai-input"
                  placeholder="Type your question..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                />
                <button className="btn-send" onClick={handleSend}>
                  ➤ Send
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default AIAssistant;
