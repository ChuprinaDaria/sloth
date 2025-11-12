import { useState } from 'react';
import { X, Mail, AlertCircle } from 'lucide-react';
import { agentAPI } from '../../api/agent';
import { useTranslation } from 'react-i18next';

const EmailSetup = ({ onClose, onSuccess }) => {
  const { t } = useTranslation();
  const [provider, setProvider] = useState('gmail');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // SMTP fields (backend expects smtp_host, smtp_port, username, password, from_email)
  const [smtpData, setSmtpData] = useState({
    smtp_host: '',
    smtp_port: '587',
    username: '',
    password: '',
    from_email: '',
  });

  const handleGmailConnect = async () => {
    try {
      setLoading(true);
      setError('');

      // Gmail використовує той самий OAuth, що і Calendar
      const { data } = await agentAPI.connectEmail('gmail', {});

      if (data.authorization_url || data.auth_url) {
        window.location.href = data.authorization_url || data.auth_url;
      } else if (data.integration) {
        // вже підключено через Calendar
        setSuccess(true);
        onSuccess?.();
        setTimeout(() => onClose(), 1500);
      }
    } catch (err) {
      const msg = err.response?.data?.error || t('common.error');
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleSMTPConnect = async () => {
    try {
      setLoading(true);
      setError('');

      await agentAPI.connectEmail('smtp', smtpData);
      setSuccess(true);
      onSuccess?.();
      setTimeout(() => onClose(), 1500);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to connect SMTP');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Mail className="text-blue-600" size={24} />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Email Integration</h2>
                <p className="text-sm text-gray-500">Send booking confirmations via email</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <X size={24} />
            </button>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
              <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={18} />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {success && (
            <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-sm text-green-800">✓ Successfully connected email!</p>
            </div>
          )}

          {/* Provider Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Provider
            </label>
            <div className="grid grid-cols-2 gap-4">
              <button
                onClick={() => setProvider('gmail')}
                className={`p-4 border-2 rounded-lg text-left transition-colors ${
                  provider === 'gmail'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="font-medium">Gmail</div>
                <div className="text-xs text-gray-500 mt-1">
                  Google account with analytics (requires Calendar OAuth)
                </div>
              </button>
              <button
                onClick={() => setProvider('smtp')}
                className={`p-4 border-2 rounded-lg text-left transition-colors ${
                  provider === 'smtp'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="font-medium">Corporate Email</div>
                <div className="text-xs text-gray-500 mt-1">
                  SMTP configuration
                </div>
              </button>
            </div>
          </div>

          {provider === 'gmail' ? (
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-medium text-blue-900 mb-2">Gmail Features:</h3>
                <ul className="space-y-2 text-sm text-blue-800">
                  <li className="flex items-start gap-2">
                    <span>✓</span>
                    <span>Send booking confirmations and reminders</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span>✓</span>
                    <span>Email analytics in Smart Analytics</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span>✓</span>
                    <span>Track received/sent emails and top senders</span>
                  </li>
                </ul>
                <p className="text-xs text-blue-700 mt-2">
                  Note: Gmail uses Google OAuth from Calendar. Please connect Calendar first.
                </p>
              </div>

              <button
                onClick={handleGmailConnect}
                disabled={loading}
                className={`w-full py-3 rounded-lg font-medium transition-colors ${
                  loading
                    ? 'bg-gray-300 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                }`}
              >
                {loading ? 'Connecting...' : 'Connect Gmail'}
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  SMTP Host
                </label>
                <input
                  type="text"
                  value={smtpData.smtp_host}
                  onChange={(e) => setSmtpData({ ...smtpData, smtp_host: e.target.value })}
                  placeholder="smtp.your-domain.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Port
                  </label>
                  <input
                    type="number"
                    value={smtpData.smtp_port}
                    onChange={(e) => setSmtpData({ ...smtpData, smtp_port: e.target.value })}
                    placeholder="587"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    From Email
                  </label>
                  <input
                    type="email"
                    value={smtpData.from_email}
                    onChange={(e) => setSmtpData({ ...smtpData, from_email: e.target.value })}
                    placeholder="noreply@your-domain.com"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Username
                </label>
                <input
                  type="text"
                  value={smtpData.username}
                  onChange={(e) => setSmtpData({ ...smtpData, username: e.target.value })}
                  placeholder="username@your-domain.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Password
                </label>
                <input
                  type="password"
                  value={smtpData.password}
                  onChange={(e) => setSmtpData({ ...smtpData, password: e.target.value })}
                  placeholder="••••••••"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <button
                onClick={handleSMTPConnect}
                disabled={loading || !smtpData.smtp_host || !smtpData.username || !smtpData.password}
                className={`w-full py-3 rounded-lg font-medium transition-colors ${
                  loading || !smtpData.smtp_host || !smtpData.username || !smtpData.password
                    ? 'bg-gray-300 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                }`}
              >
                {loading ? 'Connecting...' : 'Connect SMTP'}
              </button>
            </div>
          )}

          <p className="text-xs text-center text-gray-500 mt-4">
            Available for: Starter, Professional, Enterprise plans
          </p>
        </div>
      </div>
    </div>
  );
};

export default EmailSetup;
