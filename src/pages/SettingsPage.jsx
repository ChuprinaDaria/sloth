import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { Save, Gift } from 'lucide-react';
import api from '../api/axios';

const SettingsPage = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [settings, setSettings] = useState({
    salon_name: user?.salon_name || '',
    email: user?.email || '',
    phone: '',
    address: '',
    language: 'en',
    timezone: 'UTC',
  });

  const [referralCode, setReferralCode] = useState('');
  const [referralLoading, setReferralLoading] = useState(false);
  const [referralMessage, setReferralMessage] = useState({ type: '', text: '' });

  const handleSubmit = (e) => {
    e.preventDefault();
    // Save settings
    console.log('Saving settings:', settings);
  };

  const handleActivateReferralCode = async (e) => {
    e.preventDefault();
    setReferralLoading(true);
    setReferralMessage({ type: '', text: '' });

    try {
      const response = await api.post('/referrals/activate-code/', { code: referralCode });
      setReferralMessage({ type: 'success', text: response.data.message });
      setReferralCode('');
    } catch (err) {
      const errorMsg = err.response?.data?.error || t('settings.referralActivationFailed');
      setReferralMessage({ type: 'error', text: errorMsg });
    } finally {
      setReferralLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{t('settings.title')}</h1>
        <p className="text-gray-600">{t('settings.subtitle')}</p>
      </div>

      <div className="max-w-2xl">
        <div className="card">
          <h3 className="text-lg font-semibold mb-6">{t('settings.accountInfo')}</h3>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">{t('settings.salonName')}</label>
              <input
                type="text"
                className="input"
                value={settings.salon_name}
                onChange={(e) => setSettings({ ...settings, salon_name: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">{t('settings.email')}</label>
              <input
                type="email"
                className="input"
                value={settings.email}
                onChange={(e) => setSettings({ ...settings, email: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">{t('settings.phone')}</label>
              <input
                type="tel"
                className="input"
                value={settings.phone}
                onChange={(e) => setSettings({ ...settings, phone: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">{t('settings.address')}</label>
              <input
                type="text"
                className="input"
                value={settings.address}
                onChange={(e) => setSettings({ ...settings, address: e.target.value })}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">{t('settings.language')}</label>
                <select
                  className="input"
                  value={settings.language}
                  onChange={(e) => setSettings({ ...settings, language: e.target.value })}
                >
                  <option value="en">{t('settings.languages.en')}</option>
                  <option value="uk">{t('settings.languages.uk')}</option>
                  <option value="pl">{t('settings.languages.pl')}</option>
                  <option value="de">{t('settings.languages.de')}</option>
                  <option value="it">{t('settings.languages.it')}</option>
                  <option value="fr">{t('settings.languages.fr')}</option>
                  <option value="no">{t('settings.languages.no')}</option>
                  <option value="sv">{t('settings.languages.sv')}</option>
                  <option value="be">{t('settings.languages.be')}</option>
                  <option value="es">{t('settings.languages.es')}</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">{t('settings.timezone')}</label>
                <select
                  className="input"
                  value={settings.timezone}
                  onChange={(e) => setSettings({ ...settings, timezone: e.target.value })}
                >
                  <option value="UTC">{t('settings.timezones.utc')}</option>
                  <option value="Europe/Kiev">{t('settings.timezones.kyiv')}</option>
                  <option value="Europe/Warsaw">{t('settings.timezones.warsaw')}</option>
                  <option value="Europe/Berlin">{t('settings.timezones.berlin')}</option>
                  <option value="America/New_York">{t('settings.timezones.newYork')}</option>
                </select>
              </div>
            </div>

            <button type="submit" className="btn-primary flex items-center gap-2">
              <Save size={18} />
              {t('settings.saveChanges')}
            </button>
          </form>
        </div>

        {/* Referral Code Activation */}
        <div className="card mt-6">
          <div className="flex items-center gap-2 mb-4">
            <Gift className="text-primary-500" size={24} />
            <h3 className="text-lg font-semibold">{t('settings.activateReferralCode')}</h3>
          </div>

          <p className="text-gray-600 text-sm mb-4">
            {t('settings.referralCodeDescription')}
          </p>

          {referralMessage.text && (
            <div className={`p-3 rounded-lg mb-4 ${
              referralMessage.type === 'success'
                ? 'bg-green-50 text-green-600'
                : 'bg-red-50 text-red-600'
            }`}>
              {referralMessage.text}
            </div>
          )}

          <form onSubmit={handleActivateReferralCode} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                {t('settings.enterReferralCode')}
              </label>
              <input
                type="text"
                className="input"
                placeholder={t('settings.referralCodePlaceholder')}
                value={referralCode}
                onChange={(e) => setReferralCode(e.target.value)}
                disabled={referralLoading}
              />
            </div>

            <button
              type="submit"
              className="btn-primary flex items-center gap-2"
              disabled={referralLoading || !referralCode.trim()}
            >
              <Gift size={18} />
              {referralLoading ? t('common.loading') : t('settings.activateCode')}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
