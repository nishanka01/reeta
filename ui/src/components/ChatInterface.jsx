import React, { useRef, useEffect, useState } from 'react';
import useStore from '../store/useStore';
import { wsService } from '../services/websocket';
import { Send } from 'lucide-react';

const ChatInterface = () => {
  const messages = useStore((state) => state.messages);
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom on new message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputText.trim() === '') return;
    wsService.sendMessage(inputText);
    setInputText('');
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 rounded-xl overflow-hidden shadow-xl border border-gray-800">
      <div className="bg-gray-800 py-3 px-4 border-b border-gray-700 shadow-sm z-10 flex justify-between items-center">
        <h2 className="text-gray-100 font-semibold flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
          REETA Chat
        </h2>
        <span className="text-xs text-gray-400">Terminal & Voice History</span>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-900/50">
        {messages.map((msg, idx) => (
          <div 
            key={idx} 
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div 
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                msg.role === 'user' 
                  ? 'bg-blue-600 text-white rounded-br-none shadow-md' 
                  : 'bg-gray-800 text-gray-200 rounded-bl-none shadow-md border border-gray-700'
              }`}
            >
              {/* For production, integrate a Markdown renderer here */}
              <p className="whitespace-pre-wrap text-sm leading-relaxed font-medium">
                {msg.content}
              </p>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form 
        onSubmit={handleSubmit}
        className="p-3 bg-gray-800 border-t border-gray-700 flex gap-2"
      >
        <input 
          type="text" 
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Ask REETA anything..."
          className="flex-1 bg-gray-900 text-gray-100 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-shadow border border-gray-700 placeholder-gray-500"
        />
        <button 
          type="submit"
          disabled={!inputText.trim()}
          className="bg-blue-600 hover:bg-blue-500 text-white p-2.5 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center shadow-lg"
        >
          <Send size={18} className="mr-1" />
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;
