import { X, Copy, CheckCircle, Check } from 'lucide-react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { agentAPI } from '../../api/agent';

const TelegramSetup = ({ onClose }) => {
  const { t } = useTranslation();
  const [botToken, setBotToken] = useState('');
  const [webhookUrl, setWebhookUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(webhookUrl);
  };

  const handleConnect = async () => {
    if (!botToken.trim()) {
      setError(t('integrations.enterBotToken') || 'Please enter bot token');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await agentAPI.connectTelegram(botToken);
      setWebhookUrl(response.data.webhook_url || '');
      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.error || err.message || t('common.error'));
      setSuccess(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 max-w-lg w-full mx-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold">{t('integrations.setupTelegram')}</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X size={24} />
          </button>
        </div>

        <div className="space-y-4">
          {/* Success message */}
          {success && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-start gap-2">
                <CheckCircle className="text-green-500 flex-shrink-0" size={20} />
                <div>
                  <p className="text-sm text-green-800 font-medium flex items-center gap-1">
                    <Check size={16} /> {t('integrations.connected')}
                  </p>
                  <p className="text-sm text-green-700">
                    {t('integrations.telegramConnected')}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Error message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <div>
            <p className="text-sm text-gray-600 mb-2">
              1. {t('integrations.telegramStep1')}
            </p>
            <p className="text-sm text-gray-600 mb-2">
              2. {t('integrations.telegramStep2')}
            </p>
            <p className="text-sm text-gray-600 mb-4">
              3. {t('integrations.telegramStep3')}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              {t('integrations.botToken')}
            </label>
            <input
              type="text"
              value={botToken}
              onChange={(e) => setBotToken(e.target.value)}
              placeholder="123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ"
              className="input"
              disabled={loading || success}
            />
          </div>

          {webhookUrl && (
            <div>
              <label className="block text-sm font-medium mb-2">
                {t('integrations.webhookUrl')}
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={webhookUrl}
                  readOnly
                  className="input flex-1 bg-gray-50"
                />
                <button onClick={handleCopy} className="btn-secondary">
                  <Copy size={18} />
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                {t('integrations.webhookSetAutomatically')}
              </p>
            </div>
          )}

          <div className="flex gap-3 pt-4">
            {!success && (
              <button
                onClick={handleConnect}
                disabled={loading || !botToken.trim()}
                className="btn-primary flex-1"
              >
                {loading ? t('common.loading') : t('integrations.connect')}
              </button>
            )}
            <button onClick={onClose} className="btn-secondary flex-1">
              {success ? t('common.close') : t('common.cancel')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TelegramSetup;
