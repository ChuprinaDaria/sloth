import { useState } from 'react';
import { X, Star, AlertCircle } from 'lucide-react';
import { agentAPI } from '../../api/agent';
import { useTranslation } from 'react-i18next';

const GoogleReviewsSetup = ({ onClose }) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleConnect = async () => {
    try {
      setLoading(true);
      setError('');

      // Get OAuth URL
      const { data } = await agentAPI.getGoogleReviewsAuthUrl();

      // Redirect to Google OAuth
      window.location.href = data.auth_url;
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to connect to Google My Business');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                <Star className="text-yellow-600" size={24} />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Google Reviews</h2>
                <p className="text-sm text-gray-500">Google My Business Integration</p>
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
              <p className="text-sm text-green-800">✓ Successfully connected to Google Reviews!</p>
            </div>
          )}

          <div className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-medium text-blue-900 mb-2">Features:</h3>
              <ul className="space-y-2 text-sm text-blue-800">
                <li className="flex items-start gap-2">
                  <span className="text-blue-500">✓</span>
                  <span>AI analyzes your reviews for strengths and weaknesses</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-500">✓</span>
                  <span>Automatic objection handling tips from reviews</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-500">✓</span>
                  <span>Reviews summary in Smart Analytics</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-500">✓</span>
                  <span>AI uses reviews context to handle client objections</span>
                </li>
              </ul>
            </div>

            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">Setup Instructions:</h4>
              <ol className="space-y-2 text-sm text-gray-600 list-decimal list-inside">
                <li>Click "Connect Google My Business"</li>
                <li>Sign in with your Google Business account</li>
                <li>Grant permissions to access your reviews</li>
                <li>AI will automatically analyze your reviews</li>
              </ol>
            </div>

            <button
              onClick={handleConnect}
              disabled={loading}
              className={`w-full py-3 rounded-lg font-medium transition-colors ${
                loading
                  ? 'bg-gray-300 cursor-not-allowed'
                  : 'bg-yellow-600 hover:bg-yellow-700 text-white'
              }`}
            >
              {loading ? 'Connecting...' : 'Connect Google My Business'}
            </button>

            <p className="text-xs text-center text-gray-500">
              Available for: Starter, Professional, Enterprise plans
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GoogleReviewsSetup;
