import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Upload, MessageSquare, BookOpen, Bot, Settings } from 'lucide-react';
import { ChatInterface } from './components/ChatInterface';
import { FileUpload } from './components/FileUpload';
import type { UploadDocumentResponse } from './lib/api';

const queryClient = new QueryClient();

type Tab = 'chat' | 'upload' | 'library' | 'context';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('chat');
  const [uploadSuccess, setUploadSuccess] = useState<UploadDocumentResponse | null>(null);
  const [selectedDocs, setSelectedDocs] = useState<number[]>([0, 2]); // Initially select docs at index 0 and 2
  const [contextDocs, setContextDocs] = useState<number[]>([0, 2]); // Documents selected for context
  const [uploadedDocs, setUploadedDocs] = useState<UploadDocumentResponse[]>([]); // Track uploaded documents
  const [uploadedDocsInContext, setUploadedDocsInContext] = useState<string[]>([]); // Track which uploaded docs are in context

  const handleUploadComplete = (response: UploadDocumentResponse) => {
    setUploadSuccess(response);
    setUploadedDocs(prev => [...prev, response]);
    setUploadedDocsInContext(prev => [...prev, response.filename]); // Auto-include in context
    // Auto-switch to chat after successful upload
    setTimeout(() => {
      setActiveTab('chat');
    }, 2000);
  };

  const tabs = [
    { id: 'chat' as Tab, label: 'Chat', icon: MessageSquare },
    { id: 'upload' as Tab, label: 'Upload', icon: Upload },
    { id: 'library' as Tab, label: 'Library', icon: BookOpen },
    { id: 'context' as Tab, label: 'Context', icon: Settings },
  ];

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200">
        <div className="flex justify-center">
          <div className="w-full max-w-6xl bg-gradient-to-br from-gray-50 to-blue-50 min-h-screen shadow-2xl rounded-2xl overflow-visible">
            {/* Header */}
            <header className="bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg">
              <div className="px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                  {/* App Name - Left */}
                  <div className="flex items-center space-x-3">
                    <div className="p-3 bg-white bg-opacity-20 rounded-xl backdrop-blur-sm">
                      <Bot className="h-7 w-7 text-white" />
                    </div>
                    <div>
                      <h1 className="text-2xl font-bold text-white">Agentic RAG</h1>
                      <p className="text-blue-100">AI-powered document assistant</p>
                    </div>
                  </div>
                  
                  {/* Tab Navigation - Center */}
                  <div className="flex-1 flex justify-center">
                    <nav className="flex bg-white bg-opacity-20 backdrop-blur-sm p-1.5 rounded-2xl shadow-lg">
                      {tabs.map((tab) => {
                        const Icon = tab.icon;
                        return (
                          <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`
                              flex items-center space-x-3 px-6 py-3 rounded-xl font-medium text-sm transition-all duration-300
                              ${activeTab === tab.id
                                ? 'bg-white text-blue-600 shadow-lg'
                                : 'text-white hover:bg-white hover:bg-opacity-20'
                              }
                            `}
                          >
                            <Icon className="h-5 w-5" />
                            <span className="font-semibold">{tab.label}</span>
                          </button>
                        );
                      })}
                    </nav>
                  </div>
                  
                  {/* Right side spacer for balance */}
                  <div className="w-48"></div>
                </div>
              </div>
            </header>

            <div className="px-4 sm:px-6 lg:px-8 py-8 overflow-visible">
              <div className="w-full overflow-visible">
                {/* Main Content */}
                <div className="w-full overflow-visible">

                  {/* Tab Content */}
                  <div className="bg-white rounded-xl shadow-lg border-0 min-h-[800px] overflow-visible relative">
                    {activeTab === 'chat' && (
                      <div className="h-[750px] overflow-visible">
                        <ChatInterface />
                      </div>
                    )}

                    {activeTab === 'upload' && (
                      <div className="p-12 min-h-[750px] flex items-center">
                        <div className="max-w-3xl mx-auto w-full">
                          <div className="text-center mb-12">
                            <div className="p-4 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full w-20 h-20 mx-auto mb-6 shadow-lg">
                              <Upload className="h-12 w-12 text-white" />
                            </div>
                            <h2 className="text-4xl font-bold text-gray-900 mb-4">
                              Upload Documents
                            </h2>
                            <p className="text-xl text-gray-600 leading-relaxed max-w-2xl mx-auto">
                              Upload TXT or PDF files to add them to your knowledge base. 
                              The AI assistant can then answer questions about the uploaded content.
                            </p>
                          </div>
                          
                          <FileUpload onUploadComplete={handleUploadComplete} />
                          
                          {uploadSuccess && (
                            <div className="mt-8 p-6 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-2xl shadow-lg">
                              <p className="text-blue-800 text-center text-lg font-semibold">
                                ✨ Document uploaded successfully! Switching to chat...
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {activeTab === 'library' && (
                      <div className="p-12 min-h-[750px]">
                        <div className="max-w-4xl mx-auto w-full">
                          <div className="text-center mb-12">
                            <div className="p-4 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full w-20 h-20 mx-auto mb-6 shadow-lg">
                              <BookOpen className="h-12 w-12 text-white" />
                            </div>
                            <h2 className="text-4xl font-bold text-gray-900 mb-4">
                              Document Library
                            </h2>
                            <p className="text-xl text-gray-600 leading-relaxed max-w-2xl mx-auto">
                              Browse and select from pre-uploaded documents to include in your chat context.
                            </p>
                          </div>
                          
                          {/* Demo Documents */}
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {[
                              {
                                title: "Technical Documentation",
                                description: "API specifications and technical requirements",
                                pages: 42,
                                type: "PDF"
                              },
                              {
                                title: "Project Requirements",
                                description: "Business requirements and user stories",
                                pages: 28,
                                type: "TXT"
                              },
                              {
                                title: "Research Papers",
                                description: "Academic papers and research findings",
                                pages: 156,
                                type: "PDF"
                              },
                              {
                                title: "Meeting Notes",
                                description: "Team meetings and decision records",
                                pages: 15,
                                type: "TXT"
                              }
                            ].map((doc, index) => {
                              const isSelected = selectedDocs.includes(index);
                              return (
                                <div 
                                  key={index} 
                                  onClick={() => {
                                    if (isSelected) {
                                      setSelectedDocs(selectedDocs.filter(i => i !== index));
                                    } else {
                                      setSelectedDocs([...selectedDocs, index]);
                                    }
                                  }}
                                  className={`p-6 rounded-2xl border-2 transition-all duration-200 cursor-pointer ${
                                    isSelected 
                                      ? 'border-blue-300 bg-blue-50 shadow-lg' 
                                      : 'border-gray-200 bg-white hover:border-blue-200 hover:bg-blue-50 hover:shadow-md'
                                  }`}
                                >
                                  <div className="flex items-start justify-between mb-4">
                                    <div className="flex items-center space-x-3">
                                      <div className={`p-2 rounded-lg ${
                                        doc.type === 'PDF' ? 'bg-red-100' : 'bg-blue-100'
                                      }`}>
                                        <BookOpen className={`h-5 w-5 ${
                                          doc.type === 'PDF' ? 'text-red-600' : 'text-blue-600'
                                        }`} />
                                      </div>
                                      <div>
                                        <h3 className="font-bold text-gray-900">{doc.title}</h3>
                                        <p className="text-sm text-gray-600">{doc.description}</p>
                                      </div>
                                    </div>
                                    <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                                      isSelected 
                                        ? 'border-blue-500 bg-blue-500' 
                                        : 'border-gray-300'
                                    }`}>
                                      {isSelected && (
                                        <div className="w-2 h-2 bg-white rounded-full"></div>
                                      )}
                                    </div>
                                  </div>
                                  <div className="flex items-center justify-between text-sm text-gray-500">
                                    <span>{doc.pages} pages</span>
                                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                      doc.type === 'PDF' 
                                        ? 'bg-red-100 text-red-700' 
                                        : 'bg-blue-100 text-blue-700'
                                    }`}>
                                      {doc.type}
                                    </span>
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                          
                          <div className="mt-8 text-center">
                            <button className="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 font-semibold">
                              Update Context ({selectedDocs.length} documents selected)
                            </button>
                          </div>
                        </div>
                      </div>
                    )}

                    {activeTab === 'context' && (
                      <div className="p-12 min-h-[750px]">
                        <div className="max-w-4xl mx-auto w-full">
                          <div className="text-center mb-12">
                            <div className="p-4 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full w-20 h-20 mx-auto mb-6 shadow-lg">
                              <Settings className="h-12 w-12 text-white" />
                            </div>
                            <h2 className="text-4xl font-bold text-gray-900 mb-4">
                              Context Management
                            </h2>
                            <p className="text-xl text-gray-600 leading-relaxed max-w-2xl mx-auto">
                              Select which documents should be included as context for AI responses.
                            </p>
                          </div>
                          
                          {/* Context Documents */}
                          <div className="space-y-6">
                            <div className="bg-white rounded-2xl p-6 shadow-md border border-gray-200">
                              <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
                                <BookOpen className="h-6 w-6 text-blue-600" />
                                <span>Selected Library Documents</span>
                              </h3>
                              <div className="grid grid-cols-1 gap-4">
                                {[
                                  {
                                    title: "Technical Documentation",
                                    description: "API specifications and technical requirements",
                                    pages: 42,
                                    type: "PDF"
                                  },
                                  {
                                    title: "Project Requirements",
                                    description: "Business requirements and user stories",
                                    pages: 28,
                                    type: "TXT"
                                  },
                                  {
                                    title: "Research Papers",
                                    description: "Academic papers and research findings",
                                    pages: 156,
                                    type: "PDF"
                                  },
                                  {
                                    title: "Meeting Notes",
                                    description: "Team meetings and decision records",
                                    pages: 15,
                                    type: "TXT"
                                  }
                                ].filter((_, index) => selectedDocs.includes(index)).map((doc, index) => {
                                  const originalIndex = selectedDocs[index];
                                  const isInContext = contextDocs.includes(originalIndex);
                                  return (
                                    <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                                      <div className="flex items-center space-x-4">
                                        <div className={`p-2 rounded-lg ${
                                          doc.type === 'PDF' ? 'bg-red-100' : 'bg-blue-100'
                                        }`}>
                                          <BookOpen className={`h-5 w-5 ${
                                            doc.type === 'PDF' ? 'text-red-600' : 'text-blue-600'
                                          }`} />
                                        </div>
                                        <div className="flex-1">
                                          <h4 className="font-semibold text-gray-900">{doc.title}</h4>
                                          <p className="text-sm text-gray-600">{doc.description}</p>
                                          <div className="flex items-center space-x-4 mt-1 text-xs text-gray-500">
                                            <span>{doc.pages} pages</span>
                                            <span className={`px-2 py-1 rounded-full font-medium ${
                                              doc.type === 'PDF' 
                                                ? 'bg-red-100 text-red-700' 
                                                : 'bg-blue-100 text-blue-700'
                                            }`}>
                                              {doc.type}
                                            </span>
                                          </div>
                                        </div>
                                      </div>
                                      <button
                                        onClick={() => {
                                          if (isInContext) {
                                            setContextDocs(contextDocs.filter(i => i !== originalIndex));
                                          } else {
                                            setContextDocs([...contextDocs, originalIndex]);
                                          }
                                        }}
                                        className={`px-6 py-2 rounded-lg font-medium transition-all duration-200 ${
                                          isInContext
                                            ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-md'
                                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                        }`}
                                      >
                                        {isInContext ? 'Remove' : 'Include'}
                                      </button>
                                    </div>
                                  );
                                })}
                                {selectedDocs.length === 0 && (
                                  <div className="text-center py-8 text-gray-500">
                                    <BookOpen className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                                    <p>No documents selected from library</p>
                                    <p className="text-sm">Go to Library tab to select documents</p>
                                  </div>
                                )}
                              </div>
                            </div>
                            
                            <div className="bg-white rounded-2xl p-6 shadow-md border border-gray-200">
                              <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
                                <Upload className="h-6 w-6 text-green-600" />
                                <span>Uploaded Documents</span>
                              </h3>
                              <div className="grid grid-cols-1 gap-4">
                                {uploadedDocs.map((doc, index) => {
                                  const isInContext = uploadedDocsInContext.includes(doc.filename);
                                  const fileExtension = doc.filename.split('.').pop()?.toUpperCase() || 'FILE';
                                  const estimatedPages = Math.max(1, Math.floor(doc.file_size_bytes / 2000)); // Rough estimate
                                  
                                  return (
                                    <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                                      <div className="flex items-center space-x-4">
                                        <div className="p-2 rounded-lg bg-green-100">
                                          <BookOpen className="h-5 w-5 text-green-600" />
                                        </div>
                                        <div className="flex-1">
                                          <h4 className="font-semibold text-gray-900">{doc.filename}</h4>
                                          <p className="text-sm text-gray-600">User uploaded document</p>
                                          <div className="flex items-center space-x-4 mt-1 text-xs text-gray-500">
                                            <span>{estimatedPages} pages</span>
                                            <span className={`px-2 py-1 rounded-full font-medium ${
                                              fileExtension === 'PDF' 
                                                ? 'bg-red-100 text-red-700' 
                                                : 'bg-green-100 text-green-700'
                                            }`}>
                                              {fileExtension}
                                            </span>
                                            <span className="text-blue-600">📅 {new Date().toLocaleDateString()}</span>
                                          </div>
                                        </div>
                                      </div>
                                      <button
                                        onClick={() => {
                                          if (isInContext) {
                                            setUploadedDocsInContext(prev => prev.filter(name => name !== doc.filename));
                                          } else {
                                            setUploadedDocsInContext(prev => [...prev, doc.filename]);
                                          }
                                        }}
                                        className={`px-6 py-2 rounded-lg font-medium transition-all duration-200 ${
                                          isInContext
                                            ? 'bg-green-600 text-white hover:bg-green-700 shadow-md'
                                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                        }`}
                                      >
                                        {isInContext ? 'Remove' : 'Include'}
                                      </button>
                                    </div>
                                  );
                                })}
                                
                                {uploadedDocs.length === 0 && (
                                  <div className="text-center py-8 text-gray-500">
                                    <Upload className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                                    <p>No documents uploaded yet</p>
                                    <p className="text-sm">Upload documents in the Upload tab</p>
                                  </div>
                                )}
                              </div>
                            </div>
                            
                            <div className="text-center pt-6">
                              <div className="inline-flex items-center space-x-2 px-6 py-3 bg-blue-100 text-blue-800 rounded-xl">
                                <Settings className="h-5 w-5" />
                                <span className="font-medium">
                                  {contextDocs.length + uploadedDocsInContext.length} document{(contextDocs.length + uploadedDocsInContext.length) !== 1 ? 's' : ''} selected for context
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Footer */}
            <footer className="bg-white bg-opacity-50 backdrop-blur-sm border-t border-gray-200 mt-16">
              <div className="px-4 sm:px-6 lg:px-8 py-6">
                <div className="text-center text-sm text-gray-600">
                  <p className="font-medium">Powered by LangChain, OpenRouter & FastAPI</p>
                </div>
              </div>
            </footer>
          </div>
        </div>
      </div>
    </QueryClientProvider>
  );
}

export default App;