import { X, ExternalLink, CheckCircle } from 'lucide-react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { agentAPI } from '../../api/agent';

const WhatsAppSetup = ({ onClose, onSuccess }) => {
  const { t } = useTranslation();
  const [phoneNumberId, setPhoneNumberId] = useState('');
  const [accessToken, setAccessToken] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleConnect = async () => {
    if (!phoneNumberId.trim() || !accessToken.trim()) {
      setError(t('integrations.fillAllFields') || 'Please fill all fields');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await agentAPI.connectWhatsApp(phoneNumberId, accessToken);
      setSuccess(true);
      // Notify parent component
      if (onSuccess) {
        onSuccess();
      }
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
          <h3 className="text-xl font-semibold">{t('integrations.setupWhatsApp')}</h3>
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
                  <p className="text-sm text-green-800 font-medium">
                    ✓ {t('integrations.connected')}
                  </p>
                  <p className="text-sm text-green-700">
                    {t('integrations.whatsappConnected')}
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

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-800">
              {t('integrations.whatsappNotice')}
            </p>
          </div>

          <div>
            <p className="text-sm text-gray-600 mb-2">
              1. {t('integrations.whatsappStep1')}
            </p>
            <p className="text-sm text-gray-600 mb-2">
              2. {t('integrations.whatsappStep2')}
            </p>
            <p className="text-sm text-gray-600 mb-4">
              3. {t('integrations.whatsappStep3')}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              {t('integrations.phoneNumberId')}
            </label>
            <input
              type="text"
              value={phoneNumberId}
              onChange={(e) => setPhoneNumberId(e.target.value)}
              placeholder={t('integrations.enterPhoneNumberId')}
              className="input"
              disabled={loading || success}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              {t('integrations.accessToken')}
            </label>
            <input
              type="password"
              value={accessToken}
              onChange={(e) => setAccessToken(e.target.value)}
              placeholder={t('integrations.enterAccessToken')}
              className="input"
              disabled={loading || success}
            />
          </div>

          <a
            href="https://business.whatsapp.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-primary-500 hover:underline text-sm"
          >
            <ExternalLink size={16} />
            {t('integrations.whatsappLearnMore')}
          </a>

          <div className="flex gap-3 pt-4">
            {!success && (
              <button
                onClick={handleConnect}
                disabled={loading || !phoneNumberId.trim() || !accessToken.trim()}
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

export default WhatsAppSetup;
