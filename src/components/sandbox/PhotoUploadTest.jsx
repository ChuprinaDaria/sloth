import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Camera, X } from 'lucide-react';

const PhotoUploadTest = () => {
  const { t } = useTranslation();
  const [photo, setPhoto] = useState(null);
  const [response, setResponse] = useState('');

  const handlePhotoUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPhoto(reader.result);
        // Simulate AI analysis
        setTimeout(() => {
          setResponse(t('sandbox.imageAnalysis'));
        }, 1000);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleClear = () => {
    setPhoto(null);
    setResponse('');
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4">{t('sandbox.photoUpload')}</h3>
      <p className="text-sm text-gray-600 mb-4">
        {t('sandbox.photoSubtitle')}
      </p>

      {!photo ? (
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
          <Camera className="mx-auto mb-4 text-gray-400" size={48} />
          <input
            type="file"
            accept="image/*"
            onChange={handlePhotoUpload}
            className="hidden"
            id="photo-input"
          />
          <label htmlFor="photo-input" className="btn-primary cursor-pointer">
            {t('sandbox.uploadPhoto')}
          </label>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="relative">
            <img src={photo} alt="Uploaded" className="w-full rounded-lg" />
            <button
              onClick={handleClear}
              className="absolute top-2 right-2 bg-red-500 text-white p-2 rounded-full hover:bg-red-600"
            >
              <X size={18} />
            </button>
          </div>

          {response && (
            <div className="bg-gray-100 p-4 rounded-lg">
              <p className="font-medium text-sm mb-2">{t('sandbox.aiResponse')}</p>
              <p className="text-sm text-gray-700">{response}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PhotoUploadTest;
