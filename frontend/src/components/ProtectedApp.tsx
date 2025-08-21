import { useState, useEffect, useRef } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Upload, MessageSquare, BookOpen, User, LogOut, Menu, X, Image as ImageIcon } from 'lucide-react';
import { ChatInterface } from './ChatInterface';
import { FileUpload } from './FileUpload';
import { useAuth } from './AuthProvider';
import type { UploadDocumentResponse } from '../lib/api';

const queryClient = new QueryClient();

type Tab = 'chat' | 'upload' | 'library';

export const ProtectedApp = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState<Tab>('chat');
  const [uploadSuccess, setUploadSuccess] = useState<UploadDocumentResponse | null>(null);
  const [selectedDocs, setSelectedDocs] = useState<number[]>([]);
  const [uploadedDocs, setUploadedDocs] = useState<UploadDocumentResponse[]>([]);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [appliedDocs, setAppliedDocs] = useState<{library: number[], uploaded: string[]}>({library: [], uploaded: []});
  const [modalImage, setModalImage] = useState<{index: number, doc: any} | null>(null);
  const [ocrData, setOcrData] = useState<any>(null);
  const [showTextBoxes, setShowTextBoxes] = useState(false);
  const [extractedText, setExtractedText] = useState<string | null>(null);
  const [textBoxes, setTextBoxes] = useState<Array<{x: number, y: number, width: number, height: number, text: string}>>([]);
  const imageRef = useRef<HTMLImageElement>(null);

  const handleUploadComplete = (response: UploadDocumentResponse) => {
    setUploadSuccess(response);
    setUploadedDocs(prev => [...prev, response]);
    setTimeout(() => {
      setActiveTab('chat');
    }, 2000);
  };

  const libraryDocs = [
    {
      title: "Page 7",
      description: "Ancient manuscript page from historical document",
      imagePath: "/ocr_data/page_7.jpeg",
      size: [907, 1383], // Обновлено из JSON
      lines: 11, // Обновлено из JSON
      characters: 361, // Обновлено из JSON
      type: "Image",
      color: "blue"
    },
    {
      title: "Page 11",
      description: "Historical document page with ancient text",
      imagePath: "/ocr_data/page_11.jpeg",
      size: [947, 1383], // Обновлено из JSON
      lines: 11, // Обновлено из JSON
      characters: 457, // Обновлено из JSON
      type: "Image",
      color: "purple"
    },
    {
      title: "Page 19",
      description: "Manuscript page with traditional script",
      imagePath: "/ocr_data/page_19.jpeg",
      size: [947, 1383], // Обновлено из JSON
      lines: 11, // Обновлено из JSON
      characters: 473, // Обновлено из JSON
      type: "Image",
      color: "green"
    },
    {
      title: "Page 23",
      description: "Ancient text document page",
      imagePath: "/ocr_data/page_23.jpeg",
      size: [947, 1383], // Обновлено из JSON
      lines: 11, // Обновлено из JSON
      characters: 448, // Обновлено из JSON
      type: "Image",
      color: "orange"
    },
    {
      title: "Page 25",
      description: "Historical manuscript with traditional writing",
      imagePath: "/ocr_data/page_25.jpeg",
      size: [947, 1383], // Обновлено из JSON
      lines: 11, // Обновлено из JSON
      characters: 444, // Обновлено из JSON
      type: "Image",
      color: "blue"
    }
  ];

  const handleApplySelection = () => {
    setAppliedDocs({
      library: [...selectedDocs],
      uploaded: uploadedDocs.map(doc => doc.filename)
    });
    setActiveTab('chat');
  };

  const removeFromContext = (type: 'library' | 'uploaded', identifier: number | string) => {
    setAppliedDocs(prev => ({
      ...prev,
      [type]: prev[type].filter(item => item !== identifier)
    }));
  };

  const openImageModal = (index: number, doc: any) => {
    setModalImage({ index, doc });
  };

  const closeImageModal = () => {
    setModalImage(null);
    setShowTextBoxes(false);
    setExtractedText(null);
    setTextBoxes([]);
  };

  const calculateTextBoxes = () => {
    if (!modalImage || !ocrData || !imageRef.current) return;

    const imageFile = ocrData.files.find((file: any) =>
      file.image_path === modalImage.doc.imagePath.replace('/ocr_data/', '')
    );

    if (!imageFile) return;

    const img = imageRef.current;
    const scaleX = img.clientWidth / modalImage.doc.size[0];
    const scaleY = img.clientHeight / modalImage.doc.size[1];

    const boxes = imageFile.lines.map((line: any) => ({
      x: line.bbox[0] * scaleX,
      y: line.bbox[1] * scaleY,
      width: (line.bbox[2] - line.bbox[0]) * scaleX,
      height: (line.bbox[3] - line.bbox[1]) * scaleY,
      text: line.text
    }));

    setTextBoxes(boxes);
  };

  const toggleTextBoxes = () => {
    if (!showTextBoxes) {
      setShowTextBoxes(true);
      setTimeout(calculateTextBoxes, 100); // Allow time for image to render
    } else {
      setShowTextBoxes(false);
      setTextBoxes([]);
    }
    setExtractedText(null);
  };

  const retrieveText = () => {
    if (extractedText) {
      // If text is already showing, hide it
      setExtractedText(null);
    } else if (modalImage && ocrData) {
      // If text is not showing, extract and show it
      const imageFile = ocrData.files.find((file: any) => file.image_path === modalImage.doc.imagePath.replace('/ocr_data/', ''));
      if (imageFile) {
        const allText = imageFile.lines.map((line: any) => line.text).join('\n');
        setExtractedText(allText);
      }
    }
  };

  // Load OCR data
  useEffect(() => {
    fetch('/ocr_data/converted_ocr_results.json')
      .then(response => response.json())
      .then(data => setOcrData(data))
      .catch(error => console.error('Error loading OCR data:', error));
  }, []);

  // Handle keyboard shortcuts for modal
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (modalImage && event.key === 'Escape') {
        closeImageModal();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [modalImage]);

  // Handle window resize to recalculate text boxes
  useEffect(() => {
    const handleResize = () => {
      if (showTextBoxes) {
        calculateTextBoxes();
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [showTextBoxes, modalImage, ocrData]);

  const tabs = [
    { id: 'chat' as Tab, label: 'Chat', icon: MessageSquare },
    { id: 'upload' as Tab, label: 'Upload', icon: Upload },
    { id: 'library' as Tab, label: 'Library', icon: BookOpen },
  ];

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-50">
        {/* Top Navigation */}
        <nav className="bg-white/80 backdrop-blur-xl border-b border-gray-200/50 sticky top-0 z-50">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              {/* Logo */}
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-green-600 rounded-xl flex items-center justify-center shadow-sm">
                  <span className="text-white font-bold text-sm">I</span>
                </div>
                <h1 className="text-xl font-semibold text-gray-900 tracking-tight">INKSight</h1>
              </div>

              {/* Desktop Navigation */}
              <div className="hidden md:flex items-center space-x-1">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                        activeTab === tab.id
                          ? 'bg-gray-900 text-white shadow-sm'
                          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                      <span>{tab.label}</span>
                    </button>
                  );
                })}
              </div>

              {/* User Menu & Mobile Menu Button */}
              <div className="flex items-center space-x-3">
                {/* Desktop User Menu */}
                <div className="hidden md:flex items-center space-x-3">
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <div className="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center">
                      <User className="w-3 h-3" />
                    </div>
                    <span className="font-medium">{user?.username}</span>
                  </div>
                  <button
                    onClick={logout}
                    className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <LogOut className="w-4 h-4" />
                    <span className="hidden lg:inline">Logout</span>
                  </button>
                </div>

                {/* Mobile Menu Button */}
                <button
                  onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                  className="md:hidden p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Mobile Menu */}
            {mobileMenuOpen && (
              <div className="md:hidden border-t border-gray-200/50 py-4">
                <div className="flex flex-col space-y-2">
                  {tabs.map((tab) => {
                    const Icon = tab.icon;
                    return (
                      <button
                        key={tab.id}
                        onClick={() => {
                          setActiveTab(tab.id);
                          setMobileMenuOpen(false);
                        }}
                        className={`flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                          activeTab === tab.id
                            ? 'bg-gray-900 text-white'
                            : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                        }`}
                      >
                        <Icon className="w-5 h-5" />
                        <span>{tab.label}</span>
                      </button>
                    );
                  })}

                  {/* Mobile User Info & Logout */}
                  <div className="border-t border-gray-200 pt-4 mt-4">
                    <div className="flex items-center space-x-3 px-4 py-2 text-sm text-gray-600">
                      <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                        <User className="w-4 h-4" />
                      </div>
                      <span className="font-medium">{user?.username}</span>
                    </div>
                    <button
                      onClick={logout}
                      className="flex items-center space-x-3 px-4 py-3 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-xl transition-colors w-full"
                    >
                      <LogOut className="w-5 h-5" />
                      <span>Logout</span>
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </nav>

        {/* Main Content */}
        <main className="flex-1">
          <div className={`h-[calc(100vh-4rem)] ${activeTab === 'chat' ? 'block' : 'hidden'}`}>
            <ChatInterface
              appliedDocs={appliedDocs}
              libraryDocs={libraryDocs}
              onRemoveFromContext={removeFromContext}
              ocrData={ocrData}
            />
          </div>

          {activeTab === 'upload' && (
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
              <div className="text-center mb-12">
                <div className="w-20 h-20 bg-gradient-to-br from-blue-600 to-green-600 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                  <Upload className="w-10 h-10 text-white" />
                </div>
                <h1 className="text-3xl font-bold text-gray-900 mb-4">Upload Documents</h1>
                <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                  Upload your documents to build a knowledge base that INKSight can search through and reference in conversations.
                </p>
              </div>

              <div className="max-w-2xl mx-auto">
                <FileUpload onUploadComplete={handleUploadComplete} />

                {uploadSuccess && (
                  <div className="mt-8 p-6 bg-green-50 border border-green-200 rounded-2xl">
                    <div className="text-center">
                      <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                      <h3 className="text-lg font-semibold text-green-800 mb-2">Upload Successful!</h3>
                      <p className="text-green-700">
                        {uploadSuccess.filename} has been processed and added to your knowledge base.
                        Redirecting to chat...
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'library' && (
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
              <div className="mb-12">
                <h1 className="text-3xl font-bold text-gray-900 mb-4">Document Library</h1>
                <p className="text-lg text-gray-600">
                  Browse and manage your document collection. Select documents to include in your conversations.
                </p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {libraryDocs.map((doc, index) => {
                  const isSelected = selectedDocs.includes(index);

                  return (
                    <div
                      key={index}
                      className={`group bg-white rounded-2xl border-2 transition-all duration-300 overflow-hidden hover:shadow-lg ${
                        isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      {/* Image Preview */}
                      <div
                        className="w-full h-48 bg-gray-100 overflow-hidden cursor-pointer relative"
                        onClick={() => openImageModal(index, doc)}
                      >
                        <img
                          src={doc.imagePath}
                          alt={doc.title}
                          className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                        />
                        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all duration-300 flex items-center justify-center">
                          <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-white bg-opacity-90 rounded-full p-2">
                            <ImageIcon className="w-6 h-6 text-gray-600" />
                          </div>
                        </div>
                      </div>

                      {/* Document Info */}
                      <div className="p-4">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1 min-w-0">
                            <h3 className="text-lg font-semibold text-gray-900 truncate">
                              {doc.title}
                            </h3>
                          </div>

                          {/* Selection Checkbox */}
                          <div
                            onClick={() => {
                              if (isSelected) {
                                setSelectedDocs(selectedDocs.filter(i => i !== index));
                              } else {
                                setSelectedDocs([...selectedDocs, index]);
                              }
                            }}
                            className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all duration-200 cursor-pointer flex-shrink-0 ${
                              isSelected
                                ? 'border-blue-500 bg-blue-500'
                                : 'border-gray-300 hover:border-blue-400'
                            }`}
                          >
                            {isSelected && (
                              <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                              </svg>
                            )}
                          </div>
                        </div>

                        <p className="text-sm text-gray-600 mb-3">
                          {doc.description}
                        </p>

                        <div className="flex items-center justify-between text-xs text-gray-500">
                          <div className="flex items-center space-x-3">
                            <span>{doc.lines} lines</span>
                            <span>{doc.characters} chars</span>
                          </div>
                          <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full font-medium">
                            {doc.type}
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })}

                {/* Uploaded Documents */}
                {uploadedDocs.map((doc, index) => (
                  <div
                    key={`uploaded-${index}`}
                    className="group cursor-pointer transition-all duration-300 hover:scale-[1.01]"
                  >
                    <div className="p-6 rounded-2xl border-2 border-green-200 bg-green-50 hover:border-green-300 shadow-sm hover:shadow-lg transition-all duration-300">
                      <div className="flex items-start justify-between mb-4">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center shadow-sm">
                          <Upload className="w-6 h-6 text-white" />
                        </div>
                        <div className="text-xs text-green-600 font-medium bg-green-200 px-2 py-1 rounded-full">
                          Recently Uploaded
                        </div>
                      </div>

                      <h3 className="font-bold text-gray-900 mb-2 text-lg">
                        {doc.filename}
                      </h3>
                      <p className="text-sm text-gray-600 mb-4 leading-relaxed">
                        User uploaded document • {doc.chunks_processed} chunks processed
                      </p>

                      <div className="flex items-center justify-between text-xs">
                        <span className="font-medium text-gray-500">
                          {(doc.file_size_bytes / 1024).toFixed(1)} KB
                        </span>
                        <span className="px-3 py-1 bg-green-200 text-green-700 rounded-full font-medium">
                          {doc.filename.split('.').pop()?.toUpperCase()}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {selectedDocs.length > 0 && (
                <div className="fixed bottom-8 left-1/2 transform -translate-x-1/2 z-50">
                  <div className="bg-gray-900 text-white px-6 py-4 rounded-2xl shadow-2xl flex items-center space-x-4">
                    <span className="font-medium">
                      {selectedDocs.length} document{selectedDocs.length !== 1 ? 's' : ''} selected
                    </span>
                    <button
                      onClick={handleApplySelection}
                      className="bg-white text-gray-900 px-4 py-2 rounded-xl font-medium hover:bg-gray-100 transition-colors"
                    >
                      Apply Selection
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </main>

        {/* Image Modal */}
        {modalImage && (
          <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75 p-4"
            onClick={closeImageModal}
          >
            <div
              className={`relative bg-white rounded-2xl overflow-hidden shadow-2xl transition-all duration-300 flex flex-col ${
                extractedText ? 'max-w-7xl' : 'max-w-4xl'
              }`}
              style={{ maxHeight: '90vh' }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Modal Header */}
              <div className="flex items-center justify-between p-4 border-b border-gray-200">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{modalImage.doc.title}</h3>
                  <p className="text-sm text-gray-600">{modalImage.doc.description}</p>
                </div>
                <button
                  onClick={closeImageModal}
                  className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* Modal Content */}
              <div className={`flex flex-1 overflow-hidden ${extractedText ? 'divide-x divide-gray-200' : ''}`}>
                {/* Image Panel */}
                <div className={`p-6 bg-gray-50 overflow-y-auto ${extractedText ? 'flex-1' : 'w-full'}`}>
                  <div className="relative inline-block">
                    <img
                      ref={imageRef}
                      src={modalImage.doc.imagePath}
                      alt={modalImage.doc.title}
                      className="w-full max-w-full h-auto rounded-lg shadow-sm"
                      style={{ maxHeight: '70vh', objectFit: 'contain' }}
                      onLoad={calculateTextBoxes}
                    />

                    {/* Text Box Overlays */}
                    {showTextBoxes && textBoxes.map((box, index) => (
                      <div
                        key={index}
                        className="absolute border-2 border-red-500 bg-red-500 bg-opacity-20 hover:bg-opacity-30 transition-all duration-200 cursor-pointer"
                        style={{
                          left: `${box.x}px`,
                          top: `${box.y}px`,
                          width: `${box.width}px`,
                          height: `${box.height}px`,
                        }}
                        title={box.text}
                      />
                    ))}
                  </div>

                  <div className="mt-4 flex items-center justify-between text-sm text-gray-600">
                    <div className="flex items-center space-x-4">
                      <span>{modalImage.doc.lines} text lines</span>
                      <span>{modalImage.doc.characters} characters</span>
                      <span>{modalImage.doc.size[0]} × {modalImage.doc.size[1]}px</span>
                    </div>
                    <span className="px-3 py-1 bg-gray-200 text-gray-700 rounded-full font-medium">
                      {modalImage.doc.type}
                    </span>
                  </div>
                </div>

                {/* Text Panel - Right Side */}
                {extractedText && (
                  <div className="w-96 bg-white p-6 flex flex-col overflow-hidden">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="text-lg font-semibold text-gray-900">Extracted Text</h4>
                      <button
                        onClick={() => setExtractedText(null)}
                        className="text-gray-400 hover:text-gray-600 p-1 hover:bg-gray-100 rounded"
                      >
                        <X className="w-5 h-5" />
                      </button>
                    </div>
                    <div className="flex-1 overflow-hidden">
                      <div className="h-full overflow-y-auto">
                        <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono leading-relaxed">
                          {extractedText}
                        </pre>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Modal Footer */}
              <div className="border-t border-gray-200 px-6 py-4 bg-white flex-shrink-0">
                <div className="flex items-center justify-center">
                  <div className="flex items-center space-x-3">
                    <button
                      onClick={toggleTextBoxes}
                      className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                        showTextBoxes
                          ? 'bg-blue-600 text-white hover:bg-blue-700'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {showTextBoxes ? 'Hide Boxes' : 'Show Boxes'}
                    </button>
                    <button
                      onClick={retrieveText}
                      className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                        extractedText
                          ? 'bg-green-600 text-white hover:bg-green-700'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {extractedText ? 'Hide Text' : 'Show Text'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </QueryClientProvider>
  );
};