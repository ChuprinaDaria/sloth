import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Save } from 'lucide-react';

const SettingsPage = () => {
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
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-gray-600">Manage your account and preferences</p>
      </div>

      <div className="max-w-2xl">
        <div className="card">
          <h3 className="text-lg font-semibold mb-6">Account Information</h3>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Salon Name</label>
              <input
                type="text"
                className="input"
                value={settings.salon_name}
                onChange={(e) => setSettings({ ...settings, salon_name: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Email</label>
              <input
                type="email"
                className="input"
                value={settings.email}
                onChange={(e) => setSettings({ ...settings, email: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Phone</label>
              <input
                type="tel"
                className="input"
                value={settings.phone}
                onChange={(e) => setSettings({ ...settings, phone: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Address</label>
              <input
                type="text"
                className="input"
                value={settings.address}
                onChange={(e) => setSettings({ ...settings, address: e.target.value })}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Language</label>
                <select
                  className="input"
                  value={settings.language}
                  onChange={(e) => setSettings({ ...settings, language: e.target.value })}
                >
                  <option value="en">English</option>
                  <option value="uk">Українська</option>
                  <option value="es">Español</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Timezone</label>
                <select
                  className="input"
                  value={settings.timezone}
                  onChange={(e) => setSettings({ ...settings, timezone: e.target.value })}
                >
                  <option value="UTC">UTC</option>
                  <option value="Europe/Kiev">Kyiv</option>
                  <option value="America/New_York">New York</option>
                </select>
              </div>
            </div>

            <button type="submit" className="btn-primary flex items-center gap-2">
              <Save size={18} />
              Save Changes
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
