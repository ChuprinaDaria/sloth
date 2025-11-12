import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import IntegrationCard from '../components/integrations/IntegrationCard';
import TelegramSetup from '../components/integrations/TelegramSetup';
import WhatsAppSetup from '../components/integrations/WhatsAppSetup';
import CalendarSetup from '../components/integrations/CalendarSetup';
import GoogleSheetsSetup from '../components/integrations/GoogleSheetsSetup';
import InstagramSetup from '../components/integrations/InstagramSetup';
import GoogleReviewsSetup from '../components/integrations/GoogleReviewsSetup';
import EmailSetup from '../components/integrations/EmailSetup';
import { MessageCircle, Send, Calendar, Sheet, Instagram, Star, Mail } from 'lucide-react';
import { agentAPI as api } from '../api/agent';

const IntegrationsPage = () => {
  const { t } = useTranslation();
  const [activeSetup, setActiveSetup] = useState(null);
  const [connectedIntegrations, setConnectedIntegrations] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch integration status from backend
  useEffect(() => {
    const fetchIntegrations = async () => {
      try {
        const response = await api.getIntegrations();
        const data = response?.data;
        const normalized = Array.isArray(data)
          ? data
          : (Array.isArray(data?.results) ? data.results
            : (Array.isArray(data?.items) ? data.items
              : (Array.isArray(data?.integrations) ? data.integrations : [])));
        setConnectedIntegrations(normalized);
      } catch (error) {
        console.error('Failed to fetch integrations:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchIntegrations();
  }, []);

  // Refresh integrations when setup closes
  const handleCloseSetup = async () => {
    setActiveSetup(null);
    // Reload integrations
    try {
      const response = await api.getIntegrations();
      const data = response?.data;
      const normalized = Array.isArray(data)
        ? data
        : (Array.isArray(data?.results) ? data.results
          : (Array.isArray(data?.items) ? data.items
            : (Array.isArray(data?.integrations) ? data.integrations : [])));
      setConnectedIntegrations(normalized);
    } catch (error) {
      console.error('Failed to refresh integrations:', error);
    }
  };

  const integrationTemplates = [
    {
      id: 'telegram',
      name: t('integrations.telegram'),
      icon: Send,
      description: t('integrations.telegramDesc'),
      status: 'disconnected',
      color: 'blue',
    },
    {
      id: 'whatsapp',
      name: t('integrations.whatsapp'),
      icon: MessageCircle,
      description: t('integrations.whatsappDesc'),
      status: 'disconnected',
      color: 'green',
    },
    {
      id: 'calendar',
      name: t('integrations.calendar'),
      icon: Calendar,
      description: t('integrations.calendarDesc'),
      status: 'disconnected',
      color: 'purple',
    },
    {
      id: 'sheets',
      name: t('integrations.sheets'),
      icon: Sheet,
      description: t('integrations.sheetsDesc'),
      status: 'disconnected',
      color: 'emerald',
      planRequired: 'Starter',
    },
    {
      id: 'instagram',
      name: t('integrations.instagram'),
      icon: Instagram,
      description: t('integrations.instagramDesc'),
      status: 'disconnected',
      color: 'pink',
      planRequired: 'Professional',
    },
    {
      id: 'google-reviews',
      name: t('integrations.googleReviews'),
      icon: Star,
      description: t('integrations.googleReviewsDesc'),
      status: 'disconnected',
      color: 'yellow',
      planRequired: 'Starter',
    },
    {
      id: 'email',
      name: t('integrations.email'),
      icon: Mail,
      description: t('integrations.emailDesc'),
      status: 'disconnected',
      color: 'blue',
      planRequired: 'Starter',
    },
  ];

  // Map backend integration_type to frontend id
  const typeMapping = {
    'telegram': 'telegram',
    'whatsapp': 'whatsapp',
    'google_calendar': 'calendar',
    'google_sheets': 'sheets',
    'instagram': 'instagram',
    'google_my_business': 'google-reviews',
    'email': 'email',
  };

  // Merge templates with actual status from backend
  const safeList = Array.isArray(connectedIntegrations) ? connectedIntegrations : [];
  const integrations = integrationTemplates.map(template => {
    const backendIntegration = safeList.find(
      ci => typeMapping[ci.integration_type] === template.id
    );

    return {
      ...template,
      status: backendIntegration?.status === 'active' ? 'connected' : 'disconnected',
      backendData: backendIntegration
    };
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{t('integrations.title')}</h1>
        <p className="text-gray-600">{t('integrations.subtitle')}</p>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {integrations.map((integration) => (
            <IntegrationCard
              key={integration.id}
              {...integration}
              onSetup={() => setActiveSetup(integration.id)}
            />
          ))}
        </div>
      )}

      {activeSetup === 'telegram' && <TelegramSetup onClose={handleCloseSetup} />}
      {activeSetup === 'whatsapp' && <WhatsAppSetup onClose={handleCloseSetup} />}
      {activeSetup === 'calendar' && <CalendarSetup onClose={handleCloseSetup} />}
      {activeSetup === 'sheets' && <GoogleSheetsSetup onClose={handleCloseSetup} />}
      {activeSetup === 'instagram' && <InstagramSetup onClose={handleCloseSetup} />}
      {activeSetup === 'google-reviews' && <GoogleReviewsSetup onClose={handleCloseSetup} />}
      {activeSetup === 'email' && <EmailSetup onClose={handleCloseSetup} />}
    </div>
  );
};

export default IntegrationsPage;
