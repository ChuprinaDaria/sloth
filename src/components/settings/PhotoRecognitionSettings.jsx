import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Eye,
  Plus,
  Trash2,
  CheckCircle,
  Star,
  ExternalLink,
  Lock,
  AlertCircle,
  Crown
} from 'lucide-react';
import { photoRecognitionAPI } from '../../api/photoRecognition';
import { useAuth } from '../../context/AuthContext';

const PhotoRecognitionSettings = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [providers, setProviders] = useState([]);
  const [myConfigs, setMyConfigs] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState(null);
  const [apiKey, setApiKey] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Get user's subscription tier
  const subscriptionTier = user?.subscription?.plan?.slug || 'free';

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [providersRes, configsRes] = await Promise.all([
        photoRecognitionAPI.getProviders(),
        photoRecognitionAPI.getMyConfigs()
      ]);
      setProviders(providersRes.data);
      setMyConfigs(configsRes.data);
    } catch (err) {
      console.error('Failed to load photo recognition settings:', err);
      setError(t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const handleAddProvider = (provider) => {
    setSelectedProvider(provider);
    setApiKey('');
    setError('');
    setSuccess('');
    setShowAddModal(true);
  };

  const handleSaveProvider = async () => {
    if (!selectedProvider) return;

    // For starter tier GPT-4, API key is not required
    const requiresApiKey = !(
      subscriptionTier === 'starter' && selectedProvider.slug === 'gpt4_vision'
    );

    if (requiresApiKey && !apiKey.trim()) {
      setError(t('settings.photoRecognition.errors.apiKeyRequired'));
      return;
    }

    setSaving(true);
    setError('');

    try {
      await photoRecognitionAPI.configureProvider({
        provider_slug: selectedProvider.slug,
        api_key: apiKey
      });

      setSuccess(t('settings.photoRecognition.success.providerAdded'));
      setShowAddModal(false);
      loadData();

      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error('Failed to configure provider:', err);
      setError(
        err.response?.data?.error ||
        t('settings.photoRecognition.errors.configFailed')
      );
    } finally {
      setSaving(false);
    }
  };

  const handleSetDefault = async (configId) => {
    try {
      await photoRecognitionAPI.setDefault(configId);
      setSuccess(t('settings.photoRecognition.success.defaultSet'));
      loadData();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error('Failed to set default:', err);
      setError(t('common.error'));
    }
  };

  const handleDelete = async (configId) => {
    if (!window.confirm(t('settings.photoRecognition.confirmDelete'))) {
      return;
    }

    try {
      await photoRecognitionAPI.deleteConfig(configId);
      setSuccess(t('settings.photoRecognition.success.providerDeleted'));
      loadData();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error('Failed to delete config:', err);
      setError(t('common.error'));
    }
  };

  const getProviderIcon = (slug) => {
    const icons = {
      gpt4_vision: '🤖',
      claude_opus: '🧠',
      claude_sonnet: '💡',
      gemini_pro: '✨'
    };
    return icons[slug] || '🔮';
  };

  const isProviderConfigured = (providerSlug) => {
    return myConfigs.some(config => config.provider.slug === providerSlug);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  // Show upgrade message for free tier
  if (subscriptionTier === 'free') {
    return (
      <div className="card">
        <div className="flex items-start gap-4">
          <Lock className="text-gray-400" size={48} />
          <div className="flex-1">
            <h3 className="text-lg font-semibold mb-2">
              {t('settings.photoRecognition.upgradeRequired')}
            </h3>
            <p className="text-gray-600 mb-4">
              {t('settings.photoRecognition.upgradeDescription')}
            </p>
            <button className="btn-primary flex items-center gap-2">
              <Crown size={18} />
              {t('settings.photoRecognition.upgradeNow')}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <Eye className="text-primary-500" size={24} />
          {t('settings.photoRecognition.title')}
        </h2>
        <p className="text-gray-600 text-sm mt-1">
          {t('settings.photoRecognition.subtitle')}
        </p>
      </div>

      {/* Success/Error Messages */}
      {success && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-green-800">
            <CheckCircle size={20} />
            <span className="font-medium">{success}</span>
          </div>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-800">
            <AlertCircle size={20} />
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Configured Providers */}
      {myConfigs.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">
            {t('settings.photoRecognition.configuredProviders')}
          </h3>

          <div className="space-y-3">
            {myConfigs.map((config) => (
              <div
                key={config.id}
                className={`flex items-center justify-between p-4 rounded-lg border-2 ${
                  config.is_default
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200'
                }`}
              >
                <div className="flex items-center gap-3 flex-1">
                  <span className="text-2xl">{getProviderIcon(config.provider.slug)}</span>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{config.provider.name}</span>
                      {config.is_default && (
                        <Star size={16} className="text-yellow-500 fill-yellow-500" />
                      )}
                    </div>
                    <div className="text-sm text-gray-600">
                      {config.images_processed} {t('settings.photoRecognition.imagesProcessed')}
                      {' • '}
                      ${config.total_cost.toFixed(2)} {t('settings.photoRecognition.spent')}
                    </div>
                    {config.masked_api_key && (
                      <div className="text-xs text-gray-500 font-mono">
                        {config.masked_api_key}
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {!config.is_default && (
                    <button
                      onClick={() => handleSetDefault(config.id)}
                      className="btn-secondary text-sm"
                      title={t('settings.photoRecognition.setAsDefault')}
                    >
                      <Star size={16} />
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(config.id)}
                    className="btn-danger text-sm"
                    title={t('common.delete')}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Available Providers */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">
          {t('settings.photoRecognition.availableProviders')}
        </h3>

        {providers.length === 0 ? (
          <p className="text-gray-600">
            {t('settings.photoRecognition.noProvidersAvailable')}
          </p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {providers.map((provider) => {
              const configured = isProviderConfigured(provider.slug);
              const isStarterGPT4 = subscriptionTier === 'starter' && provider.slug === 'gpt4_vision';

              return (
                <div
                  key={provider.id}
                  className={`border-2 rounded-lg p-4 ${
                    configured ? 'border-gray-300 bg-gray-50' : 'border-gray-200'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-3xl">{getProviderIcon(provider.slug)}</span>
                    <div className="flex-1">
                      <h4 className="font-semibold">{provider.name}</h4>
                      <p className="text-sm text-gray-600 mt-1">
                        {provider.description}
                      </p>
                      <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                        <span>${provider.cost_per_image} {t('settings.photoRecognition.perImage')}</span>
                        {provider.available_in_professional_only && (
                          <span className="bg-purple-100 text-purple-700 px-2 py-0.5 rounded">
                            {t('settings.photoRecognition.professionalOnly')}
                          </span>
                        )}
                      </div>

                      {isStarterGPT4 && (
                        <div className="mt-2 text-xs text-blue-600 bg-blue-50 p-2 rounded">
                          {t('settings.photoRecognition.starterIncluded')}
                        </div>
                      )}

                      <div className="flex items-center gap-2 mt-3">
                        <button
                          onClick={() => handleAddProvider(provider)}
                          disabled={configured}
                          className={`btn-primary text-sm flex items-center gap-1 ${
                            configured ? 'opacity-50 cursor-not-allowed' : ''
                          }`}
                        >
                          <Plus size={16} />
                          {configured
                            ? t('settings.photoRecognition.configured')
                            : t('settings.photoRecognition.configure')}
                        </button>
                        <a
                          href={provider.api_documentation_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-primary-500 hover:underline text-sm flex items-center gap-1"
                        >
                          <ExternalLink size={14} />
                          {t('settings.photoRecognition.docs')}
                        </a>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Add Provider Modal */}
      {showAddModal && selectedProvider && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">
              {t('settings.photoRecognition.configureProvider', { name: selectedProvider.name })}
            </h3>

            {subscriptionTier === 'starter' && selectedProvider.slug === 'gpt4_vision' ? (
              <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-blue-800">
                  {t('settings.photoRecognition.starterAutomatic')}
                </p>
              </div>
            ) : (
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">
                  {t('settings.photoRecognition.apiKey')}
                </label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder={t('settings.photoRecognition.apiKeyPlaceholder')}
                  className="input"
                  autoFocus
                />
                <a
                  href={selectedProvider.api_documentation_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-sm text-primary-500 hover:underline mt-2"
                >
                  <ExternalLink size={14} />
                  {t('settings.photoRecognition.howToGetApiKey')}
                </a>
              </div>
            )}

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-800">
                {error}
              </div>
            )}

            <div className="flex items-center gap-2">
              <button
                onClick={handleSaveProvider}
                disabled={saving}
                className="btn-primary flex items-center gap-2 flex-1"
              >
                {saving ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    {t('common.loading')}
                  </>
                ) : (
                  <>
                    <CheckCircle size={18} />
                    {t('settings.photoRecognition.save')}
                  </>
                )}
              </button>
              <button
                onClick={() => setShowAddModal(false)}
                disabled={saving}
                className="btn-secondary flex-1"
              >
                {t('common.cancel')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PhotoRecognitionSettings;
