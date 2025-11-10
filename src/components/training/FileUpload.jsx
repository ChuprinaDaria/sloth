import { Upload } from 'lucide-react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { agentAPI } from '../../api/agent';

const FileUpload = ({ onUpload }) => {
  const { t } = useTranslation();
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  const handleFiles = async (fileList) => {
    setUploading(true);
    try {
      // Upload files one by one with progress
      const uploadedFiles = [];
      for (const file of fileList) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await agentAPI.uploadFile(formData);
        uploadedFiles.push(response.data);
      }
      
      onUpload(uploadedFiles);
      alert(t('training.uploadSuccess') || `Successfully uploaded ${uploadedFiles.length} file(s)`);
    } catch (error) {
      console.error('Error uploading files:', error);
      const errorMsg = error.response?.data?.error || error.message || 'Unknown error';
      alert(t('training.uploadError') || `Failed to upload files: ${errorMsg}`);
    } finally {
      setUploading(false);
    }
  };

  const handleFileInput = (e) => {
    const files = Array.from(e.target.files);
    handleFiles(files);
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4">{t('training.uploadFiles')}</h3>

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
          {t('training.dragDrop')}
        </p>
        <p className="text-sm text-gray-500 mb-4">
          {t('training.supportedFormats')}
        </p>
        <input
          type="file"
          multiple
          onChange={handleFileInput}
          className="hidden"
          id="file-input"
          accept=".pdf,.doc,.docx,.txt,.xls,.xlsx"
        />
        <label htmlFor="file-input" className={`btn-primary cursor-pointer ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}>
          {uploading ? (t('training.uploading') || 'Uploading...') : t('training.chooseFiles')}
        </label>
      </div>
    </div>
  );
};

export default FileUpload;
