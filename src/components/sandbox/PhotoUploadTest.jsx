import { useState } from 'react';
import { Camera, X } from 'lucide-react';

const PhotoUploadTest = () => {
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
          setResponse(
            'I can see this is a photo. In production, the AI will analyze the image and provide relevant information.'
          );
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
      <h3 className="text-lg font-semibold mb-4">Photo Upload Test</h3>
      <p className="text-sm text-gray-600 mb-4">
        Test how AI responds to image uploads
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
            Upload Photo
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
              <p className="font-medium text-sm mb-2">AI Response:</p>
              <p className="text-sm text-gray-700">{response}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PhotoUploadTest;
