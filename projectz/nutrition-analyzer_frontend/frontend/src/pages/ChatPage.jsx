import React, { useState, useEffect, useRef } from 'react';
import { sendQuery } from '../utils/api'; // Assuming api.js is in ../utils/
import { v4 as uuidv4 } from 'uuid';
import './ChatPage.css';

export default function ChatPage() {
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const containerRef = useRef(null);
  const inputRef = useRef(null);

  // --- Load initial sessions from localStorage ---
  useEffect(() => {
    let initialSessions = [];
    let initialSessionId = null;
    try {
      const stored = localStorage.getItem('chat_sessions');
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed) && parsed.length > 0 && parsed[0].id && parsed[0].name && Array.isArray(parsed[0].messages)) {
          initialSessions = parsed;
          initialSessionId = parsed[0].id;
        }
      }
    } catch (e) {
      console.error('Failed to parse stored sessions:', e);
      localStorage.removeItem('chat_sessions');
    }
    if (initialSessions.length === 0) {
      const id = uuidv4();
      const newSession = { id, name: 'Chat 1', messages: [] };
      initialSessions = [newSession];
      initialSessionId = id;
      console.log("Initialized with new session");
    }
    setSessions(initialSessions);
    setCurrentSessionId(initialSessionId);
  }, []);

  // --- Save sessions to localStorage ---
  useEffect(() => {
    if (sessions.length > 0) {
      localStorage.setItem('chat_sessions', JSON.stringify(sessions));
    }
  }, [sessions]);

  // --- Scroll to the bottom of the chat ---
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [sessions, currentSessionId]);

  // --- Get the current session object ---
  const currentSession = sessions.find(s => s.id === currentSessionId);

  // --- Handle sending a message ---
  const handleSend = async () => {
    const query = input.trim();
    if (!query || !currentSessionId || isLoading || !currentSession) {
      console.warn("Send condition not met:", { query, currentSessionId, isLoading, currentSessionExists: !!currentSession });
      return;
    }

    // Construct chat history for the API
    const recentMessages = currentSession.messages.slice(-3);
    const historyToSend = recentMessages
      .filter(m => m.user && m.bot && m.bot !== '...')
      .map(m => `User: ${m.user}\nBot: ${m.bot}`)
      .join('\n\n');

    setIsLoading(true);

    // Add a new message optimistically with a unique ID
    const newMessageId = uuidv4();
    const newUserMessage = { id: newMessageId, user: query, bot: '...' };
    setSessions(prevSessions =>
      prevSessions.map(session =>
        session.id === currentSessionId
          ? { ...session, messages: [...session.messages, newUserMessage] }
          : session
      )
    );
    setInput('');

    try {
      const response = await sendQuery(query, historyToSend);
      const botReply = response?.response;

      if (typeof botReply !== 'string') {
        throw new Error("Received invalid response from bot.");
      }

      // Update the bot's response immutably
      setSessions(prevSessions =>
        prevSessions.map(session =>
          session.id === currentSessionId
            ? {
                ...session,
                messages: session.messages.map(m =>
                  m.id === newMessageId ? { ...m, bot: botReply } : m
                )
              }
            : session
        )
      );
      inputRef.current?.focus();
    } catch (err) {
      const errorMessage = err.message || 'Failed to get response.';
      console.error('Chat error:', err);

      // Update the message with the error immutably
      setSessions(prevSessions =>
        prevSessions.map(session =>
          session.id === currentSessionId
            ? {
                ...session,
                messages: session.messages.map(m =>
                  m.id === newMessageId ? { ...m, bot: `Error: ${errorMessage}` } : m
                )
              }
            : session
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  // --- Create a new chat session ---
  const handleNewSession = () => {
    const newId = uuidv4();
    let maxNum = 0;
    sessions.forEach(s => {
      const match = s.name.match(/^Chat (\d+)$/);
      if (match && parseInt(match[1]) > maxNum) maxNum = parseInt(match[1]);
    });
    const newName = `Chat ${maxNum + 1}`;
    const newSession = { id: newId, name: newName, messages: [] };
    setSessions(prev => [newSession, ...prev]);
    setCurrentSessionId(newId);
  };

  // --- Delete a chat session ---
  const handleDeleteSession = (idToDelete) => {
    if (!idToDelete || sessions.length <= 1) {
      alert("Cannot delete the last chat session.");
      return;
    }
    const sessionToDelete = sessions.find(s => s.id === idToDelete);
    if (!window.confirm(`Delete this chat session: "${sessionToDelete?.name || 'Unknown'}"?`)) return;

    setSessions(prev => {
      const filtered = prev.filter(s => s.id !== idToDelete);
      if (currentSessionId === idToDelete && filtered.length > 0) {
        setCurrentSessionId(filtered[0].id);
      } else if (filtered.length === 0) {
        const newId = uuidv4();
        const newSession = { id: newId, name: 'Chat 1', messages: [] };
        setCurrentSessionId(newId);
        return [newSession];
      }
      return filtered;
    });
  };

  // --- Clear messages in the current session ---
  const handleClear = () => {
    if (!currentSessionId || !currentSession) return;
    if (!window.confirm(`Clear all messages in session: "${currentSession.name}"?`)) return;
    setSessions(prev =>
      prev.map(session =>
        session.id === currentSessionId ? { ...session, messages: [] } : session
      )
    );
  };

  // --- Download chat as JSON ---
  const handleDownloadJSON = () => {
    if (!currentSession) return;
    const json = JSON.stringify(currentSession, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentSession.name.replace(/[^a-z0-9]/gi, '_')}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // --- Download chat as TXT ---
  const handleDownloadTXT = () => {
    if (!currentSession) return;
    const content = currentSession.messages.map(m => `User: ${m.user}\nBot: ${m.bot}`).join('\n\n---\n\n');
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentSession.name.replace(/[^a-z0-9]/gi, '_')}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // --- Handle session selection ---
  const handleSessionChange = (e) => {
    setCurrentSessionId(e.target.value);
  };

  return (
    <div className="chat-container">
      {/* Decorative Elements */}
      <div className="background-shape shape-1"></div>
      <div className="background-shape shape-2"></div>
      <div className="background-shape shape-3"></div>
      <div className="food-icon icon-1">🍕</div>
      <div className="food-icon icon-2">🥗</div>
      <div className="food-icon icon-3">🍰</div>

      {/* Header */}
      <div className="chat-header">
        <h1 className="chat-title">Recipe Chat Bot</h1>
        <div className="button-group">
          <button onClick={handleNewSession} className="btn btn-new">New Chat</button>
          <button
            onClick={() => handleDeleteSession(currentSessionId)}
            disabled={sessions.length <= 1}
            className="btn btn-delete"
          >
            Delete Chat
          </button>
          <button
            onClick={handleClear}
            disabled={!currentSession?.messages.length}
            className="btn btn-clear"
          >
            Clear Chat
          </button>
          <button
            onClick={handleDownloadJSON}
            disabled={!currentSession?.messages.length}
            className="btn btn-download-json"
          >
            Download JSON
          </button>
          <button
            onClick={handleDownloadTXT}
            disabled={!currentSession?.messages.length}
            className="btn btn-download-txt"
          >
            Download TXT
          </button>
        </div>
      </div>

      {/* Session Selector */}
      {sessions.length > 0 && (
        <div className="session-selector">
          <div className="select-container">
            <select
              className="session-select"
              value={currentSessionId || ''}
              onChange={handleSessionChange}
            >
              {sessions.map(s => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
          </div>
        </div>
      )}

      {/* Messages Container */}
      <div ref={containerRef} className="messages-container">
        {currentSession?.messages.map((msg) => (
          <div key={msg.id} className="message-group">
            {/* User Message */}
            {msg.user && (
              <div className="user-message-wrapper">
                <div className="message user-message">{msg.user}</div>
              </div>
            )}
            {/* Bot Message */}
            {(msg.bot && msg.bot !== '...') || msg.bot?.startsWith('Error:') ? (
              <div className="bot-message-wrapper">
                <div className={`message ${msg.bot?.startsWith('Error:') ? 'error-message' : 'bot-message'}`}>
                  {msg.bot.split('\n').map((line, i) => (
                    <React.Fragment key={i}>
                      {line}
                      {i < msg.bot.split('\n').length - 1 && <br />}
                    </React.Fragment>
                  ))}
                </div>
              </div>
            ) : null}
          </div>
        ))}
        {/* Loading Indicator */}
        {isLoading && currentSession?.messages[currentSession.messages.length - 1]?.bot === '...' && (
          <div className="bot-message-wrapper">
            <div className="message typing-indicator">Typing...</div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="input-area">
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={isLoading ? "Waiting for response..." : "Type your question..."}
          className="chat-input"
          onKeyDown={(e) => { if (e.key === 'Enter' && !isLoading) handleSend(); }}
          disabled={isLoading || !currentSessionId}
        />
        <button
          onClick={handleSend}
          disabled={isLoading || !input.trim() || !currentSessionId}
          className="btn btn-send"
        >
          {isLoading ? (
            <svg className="loading-spinner" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          ) : (
            'Send'
          )}
        </button>
      </div>
    </div>
  );
}