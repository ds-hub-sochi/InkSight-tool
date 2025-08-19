import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, BookOpen, Sparkles, X } from 'lucide-react';
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
  appliedDocs?: {
    library: number[];
    uploaded: string[];
  };
  libraryDocs?: Array<{
    title: string;
    description: string;
    imagePath: string;
    size: number[];
    lines: number;
    characters: number;
    type: string;
    color: string;
  }>;
  onRemoveFromContext?: (type: 'library' | 'uploaded', identifier: number | string) => void;
  ocrData?: any;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  onSearch: _onSearch,
  appliedDocs,
  libraryDocs,
  onRemoveFromContext,
  ocrData
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [includeSources] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);


  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const extractContextFromSelectedImages = () => {
    if (!appliedDocs || !ocrData || appliedDocs.library.length === 0) {
      return '';
    }

    const extractedTexts: string[] = [];

    appliedDocs.library.forEach((docIndex) => {
      const doc = libraryDocs?.[docIndex];
      if (doc) {
        const imageFile = ocrData.files.find((file: any) =>
          file.image_path === doc.imagePath.replace('/ocr_data/', '')
        );
        if (imageFile) {
          const allText = imageFile.lines.map((line: any) => line.text).join(' ');
          if (allText.trim()) {
            extractedTexts.push(`${doc.title}: ${allText.trim()}`);
          }
        }
      }
    });

    if (extractedTexts.length > 0) {
      return `\n\nAdditional context from selected documents:\n${extractedTexts.join('\n\n')}`;
    }

    return '';
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const originalInput = input.trim();
    const contextFromImages = extractContextFromSelectedImages();
    const messageWithContext = originalInput + contextFromImages;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: originalInput, // Show only original message to user
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response: ChatResponse = await chatAPI.sendMessage({
        message: messageWithContext, // Send message with context to backend
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

  const suggestedQuestions = [
    "Can you identify any historical events or figures mentioned in these manuscripts?",
    "What literary or poetic elements can be found in these ancient writings?",
    "Can you identify any references to trade routes, cities, or geographical locations?"
  ];

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto bg-white border-l border-r border-gray-200">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="space-y-6">
          {/* Applied Documents Context - Always show when available */}
          {appliedDocs && (appliedDocs.library.length > 0 || appliedDocs.uploaded.length > 0) && (
            <div className="mb-6">
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <BookOpen className="w-4 h-4 text-blue-600" />
                </div>
                <div className="bg-blue-50 border border-blue-200 rounded-2xl px-4 py-3 flex-1">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-sm font-medium text-blue-800">
                      Context Documents ({appliedDocs.library.length + appliedDocs.uploaded.length})
                    </h3>
                    <span className="text-xs text-blue-600">OCR text will be included with questions</span>
                  </div>

                  <div className="space-y-2">
                    {/* Library Documents */}
                    {appliedDocs.library.map((docIndex) => {
                      const doc = libraryDocs?.[docIndex];
                      if (!doc) return null;
                      return (
                        <div
                          key={`library-${docIndex}`}
                          className="flex items-center justify-between bg-white px-3 py-2 rounded-lg border border-blue-200"
                        >
                          <div className="flex items-center space-x-3">
                            <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${
                              doc.color === 'blue' ? 'from-blue-500 to-blue-600' :
                              doc.color === 'purple' ? 'from-purple-500 to-purple-600' :
                              doc.color === 'green' ? 'from-green-500 to-green-600' :
                              'from-orange-500 to-orange-600'
                            }`}></div>
                            <div>
                              <p className="text-sm font-medium text-gray-800">{doc.title}</p>
                              <p className="text-xs text-gray-500">{doc.lines} lines • {doc.characters} chars • {doc.type}</p>
                            </div>
                          </div>
                          {onRemoveFromContext && (
                            <button
                              onClick={() => onRemoveFromContext('library', docIndex)}
                              className="text-gray-400 hover:text-red-500 transition-colors p-1"
                            >
                              <X className="w-5 h-5" />
                            </button>
                          )}
                        </div>
                      );
                    })}

                    {/* Uploaded Documents */}
                    {appliedDocs.uploaded.map((filename) => (
                      <div
                        key={`uploaded-${filename}`}
                        className="flex items-center justify-between bg-white px-3 py-2 rounded-lg border border-green-200"
                      >
                        <div className="flex items-center space-x-3">
                          <div className="w-3 h-3 rounded-full bg-gradient-to-r from-green-500 to-green-600"></div>
                          <div>
                            <p className="text-sm font-medium text-gray-800">{filename}</p>
                            <p className="text-xs text-gray-500">Uploaded document</p>
                          </div>
                        </div>
                        {onRemoveFromContext && (
                          <button
                            onClick={() => onRemoveFromContext('uploaded', filename)}
                            className="text-gray-400 hover:text-red-500 transition-colors p-1"
                          >
                            <X className="w-5 h-5" />
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {messages.length === 0 ? (
            <div className="text-center py-12">
              {/* Welcome Header */}
              <div className="mb-8">
                <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-r from-blue-600 to-green-600 rounded-2xl flex items-center justify-center">
                  <Sparkles className="w-8 h-8 text-white" />
                </div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome to INKSight</h1>
                <p className="text-gray-600 text-lg">Ask me anything about your documents</p>
              </div>

              {/* Suggested Questions */}
              <div className="max-w-2xl mx-auto">
                <p className="text-sm font-medium text-gray-500 mb-4">Try asking:</p>
                <div className="grid gap-3">
                  {suggestedQuestions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => setInput(question)}
                      className="p-4 text-left bg-white border border-gray-200 rounded-xl hover:border-green-300 hover:bg-green-50 transition-all duration-200 group"
                    >
                      <div className="flex items-center space-x-3">
                        <div className="w-2 h-2 bg-green-500 rounded-full opacity-60 group-hover:opacity-100 transition-opacity"></div>
                        <span className="text-gray-700 group-hover:text-green-700">{question}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message, index) => (
                <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`flex items-start space-x-3 max-w-[80%] ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                    {/* Avatar */}
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                      message.type === 'user'
                        ? 'bg-gradient-to-r from-blue-600 to-green-600'
                        : 'bg-gray-100'
                    }`}>
                      {message.type === 'user' ? (
                        <User className="w-4 h-4 text-white" />
                      ) : (
                        <Bot className="w-4 h-4 text-gray-600" />
                      )}
                    </div>

                    {/* Message Content */}
                    <div className={`rounded-2xl px-4 py-3 ${
                      message.type === 'user'
                        ? 'bg-gradient-to-r from-blue-600 to-green-600 text-white'
                        : 'bg-gray-50 text-gray-900 border border-gray-200'
                    }`}>
                      <div className="prose prose-sm max-w-none">
                        <p className="whitespace-pre-wrap m-0 leading-relaxed">{message.content}</p>
                      </div>

                      {/* Sources */}
                      {message.sources && message.sources.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-gray-200">
                          <div className="flex items-center space-x-1 mb-2">
                            <BookOpen className="w-3 h-3 text-gray-500" />
                            <span className="text-xs font-medium text-gray-500">Sources</span>
                          </div>
                          <div className="space-y-2">
                            {message.sources.slice(0, 3).map((source, idx) => (
                              <div key={idx} className="text-xs bg-white bg-opacity-70 border border-gray-200 rounded-lg p-2">
                                <p className="font-medium text-gray-600 mb-1">
                                  {source.metadata.source || 'Document'}
                                </p>
                                <p className="text-gray-700 line-clamp-2 leading-relaxed">
                                  {source.content}
                                </p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="mt-2">
                        <span className={`text-xs ${message.type === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              {/* Loading Indicator */}
              {loading && (
                <div className="flex justify-start">
                  <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                      <Bot className="w-4 h-4 text-gray-600" />
                    </div>
                    <div className="bg-gray-50 border border-gray-200 rounded-2xl px-4 py-3">
                      <div className="flex items-center space-x-2">
                        <Loader2 className="w-4 h-4 animate-spin text-gray-500" />
                        <span className="text-gray-600 text-sm">Thinking...</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 p-4 bg-white">
        <div className="flex items-end space-x-3">
            <div className="flex-1 relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Ask about your documents..."
                className="w-full resize-none rounded-2xl border border-gray-300 bg-white px-4 py-3 pr-12 text-sm placeholder-gray-500 focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500 transition-colors"
                rows={1}
                style={{
                  minHeight: '44px',
                  maxHeight: '120px',
                  overflowY: input.split('\n').length > 3 ? 'scroll' : 'hidden'
                }}
                disabled={loading}
              />
            </div>
            <button
              onClick={sendMessage}
              disabled={!input.trim() || loading}
              className={`flex items-center justify-center w-11 h-11 rounded-2xl transition-all duration-200 ${
                input.trim() && !loading
                  ? 'bg-gradient-to-r from-blue-600 to-green-600 hover:from-blue-700 hover:to-green-700 text-white shadow-sm hover:shadow-md'
                  : 'bg-gray-100 text-gray-400 cursor-not-allowed'
              }`}
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
    </div>
  );
};