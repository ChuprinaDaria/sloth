import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { ArrowLeft, Mail, MessageCircle, Phone, Clock, HelpCircle } from 'lucide-react';

const SupportPage = () => {
  const { t } = useTranslation();
  const [contact, setContact] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchContact();
  }, []);

  const fetchContact = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/core/support-contact/');
      const data = await response.json();
      setContact(data);
    } catch (error) {
      console.error('Failed to fetch support contact:', error);
      setContact({ email: 'support@lazysoft.pl' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-pink-50 to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Link
            to="/"
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft size={20} />
            <span>{t('common.backToHome')}</span>
          </Link>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12">
          <div className="text-center mb-12">
            <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <HelpCircle className="text-white" size={32} />
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              {t('support.title')}
            </h1>
            <p className="text-xl text-gray-600">
              {t('support.subtitle')}
            </p>
          </div>

          {loading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
            </div>
          ) : contact ? (
            <div className="space-y-6">
              {/* Email */}
              <div className="flex items-start gap-4 p-6 bg-gradient-to-br from-green-50 to-white rounded-xl border border-green-100">
                <div className="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Mail className="text-white" size={24} />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-2">{t('support.email')}</h3>
                  <a
                    href={`mailto:${contact.email}`}
                    className="text-green-600 hover:text-green-700 font-medium"
                  >
                    {contact.email}
                  </a>
                </div>
              </div>

              {/* Telegram */}
              {contact.telegram && (
                <div className="flex items-start gap-4 p-6 bg-gradient-to-br from-blue-50 to-white rounded-xl border border-blue-100">
                  <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center flex-shrink-0">
                    <MessageCircle className="text-white" size={24} />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-2">{t('support.telegram')}</h3>
                    <a
                      href={`https://t.me/${contact.telegram.replace('@', '')}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-700 font-medium"
                    >
                      {contact.telegram}
                    </a>
                  </div>
                </div>
              )}

              {/* Phone */}
              {contact.phone && (
                <div className="flex items-start gap-4 p-6 bg-gradient-to-br from-purple-50 to-white rounded-xl border border-purple-100">
                  <div className="w-12 h-12 bg-purple-500 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Phone className="text-white" size={24} />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-2">{t('support.phone')}</h3>
                    <a
                      href={`tel:${contact.phone}`}
                      className="text-purple-600 hover:text-purple-700 font-medium"
                    >
                      {contact.phone}
                    </a>
                  </div>
                </div>
              )}

              {/* Working Hours */}
              {contact.working_hours && (
                <div className="flex items-start gap-4 p-6 bg-gradient-to-br from-pink-50 to-white rounded-xl border border-pink-100">
                  <div className="w-12 h-12 bg-pink-500 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Clock className="text-white" size={24} />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-2">{t('support.workingHours')}</h3>
                    <p className="text-gray-700">{contact.working_hours}</p>
                    {contact.response_time && (
                      <p className="text-sm text-gray-600 mt-2">
                        {t('support.responseTime')}: {contact.response_time}
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-600">{t('support.notFound')}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SupportPage;
