import { useTranslation } from 'react-i18next';
import ChatWindow from '../components/sandbox/ChatWindow';
import PhotoUploadTest from '../components/sandbox/PhotoUploadTest';

const SandboxPage = () => {
  const { t } = useTranslation();
  
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{t('sandbox.title')}</h1>
        <p className="text-gray-600">{t('sandbox.subtitle')}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ChatWindow />
        </div>

        <div>
          <PhotoUploadTest />
        </div>
      </div>
    </div>
  );
};

export default SandboxPage;
