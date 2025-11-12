import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Sparkles } from 'lucide-react';
import { agentAPI } from '../../api/agent';

const defaultPrompt = `You are a friendly AI assistant for a beauty salon. Your role is to:
- Answer questions about services and pricing
- Help clients book appointments
- Provide information about available time slots
- Be polite and professional

Always use a warm and welcoming tone.`;

const PromptEditor = () => {
  const { t } = useTranslation();
  const [role, setRole] = useState('');
  const [instructions, setInstructions] = useState('');
  const [context, setContext] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Load prompt from backend
  useEffect(() => {
    const loadPrompt = async () => {
      try {
        const response = await agentAPI.getPrompt();
        const data = response.data;
        setRole(data.role || '');
        setInstructions(data.instructions || '');
        setContext(data.context || '');
      } catch (error) {
        console.error('Failed to load prompt:', error);
        // Set defaults on error
        setRole(defaultPrompt);
      } finally {
        setLoading(false);
      }
    };

    loadPrompt();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await agentAPI.updatePrompt({
        role,
        instructions,
        context
      });
      alert(t('training.promptSaved') || 'Prompt saved successfully!');
    } catch (error) {
      console.error('Failed to save prompt:', error);
      alert(t('training.promptSaveFailed') || 'Failed to save prompt. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    if (confirm(t('training.confirmReset') || 'Reset to default prompt?')) {
      setRole(defaultPrompt);
      setInstructions('');
      setContext('');
    }
  };

  if (loading) {
    return (
      <div className="card">
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="text-primary-500" size={20} />
        <h3 className="text-lg font-semibold">{t('training.aiBehavior')}</h3>
      </div>

      <p className="text-sm text-gray-600 mb-4">
        {t('training.customizePrompt')}
      </p>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('training.roleLabel') || 'Role (Main Instructions)'}
          </label>
          <textarea
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="w-full h-32 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none resize-none font-mono text-sm"
            placeholder="You are a helpful AI assistant..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('training.instructionsLabel') || 'Additional Instructions (Optional)'}
          </label>
          <textarea
            value={instructions}
            onChange={(e) => setInstructions(e.target.value)}
            className="w-full h-24 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none resize-none font-mono text-sm"
            placeholder="Special instructions..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('training.contextLabel') || 'Business Context (Services, Pricing, etc.)'}
          </label>
          <textarea
            value={context}
            onChange={(e) => setContext(e.target.value)}
            className="w-full h-32 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none resize-none font-mono text-sm"
            placeholder="Business information, services, pricing..."
          />
        </div>
      </div>

      <div className="mt-4 flex gap-3">
        <button
          onClick={handleSave}
          disabled={saving}
          className="btn-primary disabled:opacity-50"
        >
          {saving ? (t('training.saving') || 'Saving...') : (t('training.savePrompt') || 'Save Prompt')}
        </button>
        <button
          onClick={handleReset}
          className="btn-secondary"
        >
          {t('training.resetDefault') || 'Reset to Default'}
        </button>
      </div>
    </div>
  );
};

export default PromptEditor;
