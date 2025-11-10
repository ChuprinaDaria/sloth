import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useSearchParams } from 'react-router-dom';
import IntegrationCard from '../components/integrations/IntegrationCard';
import TelegramSetup from '../components/integrations/TelegramSetup';
import WhatsAppSetup from '../components/integrations/WhatsAppSetup';
import CalendarSetup from '../components/integrations/CalendarSetup';
import GoogleSheetsSetup from '../components/integrations/GoogleSheetsSetup';
import InstagramSetup from '../components/integrations/InstagramSetup';
import GoogleReviewsSetup from '../components/integrations/GoogleReviewsSetup';
import EmailSetup from '../components/integrations/EmailSetup';
import { agentAPI } from '../api/agent';
import { MessageCircle, Send, Calendar, Sheet, Instagram, Star, Mail } from 'lucide-react';

const IntegrationsPage = () => {
  const { t } = useTranslation();
  const [activeSetup, setActiveSetup] = useState(null);
  const [integrationsStatus, setIntegrationsStatus] = useState({});
  const [loading, setLoading] = useState(true);
  const [searchParams] = useSearchParams();

  // Load integrations status from API
  useEffect(() => {
    const loadIntegrations = async () => {
      try {
        const response = await agentAPI.getIntegrations();
        const integrations = response.data || [];
        
        // Map integration types to status
        const statusMap = {};
        integrations.forEach(integration => {
          const type = integration.integration_type;
          if (integration.status === 'active') {
            statusMap[type] = 'connected';
            // Map google_my_business to google-reviews
            if (type === 'google_my_business') {
              statusMap['google-reviews'] = 'connected';
            }
          }
        });
        
        setIntegrationsStatus(statusMap);
      } catch (error) {
        console.error('Error loading integrations:', error);
      } finally {
        setLoading(false);
      }
    };

    loadIntegrations();

    // Check for success message in URL
    const success = searchParams.get('success');
    if (success) {
      // Reload integrations after successful connection
      setTimeout(() => {
        loadIntegrations();
      }, 1000);
    }
  }, [searchParams]);

  const integrations = [
    {
      id: 'telegram',
      name: t('integrations.telegram'),
      icon: Send,
      description: t('integrations.telegramDesc'),
      status: integrationsStatus['telegram'] || 'disconnected',
      color: 'blue',
    },
    {
      id: 'whatsapp',
      name: t('integrations.whatsapp'),
      icon: MessageCircle,
      description: t('integrations.whatsappDesc'),
      status: integrationsStatus['whatsapp'] || 'disconnected',
      color: 'green',
    },
    {
      id: 'calendar',
      name: t('integrations.calendar'),
      icon: Calendar,
      description: t('integrations.calendarDesc'),
      status: integrationsStatus['google_calendar'] || 'disconnected',
      color: 'purple',
    },
    {
      id: 'sheets',
      name: t('integrations.sheets'),
      icon: Sheet,
      description: t('integrations.sheetsDesc'),
      status: integrationsStatus['google_sheets'] || 'disconnected',
      color: 'emerald',
      planRequired: 'Starter',
    },
    {
      id: 'instagram',
      name: t('integrations.instagram'),
      icon: Instagram,
      description: t('integrations.instagramDesc'),
      status: integrationsStatus['instagram'] || 'disconnected',
      color: 'pink',
      planRequired: 'Professional',
    },
    {
      id: 'google-reviews',
      name: t('integrations.googleReviews'),
      icon: Star,
      description: t('integrations.googleReviewsDesc'),
      status: integrationsStatus['google-reviews'] || integrationsStatus['google_my_business'] || 'disconnected',
      color: 'yellow',
      planRequired: 'Starter',
    },
    {
      id: 'email',
      name: t('integrations.email'),
      icon: Mail,
      description: t('integrations.emailDesc'),
      status: integrationsStatus['email'] || 'disconnected',
      color: 'blue',
      planRequired: 'Starter',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{t('integrations.title')}</h1>
        <p className="text-gray-600">{t('integrations.subtitle')}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {integrations.map((integration) => (
          <IntegrationCard
            key={integration.id}
            {...integration}
            onSetup={() => setActiveSetup(integration.id)}
          />
        ))}
      </div>

      {activeSetup === 'telegram' && <TelegramSetup onClose={() => setActiveSetup(null)} />}
      {activeSetup === 'whatsapp' && <WhatsAppSetup onClose={() => setActiveSetup(null)} />}
      {activeSetup === 'calendar' && <CalendarSetup onClose={() => setActiveSetup(null)} />}
      {activeSetup === 'sheets' && <GoogleSheetsSetup onClose={() => setActiveSetup(null)} />}
      {activeSetup === 'instagram' && <InstagramSetup onClose={() => setActiveSetup(null)} />}
      {activeSetup === 'google-reviews' && <GoogleReviewsSetup onClose={() => setActiveSetup(null)} />}
      {activeSetup === 'email' && <EmailSetup onClose={() => setActiveSetup(null)} />}
    </div>
  );
};

export default IntegrationsPage;
