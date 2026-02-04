import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import './ChatInterface.css';
import { Send, Bot, User, Loader } from 'lucide-react';
import { addMessage, updateLastMessage, setLoading } from '../store/slices/chatSlice';
import API_BASE_URL from '../config';

const ChatInterface = () => {
  const dispatch = useDispatch();
  const { messages, loading } = useSelector((state) => state.chat);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const formatMessage = (text) => {
    // Convert markdown-like formatting to HTML
    let formatted = text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/## (.*?)\n/g, '<h3>$1</h3>')
      .replace(/# (.*?)\n/g, '<h2>$1</h2>')
      .replace(/\n/g, '<br>');
    
    // Format lists
    formatted = formatted.replace(/- (.*?)(<br>|$)/g, '<li>$1</li>');
    formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    
    return formatted;
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input;
    const messageToSend = userMessage;
    
    // Add user message
    dispatch(addMessage({ role: 'user', content: userMessage }));
    
    // Add empty assistant message that we'll stream into
    dispatch(addMessage({ role: 'assistant', content: '' }));
    
    setInput('');
    dispatch(setLoading(true));

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: messageToSend, stream: true }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      // Handle streaming response
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let accumulatedContent = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.done) {
                setLoading(false);
                break;
              }
              
              if (data.content) {
                accumulatedContent += data.content;
                // Update the last message (assistant message) with accumulated content
                dispatch(updateLastMessage({ content: accumulatedContent }));
                
                // Auto-scroll as content streams
                setTimeout(scrollToBottom, 10);
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }

      dispatch(setLoading(false));
    } catch (error) {
      console.error('Error:', error);
      dispatch(updateLastMessage({ 
        content: 'Sorry, I encountered an error. Please try again or check the backend connection.' 
      }));
      dispatch(setLoading(false));
    }
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>Chat with Agent</h2>
        <p>Ask questions about gold & silver predictions, market analysis, or request specific insights</p>
      </div>

      <div className="chat-messages">
        {messages.map((msg, idx) => {
          const isLastMessage = idx === messages.length - 1;
          const isStreaming = loading && isLastMessage && msg.role === 'assistant';
          
          return (
            <div key={idx} className={`message ${msg.role}`}>
              <div className="message-avatar">
                {msg.role === 'assistant' ? (
                  <Bot size={20} />
                ) : (
                  <User size={20} />
                )}
              </div>
              <div className={`message-content ${isStreaming ? 'streaming' : ''}`}>
                {msg.content ? (
                  <>
                    <div dangerouslySetInnerHTML={{ __html: formatMessage(msg.content) }} />
                    {isStreaming && <span className="streaming-cursor">▊</span>}
                  </>
                ) : isStreaming ? (
                  <div>
                    <Loader className="typing-indicator" />
                    <span>Agent is thinking...</span>
                  </div>
                ) : null}
              </div>
            </div>
          );
        })}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSend}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about gold/silver predictions, market drivers, or request analysis..."
          className="chat-input"
          disabled={loading}
        />
        <button
          type="submit"
          className="send-button"
          disabled={loading || !input.trim()}
        >
          <Send size={18} />
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;

