import { X, Calendar, CheckCircle } from 'lucide-react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { agentAPI } from '../../api/agent';

const CalendarSetup = ({ onClose }) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleConnect = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await agentAPI.getCalendarAuthUrl();
      // Redirect to Google OAuth
      if (response.data.authorization_url) {
        window.location.href = response.data.authorization_url;
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message || t('common.error'));
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 max-w-lg w-full mx-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold">{t('integrations.setupCalendar')}</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X size={24} />
          </button>
        </div>

        <div className="space-y-4">
          {/* Error message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <div className="text-center py-4">
            <Calendar className="mx-auto text-purple-500 mb-3" size={48} />
            <p className="text-gray-600">
              {t('integrations.calendarNotice')}
            </p>
          </div>

          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <p className="text-sm text-purple-800 mb-2">
              <strong>{t('integrations.calendarSyncInfo')}:</strong>
            </p>
            <ul className="text-sm text-purple-700 space-y-1 list-disc list-inside">
              <li>{t('integrations.calendarItem1')}</li>
              <li>{t('integrations.calendarItem2')}</li>
              <li>{t('integrations.calendarItem3')}</li>
              <li>{t('integrations.calendarItem4')}</li>
            </ul>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              onClick={handleConnect}
              disabled={loading}
              className="btn-primary flex-1"
            >
              {loading ? t('common.loading') : t('integrations.connectWithGoogle')}
            </button>
            <button onClick={onClose} className="btn-secondary flex-1">
              {t('common.cancel')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CalendarSetup;
