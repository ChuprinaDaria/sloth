import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { Save } from 'lucide-react';
import BookingPreferences from '../components/settings/BookingPreferences';

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

  const handleSubmit = (e) => {
    e.preventDefault();
    // Save settings
    console.log('Saving settings:', settings);
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

        {/* Booking Preferences */}
        <BookingPreferences />
      </div>
    </div>
  );
};

export default SettingsPage;
