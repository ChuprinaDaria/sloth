import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import FileUpload from '../components/training/FileUpload';
import FileList from '../components/training/FileList';
import PhotoUpload from '../components/training/PhotoUpload';
import PhotoList from '../components/training/PhotoList';
import PromptEditor from '../components/training/PromptEditor';
import { agentAPI } from '../api/agent';

const TrainingPage = () => {
  const { t } = useTranslation();
  const [files, setFiles] = useState([]);
  const [photos, setPhotos] = useState([]);
  const [trainingStatus, setTrainingStatus] = useState('idle'); // idle, training, completed
  const [loading, setLoading] = useState(true);

  // Load files from API on mount
  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    try {
      setLoading(true);
      const response = await agentAPI.getFiles();
      setFiles(response.data || []);
    } catch (error) {
      console.error('Error loading files:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (newFiles) => {
    setFiles([...files, ...newFiles]);
    // Reload files to get updated status
    setTimeout(() => loadFiles(), 1000);
  };

  const handleDeleteFile = async (fileId) => {
    try {
      await agentAPI.deleteFile(fileId);
      setFiles(files.filter(f => f.id !== fileId));
    } catch (error) {
      console.error('Error deleting file:', error);
      alert(t('training.deleteError') || 'Failed to delete file');
    }
  };

  const handlePhotoUpload = (newPhotos) => {
    const currentPhotos = Array.isArray(photos) ? photos : [];
    const photosToAdd = Array.isArray(newPhotos) ? newPhotos : [];
    setPhotos([...currentPhotos, ...photosToAdd]);
  };

  const handleDeletePhoto = (photoId) => {
    const currentPhotos = Array.isArray(photos) ? photos : [];
    setPhotos(currentPhotos.filter(p => p.id !== photoId));
  };

  const handleUpdatePhoto = (photoId, description) => {
    const currentPhotos = Array.isArray(photos) ? photos : [];
    setPhotos(currentPhotos.map(p => p.id === photoId ? { ...p, description } : p));
  };

  const handleStartTraining = async () => {
    setTrainingStatus('training');
    try {
      // Start embeddings processing for all files
      await agentAPI.startTraining();
      
      // Poll for training status
      const checkStatus = async () => {
        try {
          const statusResponse = await agentAPI.getTrainingStatus();
          if (statusResponse.data.status === 'completed') {
            setTrainingStatus('completed');
            // Reload files to get updated processing status
            loadFiles();
          } else if (statusResponse.data.status === 'processing') {
            // Check again in 2 seconds
            setTimeout(checkStatus, 2000);
          } else {
            setTrainingStatus('idle');
          }
        } catch (error) {
          console.error('Error checking training status:', error);
          // Assume completed after timeout
          setTimeout(() => {
            setTrainingStatus('completed');
            loadFiles();
          }, 5000);
        }
      };
      
      // Start checking status after 2 seconds
      setTimeout(checkStatus, 2000);
    } catch (error) {
      console.error('Error starting training:', error);
      setTrainingStatus('idle');
      alert(t('training.trainingError') || 'Failed to start training');
    }
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
                  disabled={files.length === 0 || loading}
                  className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
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
                <button
                  onClick={() => {
                    setTrainingStatus('idle');
                    loadFiles();
                  }}
                  className="btn-secondary mt-4"
                >
                  {t('training.trainAgain') || 'Train Again'}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrainingPage;
