import { X, Instagram, ExternalLink, AlertCircle, CheckCircle } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useState } from 'react';

const InstagramSetup = ({ onClose }) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);
  const [instagramAccount, setInstagramAccount] = useState(null);

  const handleConnectFacebook = async () => {
    setLoading(true);
    try {
      // TODO: API call to get Instagram OAuth URL
      // const response = await axios.get('/api/integrations/instagram/auth/');
      // window.location.href = response.data.authorization_url;

      // Mock for now
      setTimeout(() => {
        setConnected(true);
        setInstagramAccount({
          username: '@your_salon',
          name: 'Your Salon',
        });
        setLoading(false);
      }, 1500);
    } catch (error) {
      console.error('Error connecting Instagram:', error);
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold">{t('integrations.setupInstagram')}</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X size={24} />
          </button>
        </div>

        <div className="space-y-4">
          {/* Notice */}
          <div className="bg-pink-50 border border-pink-200 rounded-lg p-4">
            <div className="flex gap-2">
              <AlertCircle className="text-pink-500 flex-shrink-0" size={20} />
              <p className="text-sm text-pink-800">
                {t('integrations.instagramNotice')}
              </p>
            </div>
          </div>

          {/* Features */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-800 mb-2">
              <strong>{t('integrations.instagramInfo')}</strong>
            </p>
            <ul className="text-sm text-blue-700 space-y-1 list-disc list-inside">
              {t('integrations.instagramItems', { returnObjects: true }).map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>

          {!connected ? (
            <div className="space-y-4">
              {/* Requirements */}
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="font-medium text-gray-800 mb-3">📋 {t('integrations.requirements')}:</p>
                <ol className="space-y-2 text-sm text-gray-700">
                  <li className="flex items-start gap-2">
                    <span className="font-semibold">1.</span>
                    <span>Instagram <strong>Business</strong> або <strong>Creator</strong> акаунт</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="font-semibold">2.</span>
                    <span>Facebook Page (сторінка) вашого салону</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="font-semibold">3.</span>
                    <span>Instagram підключений до Facebook Page</span>
                  </li>
                </ol>
              </div>

              {/* Setup Guide Link */}
              <a
                href="/docs/instagram-setup"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-pink-600 hover:text-pink-700 text-sm font-medium"
              >
                <ExternalLink size={16} />
                {t('integrations.instagramGuide')}
              </a>

              {/* Connect Button */}
              <div className="text-center py-6">
                <Instagram className="mx-auto text-pink-500 mb-3" size={48} />
                <p className="text-gray-600 text-sm mb-4">
                  {t('integrations.connectWithFacebook')}
                </p>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleConnectFacebook}
                  disabled={loading}
                  className="btn-primary flex-1 flex items-center justify-center gap-2 bg-pink-600 hover:bg-pink-700"
                >
                  <Instagram size={18} />
                  {loading ? t('common.loading') : t('integrations.connectWithFacebook')}
                </button>
                <button onClick={onClose} className="btn-secondary flex-1">
                  {t('common.cancel')}
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Connected Status */}
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <CheckCircle className="text-green-500 flex-shrink-0" size={24} />
                  <div className="flex-1">
                    <p className="text-sm text-green-800 font-medium mb-1">
                      ✓ {t('integrations.connected')}
                    </p>
                    <p className="text-sm text-green-700">
                      <strong>{instagramAccount?.username}</strong> - {instagramAccount?.name}
                    </p>
                  </div>
                </div>
              </div>

              {/* Settings */}
              <div className="space-y-3">
                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                    <input type="checkbox" className="rounded" defaultChecked />
                    Auto-відповіді увімкнено
                  </label>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Робочі години
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="time"
                      defaultValue="09:00"
                      className="input flex-1"
                    />
                    <span className="self-center text-gray-500">—</span>
                    <input
                      type="time"
                      defaultValue="20:00"
                      className="input flex-1"
                    />
                  </div>
                </div>
              </div>

              <div className="flex gap-3 pt-2">
                <button className="btn-primary flex-1">
                  {t('common.save')}
                </button>
                <button onClick={onClose} className="btn-secondary flex-1">
                  {t('common.close')}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InstagramSetup;
