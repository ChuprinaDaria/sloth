import { useRef } from 'react';
import { useTranslation } from 'react-i18next';
import ChatWindow from '../components/sandbox/ChatWindow';
import PhotoUploadTest from '../components/sandbox/PhotoUploadTest';
import VoiceRecorder from '../components/sandbox/VoiceRecorder';

const SandboxPage = () => {
  const { t } = useTranslation();
  const chatWindowRef = useRef(null);

  const handleVoiceTranscription = (text, language) => {
    // Find the input field and set its value
    const inputField = document.querySelector('input[placeholder*="' + t('sandbox.typeMessage').substring(0, 10) + '"]');
    if (inputField) {
      // Set the value
      inputField.value = text;

      // Trigger change event to update React state
      const event = new Event('input', { bubbles: true });
      inputField.dispatchEvent(event);

      // Focus the input field
      inputField.focus();
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{t('sandbox.title')}</h1>
        <p className="text-gray-600">{t('sandbox.subtitle')}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ChatWindow ref={chatWindowRef} />
        </div>

        <div className="space-y-6">
          <VoiceRecorder onTranscription={handleVoiceTranscription} />
          <PhotoUploadTest />
        </div>
      </div>
    </div>
  );
};

export default SandboxPage;
