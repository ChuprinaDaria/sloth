import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { ArrowLeft, Globe } from 'lucide-react';

const PrivacyPolicyPage = () => {
  const { t, i18n } = useTranslation();
  const [policy, setPolicy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedLang, setSelectedLang] = useState(i18n.language.split('-')[0]);

  const languages = [
    { code: 'uk', name: 'Українська' },
    { code: 'en', name: 'English' },
    { code: 'pl', name: 'Polski' },
    { code: 'ru', name: 'Русский' },
  ];

  useEffect(() => {
    fetchPolicy(selectedLang);
  }, [selectedLang]);

  const fetchPolicy = async (lang) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/core/privacy-policy/?lang=${lang}`);
      const data = await response.json();
      setPolicy(data);
    } catch (error) {
      console.error('Failed to fetch privacy policy:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-pink-50 to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <Link
              to="/"
              className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ArrowLeft size={20} />
              <span>{t('common.backToHome')}</span>
            </Link>

            {/* Language Selector */}
            <div className="flex items-center gap-2">
              <Globe size={20} className="text-gray-600" />
              <select
                value={selectedLang}
                onChange={(e) => setSelectedLang(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                {languages.map((lang) => (
                  <option key={lang.code} value={lang.code}>
                    {lang.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12">
          {loading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
            </div>
          ) : policy ? (
            <>
              <div className="mb-8">
                <h1 className="text-4xl font-bold text-gray-900 mb-4">
                  {policy.title}
                </h1>
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <span>{t('privacyPolicy.version')}: {policy.version}</span>
                  <span>•</span>
                  <span>
                    {t('privacyPolicy.lastUpdated')}: {new Date(policy.last_updated).toLocaleDateString(selectedLang)}
                  </span>
                </div>
              </div>

              <div
                className="prose prose-lg max-w-none"
                dangerouslySetInnerHTML={{ __html: policy.content }}
              />
            </>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-600">{t('privacyPolicy.notFound')}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PrivacyPolicyPage;
