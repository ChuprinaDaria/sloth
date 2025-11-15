import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Calendar, ExternalLink, CheckCircle, Save, Settings2 } from 'lucide-react';
import { bookingPreferencesAPI } from '../../api/bookingPreferences';

const BookingPreferences = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const [preferences, setPreferences] = useState({
    use_google_calendar: true,
    auto_sync_to_calendar: true,
    use_buksi: false,
    buksi_api_key: '',
    buksi_salon_id: '',
    booking_buffer_minutes: 15,
    allow_same_day_booking: true,
    max_advance_booking_days: 30,
    send_booking_confirmation: true,
    send_booking_reminder: true,
    reminder_hours_before: 24,
  });

  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      const response = await bookingPreferencesAPI.getPreferences();
      setPreferences(response.data);
    } catch (err) {
      console.error('Failed to load booking preferences:', err);
      setError(t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field, value) => {
    setPreferences(prev => ({ ...prev, [field]: value }));
    setSuccess(false);
  };

  const handleSave = async () => {
    setSaving(true);
    setError('');
    setSuccess(false);

    try {
      await bookingPreferencesAPI.updatePreferences(preferences);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      console.error('Failed to save preferences:', err);
      setError(err.response?.data?.message || t('common.error'));
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <Settings2 className="text-primary-500" size={24} />
            {t('settings.bookingPreferences.title')}
          </h2>
          <p className="text-gray-600 text-sm mt-1">
            {t('settings.bookingPreferences.subtitle')}
          </p>
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          className="btn-primary flex items-center gap-2"
        >
          {saving ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              {t('common.loading')}
            </>
          ) : (
            <>
              <Save size={18} />
              {t('common.save')}
            </>
          )}
        </button>
      </div>

      {/* Success Message */}
      {success && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-green-800">
            <CheckCircle size={20} />
            <span className="font-medium">{t('settings.bookingPreferences.saved')}</span>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Calendar Integration */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Calendar className="text-purple-500" size={20} />
          {t('settings.bookingPreferences.calendar.title')}
        </h3>

        <div className="space-y-4">
          <label className="flex items-start gap-3">
            <input
              type="checkbox"
              checked={preferences.use_google_calendar}
              onChange={(e) => handleChange('use_google_calendar', e.target.checked)}
              className="mt-1"
            />
            <div className="flex-1">
              <span className="font-medium block">
                {t('settings.bookingPreferences.calendar.useGoogleCalendar')}
              </span>
              <span className="text-sm text-gray-600">
                {t('settings.bookingPreferences.calendar.useGoogleCalendarDesc')}
              </span>
            </div>
          </label>

          {preferences.use_google_calendar && (
            <label className="flex items-start gap-3 ml-6">
              <input
                type="checkbox"
                checked={preferences.auto_sync_to_calendar}
                onChange={(e) => handleChange('auto_sync_to_calendar', e.target.checked)}
                className="mt-1"
              />
              <div className="flex-1">
                <span className="font-medium block">
                  {t('settings.bookingPreferences.calendar.autoSync')}
                </span>
                <span className="text-sm text-gray-600">
                  {t('settings.bookingPreferences.calendar.autoSyncDesc')}
                </span>
              </div>
            </label>
          )}
        </div>
      </div>

      {/* Buksi Integration */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <ExternalLink className="text-blue-500" size={20} />
          {t('settings.bookingPreferences.buksi.title')}
        </h3>

        <div className="space-y-4">
          <label className="flex items-start gap-3">
            <input
              type="checkbox"
              checked={preferences.use_buksi}
              onChange={(e) => handleChange('use_buksi', e.target.checked)}
              className="mt-1"
            />
            <div className="flex-1">
              <span className="font-medium block">
                {t('settings.bookingPreferences.buksi.enable')}
              </span>
              <span className="text-sm text-gray-600">
                {t('settings.bookingPreferences.buksi.enableDesc')}
              </span>
            </div>
          </label>

          {preferences.use_buksi && (
            <div className="ml-6 space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  {t('settings.bookingPreferences.buksi.apiKey')}
                </label>
                <input
                  type="password"
                  value={preferences.buksi_api_key}
                  onChange={(e) => handleChange('buksi_api_key', e.target.value)}
                  placeholder={t('settings.bookingPreferences.buksi.apiKeyPlaceholder')}
                  className="input"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  {t('settings.bookingPreferences.buksi.salonId')}
                </label>
                <input
                  type="text"
                  value={preferences.buksi_salon_id}
                  onChange={(e) => handleChange('buksi_salon_id', e.target.value)}
                  placeholder={t('settings.bookingPreferences.buksi.salonIdPlaceholder')}
                  className="input"
                />
              </div>

              <a
                href="https://buksi.me"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-primary-500 hover:underline text-sm"
              >
                <ExternalLink size={16} />
                {t('settings.bookingPreferences.buksi.learnMore')}
              </a>
            </div>
          )}
        </div>
      </div>

      {/* Booking Rules */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">
          {t('settings.bookingPreferences.rules.title')}
        </h3>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              {t('settings.bookingPreferences.rules.bufferTime')}
            </label>
            <select
              value={preferences.booking_buffer_minutes}
              onChange={(e) => handleChange('booking_buffer_minutes', parseInt(e.target.value))}
              className="input"
            >
              <option value="0">{t('settings.bookingPreferences.rules.noBuffer')}</option>
              <option value="15">15 {t('settings.bookingPreferences.rules.minutes')}</option>
              <option value="30">30 {t('settings.bookingPreferences.rules.minutes')}</option>
              <option value="45">45 {t('settings.bookingPreferences.rules.minutes')}</option>
              <option value="60">1 {t('settings.bookingPreferences.rules.hour')}</option>
            </select>
            <p className="text-sm text-gray-600 mt-1">
              {t('settings.bookingPreferences.rules.bufferDesc')}
            </p>
          </div>

          <label className="flex items-start gap-3">
            <input
              type="checkbox"
              checked={preferences.allow_same_day_booking}
              onChange={(e) => handleChange('allow_same_day_booking', e.target.checked)}
              className="mt-1"
            />
            <div className="flex-1">
              <span className="font-medium block">
                {t('settings.bookingPreferences.rules.sameDayBooking')}
              </span>
              <span className="text-sm text-gray-600">
                {t('settings.bookingPreferences.rules.sameDayBookingDesc')}
              </span>
            </div>
          </label>

          <div>
            <label className="block text-sm font-medium mb-2">
              {t('settings.bookingPreferences.rules.maxAdvance')}
            </label>
            <input
              type="number"
              min="1"
              max="365"
              value={preferences.max_advance_booking_days}
              onChange={(e) => handleChange('max_advance_booking_days', parseInt(e.target.value))}
              className="input"
            />
            <p className="text-sm text-gray-600 mt-1">
              {t('settings.bookingPreferences.rules.maxAdvanceDesc')}
            </p>
          </div>
        </div>
      </div>

      {/* Notifications */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">
          {t('settings.bookingPreferences.notifications.title')}
        </h3>

        <div className="space-y-4">
          <label className="flex items-start gap-3">
            <input
              type="checkbox"
              checked={preferences.send_booking_confirmation}
              onChange={(e) => handleChange('send_booking_confirmation', e.target.checked)}
              className="mt-1"
            />
            <div className="flex-1">
              <span className="font-medium block">
                {t('settings.bookingPreferences.notifications.confirmation')}
              </span>
              <span className="text-sm text-gray-600">
                {t('settings.bookingPreferences.notifications.confirmationDesc')}
              </span>
            </div>
          </label>

          <label className="flex items-start gap-3">
            <input
              type="checkbox"
              checked={preferences.send_booking_reminder}
              onChange={(e) => handleChange('send_booking_reminder', e.target.checked)}
              className="mt-1"
            />
            <div className="flex-1">
              <span className="font-medium block">
                {t('settings.bookingPreferences.notifications.reminder')}
              </span>
              <span className="text-sm text-gray-600">
                {t('settings.bookingPreferences.notifications.reminderDesc')}
              </span>
            </div>
          </label>

          {preferences.send_booking_reminder && (
            <div className="ml-6">
              <label className="block text-sm font-medium mb-2">
                {t('settings.bookingPreferences.notifications.reminderTime')}
              </label>
              <select
                value={preferences.reminder_hours_before}
                onChange={(e) => handleChange('reminder_hours_before', parseInt(e.target.value))}
                className="input"
              >
                <option value="1">1 {t('settings.bookingPreferences.rules.hour')}</option>
                <option value="2">2 {t('settings.bookingPreferences.rules.hours')}</option>
                <option value="4">4 {t('settings.bookingPreferences.rules.hours')}</option>
                <option value="12">12 {t('settings.bookingPreferences.rules.hours')}</option>
                <option value="24">24 {t('settings.bookingPreferences.rules.hours')}</option>
                <option value="48">48 {t('settings.bookingPreferences.rules.hours')}</option>
              </select>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BookingPreferences;
