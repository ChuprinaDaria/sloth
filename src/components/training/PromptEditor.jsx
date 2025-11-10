import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Sparkles } from 'lucide-react';
import { agentAPI } from '../../api/agent';

const PromptEditor = () => {
  const { t } = useTranslation();
  const defaultPrompt = `You are a friendly AI assistant for a beauty salon. Your role is to:
- Answer questions about services and pricing
- Help clients book appointments
- Provide information about available time slots
- Be polite and professional

Always use a warm and welcoming tone.`;

  const [prompt, setPrompt] = useState(defaultPrompt);
  const [originalPrompt, setOriginalPrompt] = useState(defaultPrompt);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  // Load existing prompt on mount
  useEffect(() => {
    const loadPrompt = async () => {
      try {
        setLoading(true);
        const response = await agentAPI.getPrompt();
        if (response.data && response.data.prompt) {
          setPrompt(response.data.prompt);
          setOriginalPrompt(response.data.prompt);
        }
      } catch (error) {
        console.error('Error loading prompt:', error);
        // Use default prompt if API fails
      } finally {
        setLoading(false);
      }
    };

    loadPrompt();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await agentAPI.updatePrompt(prompt);
      setOriginalPrompt(prompt);
      alert(t('training.promptSaved') || 'Prompt saved successfully!');
    } catch (error) {
      console.error('Error saving prompt:', error);
      alert(t('training.promptSaveError') || 'Failed to save prompt');
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    if (confirm(t('training.confirmReset') || 'Reset to default prompt?')) {
      setPrompt(defaultPrompt);
    }
  };

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="text-primary-500" size={20} />
        <h3 className="text-lg font-semibold">{t('training.aiBehavior')}</h3>
      </div>

      <p className="text-sm text-gray-600 mb-4">
        {t('training.customizePrompt')}
      </p>

      {loading ? (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
        </div>
      ) : (
        <>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="w-full h-64 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none resize-none font-mono text-sm"
            placeholder={t('training.promptPlaceholder')}
          />

          <div className="mt-4 flex gap-3">
            <button 
              onClick={handleSave}
              disabled={saving || prompt === originalPrompt}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving ? (t('common.saving') || 'Saving...') : t('training.savePrompt')}
            </button>
            <button 
              onClick={handleReset}
              className="btn-secondary"
            >
              {t('training.resetDefault')}
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default PromptEditor;
