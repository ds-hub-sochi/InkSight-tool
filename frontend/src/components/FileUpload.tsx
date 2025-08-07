import React, { useState } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react';
import { chatAPI } from '../lib/api';
import type { UploadDocumentResponse } from '../lib/api';

interface FileUploadProps {
  onUploadComplete?: (response: UploadDocumentResponse) => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onUploadComplete }) => {
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadDocumentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFile = async (file: File) => {
    setUploading(true);
    setError(null);
    setUploadResult(null);

    try {
      // Mock upload for demo (replace with real API call when backend is available)
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate upload delay
      
      const mockResponse: UploadDocumentResponse = {
        success: true,
        message: "Document uploaded successfully",
        filename: file.name,
        chunks_processed: Math.floor(file.size / 1000), // Mock chunk count
        file_size_bytes: file.size
      };
      
      setUploadResult(mockResponse);
      onUploadComplete?.(mockResponse);
    } catch (err: any) {
      setError('Upload failed - demo mode');
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  return (
    <div className="w-full max-w-xl mx-auto">
      <div
        className={`
          border-2 border-dashed rounded-3xl p-12 text-center transition-all duration-300
          ${dragOver ? 'border-blue-500 bg-gradient-to-br from-blue-50 to-purple-50 scale-105' : 'border-gray-300 bg-white'}
          ${uploading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:border-blue-400 hover:bg-blue-50 hover:scale-102 hover:shadow-lg'}
        `}
        onDrop={handleDrop}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onClick={() => !uploading && document.getElementById('file-input')?.click()}
      >
        {uploading ? (
          <div className="flex flex-col items-center space-y-4">
            <div className="relative">
              <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-200 border-t-blue-600"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <Upload className="h-6 w-6 text-blue-600" />
              </div>
            </div>
            <p className="text-blue-600 font-semibold text-lg">Uploading your document...</p>
            <p className="text-gray-500 text-sm">This may take a few moments</p>
          </div>
        ) : (
          <>
            <div className="p-4 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full w-20 h-20 mx-auto mb-6 shadow-lg">
              <Upload className="h-12 w-12 text-white" />
            </div>
            <p className="text-gray-800 mb-3 text-xl font-semibold">
              Drop a document here or click to browse
            </p>
            <p className="text-gray-500 text-lg">
              Supports TXT and PDF files (max 50MB)
            </p>
          </>
        )}
        
        <input
          id="file-input"
          type="file"
          accept=".txt,.pdf"
          onChange={handleFileSelect}
          className="hidden"
          disabled={uploading}
        />
      </div>

      {error && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-2xl flex items-center space-x-3 shadow-sm">
          <AlertCircle className="h-6 w-6 text-red-500 flex-shrink-0" />
          <p className="text-red-700 font-medium">{error}</p>
        </div>
      )}

      {uploadResult && (
        <div className="mt-6 p-6 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-2xl shadow-lg">
          <div className="flex items-center space-x-3 mb-4">
            <CheckCircle className="h-8 w-8 text-green-500" />
            <p className="text-lg font-bold text-green-800">Upload Successful!</p>
          </div>
          <div className="text-green-700 space-y-2">
            <p className="flex items-center text-base"><FileText className="inline h-5 w-5 mr-2" /><span className="font-semibold">{uploadResult.filename}</span></p>
            <p className="text-sm">📄 Processed: <span className="font-semibold">{uploadResult.chunks_processed}</span> chunks</p>
            <p className="text-sm">📊 Size: <span className="font-semibold">{Math.round(uploadResult.file_size_bytes / 1024)} KB</span></p>
          </div>
        </div>
      )}
    </div>
  );
};