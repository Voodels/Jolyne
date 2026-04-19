import { useState, useRef, useEffect } from 'react';
import Sidebar from '../Sidebar/Sidebar';
import TopBar from '../TopBar/TopBar';
import './AIAssistant.css';

const initialMessages = [
  {
    id: 1,
    role: 'user',
    text: 'Why is Amit Sharma recommended?',
    time: '10:33 AM',
  },
  {
    id: 2,
    role: 'ai',
    time: '10:33 AM',
    text: null,
    candidates: [
      { name: 'Purvi Sharma', skills: 'Java, Spring Boot, SQL, JavaMicroservices, HSQL' },
      { name: 'Aman Patel', skills: 'Betbeen felt, Tintap Spbt, Scringp' },
      { name: 'Rohan Gupta', skills: 'Full Stack Candidates, TrandStat SQL' },
      { name: 'Sakshi Verma', skills: 'Djl19 exporttien, satie, Sutgr, Sorting Bpp' },
      { name: 'Vikram Singh', skills: 'DevOps Engineer, Selected, MVS' },
    ],
    jobRole: 'Java Developer',
  },
];

function AIAssistant() {
  const [messages, setMessages] = useState(initialMessages);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

    const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const toggleSidebar = () => {
    setIsSidebarOpen(prev => !prev);
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
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

    setTimeout(() => {
      const aiMsg = {
        id: Date.now() + 1,
        role: 'ai',
        text: `I'm analyzing your query about "${text}". Based on the current candidate pipeline, here are my insights. Would you like me to filter candidates by specific skills or stages?`,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, aiMsg]);
      setLoading(false);
    }, 1200);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClearChat = () => {
    setMessages([]);
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
                  <p className="ai-subtitle">Ask me anything about your Java expereinlast.</p>
                </div>
              </div>
              <button className="btn-clear-chat" onClick={handleClearChat}>
                🗑 Clear Chat
              </button>
            </div>

            {/* Messages */}
            <div className="ai-messages">
              {messages.map((msg) => (
                <div key={msg.id} className={`message-row ${msg.role}`}>
                  {msg.role === 'ai' && (
                    <div className="ai-msg-avatar">🤖</div>
                  )}
                  <div className={`message-bubble ${msg.role}`}>
                    {msg.role === 'user' ? (
                      <>
                        <p className="msg-text">{msg.text}</p>
                        <span className="msg-time">{msg.time}</span>
                      </>
                    ) : (
                      <>
                        {msg.candidates ? (
                          <div>
                            <p className="ai-intro">
                              Here are the <strong>Top 5 candidates</strong> for{' '}
                              <strong>{msg.jobRole}</strong> role:
                            </p>
                            <ul className="candidate-list">
                              {msg.candidates.map((c, i) => (
                                <li key={i}>
                                  <span className="cand-name">{c.name}</span>
                                  {' – '}
                                  <span className="cand-skills">{c.skills}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        ) : (
                          <p className="msg-text">{msg.text}</p>
                        )}
                        <span className="msg-time">{msg.time}</span>
                      </>
                    )}
                  </div>
                </div>
              ))}

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

            {/* Input Area */}
            <div className="ai-input-area">
              <div className="ai-input-box-top">
                <input
                  type="text"
                  className="ai-input-top"
                  placeholder="Type your question..."
                  value=""
                  readOnly
                />
              </div>
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
