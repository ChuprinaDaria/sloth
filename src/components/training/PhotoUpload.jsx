import { Camera } from 'lucide-react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

const PhotoUpload = ({ onUpload }) => {
  const { t } = useTranslation();
  const [dragging, setDragging] = useState(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const files = Array.from(e.dataTransfer.files).filter(file => file.type.startsWith('image/'));
    handleFiles(files);
  };

  const handleFiles = (fileList) => {
    const newPhotos = fileList.map((file) => ({
      id: Date.now() + Math.random(),
      name: file.name,
      size: file.size,
      type: file.type,
      uploadedAt: new Date().toISOString(),
      description: '',
      file: file,
    }));
    onUpload(newPhotos);
  };

  const handleFileInput = (e) => {
    const files = Array.from(e.target.files);
    handleFiles(files);
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4">{t('training.uploadPhotos')}</h3>

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
        <Camera className="mx-auto mb-4 text-gray-400" size={48} />
        <p className="text-gray-700 font-medium mb-2">
          {t('training.dragDropPhotos')}
        </p>
        <p className="text-sm text-gray-500 mb-4">
          {t('training.supportedPhotoFormats')}
        </p>
        <input
          type="file"
          multiple
          onChange={handleFileInput}
          className="hidden"
          id="photo-input"
          accept="image/*"
        />
        <label htmlFor="photo-input" className="btn-primary cursor-pointer">
          {t('training.choosePhotos')}
        </label>
      </div>
    </div>
  );
};

export default PhotoUpload;

