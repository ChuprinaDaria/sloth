import { Upload } from 'lucide-react';
import { useState } from 'react';

const FileUpload = ({ onUpload }) => {
  const [dragging, setDragging] = useState(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  const handleFiles = (fileList) => {
    const newFiles = fileList.map((file) => ({
      id: Date.now() + Math.random(),
      name: file.name,
      size: file.size,
      type: file.type,
      uploadedAt: new Date().toISOString(),
    }));
    onUpload(newFiles);
  };

  const handleFileInput = (e) => {
    const files = Array.from(e.target.files);
    handleFiles(files);
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4">Upload Training Files</h3>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragging
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-primary-400'
        }`}
      >
        <Upload className="mx-auto mb-4 text-gray-400" size={48} />
        <p className="text-gray-700 font-medium mb-2">
          Drag & drop files here or click to browse
        </p>
        <p className="text-sm text-gray-500 mb-4">
          Supported: PDF, DOC, TXT, XLS (Max 10MB)
        </p>
        <input
          type="file"
          multiple
          onChange={handleFileInput}
          className="hidden"
          id="file-input"
          accept=".pdf,.doc,.docx,.txt,.xls,.xlsx"
        />
        <label htmlFor="file-input" className="btn-primary cursor-pointer">
          Choose Files
        </label>
      </div>
    </div>
  );
};

export default FileUpload;
