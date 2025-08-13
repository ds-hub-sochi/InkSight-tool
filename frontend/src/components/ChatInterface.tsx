import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, BookOpen, Search } from 'lucide-react';
import { chatAPI } from '../lib/api';
import type { ChatResponse } from '../lib/api';

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  sources?: Array<{
    content: string;
    metadata: Record<string, any>;
    score?: number;
  }>;
  timestamp: Date;
}

interface ChatInterfaceProps {
  onSearch?: (query: string) => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ onSearch: _onSearch }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [includeSources] = useState(false);
  const [includeDocuments, setIncludeDocuments] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response: ChatResponse = await chatAPI.sendMessage({
        message: userMessage.content,
        include_sources: includeSources,
      });

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: response.response,
        sources: response.sources,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: `Error: ${error.response?.data?.detail || 'Failed to get response'}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };


  return (
    <div className="flex flex-col h-full bg-white border-0 overflow-visible">

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-gradient-to-b from-transparent to-blue-50/20">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <div className="p-4 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full w-20 h-20 mx-auto mb-6 shadow-lg">
              <Bot className="h-12 w-12 text-white" />
            </div>
            <p className="text-2xl font-bold text-gray-900 mb-3">Welcome to your AI Assistant</p>
            <p className="text-gray-600 max-w-md mx-auto leading-relaxed mb-8">
              Upload documents and ask questions to get started. I can help you find information and answer questions about your uploaded content.
            </p>
            
            {/* Example Questions */}
            <div className="max-w-4xl mx-auto">
              <p className="text-sm font-semibold text-gray-500 mb-4 uppercase tracking-wide">Попробуйте спросить:</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {[
                  "Какие главные темы раскрывает Пушкин в 'Руслане и Людмиле'?",
                  "Расскажите о персонажах 'Сказки о царе Салтане'", 
                  "Каков исторический контекст написания этих произведений?",
                  "Найдите информацию о литературных приёмах автора",
                  "Сравните стилистику разных произведений Пушкина"
                ].map((question, index) => (
                  <button
                    key={index}
                    onClick={() => setInput(question)}
                    className="p-4 bg-white border border-gray-200 rounded-xl text-left hover:border-blue-300 hover:bg-blue-50 transition-all duration-200 shadow-sm hover:shadow-md group"
                  >
                    <div className="flex items-start space-x-3">
                      <div className="p-2 bg-blue-100 rounded-lg group-hover:bg-blue-200 transition-colors">
                        <Search className="h-4 w-4 text-blue-600" />
                      </div>
                      <p className="text-gray-700 text-sm leading-relaxed">{question}</p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex max-w-[85%] ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'} items-start space-x-3`}>
              <div className={`p-2.5 rounded-full shadow-md ${message.type === 'user' ? 'bg-gradient-to-r from-blue-500 to-purple-500' : 'bg-white border-2 border-gray-100'}`}>
                {message.type === 'user' ? (
                  <User className="h-5 w-5 text-white" />
                ) : (
                  <Bot className="h-5 w-5 text-blue-600" />
                )}
              </div>
              
              <div className={`rounded-2xl p-4 shadow-sm ${message.type === 'user' ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white' : 'bg-white text-gray-900 border border-gray-100'}`}>
                <p className="whitespace-pre-wrap">{message.content}</p>
                
                {message.sources && message.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-300">
                    <p className="text-sm font-medium mb-2 flex items-center">
                      <BookOpen className="h-4 w-4 mr-1" />
                      Sources:
                    </p>
                    <div className="space-y-2">
                      {message.sources.map((source, idx) => (
                        <div key={idx} className="text-sm bg-white bg-opacity-50 p-2 rounded text-gray-800">
                          <p className="font-medium text-xs text-gray-600 mb-1">
                            {source.metadata.source || 'Document'} 
                            {source.score && ` (${(source.score * 100).toFixed(1)}% match)`}
                          </p>
                          <p className="line-clamp-2">{source.content}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                <p className="text-xs opacity-75 mt-2">
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="flex items-start space-x-2">
              <div className="p-2 bg-gray-100 rounded-full">
                <Bot className="h-4 w-4 text-gray-600" />
              </div>
              <div className="bg-gray-100 rounded-lg p-3">
                <div className="flex items-center space-x-2">
                  <Loader2 className="h-4 w-4 animate-spin text-gray-600" />
                  <p className="text-gray-600">Thinking...</p>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Tools and Input Section */}
      <div className="border-t border-gray-200 p-4 bg-white relative overflow-visible">
        <div className="flex items-center justify-between mb-4 bg-blue-50 rounded-xl p-4">
          <div className="flex items-center space-x-3">
            <BookOpen className="h-5 w-5 text-blue-600" />
            <div>
              <p className="font-medium text-blue-900">Include Documents</p>
              <p className="text-xs text-blue-600">Use uploaded docs in responses</p>
            </div>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={includeDocuments}
              onChange={(e) => setIncludeDocuments(e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-blue-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-blue-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>
        
        <div className="flex space-x-4">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question about your documents..."
            className="flex-1 resize-none border border-gray-300 rounded-2xl px-6 py-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 placeholder-gray-400"
            rows={1}
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || loading}
            className="px-6 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  );
};