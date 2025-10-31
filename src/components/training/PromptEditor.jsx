import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Sparkles } from 'lucide-react';

const PromptEditor = () => {
  const { t } = useTranslation();
  const [prompt, setPrompt] = useState(
    `You are a friendly AI assistant for a beauty salon. Your role is to:
- Answer questions about services and pricing
- Help clients book appointments
- Provide information about available time slots
- Be polite and professional

Always use a warm and welcoming tone.`
  );

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="text-primary-500" size={20} />
        <h3 className="text-lg font-semibold">{t('training.aiBehavior')}</h3>
      </div>

      <p className="text-sm text-gray-600 mb-4">
        {t('training.customizePrompt')}
      </p>

      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        className="w-full h-64 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none resize-none font-mono text-sm"
        placeholder={t('training.promptPlaceholder')}
      />

      <div className="mt-4 flex gap-3">
        <button className="btn-primary">{t('training.savePrompt')}</button>
        <button className="btn-secondary">{t('training.resetDefault')}</button>
      </div>
    </div>
  );
};

export default PromptEditor;
