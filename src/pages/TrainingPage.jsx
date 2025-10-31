import { useState } from 'react';
import FileUpload from '../components/training/FileUpload';
import FileList from '../components/training/FileList';
import PromptEditor from '../components/training/PromptEditor';

const TrainingPage = () => {
  const [files, setFiles] = useState([]);
  const [trainingStatus, setTrainingStatus] = useState('idle'); // idle, training, completed

  const handleFileUpload = (newFiles) => {
    setFiles([...files, ...newFiles]);
  };

  const handleDeleteFile = (fileId) => {
    setFiles(files.filter(f => f.id !== fileId));
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
        <h1 className="text-2xl font-bold">Train Your AI</h1>
        <p className="text-gray-600">Upload files and customize your AI assistant</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-6">
          <FileUpload onUpload={handleFileUpload} />
          <FileList files={files} onDelete={handleDeleteFile} />
        </div>

        <div className="space-y-6">
          <PromptEditor />

          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Training Status</h3>
            {trainingStatus === 'idle' && (
              <div>
                <p className="text-gray-600 mb-4">
                  Upload files and click train to start
                </p>
                <button
                  onClick={handleStartTraining}
                  disabled={files.length === 0}
                  className="btn-primary"
                >
                  Start Training
                </button>
              </div>
            )}
            {trainingStatus === 'training' && (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
                <p className="text-gray-600">Training in progress...</p>
              </div>
            )}
            {trainingStatus === 'completed' && (
              <div className="text-center py-8">
                <div className="text-6xl mb-4">✅</div>
                <p className="text-lg font-semibold text-green-600">Training Complete!</p>
                <p className="text-gray-600 mt-2">Your AI is ready to use</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrainingPage;
