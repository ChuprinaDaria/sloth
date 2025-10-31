import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import FileUpload from '../components/training/FileUpload';
import FileList from '../components/training/FileList';
import PhotoUpload from '../components/training/PhotoUpload';
import PhotoList from '../components/training/PhotoList';
import PromptEditor from '../components/training/PromptEditor';

const TrainingPage = () => {
  const { t } = useTranslation();
  const [files, setFiles] = useState([]);
  const [photos, setPhotos] = useState([]);
  const [trainingStatus, setTrainingStatus] = useState('idle'); // idle, training, completed

  const handleFileUpload = (newFiles) => {
    setFiles([...files, ...newFiles]);
  };

  const handleDeleteFile = (fileId) => {
    setFiles(files.filter(f => f.id !== fileId));
  };

  const handlePhotoUpload = (newPhotos) => {
    setPhotos([...photos, ...newPhotos]);
  };

  const handleDeletePhoto = (photoId) => {
    setPhotos(photos.filter(p => p.id !== photoId));
  };

  const handleUpdatePhoto = (photoId, description) => {
    setPhotos(photos.map(p => p.id === photoId ? { ...p, description } : p));
  };

  const handleStartTraining = async () => {
    setTrainingStatus('training');
    // Simulate training
    setTimeout(() => {
      setTrainingStatus('completed');
    }, 3000);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{t('training.title')}</h1>
        <p className="text-gray-600">{t('training.subtitle')}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-6">
          <FileUpload onUpload={handleFileUpload} />
          <FileList files={files} onDelete={handleDeleteFile} />
          <PhotoUpload onUpload={handlePhotoUpload} />
          <PhotoList photos={photos} onDelete={handleDeletePhoto} onUpdate={handleUpdatePhoto} />
        </div>

        <div className="space-y-6">
          <PromptEditor />

          <div className="card">
            <h3 className="text-lg font-semibold mb-4">{t('training.trainingStatus')}</h3>
            {trainingStatus === 'idle' && (
              <div>
                <p className="text-gray-600 mb-4">
                  {t('training.uploadAndTrain')}
                </p>
                <button
                  onClick={handleStartTraining}
                  disabled={files.length === 0}
                  className="btn-primary"
                >
                  {t('training.startTraining')}
                </button>
              </div>
            )}
            {trainingStatus === 'training' && (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
                <p className="text-gray-600">{t('training.trainingInProgress')}</p>
              </div>
            )}
            {trainingStatus === 'completed' && (
              <div className="text-center py-8">
                <div className="text-6xl mb-4">✅</div>
                <p className="text-lg font-semibold text-green-600">{t('training.trainingComplete')}</p>
                <p className="text-gray-600 mt-2">{t('training.aiReady')}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrainingPage;
